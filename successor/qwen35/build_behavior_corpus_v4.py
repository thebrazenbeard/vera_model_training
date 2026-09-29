from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from collections import Counter, defaultdict
from pathlib import Path

BASE_REPO = "rodrigomt/Qwen3.5-4B-Uncensored-Aggressive"
BASE_REV = "d61dd146c8fd44c9a49cdb7f59f34e17b61902d8"
DEFAULT_THRESHOLD = 0.62


def load_recipe(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_consumed_registry(path: Path) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))["entries"]


def _norm(text: str) -> str:
    return " ".join(re.findall(r"[a-z0-9']+", text.lower()))


def _shingles(text: str, n: int = 4) -> set[str]:
    words = _norm(text).split()
    if not words:
        return set()
    if len(words) < n:
        return {" ".join(words)}
    return {" ".join(words[i:i+n]) for i in range(len(words)-n+1)}


def _similarity(a: str, b: str) -> float:
    na, nb = _norm(a), _norm(b)
    if na == nb and na:
        return 1.0
    sa, sb = _shingles(a), _shingles(b)
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


def screen_overlap(candidate: str, blocked: list[str], threshold: float = DEFAULT_THRESHOLD) -> bool:
    return all(_similarity(candidate, other) < threshold for other in blocked if other)


def _row_key(row: dict) -> str:
    return hashlib.sha256((row["prompt"] + "\0" + row["response"]).encode("utf-8")).hexdigest()


def select_targeted(rows: list[dict], quotas: dict[str, int]) -> list[dict]:
    by_dimension: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        by_dimension[row["dimension"]].append(row)
    selected = []
    for dimension in sorted(quotas):
        candidates = sorted(by_dimension.get(dimension, []), key=lambda r: (int(r.get("priority", 9)), _row_key(r)))
        need = int(quotas[dimension])
        if len(candidates) < need:
            raise RuntimeError(f"{dimension}: only {len(candidates)} eligible targeted rows for quota {need}")
        selected.extend(candidates[:need])
    return selected


def _rendered_tokens(tokenizer, prompt: str, response: str) -> int:
    messages = [{"role": "user", "content": prompt}, {"role": "assistant", "content": response}]
    try:
        text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=False, enable_thinking=False)
    except TypeError:
        text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=False)
    return len(tokenizer(text, add_special_tokens=False)["input_ids"])


def _canonical_bytes(rows: list[dict]) -> bytes:
    return "".join(json.dumps(r, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n" for r in rows).encode("utf-8")


def _filter_rows(rows: list[dict], tokenizer, blocked_texts: list[str], max_length: int, reject_taxonomy: bool) -> tuple[list[dict], dict]:
    accepted: list[dict] = []
    accepted_dedupe_texts: list[str] = []
    stats = Counter()
    max_tokens = 0
    for row in sorted(rows, key=lambda r: (int(r.get("priority", 9)), _row_key(r))):
        prompt, response = row["prompt"].strip(), row["response"].strip()
        dedupe_text = str(row.get("dedupe_text") or prompt).strip()
        if not prompt or not response:
            stats["empty"] += 1
            continue
        lower = prompt.lower()
        if reject_taxonomy and (re.search(r"\bH\d{2}\b", prompt) or "thebrazenbeard" in lower or re.search(r"\bvera\b", lower)):
            stats["marker"] += 1
            continue
        if not screen_overlap(prompt, blocked_texts) or (dedupe_text != prompt and not screen_overlap(dedupe_text, blocked_texts)):
            stats["consumed_overlap"] += 1
            continue
        if not screen_overlap(dedupe_text, accepted_dedupe_texts):
            stats["internal_near_duplicate"] += 1
            continue
        tokens = _rendered_tokens(tokenizer, prompt, response)
        if tokens > max_length:
            stats["over_budget"] += 1
            continue
        max_tokens = max(max_tokens, tokens)
        clean = dict(row)
        clean["prompt"], clean["response"] = prompt, response
        clean["formatted_tokens"] = tokens
        accepted.append(clean)
        accepted_dedupe_texts.append(dedupe_text)
    return accepted, {"accepted": len(accepted), "max_tokens": max_tokens, **dict(stats)}


def build_v4_corpus(recipe: dict, targeted_rows: list[dict], general_rows: list[dict], tokenizer, blocked_texts: list[str]) -> tuple[list[dict], dict]:
    c = recipe["corpus"]
    max_length = int(recipe.get("training", {}).get("max_length", 512))
    targeted_eligible, targeted_screen = _filter_rows(targeted_rows, tokenizer, blocked_texts, max_length, True)
    selected_targeted = select_targeted(targeted_eligible, c["dimension_quotas"])
    targeted_prompts = [r["prompt"] for r in selected_targeted]
    general_eligible, general_screen = _filter_rows(general_rows, tokenizer, blocked_texts + targeted_prompts, max_length, False)
    general_sorted = sorted(general_eligible, key=_row_key)
    need_general = int(c["general_rehearsal_rows"])
    if len(general_sorted) < need_general:
        raise RuntimeError(f"only {len(general_sorted)} eligible general rows for quota {need_general}")
    selected_general = general_sorted[:need_general]
    out = []
    for i, row in enumerate(sorted(selected_targeted, key=lambda r: (r["dimension"], _row_key(r))), 1):
        item = {
            "schema": "VERA_QWEN35_BEHAVIOR_V4_SFT",
            "record_id": f"v4-targeted-{i:03d}",
            "source_class": "targeted",
            "source": row["source"],
            "dimension": row["dimension"],
            "prompt": row["prompt"],
            "response": row["response"],
        }
        for key in ("verification_class", "mechanism", "source_record_id"):
            if row.get(key) is not None:
                item[key] = row[key]
        out.append(item)
    for i, row in enumerate(selected_general, 1):
        out.append({
            "schema": "VERA_QWEN35_BEHAVIOR_V4_SFT",
            "record_id": f"v4-general-{i:03d}",
            "source_class": "general_rehearsal",
            "source": row["source"],
            "dimension": None,
            "prompt": row["prompt"],
            "response": row["response"],
        })
    if len(out) != int(c["total_sft_rows"]):
        raise RuntimeError(f"corpus count mismatch {len(out)} != {c['total_sft_rows']}")
    lengths = [_rendered_tokens(tokenizer, r["prompt"], r["response"]) for r in out]
    raw = _canonical_bytes(out)
    manifest = {
        "schema": "VERA_QWEN35_BEHAVIOR_V4_FROZEN_CORPUS_MANIFEST",
        "base_repo": recipe.get("base_repo", BASE_REPO),
        "base_revision": recipe.get("base_revision", BASE_REV),
        "rows": len(out),
        "targeted_rows": len(selected_targeted),
        "general_rehearsal_rows": len(selected_general),
        "dimension_counts": dict(sorted(Counter(r["dimension"] for r in selected_targeted).items())),
        "source_counts": dict(sorted(Counter(r["source"] for r in out).items())),
        "token_budget": {"max_length": max_length, "max_tokens": max(lengths, default=0), "over_budget": sum(n > max_length for n in lengths)},
        "overlap_screen": {"threshold": DEFAULT_THRESHOLD, "failures": 0, "targeted": targeted_screen, "general": general_screen},
        "corpus_sha256": hashlib.sha256(raw).hexdigest(),
    }
    return out, manifest


def _read_jsonl(path: Path) -> list[dict]:
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]


def _blocked_texts(root: Path, registry_entries: list[dict]) -> list[str]:
    texts = []
    for entry in registry_entries:
        path = root / entry["path"]
        if not path.exists():
            raise RuntimeError(f"consumed evidence missing: {entry['path']}")
        if hashlib.sha256(path.read_bytes()).hexdigest() != entry["sha256"]:
            raise RuntimeError(f"consumed evidence hash mismatch: {entry['path']}")
        if path.suffix == ".jsonl":
            objs = _read_jsonl(path)
        else:
            obj = json.loads(path.read_text(encoding="utf-8"))
            objs = obj if isinstance(obj, list) else [obj]
        for obj in objs:
            if not isinstance(obj, dict):
                continue
            for key in ("prompt", "chosen", "rejected", "response"):
                value = obj.get(key)
                if isinstance(value, str) and value.strip():
                    texts.append(value.strip())
    return texts


def _targeted_source_pool(q: Path) -> list[dict]:
    c = q / "corpus"
    accepted = _read_jsonl(c / "history_behavior_targeted_v2.jsonl")
    accepted_ids = {r.get("pair_sha256") for r in accepted}
    pool = []
    for r in accepted:
        pool.append({"dimension": r["dimension"], "prompt": r["prompt"], "response": r["chosen"], "source": "targeted_v2", "priority": 0})
    for r in _read_jsonl(c / "history_behavior_targeted_v2_candidates.jsonl"):
        if r.get("pair_sha256") in accepted_ids:
            continue
        priority = 3 if r["dimension"] == "H07" else 1
        pool.append({"dimension": r["dimension"], "prompt": r["prompt"], "response": r["chosen"], "source": "targeted_v2_candidate", "priority": priority})
    for r in _read_jsonl(c / "h07_rule_transfer_v2_train_sft.jsonl"):
        prompt = r["prompt"]
        first, sep, rest = prompt.partition("\n\n")
        if first.strip().startswith("H07 "):
            prompt = rest
        anchor_ids = {"h07-v2-train-001", "h07-v2-train-004", "h07-v2-train-007", "h07-v2-train-009"}
        priority = 1 if r["record_id"] in anchor_ids else 2
        dedupe_text = prompt.split("\n\nCASE\n", 1)[-1] if "\n\nCASE\n" in prompt else prompt
        pool.append({"dimension": "H07", "prompt": prompt, "dedupe_text": dedupe_text, "response": r["response"], "source": "h07_rule_transfer_v2", "priority": priority, "verification_class": r["verification_class"], "mechanism": r["mechanism"], "source_record_id": r["record_id"]})
    for r in _read_jsonl(c / "v4_rule_transfer_supplement_v1.jsonl"):
        pool.append({"dimension": r["dimension"], "prompt": r["prompt"], "response": r["response"], "source": r["source"], "priority": 2})
    return pool


def _general_source_pool(q: Path) -> list[dict]:
    rows = _read_jsonl(q / "corpus" / "vera_qwen35_behavior_v2_sft.jsonl")
    return [
        {"prompt": r["prompt"], "response": r["response"], "source": r["source"], "priority": 0}
        for r in rows
        if r.get("source") == "ultrafeedback_train_sft" or str(r.get("source", "")).startswith("smoltalk2:")
    ]


def load_tokenizer(base_dir: str | None = None):
    from transformers import AutoTokenizer
    source = base_dir or os.environ.get("QWEN35_BASE_DIR") or BASE_REPO
    kwargs = {} if base_dir or os.environ.get("QWEN35_BASE_DIR") else {"revision": BASE_REV}
    tok = AutoTokenizer.from_pretrained(source, **kwargs)
    if tok.pad_token_id is None:
        tok.pad_token = tok.eos_token
    return tok


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-dir")
    ap.add_argument("--output-dir", type=Path)
    args = ap.parse_args()
    root = Path(__file__).resolve().parents[2]
    q = root / "successor" / "qwen35"
    recipe_path = q / "V4_TRAINING_RECIPE_V1.json"
    registry_path = q / "corpus" / "v4_consumed_evidence_registry.json"
    recipe = load_recipe(recipe_path)
    registry = load_consumed_registry(registry_path)
    blocked = _blocked_texts(root, registry)
    tok = load_tokenizer(args.base_dir)
    rows, manifest = build_v4_corpus(recipe, _targeted_source_pool(q), _general_source_pool(q), tok, blocked)
    output_dir = args.output_dir or (q / "corpus")
    output_dir.mkdir(parents=True, exist_ok=True)
    corpus_path = output_dir / "vera_qwen35_behavior_v4_sft.jsonl"
    manifest_path = output_dir / "vera_qwen35_behavior_v4_manifest.json"
    raw = _canonical_bytes(rows)
    corpus_path.write_bytes(raw)
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print("V4_CORPUS=" + json.dumps(manifest, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
