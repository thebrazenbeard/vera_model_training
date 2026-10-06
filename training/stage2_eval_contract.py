from __future__ import annotations

REQUIRED_EVAL_BANKS = (
    "correction_proposition_fidelity",
    "truth_over_agreement",
    "currentness_source_hierarchy",
    "tool_honesty_effect_verification",
    "privacy_memory_placement",
    "authority_boundaries",
    "catastrophic_forgetting_replay",
    "novel_task_acquisition",
    "late_relevance_exact_recovery",
    "hidden_state_isolation",
    "adapter_routing_conflict",
    "stale_memory_supersession",
)

REQUIRED_CONTROL_ARMS = (
    "untouched_base_control",
    "deterministic_decoding_or_fixed_seeds",
    "blinded_candidate_identity",
    "no_acquisition_stateless",
    "shuffled_labels",
    "irrelevant_memory",
    "support_omitted",
    "familiar_lookalike",
    "contradictory_prior",
    "fresh_process_reopened_session",
    "adapter_disabled",
)

REQUIRED_HIDDEN_GRADING_FIELDS = (
    "must_assert",
    "must_not_assert",
    "acceptable_variants",
    "severity",
    "critical_failures",
)


def build_stage2_eval_contract(
    *,
    banks: list[str],
    controls: list[str],
    hidden_grading_fields: list[str],
    candidate_identity_blinded: bool,
    deterministic_decoding_or_fixed_seeds: bool,
    promotion_cases_per_family: int,
    power_preregistered: bool,
    grader_count: int,
    adjudication_required: bool,
    exact_training_subject_verified: bool = False,
    manifest_hashes_verified: bool = False,
    shard_hashes_verified: bool = False,
) -> dict:
    missing_banks = sorted(set(REQUIRED_EVAL_BANKS) - set(banks))
    missing_controls = sorted(set(REQUIRED_CONTROL_ARMS) - set(controls))
    missing_grading = sorted(
        set(REQUIRED_HIDDEN_GRADING_FIELDS) - set(hidden_grading_fields)
    )
    reasons: list[str] = []
    if missing_banks:
        reasons.append("missing_eval_banks")
    if missing_controls:
        reasons.append("missing_control_arms")
    if missing_grading:
        reasons.append("missing_hidden_grading_fields")
    if not candidate_identity_blinded:
        reasons.append("candidate_identity_not_blinded")
    if not deterministic_decoding_or_fixed_seeds:
        reasons.append("decoding_or_seed_contract_missing")
    if promotion_cases_per_family < 80:
        reasons.append("promotion_power_below_planning_default")
    if not power_preregistered:
        reasons.append("promotion_power_not_preregistered")
    if grader_count < 2:
        reasons.append("two_graders_required")
    if not adjudication_required:
        reasons.append("adjudication_required")
    if not exact_training_subject_verified:
        reasons.append("exact_training_subject_not_verified")
    if not manifest_hashes_verified:
        reasons.append("manifest_hashes_not_verified")
    if not shard_hashes_verified:
        reasons.append("shard_hashes_not_verified")

    return {
        "schema": "STAGE2_EVAL_CONTRACT_V1",
        "status": "PASS" if not reasons else "HOLD",
        "bank_count": len(set(banks)),
        "missing_banks": missing_banks,
        "missing_controls": missing_controls,
        "missing_hidden_grading_fields": missing_grading,
        "promotion_cases_per_family": promotion_cases_per_family,
        "grader_count": grader_count,
        "adjudication_required": adjudication_required,
        "reasons": reasons,
    }
