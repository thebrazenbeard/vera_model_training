from __future__ import annotations

import json

import pytest

from successor.experiments.run_v10_retention_independent_audit import (
    parse_review,
    review_prompt,
    summarize_reviews,
)


def test_review_prompt_contains_subject_not_prior_verdict() -> None:
    case = {
        "case_id": "ret-x",
        "category": "coding",
        "prompt": "Implement f.",
        "grader_contract": {"kind": "deterministic", "tests": ["assert f()==1"]},
        "source_evidence": None,
    }
    prompt = review_prompt(case)
    assert "ret-x" in prompt
    assert "assert f()==1" in prompt
    assert "PENDING_INDEPENDENT_REVIEW" not in prompt


def test_parse_review_requires_closed_schema() -> None:
    value = parse_review(
        json.dumps({
            "verdict": "ADMIT",
            "prompt_well_posed": True,
            "grader_matches_prompt": True,
            "source_evidence_sufficient": True,
            "issue_code": "NONE",
            "reason": "No material defect.",
            "confidence": "high",
        })
    )
    assert value["verdict"] == "ADMIT"
    with pytest.raises(ValueError):
        parse_review('{"verdict":"MAYBE"}')


def test_summary_refuses_any_reject() -> None:
    reviews = [
        {"verdict": "ADMIT", "category": "a"},
        {"verdict": "REJECT", "category": "b"},
    ]
    result = summarize_reviews(reviews)
    assert result["status"] == "HOLD"
    assert result["admit"] == 1
    assert result["reject"] == 1
