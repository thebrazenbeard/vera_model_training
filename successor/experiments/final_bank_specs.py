from __future__ import annotations

import hashlib
import json


DIMENSIONS = [f"H{i:02d}" for i in range(1, 21)]
SEMANTIC_HUMAN_DIMENSIONS = [
    "H01", "H03", "H04", "H05", "H06", "H11", "H14", "H15", "H18"
]
MIXED_DIMENSIONS = [
    dimension for dimension in DIMENSIONS
    if dimension not in SEMANTIC_HUMAN_DIMENSIONS
]
PLAINTEXT_CASE_KEYS = {
    "prompt",
    "response",
    "answer",
    "reference_answer",
    "answer_key",
    "case_text",
}


def _canonical_sha256(value: dict) -> str:
    unsigned = dict(value)
    unsigned.pop("spec_sha256", None)
    raw = json.dumps(
        unsigned,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _find_plaintext_case_keys(value, *, path: str = "$") -> list[str]:
    found: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            key_text = str(key)
            if key_text.casefold() in PLAINTEXT_CASE_KEYS:
                found.append(f"{path}.{key_text}")
            found.extend(
                _find_plaintext_case_keys(
                    child,
                    path=f"{path}.{key_text}",
                )
            )
    elif isinstance(value, list):
        for index, child in enumerate(value):
            found.extend(
                _find_plaintext_case_keys(
                    child,
                    path=f"{path}[{index}]",
                )
            )
    return found


def _check_spec_sha(value: dict, reasons: list[str]) -> None:
    if value.get("spec_sha256") != _canonical_sha256(value):
        reasons.append("spec_sha256_mismatch")


def validate_generation_spec(value: dict) -> dict:
    reasons: list[str] = []
    if not isinstance(value, dict):
        return {
            "schema": "V10_FINAL_BANK_GENERATION_SPEC_CHECK_V1",
            "status": "HOLD",
            "reasons": ["spec_not_object"],
        }

    if value.get("schema") != "V10_FINAL_BANK_GENERATION_SPEC_V1":
        reasons.append("schema_mismatch")
    if value.get("status") != "FROZEN_PRETRAINING_GENERATION_SPEC":
        reasons.append("status_mismatch")
    if value.get("effect") != "SPEC_ONLY_NO_CASE_GENERATION":
        reasons.append("effect_mismatch")
    if value.get("dimensions") != DIMENSIONS:
        reasons.append("dimension_sequence_mismatch")
    if value.get("final_plaintext_generation_authorized") is not False:
        reasons.append("final_plaintext_generation_authorized_not_false")

    for path in _find_plaintext_case_keys(value):
        reasons.append(f"plaintext_case_field_present:{path}")

    behavioral = value.get("behavioral")
    if not isinstance(behavioral, dict):
        reasons.append("behavioral_missing")
        behavioral = {}
    expected_behavioral = {
        "rows_per_dimension": 500,
        "families_per_dimension": 50,
        "cases_per_family": 10,
        "total_rows": 10000,
        "total_families": 1000,
    }
    for field, expected in expected_behavioral.items():
        if behavioral.get(field) != expected:
            reasons.append(f"behavioral_{field}_mismatch")
    if behavioral.get("family_provenance_per_dimension") != {
        "synthetic_A": 20,
        "synthetic_B": 20,
        "human_seeded": 10,
    }:
        reasons.append("behavioral_family_provenance_mismatch")
    if behavioral.get("generator_share_ceiling") != 0.40:
        reasons.append("behavioral_generator_share_ceiling_mismatch")
    if (
        behavioral.get("rows_per_dimension", 0) * len(DIMENSIONS)
        != behavioral.get("total_rows")
    ):
        reasons.append("behavioral_total_rows_inconsistent")
    if (
        behavioral.get("families_per_dimension", 0) * len(DIMENSIONS)
        != behavioral.get("total_families")
    ):
        reasons.append("behavioral_total_families_inconsistent")
    if (
        behavioral.get("families_per_dimension", 0)
        * behavioral.get("cases_per_family", 0)
        != behavioral.get("rows_per_dimension")
    ):
        reasons.append("behavioral_family_case_product_inconsistent")

    adversarial = value.get("adversarial")
    if not isinstance(adversarial, dict):
        reasons.append("adversarial_missing")
        adversarial = {}
    expected_adversarial = {
        "rows_per_dimension": 100,
        "families_per_dimension": 20,
        "cases_per_family": 5,
        "total_rows": 2000,
        "total_families": 400,
    }
    for field, expected in expected_adversarial.items():
        if adversarial.get(field) != expected:
            reasons.append(f"adversarial_{field}_mismatch")
    if adversarial.get("family_provenance_per_dimension") != {
        "synthetic_A": 8,
        "synthetic_B": 8,
        "human_seeded": 4,
    }:
        reasons.append("adversarial_family_provenance_mismatch")
    pressure = adversarial.get("pressure_classes")
    if not isinstance(pressure, list) or len(pressure) < 8:
        reasons.append("adversarial_pressure_classes_insufficient")
    elif len(pressure) != len(set(pressure)):
        reasons.append("adversarial_pressure_classes_duplicate")
    if (
        adversarial.get("families_per_dimension", 0)
        * adversarial.get("cases_per_family", 0)
        != adversarial.get("rows_per_dimension")
    ):
        reasons.append("adversarial_family_case_product_inconsistent")

    retention = value.get("retention")
    if not isinstance(retention, dict):
        reasons.append("retention_missing")
        retention = {}
    if retention.get("required_rows") != 1500:
        reasons.append("retention_required_rows_mismatch")
    if retention.get("allocation") != {
        "knowledge_factuality": 300,
        "reasoning_math": 300,
        "coding": 250,
        "instruction_following": 250,
        "extraction_structured": 200,
        "truthfulness_factual_calibration": 200,
    }:
        reasons.append("retention_allocation_mismatch")
    if sum(retention.get("allocation", {}).values()) != 1500:
        reasons.append("retention_allocation_total_mismatch")
    if retention.get("regenerate_in_h01_h20_custody") is not False:
        reasons.append("retention_regeneration_not_false")
    if retention.get("final_inclusion_requires_v3_pass") is not True:
        reasons.append("retention_v3_gate_not_true")

    family = value.get("family_independence")
    required_true = (
        "scenario_skeleton_defines_family",
        "entity_swap_does_not_create_family",
        "value_swap_does_not_create_family",
        "style_change_does_not_create_family",
        "order_permutation_does_not_create_family",
        "independent_family_requires_distinct_failure_mechanism",
        "behavioral_and_adversarial_family_ids_disjoint",
        "family_manifest_required",
    )
    if not isinstance(family, dict):
        reasons.append("family_independence_missing")
        family = {}
    for field in required_true:
        if family.get(field) is not True:
            reasons.append(f"family_independence_{field}_not_true")

    custody = value.get("custody")
    if not isinstance(custody, dict):
        reasons.append("custody_missing")
        custody = {}
    if custody.get(
        "training_lane_plaintext_access_before_candidate_freeze"
    ) is not False:
        reasons.append("custody_training_plaintext_access_not_false")
    if custody.get(
        "candidate_development_plaintext_access_before_candidate_freeze"
    ) is not False:
        reasons.append("custody_candidate_plaintext_access_not_false")
    if custody.get("hash_only_publication_before_candidate_freeze") is not True:
        reasons.append("custody_hash_only_publication_not_true")
    if custody.get("post_freeze_case_mutation") is not False:
        reasons.append("custody_post_freeze_mutation_not_false")

    _check_spec_sha(value, reasons)
    reasons = sorted(set(reasons))
    return {
        "schema": "V10_FINAL_BANK_GENERATION_SPEC_CHECK_V1",
        "status": "GENERATION_SPEC_PASS" if not reasons else "HOLD",
        "reasons": reasons,
        "spec_sha256": value.get("spec_sha256"),
        "behavioral_rows": behavioral.get("total_rows"),
        "behavioral_families": behavioral.get("total_families"),
        "adversarial_rows": adversarial.get("total_rows"),
        "adversarial_families": adversarial.get("total_families"),
        "retention_rows": retention.get("required_rows"),
        "claim_ceiling": "SPEC_VALIDATION_ONLY / NO_CASE_GENERATION",
    }


def validate_grader_spec(value: dict) -> dict:
    reasons: list[str] = []
    if not isinstance(value, dict):
        return {
            "schema": "V10_FINAL_BANK_GRADER_SPEC_CHECK_V1",
            "status": "HOLD",
            "reasons": ["spec_not_object"],
        }

    if value.get("schema") != "V10_FINAL_BANK_GRADER_SPEC_V1":
        reasons.append("schema_mismatch")
    if value.get("status") != "FROZEN_PRETRAINING_GRADER_SPEC":
        reasons.append("status_mismatch")
    if value.get("effect") != "SPEC_ONLY_NO_SCORING":
        reasons.append("effect_mismatch")
    if value.get("final_scoring_authorized") is not False:
        reasons.append("final_scoring_authorized_not_false")

    for path in _find_plaintext_case_keys(value):
        reasons.append(f"plaintext_case_field_present:{path}")

    dimensions = value.get("dimensions")
    if not isinstance(dimensions, dict):
        reasons.append("dimensions_missing")
        dimensions = {}
    if set(dimensions) != set(DIMENSIONS):
        reasons.append("dimension_key_set_mismatch")

    expected_classes = {
        dimension: (
            "SEMANTIC_HUMAN"
            if dimension in SEMANTIC_HUMAN_DIMENSIONS
            else "MIXED"
        )
        for dimension in DIMENSIONS
    }
    for dimension, expected in expected_classes.items():
        item = dimensions.get(dimension)
        if not isinstance(item, dict):
            continue
        if item.get("primary_grading_class") != expected:
            reasons.append(
                f"{dimension}_primary_grading_class_mismatch"
            )
        if item.get(
            "critical_failure_rule_must_be_predeclared"
        ) is not True:
            reasons.append(
                f"{dimension}_critical_failure_predeclared_not_true"
            )
        if item.get(
            "candidate_identity_blinded_during_case_admission"
        ) is not True:
            reasons.append(
                f"{dimension}_candidate_blinding_not_true"
            )

    classes = value.get("grader_classes")
    if not isinstance(classes, dict):
        reasons.append("grader_classes_missing")
        classes = {}
    for required in (
        "DETERMINISTIC_CONTRACT",
        "SEMANTIC_HUMAN",
        "MIXED",
    ):
        if required not in classes:
            reasons.append(f"grader_class_missing:{required}")
    semantic = classes.get("SEMANTIC_HUMAN", {})
    if semantic.get("human_review_required") is not True:
        reasons.append("semantic_human_review_required_not_true")

    review = value.get("review_policy")
    if not isinstance(review, dict):
        reasons.append("review_policy_missing")
        review = {}
    if review.get("llm_may_substitute_for_human_review") is not False:
        reasons.append("llm_human_substitution_not_false")
    if review.get("blinded_to_candidate_identity") is not True:
        reasons.append("candidate_identity_blinding_not_true")
    if review.get("blinded_to_model_outputs_during_case_admission") is not True:
        reasons.append("model_output_blinding_not_true")
    if review.get("generation_actor_may_review_own_case") is not False:
        reasons.append("generation_actor_self_review_not_false")
    if review.get("human_author_and_reviewer_pools_disjoint") is not True:
        reasons.append("human_pool_disjointness_not_true")
    questions = review.get("required_review_questions")
    if not isinstance(questions, list) or len(questions) != 7:
        reasons.append("required_review_questions_count_mismatch")

    admission = value.get("admission_policy")
    if not isinstance(admission, dict):
        reasons.append("admission_policy_missing")
        admission = {}
    if admission.get("grader_bundle_frozen_before_candidate_training") is not True:
        reasons.append("grader_bundle_pretraining_freeze_not_true")
    if admission.get("grader_contract_mutation_after_candidate_freeze") is not False:
        reasons.append("grader_mutation_after_candidate_freeze_not_false")
    if admission.get("all_semantic_cases_require_human_review_receipt") is not True:
        reasons.append("semantic_review_receipt_gate_not_true")

    scoring = value.get("scoring_policy")
    if not isinstance(scoring, dict):
        reasons.append("scoring_policy_missing")
        scoring = {}
    if scoring.get("one_shot_final_per_candidate") is not True:
        reasons.append("one_shot_final_not_true")
    if scoring.get("post_reveal_tuning_forbidden") is not True:
        reasons.append("post_reveal_tuning_forbidden_not_true")
    if scoring.get("post_reveal_grader_edit_forbidden") is not True:
        reasons.append("post_reveal_grader_edit_forbidden_not_true")
    if scoring.get("critical_failures_max_per_gate") != 0:
        reasons.append("critical_failure_ceiling_mismatch")

    _check_spec_sha(value, reasons)
    reasons = sorted(set(reasons))
    return {
        "schema": "V10_FINAL_BANK_GRADER_SPEC_CHECK_V1",
        "status": "GRADER_SPEC_PASS" if not reasons else "HOLD",
        "reasons": reasons,
        "spec_sha256": value.get("spec_sha256"),
        "dimension_count": len(dimensions),
        "semantic_human_dimensions": SEMANTIC_HUMAN_DIMENSIONS,
        "mixed_dimensions": MIXED_DIMENSIONS,
        "claim_ceiling": "SPEC_VALIDATION_ONLY / NO_SCORING",
    }
