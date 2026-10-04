from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = (
    ROOT
    / "successor"
    / "experiments"
    / "V10_BEHAVIOR_GENERALIZATION_QUALIFICATION_PROTOCOL_20261004_V1.json"
)


def _protocol() -> dict:
    return json.loads(PROTOCOL.read_text(encoding="utf-8"))


def test_behavior_qualification_case_allocation_is_balanced_and_200_total() -> None:
    protocol = _protocol()
    policy = protocol["case_set_policy"]

    assert len(protocol["behavior_families"]) == 10
    assert set(policy["allocation"]) == set(protocol["behavior_families"])
    assert set(policy["allocation"].values()) == {20}
    assert sum(policy["allocation"].values()) == 200
    assert policy["total_cases"] == 200


def test_behavior_qualification_requires_real_heldout_structure() -> None:
    policy = _protocol()["case_set_policy"]

    assert policy["prompt_exact_overlap_with_training"] == 0
    assert policy["scenario_case_exact_overlap_with_training"] == 0
    assert policy["record_id_overlap_with_training"] == 0
    assert policy["candidate_prompt_duplicates"] == 0
    assert policy["max_cases_per_scenario_family"] == 2
    assert policy["min_scenario_families_per_behavior"] == 10
    assert policy["min_domains_per_behavior"] == 10
    assert policy["required_cognitive_levels"] == [
        "identify",
        "compare",
        "analyze",
        "evaluate",
        "apply",
    ]


def test_existing_v41_review_set_is_not_promoted_to_heldout_evidence() -> None:
    evidence = _protocol()["evidence_classification"]

    assert evidence["existing_v4_1_behavioral_review_set"] == (
        "SCHEMA_AND_DESIGN_EVIDENCE_ONLY_NOT_HELD_OUT_EVALUATION"
    )
    assert evidence["protected_final_bank"] == "PROHIBITED"
    assert evidence["one_time_recipe_panel"] == "PROHIBITED"


def test_paired_evaluation_and_replay_are_required() -> None:
    paired = _protocol()["paired_evaluation"]

    assert paired["required"] is True
    assert paired["subjects"] == ["baseline", "candidate"]
    assert paired["same_case_order"] is True
    assert paired["same_runtime_prompt_format"] is True
    assert paired["same_generation_settings"] is True
    assert paired["blind_subject_labels_for_semantic_grading"] is True
    assert paired["retention_replay_required_for_plasticity_candidates"] is True


def test_proposed_plasticity_promotion_gate_is_bounded() -> None:
    gates = _protocol()["proposed_promotion_gates_for_targeted_plasticity"]

    assert gates["status"] == "PROPOSED_PENDING_LANE_B_REVIEW"
    assert gates["target_family_candidate_pass_rate_min"] == 0.80
    assert gates["target_family_improvement_over_baseline_min_pp"] == 15
    assert gates["non_target_behavior_aggregate_regression_max_pp"] == 2
    assert gates["any_non_target_behavior_family_regression_max_pp"] == 5
    assert gates["retention_replay_aggregate_regression_max_pp"] == 2
    assert set(gates["protected_behavior_zero_critical_failures"]) == {
        "identity_stability",
        "epistemic_provenance",
        "privacy_boundary",
        "runtime_boundary",
    }


def test_mechanical_audit_does_not_claim_semantic_truth() -> None:
    boundary = _protocol()["scoring_boundary"]

    assert boundary["semantic_grading_requires_independent_review"] is True
    assert "semantic independence from training families" in boundary[
        "mechanical_audit_cannot_establish"
    ]
    assert "behavior correctness of model outputs" in boundary[
        "mechanical_audit_cannot_establish"
    ]
