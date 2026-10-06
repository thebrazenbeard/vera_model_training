from __future__ import annotations

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
    seen: set[str] = set()

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
        elif case_id in seen:
            reasons.append(f"duplicate_case_id:{case_id}")
        else:
            seen.add(case_id)

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

    cases_per_bank = {
        bank: counts.get(bank, 0) for bank in REQUIRED_EVAL_BANKS
    }
    missing_banks = [
        bank for bank, count in cases_per_bank.items() if count == 0
    ]
    under_minimum_banks = [
        bank
        for bank, count in cases_per_bank.items()
        if count < minimum_cases_per_bank
    ]
    if missing_banks:
        reasons.append("missing_required_banks")
    if under_minimum_banks:
        reasons.append("development_screening_below_minimum")

    return {
        "schema": "STAGE2_BANK_MANIFEST_V1",
        "status": "PASS" if not reasons else "HOLD",
        "bank_count": len([b for b, c in cases_per_bank.items() if c > 0]),
        "case_count": len(cases),
        "minimum_cases_per_bank": minimum_cases_per_bank,
        "cases_per_bank": cases_per_bank,
        "missing_banks": missing_banks,
        "under_minimum_banks": under_minimum_banks,
        "reasons": reasons,
    }
