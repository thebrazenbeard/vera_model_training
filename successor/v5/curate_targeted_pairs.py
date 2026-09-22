from __future__ import annotations

import hashlib
import json
import math
import re
import gc
from collections import defaultdict
from pathlib import Path
from typing import Any

from successor.v5.generate_targeted_pairs import DIMENSIONS, QUOTAS

JUDGE_REPO = "Qwen/Qwen2.5-14B-Instruct"
JUDGE_REV = "cf98f3b3bbb457ad9e2bb7baf9a0125b6b88caa8"

BANNED_PROMPT_MARKERS = (
    "taxonomy", "training example", "training data", "benchmark", "evaluation rubric",
    "preferred response", "rejected response", "chosen response", "disfavored response",
)
BANNED_PROJECT_MARKERS = (
    "thebrazenbeard", "god-brain", "hc-brain", "driftguard", "chat-communication-bus",
    "vera_model_training", "build team two", "project lantern", "veramesh", "vera mesh",
)


def normalize(text: str) -> str:
    return " ".join(re.findall(r"[a-z0-9']+", text.lower()))


def word_shingles(text: str, n: int = 4) -> set[str]:
    words = normalize(text).split()
    if len(words) < n:
        return {" ".join(words)} if words else set()
    return {" ".join(words[i:i+n]) for i in range(len(words)-n+1)}


def minhash_signature(text: str, k: int = 12) -> tuple[int, ...]:
    vals = sorted(int(hashlib.sha256(s.encode()).hexdigest()[:16], 16) for s in word_shingles(text))
    return tuple(vals[:k])


class NearDuplicateIndex:
    def __init__(self):
        self.signatures: dict[str, tuple[int, ...]] = {}
        self.inverted: dict[int, set[str]] = defaultdict(set)

    def is_near(self, key: str, text: str) -> bool:
        sig = minhash_signature(text)
        if not sig:
            return True
        candidates: set[str] = set()
        for v in sig:
            candidates.update(self.inverted.get(v, ()))
        a = set(sig)
        for other in candidates:
            b = set(self.signatures[other])
            if len(a & b) >= max(4, min(len(a), len(b)) // 2):
                return True
        self.signatures[key] = sig
        for v in sig:
            self.inverted[v].add(key)
        return False


def deterministic_reason(row: dict, index: NearDuplicateIndex) -> str | None:
    prompt = row.get("prompt", "").strip()
    chosen = row.get("chosen", "").strip()
    rejected = row.get("rejected", "").strip()
    if not prompt or not chosen or not rejected:
        return "empty_field"
    if chosen == rejected:
        return "identical_responses"
    if not 20 <= len(prompt) <= 3000:
        return "prompt_length"
    if not 30 <= len(chosen) <= 5000 or not 30 <= len(rejected) <= 5000:
        return "response_length"
    ratio = (len(chosen) + 1) / (len(rejected) + 1)
    if not 0.60 <= ratio <= 1.70:
        return "chosen_rejected_length_ratio"
    low = (prompt + "\n" + chosen + "\n" + rejected).lower()
    if any(marker in prompt.lower() for marker in BANNED_PROMPT_MARKERS):
        return "meta_training_marker"
    if any(marker in low for marker in BANNED_PROJECT_MARKERS):
        return "project_marker"
    if normalize(chosen) == normalize(rejected):
        return "normalized_identical_responses"
    cset, rset = word_shingles(chosen, 3), word_shingles(rejected, 3)
    if cset and rset:
        jaccard = len(cset & rset) / max(1, len(cset | rset))
        if jaccard > 0.92:
            return "responses_too_similar"
    if index.is_near(row["candidate_id"], prompt):
        return "near_duplicate_prompt"
    return None


SYSTEM = """You are an independent curator of behavioral preference data.
Your task is to decide whether a candidate pair genuinely teaches ONE requested behavioral distinction.

The pair must be useful even if the behavior label is removed:
- the user prompt must be natural and self-contained;
- both responses must be fluent and plausibly helpful;
- the preferred response must actually be better on the target distinction;
- the disfavored response must fail subtly, not as a caricature;
- the preferred response must not win mainly because it is longer, more detailed, safer, or factually advantaged on an unrelated issue;
- no answer should talk about training, benchmarks, taxonomies, or being the preferred/rejected answer;
- the pair should not require private context or a named project;
- the distinction should generalize to unrelated users and domains.

Return JSON only with:
pass (boolean),
target_isolated (1-5),
naturalness (1-5),
bad_plausibility (1-5),
length_fairness (1-5),
substance (1-5),
reason (one concise sentence).
A pass requires every numeric field >= 4.
"""


def judge_prompt(row: dict) -> str:
    d = DIMENSIONS[row["dimension"]]
    return f"""Behavior to isolate:
Desired: {d['target']}
Failure mode: {d['failures']}

USER PROMPT:
{row['prompt']}

PREFERRED RESPONSE:
{row['chosen']}

DISFAVORED RESPONSE:
{row['rejected']}

Judge only whether this is a strong contrastive training pair for the requested behavior."""


def parse_object(text: str) -> dict[str, Any] | None:
    start, end = text.find("{"), text.rfind("}")
    if start < 0 or end <= start:
        return None
    try:
        obj = json.loads(text[start:end+1])
    except json.JSONDecodeError:
        return None
    return obj if isinstance(obj, dict) else None


def model_judge(rows: list[dict], batch_size: int = 8) -> list[dict]:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

    tokenizer = AutoTokenizer.from_pretrained(JUDGE_REPO, revision=JUDGE_REV)
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "left"
    quant = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_use_double_quant=True,
        bnb_4bit_compute_dtype=torch.bfloat16,
    )
    model = AutoModelForCausalLM.from_pretrained(
        JUDGE_REPO,
        revision=JUDGE_REV,
        quantization_config=quant,
        device_map={"":0},
        dtype=torch.bfloat16,
    )
    model.eval()
    out: list[dict] = []
    for start in range(0, len(rows), batch_size):
        batch = rows[start:start+batch_size]
        rendered = [
            tokenizer.apply_chat_template(
                [{"role":"system","content":SYSTEM},{"role":"user","content":judge_prompt(row)}],
                tokenize=False,
                add_generation_prompt=True,
            )
            for row in batch
        ]
        inputs = tokenizer(rendered, return_tensors="pt", padding=True, truncation=True, max_length=3200).to(model.device)
        with torch.inference_mode():
            generated = model.generate(
                **inputs,
                max_new_tokens=180,
                do_sample=False,
                pad_token_id=tokenizer.pad_token_id,
            )
        for bi, row in enumerate(batch):
            text = tokenizer.decode(generated[bi, inputs["input_ids"].shape[1]:], skip_special_tokens=True)
            verdict = parse_object(text)
            if verdict is None:
                continue
            numeric = [verdict.get(k) for k in ("target_isolated","naturalness","bad_plausibility","length_fairness","substance")]
            pass_flag = verdict.get("pass") is True and all(isinstance(x,(int,float)) and not isinstance(x,bool) and x >= 4 for x in numeric)
            if not pass_flag:
                continue
            accepted = dict(row)
            accepted["curation"] = {
                "judge_repo": JUDGE_REPO,
                "judge_revision": JUDGE_REV,
                "target_isolated": verdict["target_isolated"],
                "naturalness": verdict["naturalness"],
                "bad_plausibility": verdict["bad_plausibility"],
                "length_fairness": verdict["length_fairness"],
                "substance": verdict["substance"],
                "reason": str(verdict.get("reason",""))[:500],
            }
            out.append(accepted)
    del model
    gc.collect()
    if torch.cuda.is_available(): torch.cuda.empty_cache()
    return out


def curate(candidate_path: Path, output_path: Path) -> dict:
    candidates = [json.loads(x) for x in candidate_path.read_text(encoding="utf-8").splitlines() if x.strip()]
    index = NearDuplicateIndex()
    deterministic_pass: list[dict] = []
    rejections = defaultdict(int)
    for row in candidates:
        reason = deterministic_reason(row, index)
        if reason:
            rejections[reason] += 1
        else:
            deterministic_pass.append(row)

    judged = model_judge(deterministic_pass)
    by_dim: dict[str, list[dict]] = defaultdict(list)
    for row in judged:
        by_dim[row["dimension"]].append(row)

    accepted: list[dict] = []
    stats = {}
    for dim, quota in QUOTAS.items():
        ranked = sorted(by_dim.get(dim, []), key=lambda r: hashlib.sha256(("v5-final:"+r["pair_sha256"]).encode()).hexdigest())
        chosen = ranked[:quota]
        if len(chosen) != quota:
            raise RuntimeError(f"{dim} curated {len(chosen)}/{quota}; generated/judged pool insufficient")
        accepted.extend(chosen)
        stats[dim] = {
            "quota": quota,
            "model_judge_pass": len(ranked),
            "accepted": len(chosen),
        }

    accepted.sort(key=lambda r: hashlib.sha256(("v5-target-order:"+r["pair_sha256"]).encode()).hexdigest())
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = ("\n".join(json.dumps(row, ensure_ascii=False, separators=(",",":")) for row in accepted) + "\n").encode()
    output_path.write_bytes(payload)
    return {
        "schema":"VERA_V5_TARGETED_CURATED_MANIFEST_V1",
        "candidate_rows":len(candidates),
        "deterministic_pass":len(deterministic_pass),
        "model_judge_pass":len(judged),
        "accepted_rows":len(accepted),
        "rejection_counts":dict(sorted(rejections.items())),
        "stats":stats,
        "sha256":hashlib.sha256(payload).hexdigest(),
        "judge_repo":JUDGE_REPO,
        "judge_revision":JUDGE_REV,
    }


if __name__=="__main__":
    import argparse
    ap=argparse.ArgumentParser()
    ap.add_argument("--candidates",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()
    print(json.dumps(curate(args.candidates,args.output),sort_keys=True))
