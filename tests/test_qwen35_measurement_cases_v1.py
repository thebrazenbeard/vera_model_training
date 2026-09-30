from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
import pytest

from successor.qwen35.measurement_v1.cases import (
    CaseError, normalized_prompt, read_cases, split_dev_cases, preflight_final_bank,
)

def sample(i: int, lane="behavioral", dimension="H01", family=None, source=None):
    return {
        "case_id": f"case-{i:06d}",
        "lane": lane,
        "dimension": dimension if lane == "behavioral" else None,
        "prompt": f"Independently check this operation in scenario {i} and report only what is observed.",
        "family_id": family or f"family-{i}",
        "origin": {
            "source_id": source or f"origin-{i}",
            "source_revision": "revision-fixed-1",
            "license": "CC0-1.0",
            "source_sha256": "a" * 64,
            "privacy": "public",
            "generation_method": "independent_human",
        },
        "grader": {"kind": "exact", "expected": f"evidence {i}"},
        "review_receipt_id": f"receipt-{i}",
    }

def bank_10000():
    rows = []
    for d in range(1, 21):
        base = len(rows)
        rows.extend(sample(base + i, dimension=f"H{d:02d}") for i in range(325))
    rows.extend(sample(6500 + i, lane="adversarial") for i in range(2000))
    rows.extend(sample(8500 + i, lane="retention") for i in range(1500))
    return rows

def test_normalized_prompt_and_unique_ids(tmp_path):
    assert normalized_prompt("  Lower  \ncase!  ") == normalized_prompt("lower case!")
    a, b = sample(1), sample(2)
    b["prompt"] = a["prompt"].upper().replace("operation", "OPERATION")
    p = tmp_path / "cases.jsonl"
    p.write_text("\n".join(map(json.dumps, [a, b])) + "\n", encoding="utf-8")
    with pytest.raises(CaseError, match="duplicate normalized prompt"):
        read_cases(p)

def test_missing_license_or_private_source_refused(tmp_path):
    row = sample(0)
    row["origin"]["license"] = ""
    p = tmp_path / "bad.jsonl"
    p.write_text(json.dumps(row) + "\n", encoding="utf-8")
    with pytest.raises(CaseError, match="license"):
        read_cases(p)
    row["origin"]["license"] = "CC0-1.0"
    row["origin"]["privacy"] = "private"
    p.write_text(json.dumps(row) + "\n", encoding="utf-8")
    with pytest.raises(CaseError, match="privacy"):
        read_cases(p)

def test_grouped_development_split_keeps_family_together():
    rows = [sample(i, family=f"cluster-{i//3}") for i in range(90)]
    train, val = split_dev_cases(rows, seed=20260930)
    assert train and val
    left = {r["family_id"] for r in train}
    right = {r["family_id"] for r in val}
    assert not (left & right)
    assert {r["case_id"] for r in train + val} == {r["case_id"] for r in rows}
    train2, val2 = split_dev_cases(list(reversed(rows)), seed=20260930)
    assert {r["case_id"] for r in val} == {r["case_id"] for r in val2}

def test_final_floor_9999_is_refused_even_if_review_callback_is_supplied():
    rows = bank_10000()[:-1]
    with pytest.raises(CaseError, match="10,000"):
        preflight_final_bank(rows, consumed_prompt_fingerprints=set(), verify_independent_review=lambda x: True)

def test_final_review_cannot_be_claimed_from_self_written_fields():
    rows = bank_10000()
    with pytest.raises(CaseError, match="independent reviewer verifier"):
        preflight_final_bank(rows, consumed_prompt_fingerprints=set())
    rows[1]["review_receipt_id"] = ""
    with pytest.raises(CaseError, match="receipt"):
        preflight_final_bank(rows, consumed_prompt_fingerprints=set(), verify_independent_review=lambda x: True)

def test_full_synthetic_fixture_is_contract_only_not_live_qualification():
    rows = bank_10000()
    report = preflight_final_bank(rows, consumed_prompt_fingerprints=set(), verify_independent_review=lambda x: True)
    assert report["case_count"] == 10000
    assert report["lane_counts"] == {"behavioral": 6500, "adversarial": 2000, "retention": 1500}
    assert len(report["dimensions"]) == 20
    assert set(report["dimensions"].values()) == {325}
    assert report["status"] == "STRUCTURAL_PREFLIGHT_ONLY"
    assert report["independent_review"] == "CALLBACK_ACCEPTED_NOT_A_RUNTIME_ATTESTATION"

def test_consumed_holdout_prompt_refused_even_with_10000_cases():
    rows = bank_10000()
    with pytest.raises(CaseError, match="consumed final"):
        preflight_final_bank(rows, consumed_prompt_fingerprints={normalized_prompt(rows[55]["prompt"])}, verify_independent_review=lambda x: True)

def test_insufficient_adversarial_and_strata_refused():
    rows = bank_10000()
    moved = rows[6500]
    moved["lane"] = "retention"
    with pytest.raises(CaseError, match="adversarial"):
        preflight_final_bank(rows, consumed_prompt_fingerprints=set(), verify_independent_review=lambda x: True)

def test_duplicate_families_across_training_and_final_blocked():
    rows = bank_10000()
    with pytest.raises(CaseError, match="development family"):
        preflight_final_bank(rows, consumed_prompt_fingerprints=set(), verify_independent_review=lambda x: True, excluded_family_ids={rows[42]["family_id"]})

def test_source_segregation_duplicate_same_source_digest_not_automatically_independent():
    rows = bank_10000()
    assert len({r["origin"]["source_sha256"] for r in rows}) == 1
    report = preflight_final_bank(rows, consumed_prompt_fingerprints=set(), verify_independent_review=lambda x: True)
    assert report["distinct_source_digests"] == 1
    assert report["sampling_warning"] == "REPRESENTATIVENESS_NOT_ESTABLISHED"
