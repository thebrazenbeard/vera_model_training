from __future__ import annotations
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
Q = ROOT / "successor" / "qwen35" / "qualification"
EXPECTED = {
    "final_holdout_v3.jsonl": (100, "1b80a0ef64e765e8d901bb2237edb0c7e14163c4211c2ee1b7032891f15261b3"),
    "final_retention_v3.jsonl": (20, "4105efadbfe3cd0b63edfa3f4f336f2098b8e544beda968ddbd4b46a40fa4766"),
    "final_adversarial_proxy_v3.jsonl": (20, "b952154d2e9424161f54d825b29e7569c6e02f22fe350f2b698b7d5c22a75229"),
}

def load(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]

def test_frozen_suite_hashes_and_counts():
    for name, (count, digest) in EXPECTED.items():
        path = Q / name
        assert hashlib.sha256(path.read_bytes()).hexdigest() == digest
        assert len(load(path)) == count

def test_behavioral_holdout_is_balanced_and_unique():
    rows = load(Q / "final_holdout_v3.jsonl")
    counts = Counter(row["dimension"] for row in rows)
    assert set(counts) == {f"H{i:02d}" for i in range(1, 21)}
    assert all(counts[d] == 5 for d in counts)
    prompts = [row["prompt"] for row in rows]
    assert len(prompts) == len(set(prompts))

def test_spec_is_bound_before_evaluation():
    spec_path = Q / "FINAL_QUALIFICATION_V3_SPEC.json"
    freeze = json.loads((Q / "FINAL_QUALIFICATION_V3_FREEZE.json").read_text(encoding="utf-8"))
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    assert hashlib.sha256(spec_path.read_bytes()).hexdigest() == freeze["spec_sha256"]
    assert freeze["evaluation_started"] is False
    assert freeze["screening"]["lexical_sequence"]["failures"] == 0
    assert freeze["screening"]["embedding"]["failures"] == 0
    assert spec["subject"] == "OBJECTIVE_FIDELITY_V2_760_648"
    assert spec["adapter"]["archive_sha256"] == "1645cbe359cfdf4b3c9acd80471f71d2d6dfbce3c2a1a0fe6be24fc0513d1e69"