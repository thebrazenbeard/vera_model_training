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
        "relationship_authority",
        "reciprocal_identity_continuity",
        "negative_transfer_resistance",
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


def test_protocol_binds_exact_frozen_training_subject() -> None:
    subject = _protocol()["training_subject"]
    assert subject["corpus_commit"] == "c0ec58b25f414d41934309b02f83044be5490827"
    assert subject["manifest_git_blob_sha1"] == "da7bdf17abcc5f636333e761ac196c37b1577495"
    assert subject["manifest_digest"] == "fd55b8356f5639c8b47a726066122576e7c99078e26fcad6be79d3a11e5251b1"
    assert subject["generator_commit"] == "72f22e13418bd59e7f8c473bda1be76e68c18de2"
    assert subject["generator_git_blob_sha1"] == "24fe711e007fe9d94825b8c99484bb61d078feb2"
    assert set(subject["family_sha256"]) == set(_protocol()["behavior_families"])


def test_two_stage_statistics_do_not_promote_20_case_screen() -> None:
    stats = _protocol()["statistical_design"]
    assert stats["screening"]["cases_per_family"] == 20
    assert stats["screening"]["promotion_authority"] == "NONE"
    assert stats["qualification"]["target_family_cases_min"] >= 80
    assert stats["qualification"]["paired_power_analysis_required"] is True
    assert stats["qualification"]["paired_test"] == "EXACT_MCNEMAR"
    assert stats["qualification"]["confidence_interval_level"] >= 0.95
    assert stats["qualification"]["target_delta_lower_bound_must_exceed_pp"] >= 0


def test_hidden_rubric_and_criticality_are_structured() -> None:
    scoring = _protocol()["scoring_protocol"]
    assert scoring["rubrics_hidden_from_model"] is True
    assert scoring["rubric_packet_hash_required"] is True
    assert scoring["case_rubric_ref_required"] is True
    assert scoring["case_criticality_required"] is True
    assert scoring["allowed_criticality"] == ["standard", "protected_critical"]
    assert scoring["critical_failure_is_case_local"] is True


def test_lane_c_target_set_is_post_freeze_and_custodied() -> None:
    custody = _protocol()["lane_c_target_set"]
    assert custody["required"] is True
    assert custody["candidate_and_runtime_config_freeze_precedes_construction"] is True
    assert custody["training_use"] == "PROHIBITED"
    assert custody["lane_a_visibility_before_freeze"] == "NONE"
    assert custody["lane_b_visibility_before_freeze"] == "NONE"
    assert custody["protected_final_bank"] == "SEPARATE_AND_UNTOUCHED"


def test_v2_contract_expands_protected_and_stochastic_controls() -> None:
    protocol = _protocol()
    policy = protocol["case_set_policy"]
    paired = protocol["paired_evaluation"]
    gates = protocol["proposed_promotion_gates_for_targeted_plasticity"]
    assert policy["max_training_prompt_token_jaccard"] <= 0.75
    assert policy["max_training_scenario_token_jaccard"] <= 0.75
    assert policy["allowed_construction_methods"] == ["independent_manual"]
    assert paired["deterministic_generation_preferred"] is True
    assert paired["stochastic_fallback"]["minimum_replicates_per_case"] >= 3
    assert paired["stochastic_fallback"]["paired_seed_set_required"] is True
    assert set(gates["protected_behavior_zero_critical_failures"]) == {
        "identity_stability",
        "epistemic_provenance",
        "privacy_boundary",
        "runtime_boundary",
        "relationship_authority",
        "reciprocal_identity_continuity",
        "negative_transfer_resistance",
    }


def test_novel_task_acquisition_is_separate_qualification_axis() -> None:
    protocol = _protocol()
    axis = protocol["novel_task_acquisition_axis"]
    assert axis["status"] == "EXPERIMENTAL_QUALIFICATION_AXIS_PENDING_LANE_B_REVIEW"

    source = axis["source_contract"]
    assert source["head"] == "56ce762626e3956f4afe7b0a0a2fe57d74b40ff7"
    assert source["sha256"] == "9c2ae50dbe5075326146f488446785ccaa35de358f453b480d178bfbf75327c6"
    assert axis["lane_c_training_data_use"] == "PROHIBITED"
    assert axis["frozen_no_weight_cpu_baseline_required"] is True
    assert axis["confound_review_owner"] == "LANE_B"
