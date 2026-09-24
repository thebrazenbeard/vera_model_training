from __future__ import annotations

import argparse
import hashlib
import json
import math
import tarfile
import urllib.request
from collections import defaultdict
from pathlib import Path

BASE_REPO = "rodrigomt/Qwen3.5-4B-Uncensored-Aggressive"
BASE_REV = "d61dd146c8fd44c9a49cdb7f59f34e17b61902d8"
ARTIFACT_COMMIT = "24ec44412ece8264693ded920f09dec85bbfccc5"
ARTIFACT_SHA256 = "990fe607d76f457037b8b4c2db71ab6c69ee0a99f13cc7d2357b168798ea1d53"
PART_COUNT = 11
HOLDOUT_URL = "https://raw.githubusercontent.com/thebrazenbeard/vera_model_training/513f8410c0c2d4768efa8e6bb845d6df028b2cbc/successor/qwen35/qualification/history_behavior_holdout_v1.jsonl"
MAX_LENGTH = 1024


def raw_url(path: str) -> str:
    return f"https://raw.githubusercontent.com/thebrazenbeard/vera_model_training/{ARTIFACT_COMMIT}/{path}"


def download(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "vera-qwen35-qualification/1"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read()


def recover_adapter(work: Path) -> Path:
    work.mkdir(parents=True, exist_ok=True)
    archive = work / "adapter.tar.gz"
    h = hashlib.sha256()
    total = 0
    with archive.open("wb") as out:
        for i in range(PART_COUNT):
            path = f"successor/qwen35/artifacts/vera-qwen35-history-v1-adapter.tar.gz.part{i:03d}"
            data = download(raw_url(path))
            out.write(data)
            h.update(data)
            total += len(data)
    digest = h.hexdigest()
    if digest != ARTIFACT_SHA256:
        raise RuntimeError(f"adapter SHA mismatch {digest} != {ARTIFACT_SHA256}")
    extract = work / "extracted"
    extract.mkdir(exist_ok=True)
    with tarfile.open(archive, "r:gz") as tf:
        tf.extractall(extract, filter="data")
    adapter = extract / "adapter"
    if not (adapter / "adapter_config.json").exists():
        raise RuntimeError(f"adapter_config.json not found under {adapter}")
    print(f"ADAPTER_READBACK|bytes={total}|sha256={digest}", flush=True)
    return adapter


def load_holdout() -> list[dict]:
    raw = download(HOLDOUT_URL).decode("utf-8")
    rows = [json.loads(x) for x in raw.splitlines() if x.strip()]
    if len(rows) != 40:
        raise RuntimeError(f"holdout rows {len(rows)} != 40")
    if any(r.get("training_seen") is not False or not r.get("qualification_eligible") for r in rows):
        raise RuntimeError("holdout qualification metadata invalid")
    return rows


def prompt_prefix(tokenizer, prompt: str) -> str:
    msgs = [{"role": "user", "content": prompt}]
    try:
        return tokenizer.apply_chat_template(
            msgs, tokenize=False, add_generation_prompt=True, enable_thinking=False
        )
    except TypeError:
        return tokenizer.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)


def encode_pair(tokenizer, prompt: str, response: str):
    prefix = prompt_prefix(tokenizer, prompt)
    pids = tokenizer(prefix, add_special_tokens=False)["input_ids"]
    rids = tokenizer(response, add_special_tokens=False)["input_ids"]
    eos = tokenizer.eos_token_id
    if eos is not None and (not rids or rids[-1] != eos):
        rids = rids + [eos]
    ids = pids + rids
    if len(ids) > MAX_LENGTH:
        raise RuntimeError(f"holdout example exceeds max length: {len(ids)}")
    return ids, len(pids)


def mean_response_logprob(model, tokenizer, prompt: str, response: str) -> float:
    import torch
    ids, p = encode_pair(tokenizer, prompt, response)
    x = torch.tensor([ids], device=model.device, dtype=torch.long)
    with torch.inference_mode():
        logits = model(input_ids=x, use_cache=False).logits[0]
        logp = torch.log_softmax(logits.float(), dim=-1)
    vals = []
    for t in range(p, len(ids)):
        vals.append(logp[t - 1, ids[t]])
    if not vals:
        raise RuntimeError("empty response scoring span")
    return float(torch.stack(vals).mean().item())


def evaluate(model, tokenizer, rows: list[dict]) -> dict:
    results = []
    dims = defaultdict(list)
    for r in rows:
        c = mean_response_logprob(model, tokenizer, r["prompt"], r["chosen"])
        z = mean_response_logprob(model, tokenizer, r["prompt"], r["rejected"])
        margin = c - z
        item = {
            "record_id": r["record_id"],
            "dimension": r["dimension"],
            "chosen_logp": c,
            "rejected_logp": z,
            "margin": margin,
            "correct": margin > 0,
        }
        results.append(item)
        dims[r["dimension"]].append(item)
    return {
        "n": len(results),
        "accuracy": sum(x["correct"] for x in results) / len(results),
        "mean_margin": sum(x["margin"] for x in results) / len(results),
        "by_dimension": {
            d: {
                "n": len(xs),
                "accuracy": sum(x["correct"] for x in xs) / len(xs),
                "mean_margin": sum(x["margin"] for x in xs) / len(xs),
            }
            for d, xs in sorted(dims.items())
        },
        "rows": results,
    }


def generate_samples(model, tokenizer, rows: list[dict]) -> list[dict]:
    import torch
    picks = ["H01", "H02", "H04", "H07", "H13", "H16", "H18", "H19"]
    out = []
    for dim in picks:
        r = next(x for x in rows if x["dimension"] == dim)
        prefix = prompt_prefix(tokenizer, r["prompt"])
        x = tokenizer(prefix, return_tensors="pt", add_special_tokens=False).to(model.device)
        with torch.inference_mode():
            y = model.generate(
                **x,
                max_new_tokens=96,
                do_sample=False,
                use_cache=True,
                pad_token_id=tokenizer.eos_token_id,
            )
        new = y[0, x["input_ids"].shape[1]:]
        out.append({
            "dimension": dim,
            "prompt": r["prompt"],
            "generation": tokenizer.decode(new, skip_special_tokens=True).strip(),
        })
    return out


def main(work: Path):
    import torch
    from peft import PeftModel
    from transformers import AutoTokenizer, BitsAndBytesConfig, Qwen3_5ForCausalLM

    adapter_dir = recover_adapter(work)
    rows = load_holdout()

    tokenizer = AutoTokenizer.from_pretrained(BASE_REPO, revision=BASE_REV)
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token
    quant = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_use_double_quant=True,
        bnb_4bit_compute_dtype=torch.bfloat16,
    )
    base = Qwen3_5ForCausalLM.from_pretrained(
        BASE_REPO,
        revision=BASE_REV,
        quantization_config=quant,
        device_map={"": 0},
        dtype=torch.bfloat16,
    )
    base.eval()
    print("QUALIFICATION_STAGE=BASE_SCORING", flush=True)
    base_eval = evaluate(base, tokenizer, rows)

    adapted = PeftModel.from_pretrained(base, adapter_dir)
    adapted.eval()
    print("QUALIFICATION_STAGE=ADAPTER_SCORING", flush=True)
    adapter_eval = evaluate(adapted, tokenizer, rows)
    generations = generate_samples(adapted, tokenizer, rows)

    result = {
        "schema": "VERA_QWEN35_HISTORY_BEHAVIOR_QUALIFICATION_V1",
        "subject": {
            "base_repo": BASE_REPO,
            "base_revision": BASE_REV,
            "adapter_sha256": ARTIFACT_SHA256,
            "artifact_commit": ARTIFACT_COMMIT,
            "holdout_rows": len(rows),
        },
        "method": "mean_response_token_logprob_preference_margin",
        "base": {k: v for k, v in base_eval.items() if k != "rows"},
        "adapter": {k: v for k, v in adapter_eval.items() if k != "rows"},
        "delta": {
            "accuracy": adapter_eval["accuracy"] - base_eval["accuracy"],
            "mean_margin": adapter_eval["mean_margin"] - base_eval["mean_margin"],
        },
        "rows": {
            "base": base_eval["rows"],
            "adapter": adapter_eval["rows"],
        },
        "generations": generations,
    }
    print("QUALIFICATION_RESULT=" + json.dumps(result, sort_keys=True), flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", type=Path, default=Path("/tmp/qwen35-qualification"))
    args = ap.parse_args()
    main(args.work)
