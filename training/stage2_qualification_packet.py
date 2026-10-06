from __future__ import annotations


def _append_component_reasons(
    reasons: list[str],
    *,
    label: str,
    component: dict,
) -> None:
    if component.get("status") == "PASS":
        return
    component_reasons = component.get("reasons") or []
    if component_reasons:
        reasons.extend(f"{label}:{reason}" for reason in component_reasons)
    else:
        reasons.append(f"{label}:not_pass")


def build_stage2_qualification_packet(
    *,
    baseline_manifest: dict,
    eval_contract: dict,
    contamination_report: dict,
    bank_manifest: dict,
    paired_inference: dict,
    custody_report: dict,
) -> dict:
    reasons: list[str] = []

    if baseline_manifest.get("status") != "PASS":
        reasons.append("baseline_manifest:not_pass")
    _append_component_reasons(
        reasons, label="eval_contract", component=eval_contract
    )
    _append_component_reasons(
        reasons,
        label="contamination_report",
        component=contamination_report,
    )
    _append_component_reasons(
        reasons, label="bank_manifest", component=bank_manifest
    )
    _append_component_reasons(
        reasons, label="paired_inference", component=paired_inference
    )
    _append_component_reasons(
        reasons, label="custody_report", component=custody_report
    )

    baseline_sha = baseline_manifest.get("manifest_sha256")
    bank_sha = bank_manifest.get("manifest_sha256")
    if not baseline_sha:
        reasons.append("baseline_manifest:manifest_sha256_missing")
    if not bank_sha:
        reasons.append("bank_manifest:manifest_sha256_missing")

    return {
        "schema": "STAGE2_QUALIFICATION_PACKET_V2",
        "status": "PASS" if not reasons else "HOLD",
        "baseline_manifest_sha256": baseline_sha,
        "bank_manifest_sha256": bank_sha,
        "eval_contract_status": eval_contract.get("status"),
        "contamination_status": contamination_report.get("status"),
        "paired_inference_status": paired_inference.get("status"),
        "custody_status": custody_report.get("status"),
        "reasons": reasons,
    }
