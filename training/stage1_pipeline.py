from __future__ import annotations

from training.stage1_admissibility import evaluate_record
from training.stage1_capability_coverage import build_coverage_report
from training.stage1_corpus_manifest import Stage1ManifestHold, build_stage1_manifest


def build_stage1_packet(records: list[dict], *, source_head: str, plan_blob: str) -> dict:
    admissibility = [evaluate_record(record) for record in records]
    reasons: list[str] = []
    for index, result in enumerate(admissibility):
        if result["status"] != "PASS":
            reasons.extend(
                f"record[{index}]:{reason}" for reason in result.get("reasons", [])
            )

    coverage = build_coverage_report(records)
    if coverage["status"] != "PASS":
        reasons.extend(
            f"missing_capability_family:{family}"
            for family in coverage.get("missing_families", [])
        )
        reasons.extend(
            f"unknown_capability_family:{family}"
            for family in coverage.get("unknown_families", [])
        )

    manifest = None
    if not reasons:
        try:
            manifest = build_stage1_manifest(
                records,
                source_head=source_head,
                plan_blob=plan_blob,
            )
        except Stage1ManifestHold as exc:
            reasons.append(f"manifest_hold:{exc}")

    return {
        "schema": "STAGE1_ABC_GATE_PACKET_V1",
        "status": "PASS" if not reasons and manifest is not None else "HOLD",
        "admissibility": admissibility,
        "coverage": coverage,
        "manifest": manifest,
        "reasons": reasons,
    }
