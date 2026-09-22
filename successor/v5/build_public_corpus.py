from __future__ import annotations

import hashlib
import json
import random
from pathlib import Path
from typing import Iterable

UF_REPO = "HuggingFaceH4/ultrafeedback_binarized"
UF_REV = "3949bf5f8c17c394422ccfab0c31ea9c20bdeb85"
SMOL_REPO = "HuggingFaceTB/smoltalk2"
SMOL_REV = "fc6cc2103c066455aade5d7fbb346039ae36ca5e"
SMOL_CONFIG = "SFT"
TOKENIZER_REPO = "HuggingFaceTB/SmolLM3-3B"
TOKENIZER_REV = "a07cc9a04f16550a088caea529712d1d335b0ac1"
SYSTEM = {"role": "system", "content": "/no_think /system_override"}
SEED = 20260922
MAX_TOKENS = 1536

SMOL_SFT_TARGETS = {
    "smoltalk_smollm3_explore_instruct_rewriting_no_think": 8000,
    "smoltalk_smollm3_smol_rewrite_no_think": 6000,
    "smoltalk_smollm3_smol_summarize_no_think": 6000,
    "Mixture_of_Thoughts_science_no_think": 6000,
    "table_gpt_no_think": 4000,
}


def stable_digest(*parts: str) -> str:
    return hashlib.sha256("\0".join(parts).encode("utf-8")).hexdigest()


def pair_from_messages(messages) -> tuple[str, str] | None:
    if not isinstance(messages, list) or len(messages) != 2:
        return None
    a, b = messages
    if not isinstance(a, dict) or not isinstance(b, dict):
        return None
    if a.get("role") != "user" or b.get("role") != "assistant":
        return None
    prompt, response = a.get("content"), b.get("content")
    if not isinstance(prompt, str) or not isinstance(response, str):
        return None
    prompt, response = prompt.strip(), response.strip()
    if not prompt or not response:
        return None
    return prompt, response


def rendered_tokens(tokenizer, prompt: str, response: str) -> int:
    text = tokenizer.apply_chat_template(
        [SYSTEM, {"role": "user", "content": prompt}, {"role": "assistant", "content": response}],
        tokenize=False,
        add_generation_prompt=False,
        enable_thinking=False,
    )
    return len(tokenizer(text, add_special_tokens=False)["input_ids"])


def write_jsonl(path: Path, rows: list[dict]) -> dict:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = ("\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in rows) + "\n").encode("utf-8")
    path.write_bytes(payload)
    return {"rows": len(rows), "bytes": len(payload), "sha256": hashlib.sha256(payload).hexdigest()}


def build_general_sft(tokenizer) -> tuple[list[dict], dict]:
    from datasets import load_dataset

    rows: list[dict] = []
    seen: set[str] = set()
    source_counts: dict[str, int] = {}

    uf = load_dataset(UF_REPO, split="train_sft", revision=UF_REV)
    order = list(range(len(uf)))
    random.Random(SEED + 11).shuffle(order)
    accepted = 0
    for idx in order:
        row = uf[idx]
        pair = pair_from_messages(row.get("messages"))
        if pair is None:
            continue
        prompt, response = pair
        digest = stable_digest(prompt, response)
        if digest in seen or rendered_tokens(tokenizer, prompt, response) > MAX_TOKENS:
            continue
        seen.add(digest)
        rows.append({
            "schema": "VERA_V5_SFT_ROW_V1",
            "record_id": f"v5-uf-sft-{row.get('prompt_id') or digest[:24]}",
            "source_class": "general_sft",
            "source_repo": UF_REPO,
            "source_revision": UF_REV,
            "source_split": "train_sft",
            "prompt": prompt,
            "response": response,
            "pair_sha256": digest,
        })
        accepted += 1
        if accepted >= 40000:
            break
    if accepted != 40000:
        raise RuntimeError(f"UltraFeedback SFT accepted {accepted}/40000")
    source_counts["ultrafeedback_train_sft"] = accepted

    for split_i, (split, target) in enumerate(SMOL_SFT_TARGETS.items()):
        stream = load_dataset(
            SMOL_REPO,
            SMOL_CONFIG,
            split=split,
            revision=SMOL_REV,
            streaming=True,
        ).shuffle(seed=SEED + 101 + split_i * 1009, buffer_size=20000)
        accepted = 0
        for row in stream:
            pair = pair_from_messages(row.get("messages"))
            if pair is None:
                continue
            prompt, response = pair
            digest = stable_digest(prompt, response)
            if digest in seen or rendered_tokens(tokenizer, prompt, response) > MAX_TOKENS:
                continue
            seen.add(digest)
            rows.append({
                "schema": "VERA_V5_SFT_ROW_V1",
                "record_id": f"v5-smol-{split}-{digest[:24]}",
                "source_class": "general_sft",
                "source_repo": SMOL_REPO,
                "source_revision": SMOL_REV,
                "source_split": split,
                "source": row.get("source"),
                "prompt": prompt,
                "response": response,
                "pair_sha256": digest,
            })
            accepted += 1
            if accepted >= target:
                break
        if accepted != target:
            raise RuntimeError(f"{split} accepted {accepted}/{target}")
        source_counts[split] = accepted

    if len(rows) != 70000 or len(seen) != 70000:
        raise RuntimeError(f"general SFT count mismatch rows={len(rows)} unique={len(seen)}")
    random.Random(SEED + 211).shuffle(rows)
    return rows, {"rows": len(rows), "unique_pairs": len(seen), "source_counts": source_counts}


def build_general_preferences(tokenizer) -> tuple[list[dict], dict]:
    from datasets import load_dataset

    ds = load_dataset(UF_REPO, split="train_prefs", revision=UF_REV)
    eligible: list[dict] = []
    seen: set[str] = set()
    rejection = {"score_margin": 0, "shape": 0, "length_ratio": 0, "tokens": 0, "duplicate": 0}

    for row in ds:
        try:
            margin = float(row["score_chosen"]) - float(row["score_rejected"])
        except Exception:
            rejection["shape"] += 1
            continue
        if margin < 1.0:
            rejection["score_margin"] += 1
            continue
        chosen_pair = pair_from_messages(row.get("chosen"))
        rejected_pair = pair_from_messages(row.get("rejected"))
        if chosen_pair is None or rejected_pair is None or chosen_pair[0] != rejected_pair[0]:
            rejection["shape"] += 1
            continue
        prompt = chosen_pair[0]
        chosen = chosen_pair[1]
        rejected = rejected_pair[1]
        ratio = (len(chosen) + 1) / (len(rejected) + 1)
        if not 0.5 <= ratio <= 2.0:
            rejection["length_ratio"] += 1
            continue
        if max(rendered_tokens(tokenizer, prompt, chosen), rendered_tokens(tokenizer, prompt, rejected)) > MAX_TOKENS:
            rejection["tokens"] += 1
            continue
        digest = stable_digest(prompt, chosen, rejected)
        if digest in seen:
            rejection["duplicate"] += 1
            continue
        seen.add(digest)
        eligible.append({
            "schema": "VERA_V5_PREFERENCE_ROW_V1",
            "record_id": f"v5-uf-pref-{row.get('prompt_id') or digest[:24]}",
            "source_class": "general_preference",
            "source_repo": UF_REPO,
            "source_revision": UF_REV,
            "source_split": "train_prefs",
            "prompt": prompt,
            "chosen": chosen,
            "rejected": rejected,
            "score_chosen": float(row["score_chosen"]),
            "score_rejected": float(row["score_rejected"]),
            "pair_sha256": digest,
        })

    eligible.sort(key=lambda r: stable_digest(str(SEED), r["record_id"]))
    rows = eligible[:20000]
    if len(rows) != 20000:
        raise RuntimeError(f"general preference accepted {len(rows)}/20000")
    return rows, {
        "rows": len(rows),
        "eligible_before_cap": len(eligible),
        "rejection_counts": rejection,
    }


def build_seed_pool(general_sft: list[dict], target: int = 24000) -> list[dict]:
    ranked = sorted(general_sft, key=lambda r: stable_digest("seed-pool", r["record_id"]))
    seeds: list[dict] = []
    seen_prompts: set[str] = set()
    for row in ranked:
        normalized = " ".join(row["prompt"].lower().split())
        digest = hashlib.sha256(normalized.encode()).hexdigest()
        if digest in seen_prompts:
            continue
        seen_prompts.add(digest)
        seeds.append({
            "schema": "VERA_V5_TARGET_SEED_V1",
            "seed_id": f"seed-{len(seeds)+1:05d}",
            "source_record_id": row["record_id"],
            "source_class": row["source_class"],
            "topic_prompt": row["prompt"],
            "topic_prompt_sha256": hashlib.sha256(row["prompt"].encode()).hexdigest(),
        })
        if len(seeds) >= target:
            break
    if len(seeds) != target:
        raise RuntimeError(f"seed pool accepted {len(seeds)}/{target}")
    return seeds


def build(output_dir: Path) -> dict:
    import datasets
    import transformers
    from transformers import AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(TOKENIZER_REPO, revision=TOKENIZER_REV)
    sft, sft_meta = build_general_sft(tokenizer)
    prefs, pref_meta = build_general_preferences(tokenizer)
    seeds = build_seed_pool(sft)

    files = {
        "general_sft": write_jsonl(output_dir / "general_sft.jsonl", sft),
        "general_preferences": write_jsonl(output_dir / "general_preferences.jsonl", prefs),
        "target_seeds": write_jsonl(output_dir / "target_seeds.jsonl", seeds),
    }
    manifest = {
        "schema": "VERA_V5_PUBLIC_CORPUS_MANIFEST_V1",
        "datasets_version": datasets.__version__,
        "transformers_version": transformers.__version__,
        "tokenizer_repo": TOKENIZER_REPO,
        "tokenizer_revision": TOKENIZER_REV,
        "seed": SEED,
        "max_tokens": MAX_TOKENS,
        "sft": sft_meta,
        "preferences": pref_meta,
        "files": files,
    }
    canonical = json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode()
    manifest["manifest_sha256"] = hashlib.sha256(canonical).hexdigest()
    (output_dir / "public_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--output-dir", type=Path, required=True)
    args = ap.parse_args()
    print(json.dumps(build(args.output_dir), sort_keys=True))
