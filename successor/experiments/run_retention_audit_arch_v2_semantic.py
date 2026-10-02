from __future__ import annotations

from collections import Counter
import json
from typing import Callable

from successor.experiments.retention_audit_arch_v2_reviewer import (
    parse_witness_response,
    review_prompt,
)


def run_semantic_audit(
    cases: list[dict],
    *,
    call_reviewer: Callable[[str, list[dict]], str],
    expected_count: int,
    max_attempts: int = 3,
) -> dict:
    if max_attempts < 1:
        raise ValueError("max_attempts must be positive")
    if len(cases) != expected_count:
        return {
            "status": "SEMANTIC_AUDIT_HOLD",
            "reviewed": 0,
            "expected_count": expected_count,
            "observation_counts": {},
            "reasons": ["row_count_mismatch"],
            "rows": [],
        }

    rows: list[dict] = []
    for case in cases:
        case_id = case["case_id"]
        prompt = review_prompt([case])
        failures: list[str] = []

        parsed: list[dict] | None = None
        attempts = 0
        for attempts in range(1, max_attempts + 1):
            try:
                response_text = call_reviewer(prompt, [case])
                if not isinstance(response_text, str) or not response_text.strip():
                    raise ValueError("empty reviewer response")
                parsed = parse_witness_response(
                    response_text,
                    expected_case_ids=[case_id],
                )
                break
            except (ValueError, json.JSONDecodeError) as exc:
                failures.append(
                    f"attempt_{attempts}:{type(exc).__name__}:{exc}"
                )

        if parsed is None:
            return {
                "status": "SEMANTIC_AUDIT_HOLD",
                "reviewed": len(rows),
                "expected_count": expected_count,
                "observation_counts": dict(
                    sorted(
                        Counter(
                            row["observation"] for row in rows
                        ).items()
                    )
                ),
                "reasons": [f"transport_failure:{case_id}"],
                "rows": rows,
                "transport_failures": failures,
            }

        review = parsed[0]
        rows.append({
            "case_id": case_id,
            "family_id": case.get("family_id"),
            "observation": review["observation"],
            "derived_answer": review["derived_answer"],
            "witness": review["witness"],
            "reason": review["reason"],
            "confidence": review["confidence"],
            "attempts": attempts,
            "prior_attempt_failures": failures,
        })

    counts = Counter(row["observation"] for row in rows)
    return {
        "status": "SEMANTIC_AUDIT_COMPLETE",
        "reviewed": len(rows),
        "expected_count": expected_count,
        "observation_counts": dict(sorted(counts.items())),
        "reasons": [],
        "rows": rows,
    }
