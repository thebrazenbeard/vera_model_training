from __future__ import annotations


def build_stage2_gate_packet(
    *,
    baseline_manifest: dict,
    eval_contract: dict,
    contamination_report: dict,
) -> dict:
    reasons: list[str] = []
    if baseline_manifest.get("status") != "PASS":
        reasons.append("baseline_manifest_not_pass")
    if eval_contract.get("status") != "PASS":
        reasons.extend(
            f"eval_contract:{reason}"
            for reason in eval_contract.get("reasons", [])
        )
        if not eval_contract.get("reasons"):
            reasons.append("eval_contract_not_pass")
    if contamination_report.get("status") != "PASS":
        reasons.extend(
            f"contamination_report:{reason}"
            for reason in contamination_report.get("reasons", [])
        )
        if not contamination_report.get("reasons"):
            reasons.append("contamination_report_not_pass")

    manifest_sha = baseline_manifest.get("manifest_sha256")
    if not manifest_sha:
        reasons.append("baseline_manifest_sha256_missing")

    return {
        "schema": "STAGE2_ABC_GATE_PACKET_V1",
        "status": "PASS" if not reasons else "HOLD",
        "baseline_manifest_sha256": manifest_sha,
        "eval_contract_status": eval_contract.get("status"),
        "contamination_status": contamination_report.get("status"),
        "reasons": reasons,
    }
