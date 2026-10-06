from __future__ import annotations

REQUIRED_H0_CONTROLS = (
    "frozen_base_zero_shot",
    "in_context_support",
    "governed_external_memory",
    "family_transfer",
    "retrieval_disabled",
    "support_removed_fresh_process",
    "prior_behavior_regression",
)


def build_h0_control_contract(
    *,
    controls: list[str],
    context_enabled: bool,
    governed_external_memory_enabled: bool,
    weight_updates_authorized: bool,
    frozen_base_verified: bool,
    additional_mutable_state_enabled: bool,
) -> dict:
    present = {str(item) for item in controls}
    required = set(REQUIRED_H0_CONTROLS)
    missing = [item for item in REQUIRED_H0_CONTROLS if item not in present]
    unknown = sorted(present - required)
    reasons: list[str] = []

    if missing:
        reasons.append("required_h0_controls_missing")
    if unknown:
        reasons.append("unknown_h0_control")
    if weight_updates_authorized:
        reasons.append("h0_weight_updates_forbidden")
    if not frozen_base_verified:
        reasons.append("h0_frozen_base_not_verified")
    if not context_enabled:
        reasons.append("h0_context_control_disabled")
    if not governed_external_memory_enabled:
        reasons.append("h0_governed_external_memory_disabled")
    if additional_mutable_state_enabled:
        reasons.append("h0_unapproved_mutable_state_enabled")

    return {
        "schema": "STAGE3_H0_CONTROL_CONTRACT_V2",
        "status": "PASS" if not reasons else "HOLD",
        "required_controls": list(REQUIRED_H0_CONTROLS),
        "present_controls": sorted(present),
        "missing_controls": missing,
        "unknown_controls": unknown,
        "context_enabled": bool(context_enabled),
        "governed_external_memory_enabled": bool(
            governed_external_memory_enabled
        ),
        "weight_updates_authorized": bool(weight_updates_authorized),
        "frozen_base_verified": bool(frozen_base_verified),
        "additional_mutable_state_enabled": bool(
            additional_mutable_state_enabled
        ),
        "claim_ceiling": "FROZEN_BASE_CONTEXT_GOVERNED_MEMORY_CONTROL_ONLY",
        "reasons": reasons,
    }
