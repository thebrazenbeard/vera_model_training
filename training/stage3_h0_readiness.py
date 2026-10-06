from __future__ import annotations

import re

from training.stage2_eval_contract import REQUIRED_EVAL_BANKS

_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_HEAD = re.compile(r"^[0-9a-f]{40}$")


def _sha(value) -> bool:
    return isinstance(value, str) and _SHA256.fullmatch(value) is not None


def build_stage3_h0_readiness(
    *,
    stage0_runtime_receipt: dict,
    stage2_qualification_packet: dict,
    bank_manifest: dict,
    h0_control_contract: dict,
    development_bank_materialized: bool,
    independent_review_complete: bool,
    protected_final_used: bool,
) -> dict:
    reasons: list[str] = []

    if stage0_runtime_receipt.get("status") != "STAGE0_RUNTIME_QUALIFIED":
        reasons.append("stage0_runtime_not_qualified")
    subject = stage0_runtime_receipt.get("qualified_subject_head")
    if not isinstance(subject, str) or _HEAD.fullmatch(subject) is None:
        reasons.append("stage0_qualified_subject_invalid")

    if stage2_qualification_packet.get("status") != "PASS":
        reasons.append("stage2_qualification_packet_not_pass")
    baseline_sha = stage2_qualification_packet.get("baseline_manifest_sha256")
    stage2_bank_sha = stage2_qualification_packet.get("bank_manifest_sha256")
    if not _sha(baseline_sha):
        reasons.append("stage2_baseline_manifest_sha_invalid")
    if not _sha(stage2_bank_sha):
        reasons.append("stage2_bank_manifest_sha_invalid")

    if bank_manifest.get("status") != "PASS":
        reasons.append("development_bank_manifest_not_pass")
    if bank_manifest.get("bank_count") != len(REQUIRED_EVAL_BANKS):
        reasons.append("development_bank_count_invalid")
    expected_minimum_cases = len(REQUIRED_EVAL_BANKS) * 20
    if int(bank_manifest.get("case_count") or 0) < expected_minimum_cases:
        reasons.append("development_bank_case_count_below_floor")
    if int(bank_manifest.get("minimum_cases_per_bank") or 0) < 20:
        reasons.append("development_bank_per_family_floor_below_20")
    if bank_manifest.get("under_minimum_banks"):
        reasons.append("development_bank_under_minimum_banks")
    manifest_sha = bank_manifest.get("manifest_sha256")
    if not _sha(manifest_sha):
        reasons.append("development_bank_manifest_sha_invalid")
    elif _sha(stage2_bank_sha) and manifest_sha != stage2_bank_sha:
        reasons.append("stage2_bank_manifest_binding_mismatch")

    if h0_control_contract.get("status") != "PASS":
        reasons.append("h0_control_contract_not_pass")
    if not _sha(h0_control_contract.get("isolation_receipt_sha256")):
        reasons.append("h0_isolation_receipt_missing_or_invalid")

    if not development_bank_materialized:
        reasons.append("development_bank_not_materialized")
    if not independent_review_complete:
        reasons.append("development_bank_independent_review_incomplete")
    if protected_final_used:
        reasons.append("protected_final_use_forbidden")

    return {
        "schema": "STAGE3_H0_READINESS_V1",
        "status": (
            "READY_FOR_H0_DEVELOPMENT_RUN" if not reasons else "HOLD"
        ),
        "stage0_qualified_subject_head": subject,
        "stage2_baseline_manifest_sha256": baseline_sha,
        "stage2_bank_manifest_sha256": stage2_bank_sha,
        "development_bank_manifest_sha256": manifest_sha,
        "required_bank_count": len(REQUIRED_EVAL_BANKS),
        "minimum_development_cases_per_bank": 20,
        "development_bank_materialized": bool(development_bank_materialized),
        "independent_review_complete": bool(independent_review_complete),
        "protected_final_used": bool(protected_final_used),
        "claim_ceiling": (
            "H0_DEVELOPMENT_READINESS_ONLY_NOT_PROMOTION_OR_FINAL_QUALIFICATION"
        ),
        "reasons": reasons,
    }
