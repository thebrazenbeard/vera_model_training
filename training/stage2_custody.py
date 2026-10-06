from __future__ import annotations


def build_stage2_custody_report(
    *,
    c_target_record_ids: set[str],
    training_record_ids: set[str],
    config_visible_record_ids: set[str],
    c_freeze_complete: bool,
    custody_owner: str,
) -> dict:
    targets = {str(x) for x in c_target_record_ids}
    training = {str(x) for x in training_record_ids}
    config_visible = {str(x) for x in config_visible_record_ids}

    training_overlap = sorted(targets & training)
    config_overlap = sorted(targets & config_visible)
    reasons: list[str] = []

    if training_overlap:
        reasons.append("c_target_rows_in_training")
    if not c_freeze_complete and config_overlap:
        reasons.append("c_target_rows_visible_before_c_freeze")
    if not c_freeze_complete and custody_owner != "Lane-C":
        reasons.append("pre_freeze_custody_owner_must_be_lane_c")

    return {
        "schema": "STAGE2_C_TARGET_CUSTODY_REPORT_V1",
        "status": "PASS" if not reasons else "HOLD",
        "c_freeze_complete": bool(c_freeze_complete),
        "custody_owner": custody_owner,
        "c_target_count": len(targets),
        "c_target_training_overlap": training_overlap,
        "c_target_config_overlap": config_overlap,
        "reasons": reasons,
    }
