from __future__ import annotations

from collections import Counter, defaultdict

from training.stage2_eval_contract import REQUIRED_EVAL_BANKS

REQUIRED_PROMOTION_FAMILIES = tuple(REQUIRED_EVAL_BANKS)


def build_paired_inference_contract(
    rows: list[dict],
    *,
    minimum_pairs_per_family: int = 80,
    power_preregistered: bool,
) -> dict:
    reasons: list[str] = []
    counts = Counter()
    deltas: dict[str, list[float]] = defaultdict(list)
    seen: set[tuple[str, str]] = set()
    unknown_families: set[str] = set()

    if minimum_pairs_per_family < 1:
        reasons.append("minimum_pairs_per_family_invalid")
    if not power_preregistered:
        reasons.append("power_not_preregistered")

    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            reasons.append(f"row[{index}]:not_object")
            continue
        case_id = str(row.get("case_id") or "")
        family = str(row.get("family") or "")
        key = (family, case_id)
        if not family:
            reasons.append(f"row[{index}]:family_missing")
            continue
        if family not in REQUIRED_PROMOTION_FAMILIES:
            unknown_families.add(family)
        if not case_id:
            reasons.append(f"row[{index}]:case_id_missing")
            continue
        if key in seen:
            reasons.append(f"duplicate_pair:{family}:{case_id}")
            continue
        seen.add(key)

        control = row.get("control_score")
        candidate = row.get("candidate_score")
        if not isinstance(control, (int, float)) or not isinstance(candidate, (int, float)):
            reasons.append(f"row[{index}]:paired_scores_missing")
            continue

        counts[family] += 1
        deltas[family].append(float(candidate) - float(control))

    family_pair_counts = {
        family: counts.get(family, 0)
        for family in REQUIRED_PROMOTION_FAMILIES
    }
    missing_families = [
        family for family, count in family_pair_counts.items() if count == 0
    ]
    underpowered_families = [
        family for family, count in family_pair_counts.items()
        if count < minimum_pairs_per_family
    ]
    if missing_families:
        reasons.append("required_promotion_family_missing")
    if underpowered_families:
        reasons.append("paired_family_below_preregistered_minimum")
    if unknown_families:
        reasons.append("unknown_promotion_family")
    if not any(family_pair_counts.values()):
        reasons.append("no_paired_families")

    family_mean_delta = {
        family: sum(values) / len(values)
        for family, values in sorted(deltas.items())
        if family in REQUIRED_PROMOTION_FAMILIES and values
    }
    return {
        "schema": "STAGE2_PAIRED_INFERENCE_CONTRACT_V1",
        "status": "PASS" if not reasons else "HOLD",
        "paired_design": True,
        "power_preregistered": bool(power_preregistered),
        "minimum_pairs_per_family": minimum_pairs_per_family,
        "family_pair_counts": family_pair_counts,
        "missing_families": missing_families,
        "underpowered_families": underpowered_families,
        "unknown_families": sorted(unknown_families),
        "family_mean_delta": family_mean_delta,
        "claim_ceiling": "PAIRED_ANALYSIS_CONTRACT_ONLY_NOT_PROMOTION_WIN",
        "reasons": reasons,
    }
