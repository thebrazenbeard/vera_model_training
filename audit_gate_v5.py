from __future__ import annotations

from typing import Any

import quality_gate


_ORIGINAL_QUALIFY = quality_gate.conservative_qualification
_ORIGINAL_BUILD_CAPSULE = quality_gate.build_capsule


def conservative_qualification(spec, caps, audit, transfers, evidence) -> dict[str, Any]:
    result = _ORIGINAL_QUALIFY(spec, caps, audit, transfers, evidence)

    clean_flags = []
    for item in transfers:
        exam = item.get("exam", {}) if isinstance(item, dict) else {}
        corrections = exam.get("corrections") if isinstance(exam.get("corrections"), list) else []
        clean_flags.append(
            int(exam.get("score", 0) or 0) >= 3
            and bool(exam.get("passed", True))
            and not bool(exam.get("critical_failure", False))
            and not corrections
        )
    transfer_clean = len(clean_flags) == 2 and all(clean_flags)

    profile = [bool(x.get("task", {}).get("adversarial", False)) for x in transfers]
    transfer_profile_ready = profile == [False, True]

    result["transfer_clean"] = transfer_clean
    result["transfer_profile_ready"] = transfer_profile_ready
    result["transfer_corrections"] = [
        str(correction)
        for item in transfers
        for correction in (item.get("exam", {}).get("corrections") or [])
        if str(correction).strip()
    ]

    if not transfer_clean or not transfer_profile_ready:
        result["training_package_ready"] = False
        result["outcome"] = "FAIL"
        result["condition"] = (
            "External proxy transfer must contain one clean ordinary case and one clean adversarial case, "
            "with no examiner-reported corrections, before the package can be handed to native qualification."
        )
    return result


def build_capsule(spec, knowledge: str, caps, lessons: list[str], qual: dict[str, Any]) -> str:
    capsule = _ORIGINAL_BUILD_CAPSULE(spec, knowledge, caps, lessons, qual)
    for cap in qual.get("capability_proxy_evidence", []):
        name = str(cap.get("name", "")).strip()
        description = str(cap.get("description", "")).strip()
        if not name or not description:
            continue
        old = f"- **{name}**: {description}"
        new = f"- **{name}**: MODEL-PROPOSED SCOPE (UNVERIFIED): {description}"
        capsule = capsule.replace(old, new)
    return capsule
