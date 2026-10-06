from __future__ import annotations


def classify_h0_retention(
    *,
    zero_shot_score: float,
    supported_score: float,
    support_removed_score: float,
    retrieval_disabled_score: float,
    weight_change_performed: bool,
    fresh_process_retest: bool,
) -> dict:
    values = {
        "zero_shot_score": zero_shot_score,
        "supported_score": supported_score,
        "support_removed_score": support_removed_score,
        "retrieval_disabled_score": retrieval_disabled_score,
    }
    for name, value in values.items():
        if not isinstance(value, (int, float)):
            raise ValueError(f"{name} must be numeric")

    zero = float(zero_shot_score)
    supported = float(supported_score)
    support_removed = float(support_removed_score)
    retrieval_disabled = float(retrieval_disabled_score)
    support_gain = supported - zero
    support_removed_retention = support_removed - zero
    retrieval_disabled_retention = retrieval_disabled - zero

    if weight_change_performed:
        classification = "OUTSIDE_H0_WEIGHT_CHANGE_PRESENT"
    elif not fresh_process_retest:
        classification = "UNRESOLVED_NO_FRESH_PROCESS"
    elif (
        support_gain > 0
        and support_removed_retention <= 0
        and retrieval_disabled_retention <= 0
    ):
        classification = "IN_CONTEXT_ADAPTATION_NOT_DURABLE_LEARNING"
    elif support_gain > 0:
        classification = "NO_WEIGHT_RETENTION_UNRESOLVED"
    else:
        classification = "NO_MEASURED_H0_GAIN"

    return {
        "schema": "STAGE3_H0_RETENTION_FALSIFIER_V2",
        "classification": classification,
        "weight_change_performed": bool(weight_change_performed),
        "fresh_process_retest": bool(fresh_process_retest),
        "support_gain": support_gain,
        "support_removed_retention": support_removed_retention,
        "retrieval_disabled_retention": retrieval_disabled_retention,
        "durable_learning_claim_allowed": False,
        "durable_weight_learning_claim_allowed": False,
        "claim_ceiling": "H0_NO_WEIGHT_ATTRIBUTION_ONLY",
    }
