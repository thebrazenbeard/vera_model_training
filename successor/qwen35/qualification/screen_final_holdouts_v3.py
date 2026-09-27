from __future__ import annotations
import json
import pathlib
import re
import difflib
import hashlib

ROOT = pathlib.Path(__file__).resolve().parents[3]
Q = ROOT / "successor" / "qwen35"
TARGETS = [
    Q / "qualification" / "final_holdout_v3.jsonl",
    Q / "qualification" / "final_retention_v3.jsonl",
    Q / "qualification" / "final_adversarial_proxy_v3.jsonl",
]

def norm(value: str) -> str:
    return " ".join(re.findall(r"[a-z0-9]+", value.lower()))

def toks(value: str) -> set[str]:
    return set(norm(value).split())

def load_jsonl(path: pathlib.Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]

def source_material() -> tuple[int, list[tuple]]:
    excluded = set(TARGETS)
    texts = []
    row_count = 0
    paths = list((Q / "corpus").rglob("*.jsonl")) + list((Q / "qualification").rglob("*.jsonl"))
    for path in paths:
        if path in excluded:
            continue
        try:
            rows = load_jsonl(path)
        except Exception:
            continue
        row_count += len(rows)
        for row_index, row in enumerate(rows):
            for key in ("prompt", "chosen", "rejected", "response"):
                value = row.get(key)
                if isinstance(value, str) and value.strip():
                    texts.append((path.relative_to(ROOT).as_posix(), row_index, key, value, norm(value), toks(value)))
    return row_count, texts

def main() -> int:
    source_rows, source_texts = source_material()
    print(f"SOURCE_ROWS={source_rows} SOURCE_TEXTS={len(source_texts)}")
    failures = []
    for path in TARGETS:
        rows = load_jsonl(path)
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        print(f"TARGET={path.name} ROWS={len(rows)} SHA256={digest}")
        for row in rows:
            record_id = row["record_id"]
            for key in ("prompt", "chosen", "rejected"):
                value = row[key]
                normalized = norm(value)
                token_set = toks(value)
                best_jaccard = (0.0, None)
                best_ratio = (0.0, None)
                for src_path, row_index, src_key, src_value, src_norm, src_tokens in source_texts:
                    if normalized == src_norm:
                        failures.append((record_id, key, "EXACT", src_path, row_index, src_key, 1.0))
                        continue
                    if key != "prompt":
                        continue
                    union = token_set | src_tokens
                    jaccard = len(token_set & src_tokens) / len(union) if union else 0.0
                    if jaccard > best_jaccard[0]:
                        best_jaccard = (jaccard, (src_path, row_index, src_key, src_value))
                    if jaccard > 0.45:
                        ratio = difflib.SequenceMatcher(None, normalized, src_norm).ratio()
                        if ratio > best_ratio[0]:
                            best_ratio = (ratio, (src_path, row_index, src_key, src_value))
                if key == "prompt":
                    if best_jaccard[0] >= 0.72:
                        src = best_jaccard[1]
                        failures.append((record_id, key, "JACCARD", src[0], src[1], src[2], best_jaccard[0]))
                    if best_ratio[0] >= 0.82:
                        src = best_ratio[1]
                        failures.append((record_id, key, "SEQRATIO", src[0], src[1], src[2], best_ratio[0]))
                    if best_jaccard[0] >= 0.40:
                        src = best_jaccard[1]
                        preview = src[3].replace("\n", " ")[:120]
                        print(f"TOP={record_id} JACCARD={best_jaccard[0]:.3f} SOURCE={src[0]} PREVIEW={preview}")
    print(f"FAIL_COUNT={len(failures)}")
    for failure in failures[:100]:
        print("FAIL", failure)
    return 1 if failures else 0

if __name__ == "__main__":
    raise SystemExit(main())