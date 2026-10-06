from __future__ import annotations

import hashlib
import json


def review_subject_digest(case: dict) -> str:
    payload = {
        "case_id": case.get("case_id"),
        "generator_actor_id": case.get("generator_actor_id"),
        "prompt": case.get("prompt"),
        "grading": case.get("grading"),
    }
    return hashlib.sha256(
        json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
    ).hexdigest()


def build_development_bank_review_report(
    cases: list[dict],
    *,
    case_reviews: list[dict],
    grader_ids: list[str],
    adjudicator_id: str | None,
) -> dict:
    reasons: list[str] = []
    case_map = {}
    for case in cases:
        if not isinstance(case, dict):
            reasons.append("case_not_object")
            continue
        case_id = case.get("case_id")
        if not isinstance(case_id, str) or not case_id:
            reasons.append("case_id_missing")
            continue
        if case_id in case_map:
            reasons.append("duplicate_case_id")
        case_map[case_id] = case

    admitted: set[str] = set()
    invalid_reviews: list[str] = []
    for review in case_reviews:
        if not isinstance(review, dict):
            invalid_reviews.append("not_object")
            continue
        case_id = review.get("case_id")
        case = case_map.get(case_id)
        if case is None:
            invalid_reviews.append(str(case_id))
            continue
        reviewer_id = review.get("reviewer_id")
        valid = (
            review.get("verdict") == "ADMIT"
            and isinstance(reviewer_id, str)
            and bool(reviewer_id)
            and reviewer_id != case.get("generator_actor_id")
            and review.get("independent_from_generation") is True
            and review.get("semantic_ancestry_reviewed") is True
            and review.get("subject_digest") == review_subject_digest(case)
        )
        if valid:
            admitted.add(case_id)
        else:
            invalid_reviews.append(case_id)

    missing_reviews = sorted(set(case_map) - admitted)
    if missing_reviews or invalid_reviews:
        reasons.append("independent_case_review_incomplete")

    unique_graders = [item for item in dict.fromkeys(grader_ids) if item]
    if len(unique_graders) < 2:
        reasons.append("two_graders_required")
    if not isinstance(adjudicator_id, str) or not adjudicator_id:
        reasons.append("adjudicator_required")
    elif adjudicator_id in set(unique_graders):
        reasons.append("adjudicator_must_be_distinct_from_graders")

    return {
        "schema": "STAGE2_DEVELOPMENT_BANK_REVIEW_V1",
        "status": "INDEPENDENTLY_REVIEWED" if not reasons else "HOLD",
        "case_count": len(case_map),
        "reviewed_case_count": len(admitted),
        "missing_case_reviews": missing_reviews,
        "invalid_case_reviews": sorted(set(invalid_reviews)),
        "grader_ids": unique_graders,
        "grader_count": len(unique_graders),
        "adjudicator_id": adjudicator_id,
        "claim_ceiling": (
            "DEVELOPMENT_BANK_REVIEW_CONTRACT_ONLY_NOT_BEHAVIORAL_PROMOTION"
        ),
        "reasons": reasons,
    }
