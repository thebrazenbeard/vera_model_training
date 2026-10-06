from __future__ import annotations


def _values(records: list[dict], key: str) -> set[str]:
    return {
        str(row[key])
        for row in records
        if isinstance(row, dict) and row.get(key) not in (None, "")
    }




def _normalize_text(value: object) -> str:
    return " ".join(str(value or "").casefold().split())


def _normalized_pair(record: dict) -> tuple[str, str]:
    return (
        _normalize_text(record.get("prompt")),
        _normalize_text(record.get("response")),
    )


def _normalized_duplicate_pairs(
    train_records: list[dict],
    protected_records: list[dict],
) -> list[list[str]]:
    train_by_pair: dict[tuple[str, str], list[str]] = {}
    for index, row in enumerate(train_records):
        if not isinstance(row, dict):
            continue
        pair = _normalized_pair(row)
        if not any(pair):
            continue
        train_by_pair.setdefault(pair, []).append(
            str(row.get("stable_record_id") or f"train[{index}]")
        )
    overlaps: list[list[str]] = []
    for index, row in enumerate(protected_records):
        if not isinstance(row, dict):
            continue
        pair = _normalized_pair(row)
        protected_id = str(row.get("stable_record_id") or f"protected[{index}]")
        for train_id in train_by_pair.get(pair, []):
            overlaps.append([train_id, protected_id])
    return sorted(overlaps)

def build_stage2_contamination_report(
    train_records: list[dict],
    protected_records: list[dict],
    *,
    near_duplicate_pairs: list[dict],
    near_duplicate_scan_performed: bool = False,
) -> dict:
    record_id_overlap = sorted(
        _values(train_records, "stable_record_id")
        & _values(protected_records, "stable_record_id")
    )
    content_hash_overlap = sorted(
        _values(train_records, "content_hash")
        & _values(protected_records, "content_hash")
    )
    template_ancestry_overlap = sorted(
        _values(train_records, "semantic_template_ancestry")
        & _values(protected_records, "semantic_template_ancestry")
    )
    source_overlap = sorted(
        _values(train_records, "exact_source_provenance")
        & _values(protected_records, "exact_source_provenance")
    )
    counterfactual_twin_overlap = sorted(
        _values(train_records, "counterfactual_twin_group")
        & _values(protected_records, "counterfactual_twin_group")
    )

    train_text = "\n".join(
        str(row.get(field, ""))
        for row in train_records
        if isinstance(row, dict)
        for field in ("prompt", "response")
    )
    protected_canary_hits = sorted(
        {
            str(row["protected_canary"])
            for row in protected_records
            if isinstance(row, dict)
            and row.get("protected_canary")
            and str(row["protected_canary"]) in train_text
        }
    )
    normalized_duplicate_pairs = _normalized_duplicate_pairs(
        train_records, protected_records
    )
    reasons: list[str] = []
    if not near_duplicate_scan_performed:
        reasons.append("near_duplicate_scan_not_performed")
    if record_id_overlap:
        reasons.append("record_id_overlap")
    if content_hash_overlap:
        reasons.append("content_hash_overlap")
    if template_ancestry_overlap:
        reasons.append("template_ancestry_overlap")
    if source_overlap:
        reasons.append("source_provenance_overlap")
    if counterfactual_twin_overlap:
        reasons.append("counterfactual_twin_overlap")
    if near_duplicate_pairs:
        reasons.append("near_duplicate_overlap")
    if protected_canary_hits:
        reasons.append("protected_canary_leakage")
    if normalized_duplicate_pairs:
        reasons.append("normalized_duplicate_overlap")

    return {
        "schema": "STAGE2_CONTAMINATION_REPORT_V1",
        "status": "PASS" if not reasons else "HOLD",
        "record_id_overlap": record_id_overlap,
        "content_hash_overlap": content_hash_overlap,
        "template_ancestry_overlap": template_ancestry_overlap,
        "source_provenance_overlap": source_overlap,
        "counterfactual_twin_overlap": counterfactual_twin_overlap,
        "near_duplicate_pairs": list(near_duplicate_pairs),
        "near_duplicate_scan_performed": bool(near_duplicate_scan_performed),
        "protected_canary_hits": protected_canary_hits,
        "normalized_duplicate_pairs": normalized_duplicate_pairs,
        "reasons": reasons,
    }
