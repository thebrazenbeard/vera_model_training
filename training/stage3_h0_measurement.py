from __future__ import annotations

from collections import defaultdict

REQUIRED_H0_CONDITIONS = (
    "zero_shot",
    "supported",
    "family_transfer",
    "retrieval_disabled",
    "support_removed",
    "prior_behavior",
)


def _mean(values: list[float]) -> float:
    return sum(values) / len(values)


def build_h0_measurement_report(
    rows: list[dict],
    *,
    weight_change_performed: bool,
    success_threshold: float = 0.75,
) -> dict:
    reasons: list[str] = []
    by_family: dict[str, dict[str, list[dict]]] = defaultdict(
        lambda: defaultdict(list)
    )
    seen_case_ids: set[str] = set()
    peak_ram = 0.0
    peak_vram = 0.0
    max_latency = 0.0

    if weight_change_performed:
        reasons.append("h0_weight_change_forbidden")
    if not isinstance(success_threshold, (int, float)) or not 0 <= success_threshold <= 1:
        reasons.append("success_threshold_invalid")

    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            reasons.append(f"row[{index}]:not_object")
            continue
        case_id = str(row.get("case_id") or "")
        family = str(row.get("family") or "")
        condition = str(row.get("condition") or "")
        score = row.get("score")
        if not case_id:
            reasons.append(f"row[{index}]:case_id_missing")
        elif case_id in seen_case_ids:
            if "duplicate_case_id" not in reasons:
                reasons.append("duplicate_case_id")
        else:
            seen_case_ids.add(case_id)
        if not family:
            reasons.append(f"row[{index}]:family_missing")
            continue
        if condition not in REQUIRED_H0_CONDITIONS:
            reasons.append(f"row[{index}]:unknown_condition:{condition}")
            continue
        if not isinstance(score, (int, float)):
            reasons.append(f"row[{index}]:score_missing")
            continue
        demonstrations = row.get("demonstrations_seen", 0)
        failures = row.get("failures_seen", 0)
        if not isinstance(demonstrations, int) or demonstrations < 0:
            reasons.append(f"row[{index}]:demonstrations_seen_invalid")
            continue
        if not isinstance(failures, int) or failures < 0:
            reasons.append(f"row[{index}]:failures_seen_invalid")
            continue
        baseline = row.get("baseline_score")
        if condition == "prior_behavior" and not isinstance(baseline, (int, float)):
            reasons.append(f"row[{index}]:prior_behavior_baseline_missing")
            continue

        normalized = {
            "case_id": case_id,
            "score": float(score),
            "baseline_score": float(baseline) if isinstance(baseline, (int, float)) else None,
            "demonstrations_seen": demonstrations,
            "failures_seen": failures,
        }
        by_family[family][condition].append(normalized)

        for key, target in (
            ("ram_mib", "ram"),
            ("vram_mib", "vram"),
            ("latency_ms", "latency"),
        ):
            value = row.get(key, 0)
            if not isinstance(value, (int, float)) or value < 0:
                reasons.append(f"row[{index}]:{key}_invalid")
                continue
            if target == "ram":
                peak_ram = max(peak_ram, float(value))
            elif target == "vram":
                peak_vram = max(peak_vram, float(value))
            else:
                max_latency = max(max_latency, float(value))

    missing: dict[str, list[str]] = {}
    family_metrics: dict[str, dict] = {}
    for family, conditions in sorted(by_family.items()):
        absent = [
            condition for condition in REQUIRED_H0_CONDITIONS
            if not conditions.get(condition)
        ]
        if absent:
            missing[family] = absent
            continue

        zero = _mean([r["score"] for r in conditions["zero_shot"]])
        supported = _mean([r["score"] for r in conditions["supported"]])
        transfer = _mean([r["score"] for r in conditions["family_transfer"]])
        retrieval_disabled = _mean(
            [r["score"] for r in conditions["retrieval_disabled"]]
        )
        support_removed = _mean(
            [r["score"] for r in conditions["support_removed"]]
        )
        prior_current = _mean(
            [r["score"] for r in conditions["prior_behavior"]]
        )
        prior_baseline = _mean(
            [r["baseline_score"] for r in conditions["prior_behavior"]]
        )
        support_gain = supported - zero

        successful_supported = [
            r for r in conditions["supported"]
            if r["score"] >= float(success_threshold)
        ]
        examples_to_success = (
            min(r["demonstrations_seen"] for r in successful_supported)
            if successful_supported else None
        )
        mean_demos = _mean(
            [float(r["demonstrations_seen"]) for r in conditions["supported"]]
        )
        mean_failures = _mean(
            [float(r["failures_seen"]) for r in conditions["supported"]]
        )

        family_metrics[family] = {
            "zero_shot_competence": zero,
            "supported_competence": supported,
            "examples_to_success": examples_to_success,
            "support_gain": support_gain,
            "improvement_per_demonstration": (
                support_gain / mean_demos if mean_demos > 0 else None
            ),
            "improvement_per_failure": (
                support_gain / mean_failures if mean_failures > 0 else None
            ),
            "family_transfer": transfer,
            "retrieval_dependence": supported - retrieval_disabled,
            "support_removed_retention": support_removed - zero,
            "prior_behavior_regression": prior_current - prior_baseline,
        }

    if not by_family:
        reasons.append("no_h0_families")
    if missing:
        reasons.append("required_h0_condition_missing")

    return {
        "schema": "STAGE3_H0_MEASUREMENT_REPORT_V2",
        "status": "PASS" if not reasons else "HOLD",
        "weight_change_performed": bool(weight_change_performed),
        "success_threshold": float(success_threshold),
        "required_conditions": list(REQUIRED_H0_CONDITIONS),
        "missing_conditions_by_family": missing,
        "family_metrics": family_metrics,
        "peak_ram_mib": peak_ram,
        "peak_vram_mib": peak_vram,
        "max_latency_ms": max_latency,
        "claim_ceiling": "H0_NO_WEIGHT_BASELINE_MEASUREMENT_ONLY",
        "reasons": reasons,
    }
