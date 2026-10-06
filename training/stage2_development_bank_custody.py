from __future__ import annotations

import re

_HEAD = re.compile(r"^[0-9a-f]{40}$")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_ALLOWED_CUSTODY = {"dev", "open-test"}


def build_development_bank_custody_report(
    cases: list[dict],
    *,
    c_freeze_complete: bool,
    custody_owner: str,
    c_config_visible_case_ids: set[str],
    c_freeze_subject: str | None = None,
    custody_receipt_sha256: str | None = None,
) -> dict:
    reasons: list[str] = []
    if not isinstance(custody_owner, str) or not custody_owner:
        reasons.append("custody_owner_missing")
    if not isinstance(c_config_visible_case_ids, set):
        raise ValueError("c_config_visible_case_ids must be a set")

    c_targets: set[str] = set()
    invalid_custody: list[str] = []
    for index, case in enumerate(cases):
        if not isinstance(case, dict):
            reasons.append(f"case[{index}]:not_object")
            continue
        case_id = str(case.get("case_id") or "")
        if not case_id:
            reasons.append(f"case[{index}]:case_id_missing")
            continue
        if case.get("intended_custody") not in _ALLOWED_CUSTODY:
            invalid_custody.append(case_id)
        if case.get("lane_c_target") is True:
            c_targets.add(case_id)

    if invalid_custody:
        reasons.append("development_bank_contains_invalid_or_protected_custody")

    overlap = sorted(c_targets & {str(x) for x in c_config_visible_case_ids})
    if not c_freeze_complete:
        if custody_owner == "Lane-C":
            reasons.append("pre_freeze_custodian_must_be_independent_of_lane_c")
        if overlap:
            reasons.append("c_target_visible_to_lane_c_before_freeze")
    else:
        if _HEAD.fullmatch(str(c_freeze_subject or "")) is None:
            reasons.append("c_freeze_subject_missing_or_invalid")
        if _SHA256.fullmatch(str(custody_receipt_sha256 or "")) is None:
            reasons.append("custody_receipt_sha256_missing_or_invalid")

    return {
        "schema": "STAGE2_DEVELOPMENT_BANK_CUSTODY_V1",
        "status": "PASS" if not reasons else "HOLD",
        "c_freeze_complete": bool(c_freeze_complete),
        "custody_owner": custody_owner,
        "c_target_count": len(c_targets),
        "c_target_case_ids": sorted(c_targets),
        "c_target_config_overlap": overlap,
        "invalid_custody_case_ids": sorted(invalid_custody),
        "c_freeze_subject": c_freeze_subject,
        "custody_receipt_sha256": custody_receipt_sha256,
        "claim_ceiling": "DEVELOPMENT_BANK_CUSTODY_ONLY_NOT_FINAL_BANK",
        "reasons": reasons,
    }
