from __future__ import annotations

from successor.experiments.build_v10_behavior_qualification import (
    assess_case_set,
)


def _train_rows() -> list[dict]:
    return [
        {
            "record_id": "train-a-1",
            "family": "family_a",
            "scenario_case": "old scenario alpha",
            "domain": "software",
            "cognitive_level": "identify",
            "prompt": "Use the evidence from scenario alpha.",
        },
        {
            "record_id": "train-b-1",
            "family": "family_b",
            "scenario_case": "old scenario beta",
            "domain": "research",
            "cognitive_level": "apply",
            "prompt": "Apply the rule in scenario beta.",
        },
    ]


def _policy() -> dict:
    return {
        "allocation": {"family_a": 2, "family_b": 2},
        "max_cases_per_scenario_family": 1,
        "min_scenario_families_per_behavior": 2,
        "min_domains_per_behavior": 2,
        "required_cognitive_levels": ["identify", "apply"],
    }


def _clean_candidates() -> list[dict]:
    return [
        {
            "case_id": "eval-a-1",
            "family": "family_a",
            "scenario_family_id": "a-new-1",
            "scenario_case": "novel scenario one",
            "domain": "finance",
            "cognitive_level": "identify",
            "prompt": "Identify what the new evidence establishes in case one.",
            "expected_behavior": "state the evidence boundary",
        },
        {
            "case_id": "eval-a-2",
            "family": "family_a",
            "scenario_family_id": "a-new-2",
            "scenario_case": "novel scenario two",
            "domain": "history",
            "cognitive_level": "apply",
            "prompt": "Apply the behavior to a new historical conflict.",
            "expected_behavior": "apply the evidence boundary",
        },
        {
            "case_id": "eval-b-1",
            "family": "family_b",
            "scenario_family_id": "b-new-1",
            "scenario_case": "novel scenario three",
            "domain": "operations",
            "cognitive_level": "identify",
            "prompt": "Identify the correct action in a new operations case.",
            "expected_behavior": "state the bounded action",
        },
        {
            "case_id": "eval-b-2",
            "family": "family_b",
            "scenario_family_id": "b-new-2",
            "scenario_case": "novel scenario four",
            "domain": "writing",
            "cognitive_level": "apply",
            "prompt": "Apply the behavior to a new writing case.",
            "expected_behavior": "apply the bounded action",
        },
    ]


def test_clean_heldout_case_set_passes() -> None:
    result = assess_case_set(
        training_rows=_train_rows(),
        candidate_rows=_clean_candidates(),
        policy=_policy(),
    )

    assert result["status"] == "PASS"
    assert result["reasons"] == []
    assert result["total_cases"] == 4


def test_training_scenario_overlap_holds_even_with_new_prompt_and_id() -> None:
    candidates = _clean_candidates()
    candidates[0] = {
        **candidates[0],
        "case_id": "different-id",
        "scenario_case": "old scenario alpha",
        "prompt": "A completely different prompt surface.",
    }

    result = assess_case_set(
        training_rows=_train_rows(),
        candidate_rows=candidates,
        policy=_policy(),
    )

    assert result["status"] == "HOLD"
    assert "training_scenario_overlap:different-id" in result["reasons"]


def test_normalized_training_prompt_overlap_holds() -> None:
    candidates = _clean_candidates()
    candidates[0] = {
        **candidates[0],
        "prompt": "  USE   the evidence from SCENARIO alpha. ",
    }

    result = assess_case_set(
        training_rows=_train_rows(),
        candidate_rows=candidates,
        policy=_policy(),
    )

    assert result["status"] == "HOLD"
    assert "training_prompt_overlap:eval-a-1" in result["reasons"]


def test_pseudoreplicated_scenario_family_holds() -> None:
    candidates = _clean_candidates()
    candidates[1] = {
        **candidates[1],
        "scenario_family_id": "a-new-1",
    }

    result = assess_case_set(
        training_rows=_train_rows(),
        candidate_rows=candidates,
        policy=_policy(),
    )

    assert result["status"] == "HOLD"
    assert "scenario_family_size:family_a:a-new-1:2>1" in result["reasons"]
    assert "scenario_family_count:family_a:1<2" in result["reasons"]


def test_insufficient_domain_and_cognitive_coverage_holds() -> None:
    candidates = _clean_candidates()
    candidates[1] = {
        **candidates[1],
        "domain": candidates[0]["domain"],
        "cognitive_level": candidates[0]["cognitive_level"],
    }

    result = assess_case_set(
        training_rows=_train_rows(),
        candidate_rows=candidates,
        policy=_policy(),
    )

    assert result["status"] == "HOLD"
    assert "domain_count:family_a:1<2" in result["reasons"]
    assert "cognitive_level_missing:family_a:apply" in result["reasons"]


def test_candidate_duplicate_prompt_holds() -> None:
    candidates = _clean_candidates()
    candidates[1] = {
        **candidates[1],
        "prompt": candidates[0]["prompt"],
    }

    result = assess_case_set(
        training_rows=_train_rows(),
        candidate_rows=candidates,
        policy=_policy(),
    )

    assert result["status"] == "HOLD"
    assert "candidate_prompt_duplicate:eval-a-2" in result["reasons"]
