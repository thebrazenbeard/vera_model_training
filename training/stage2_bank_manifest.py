from __future__ import annotations

import hashlib
import json
import re
from collections import Counter

from training.stage2_eval_contract import REQUIRED_EVAL_BANKS

_SHA256 = re.compile(r"^[0-9a-f]{64}$")


def build_stage2_bank_manifest(
    cases: list[dict],
    *,
    minimum_cases_per_bank: int = 20,
) -> dict:
    reasons: list[str] = []
    counts = Counter()
    seen_ids: set[str] = set()
    seen_payloads: set[tuple[str, str]] = set()
    normalized_cases: list[dict] = []

    if minimum_cases_per_bank < 1:
        reasons.append("minimum_cases_per_bank_invalid")

    for index, row in enumerate(cases):
        if not isinstance(row, dict):
            reasons.append(f"case[{index}]:not_object")
            continue
        case_id = str(row.get("case_id") or "")
        bank = str(row.get("bank") or "")
        prompt_hash = str(row.get("prompt_hash") or "")
        grading_hash = str(row.get("grading_hash") or "")
        custody = str(row.get("custody") or "")

        if not case_id:
            reasons.append(f"case[{index}]:case_id_missing")
        elif case_id in seen_ids:
            reasons.append(f"duplicate_case_id:{case_id}")
        else:
            seen_ids.add(case_id)

        payload_key = (prompt_hash, grading_hash)
        if payload_key in seen_payloads:
            if "duplicate_case_payload" not in reasons:
                reasons.append("duplicate_case_payload")
        else:
            seen_payloads.add(payload_key)

        if bank not in REQUIRED_EVAL_BANKS:
            reasons.append(f"case[{index}]:unknown_bank:{bank}")
        else:
            counts[bank] += 1

        if _SHA256.fullmatch(prompt_hash) is None:
            reasons.append(f"case[{index}]:prompt_hash_invalid")
        if _SHA256.fullmatch(grading_hash) is None:
            reasons.append(f"case[{index}]:grading_hash_invalid")
        if not custody:
            reasons.append(f"case[{index}]:custody_missing")

        normalized_cases.append({
            "case_id": case_id,
            "bank": bank,
            "prompt_hash": prompt_hash,
            "grading_hash": grading_hash,
            "custody": custody,
        })

    cases_per_bank = {
        bank: counts.get(bank, 0) for bank in REQUIRED_EVAL_BANKS
    }
    missing_banks = [
        bank for bank, count in cases_per_bank.items() if count == 0
    ]
    under_minimum_banks = [
        bank for bank, count in cases_per_bank.items()
        if count < minimum_cases_per_bank
    ]
    if missing_banks:
        reasons.append("missing_required_banks")
    if under_minimum_banks:
        reasons.append("development_screening_below_minimum")

    normalized_cases.sort(key=lambda row: row["case_id"])
    identity = {
        "schema": "STAGE2_BANK_MANIFEST_V1",
        "case_count": len(cases),
        "minimum_cases_per_bank": minimum_cases_per_bank,
        "cases_per_bank": cases_per_bank,
        "cases": normalized_cases,
    }
    digest = hashlib.sha256(
        json.dumps(identity, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()

    return {
        **identity,
        "status": "PASS" if not reasons else "HOLD",
        "bank_count": len([b for b, c in cases_per_bank.items() if c > 0]),
        "missing_banks": missing_banks,
        "under_minimum_banks": under_minimum_banks,
        "manifest_sha256": digest,
        "reasons": reasons,
    }
