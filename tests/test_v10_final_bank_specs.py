from __future__ import annotations

import json
from pathlib import Path

from successor.experiments.final_bank_specs import (
    validate_generation_spec,
    validate_grader_spec,
)


ROOT = Path(__file__).parents[1]
GEN = (
    ROOT
    / "successor/experiments/V10_FINAL_BANK_GENERATION_SPEC_V1.json"
)
GRADER = (
    ROOT
    / "successor/experiments/V10_FINAL_BANK_GRADER_SPEC_V1.json"
)


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_frozen_generation_spec_passes() -> None:
    result = validate_generation_spec(_load(GEN))
    assert result["status"] == "GENERATION_SPEC_PASS"
    assert result["behavioral_rows"] == 10000
    assert result["behavioral_families"] == 1000
    assert result["adversarial_rows"] == 2000
    assert result["adversarial_families"] == 400
    assert result["retention_rows"] == 1500


def test_generation_spec_rejects_quota_drift() -> None:
    value = _load(GEN)
    value["behavioral"]["rows_per_dimension"] = 499
    result = validate_generation_spec(value)
    assert result["status"] == "HOLD"
    assert "behavioral_rows_per_dimension_mismatch" in result["reasons"]


def test_generation_spec_rejects_plaintext_case_fields() -> None:
    value = _load(GEN)
    value["example"] = {"prompt": "secret final prompt"}
    result = validate_generation_spec(value)
    assert result["status"] == "HOLD"
    assert any(
        reason.startswith("plaintext_case_field_present:")
        for reason in result["reasons"]
    )


def test_generation_spec_self_hash_is_binding() -> None:
    value = _load(GEN)
    value["behavioral"]["cases_per_family"] = 11
    result = validate_generation_spec(value)
    assert "spec_sha256_mismatch" in result["reasons"]


def test_frozen_grader_spec_passes() -> None:
    result = validate_grader_spec(_load(GRADER))
    assert result["status"] == "GRADER_SPEC_PASS"
    assert result["dimension_count"] == 20
    assert result["semantic_human_dimensions"] == [
        "H01",
        "H03",
        "H04",
        "H05",
        "H06",
        "H11",
        "H14",
        "H15",
        "H18",
    ]


def test_grader_spec_rejects_llm_as_human_substitution() -> None:
    value = _load(GRADER)
    value["review_policy"]["llm_may_substitute_for_human_review"] = True
    result = validate_grader_spec(value)
    assert result["status"] == "HOLD"
    assert "llm_human_substitution_not_false" in result["reasons"]


def test_grader_spec_requires_all_h_dimensions_exactly_once() -> None:
    value = _load(GRADER)
    value["dimensions"].pop("H20")
    result = validate_grader_spec(value)
    assert result["status"] == "HOLD"
    assert "dimension_key_set_mismatch" in result["reasons"]


def test_semantic_dimension_cannot_be_downgraded_to_deterministic() -> None:
    value = _load(GRADER)
    value["dimensions"]["H01"]["primary_grading_class"] = "DETERMINISTIC"
    result = validate_grader_spec(value)
    assert result["status"] == "HOLD"
    assert "H01_primary_grading_class_mismatch" in result["reasons"]


def test_grader_spec_self_hash_is_binding() -> None:
    value = _load(GRADER)
    value["review_policy"]["blinded_to_candidate_identity"] = False
    result = validate_grader_spec(value)
    assert "spec_sha256_mismatch" in result["reasons"]
