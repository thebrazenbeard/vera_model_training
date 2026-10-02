from __future__ import annotations

import json

import pytest

from successor.experiments.retention_audit_arch_v2_reviewer import (
    ALLOWED_OBSERVATIONS,
    build_reviewer_qualification_controls,
    qualify_reviewer,
    review_prompt,
    parse_witness_response,
)


def _sample_case() -> dict:
    return {
        "case_id": "sample-1",
        "category": "knowledge_factuality",
        "family_id": "location:code_from_name",
        "prompt": "What code is assigned to Alpha? Return only the code.",
        "source_id": "source:country:AA",
        "source_revision": "TEST",
        "source_terms": "TEST",
        "source_hash": "0" * 64,
        "generation_method": "test",
        "grader_contract": {
            "kind": "deterministic",
            "grader_id": "exact_text_v1",
            "grader_version": "1",
            "answer_key": "AA",
            "answer_key_digest": "1" * 64,
        },
        "source_evidence": {
            "name": "Alpha",
            "code": "AA",
            "regions": 1,
            "settlements": 2,
        },
    }


def test_qualification_controls_are_exactly_48_balanced_across_six_classes() -> None:
    controls = build_reviewer_qualification_controls()
    defect_classes = {
        "referent_ambiguity",
        "prompt_grader_semantic_mismatch",
        "contradictory_instructions",
        "underspecified_output_format",
        "evidence_policy_ambiguity",
        "scope_negation_ambiguity",
    }

    assert len(controls) == 48
    assert {row["defect_class"] for row in controls} == defect_classes
    for defect_class in defect_classes:
        rows = [row for row in controls if row["defect_class"] == defect_class]
        assert sum(row["expected_defect"] for row in rows) == 4
        assert sum(not row["expected_defect"] for row in rows) == 4


def test_blind_prompt_never_contains_hidden_answer_fields() -> None:
    prompt = review_prompt([_sample_case()])

    assert "answer_key" not in prompt
    assert "answer_key_digest" not in prompt
    assert '"verdict"' not in prompt
    assert "ADMIT" not in prompt
    assert "REJECT" not in prompt
    assert "AA" in prompt  # supplied source evidence remains visible


def test_witness_parser_accepts_only_witness_observations() -> None:
    raw = json.dumps({
        "reviews": [{
            "case_id": "sample-1",
            "observation": "NO_SEMANTIC_DEFECT_FOUND",
            "derived_answer": "AA",
            "witness": None,
            "reason": "The referent and requested output are unambiguous.",
            "confidence": "high",
        }]
    })

    parsed = parse_witness_response(raw, expected_case_ids=["sample-1"])
    assert parsed[0]["observation"] in ALLOWED_OBSERVATIONS

    bad = json.dumps({
        "reviews": [{
            "case_id": "sample-1",
            "observation": "ADMIT",
            "derived_answer": "AA",
            "witness": None,
            "reason": "No defect.",
            "confidence": "high",
        }]
    })
    with pytest.raises(ValueError, match="observation"):
        parse_witness_response(bad, expected_case_ids=["sample-1"])


def test_reviewer_qualification_requires_thresholds_and_per_class_floor() -> None:
    controls = build_reviewer_qualification_controls()

    def perfect(control: dict) -> dict:
        return {
            "case_id": control["case_id"],
            "observed_defect": control["expected_defect"],
            "defect_class": control["defect_class"],
            "witness": (
                "seeded semantic defect"
                if control["expected_defect"]
                else None
            ),
            "reason": "matched control",
        }

    result = qualify_reviewer(perfect)
    assert result["status"] == "REVIEWER_QUALIFIED"
    assert result["sensitivity"] == [24, 24]
    assert result["specificity"] == [24, 24]
    assert all(value == [4, 4] for value in result["per_class"].values())

    def misses_one_class(control: dict) -> dict:
        value = perfect(control)
        if control["defect_class"] == "referent_ambiguity":
            value["observed_defect"] = False
            value["witness"] = None
        return value

    failed = qualify_reviewer(misses_one_class)
    assert failed["status"] == "REVIEWER_UNQUALIFIED"


def test_qualification_prompt_hides_expected_label() -> None:
    from successor.experiments.retention_audit_arch_v2_reviewer import (
        qualification_prompt,
    )

    control = build_reviewer_qualification_controls()[0]
    prompt = qualification_prompt(control)

    assert "expected_defect" not in prompt
    assert str(control["expected_defect"]).lower() not in prompt.lower()
    assert control["prompt"] in prompt
    assert control["defect_class"] in prompt


def test_qualification_response_parser_requires_concrete_witness_for_defect() -> None:
    from successor.experiments.retention_audit_arch_v2_reviewer import (
        parse_qualification_response,
    )

    control = build_reviewer_qualification_controls()[0]
    raw = json.dumps({
        "case_id": control["case_id"],
        "observed_defect": True,
        "defect_class": control["defect_class"],
        "witness": "The pronoun has two plausible referents.",
        "reason": "Concrete alternate reading exists.",
    })
    parsed = parse_qualification_response(raw, control=control)
    assert parsed["observed_defect"] is True

    bad = json.dumps({
        "case_id": control["case_id"],
        "observed_defect": True,
        "defect_class": control["defect_class"],
        "witness": None,
        "reason": "Concern.",
    })
    with pytest.raises(ValueError, match="witness"):
        parse_qualification_response(bad, control=control)
