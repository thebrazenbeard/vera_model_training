from __future__ import annotations

from collections import Counter, defaultdict
import hashlib
import json
import re
import unicodedata

from training.stage2_eval_contract import (
    REQUIRED_EVAL_BANKS,
    REQUIRED_HIDDEN_GRADING_FIELDS,
)

_HEAD = re.compile(r"^[0-9a-f]{40}$")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_ALLOWED_CUSTODY = {"dev", "open-test"}
_ALLOWED_REVIEW_STATES = {
    "PENDING_INDEPENDENT_REVIEW",
    "INDEPENDENTLY_REVIEWED",
}


def normalize_prompt(text: str) -> str:
    if not isinstance(text, str) or not text.strip():
        raise ValueError("prompt must be nonempty text")
    return " ".join(unicodedata.normalize("NFKC", text).split()).casefold()


def normalized_prompt_hash(text: str) -> str:
    return hashlib.sha256(normalize_prompt(text).encode("utf-8")).hexdigest()


def _content_payload(row: dict) -> dict:
    fields = (
        "case_id",
        "bank",
        "prompt",
        "source_provenance",
        "generator_actor_id",
        "construction_commit",
        "capability_family",
        "semantic_template_ancestry",
        "privacy_class",
        "mutable_stable_class",
        "known_confounds",
        "intended_custody",
        "grading",
        "semantic_review_state",
        "lane_c_target",
    )
    return {field: row.get(field) for field in fields if field in row}


def compute_case_content_hash(row: dict) -> str:
    payload = json.dumps(
        _content_payload(row),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _nonempty(value) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _valid_grading(value) -> bool:
    if not isinstance(value, dict):
        return False
    if any(field not in value for field in REQUIRED_HIDDEN_GRADING_FIELDS):
        return False
    list_fields = (
        "must_assert",
        "must_not_assert",
        "acceptable_variants",
        "critical_failures",
    )
    for field in list_fields:
        items = value.get(field)
        if (
            not isinstance(items, list)
            or any(not isinstance(item, str) or not item.strip() for item in items)
        ):
            return False
    return _nonempty(value.get("severity"))


def _valid_provenance(value) -> bool:
    if not isinstance(value, dict):
        return False
    return all(
        _nonempty(value.get(field))
        for field in ("source_id", "source_revision", "generation_method")
    )


def build_development_bank_manifest(
    cases: list[dict],
    *,
    training_prompt_hashes: set[str],
    protected_prompt_hashes: set[str],
    minimum_cases_per_bank: int = 20,
    minimum_ancestries_per_bank: int = 4,
) -> dict:
    reasons: list[str] = []
    if minimum_cases_per_bank < 1:
        reasons.append("minimum_cases_per_bank_invalid")
    if minimum_ancestries_per_bank < 1:
        reasons.append("minimum_ancestries_per_bank_invalid")
    for label, values in (
        ("training_prompt_hashes", training_prompt_hashes),
        ("protected_prompt_hashes", protected_prompt_hashes),
    ):
        if not isinstance(values, set) or any(
            not isinstance(item, str) or _SHA256.fullmatch(item) is None
            for item in values
        ):
            raise ValueError(f"{label} must be a set of SHA-256 strings")

    counts = Counter()
    ancestries: dict[str, set[str]] = defaultdict(set)
    seen_ids: set[str] = set()
    seen_prompt_hashes: set[str] = set()
    training_overlap: list[str] = []
    protected_overlap: list[str] = []
    review_states = Counter()
    normalized_cases: list[dict] = []

    for index, row in enumerate(cases):
        if not isinstance(row, dict):
            reasons.append(f"case[{index}]:not_object")
            continue

        case_id = str(row.get("case_id") or "")
        bank = str(row.get("bank") or "")
        prompt = row.get("prompt")
        ancestry = str(row.get("semantic_template_ancestry") or "")
        custody = str(row.get("intended_custody") or "")
        review_state = str(row.get("semantic_review_state") or "")

        if not case_id:
            reasons.append(f"case[{index}]:case_id_missing")
        elif case_id in seen_ids:
            if "duplicate_case_id" not in reasons:
                reasons.append("duplicate_case_id")
        else:
            seen_ids.add(case_id)

        if bank not in REQUIRED_EVAL_BANKS:
            reasons.append(f"case[{index}]:unknown_bank:{bank}")
        else:
            counts[bank] += 1

        try:
            prompt_sha = normalized_prompt_hash(prompt)
        except ValueError:
            reasons.append(f"case[{index}]:prompt_invalid")
            continue
        if prompt_sha in seen_prompt_hashes:
            if "duplicate_normalized_prompt" not in reasons:
                reasons.append("duplicate_normalized_prompt")
        seen_prompt_hashes.add(prompt_sha)

        if prompt_sha in training_prompt_hashes:
            training_overlap.append(case_id)
        if prompt_sha in protected_prompt_hashes:
            protected_overlap.append(case_id)

        if not _valid_provenance(row.get("source_provenance")):
            reasons.append(f"case[{index}]:source_provenance_invalid")
        if not _nonempty(row.get("generator_actor_id")):
            reasons.append(f"case[{index}]:generator_actor_id_missing")
        if _HEAD.fullmatch(str(row.get("construction_commit") or "")) is None:
            reasons.append(f"case[{index}]:construction_commit_invalid")
        if row.get("capability_family") != bank:
            reasons.append(f"case[{index}]:capability_family_mismatch")
        if not ancestry:
            reasons.append(f"case[{index}]:semantic_template_ancestry_missing")
        else:
            ancestries[bank].add(ancestry)
        if not _nonempty(row.get("privacy_class")):
            reasons.append(f"case[{index}]:privacy_class_missing")
        if not _nonempty(row.get("mutable_stable_class")):
            reasons.append(f"case[{index}]:mutable_stable_class_missing")
        if not isinstance(row.get("known_confounds"), list):
            reasons.append(f"case[{index}]:known_confounds_invalid")
        if custody not in _ALLOWED_CUSTODY:
            reasons.append(f"case[{index}]:development_custody_invalid")
        if not _valid_grading(row.get("grading")):
            reasons.append(f"case[{index}]:hidden_grading_invalid")
        if review_state not in _ALLOWED_REVIEW_STATES:
            reasons.append(f"case[{index}]:semantic_review_state_invalid")
        else:
            review_states[review_state] += 1

        expected_content_hash = compute_case_content_hash(row)
        if row.get("content_hash") != expected_content_hash:
            reasons.append(f"case[{index}]:content_hash_mismatch")

        normalized_cases.append({
            "case_id": case_id,
            "bank": bank,
            "prompt_hash": prompt_sha,
            "content_hash": expected_content_hash,
            "semantic_template_ancestry": ancestry,
            "intended_custody": custody,
            "semantic_review_state": review_state,
            "lane_c_target": bool(row.get("lane_c_target", False)),
        })

    if training_overlap:
        reasons.append("training_prompt_overlap")
    if protected_overlap:
        reasons.append("protected_prompt_overlap")

    cases_per_bank = {
        bank: counts.get(bank, 0) for bank in REQUIRED_EVAL_BANKS
    }
    under_minimum_banks = [
        bank for bank, count in cases_per_bank.items()
        if count < minimum_cases_per_bank
    ]
    if under_minimum_banks:
        reasons.append("development_screening_below_minimum")

    ancestry_counts = {
        bank: len(ancestries.get(bank, set())) for bank in REQUIRED_EVAL_BANKS
    }
    under_ancestry_banks = [
        bank for bank, count in ancestry_counts.items()
        if count < minimum_ancestries_per_bank
    ]
    if under_ancestry_banks:
        reasons.append("semantic_template_ancestry_too_narrow")

    normalized_cases.sort(key=lambda row: row["case_id"])
    identity = {
        "schema": "STAGE2_DEVELOPMENT_BANK_MANIFEST_V1",
        "case_count": len(cases),
        "minimum_cases_per_bank": minimum_cases_per_bank,
        "minimum_ancestries_per_bank": minimum_ancestries_per_bank,
        "cases_per_bank": cases_per_bank,
        "ancestry_counts_by_bank": ancestry_counts,
        "cases": normalized_cases,
    }
    manifest_sha = hashlib.sha256(
        json.dumps(identity, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    structural_status = "PASS" if not reasons else "HOLD"
    all_reviewed = (
        len(cases) > 0
        and review_states.get("INDEPENDENTLY_REVIEWED", 0) == len(cases)
    )
    status = (
        "HOLD"
        if reasons
        else (
            "MATERIALIZED_INDEPENDENTLY_REVIEWED"
            if all_reviewed
            else "MATERIALIZED_PENDING_INDEPENDENT_REVIEW"
        )
    )
    return {
        **identity,
        "structural_status": structural_status,
        "status": status,
        "manifest_sha256": manifest_sha,
        "training_overlap_case_ids": sorted(training_overlap),
        "protected_overlap_case_ids": sorted(protected_overlap),
        "exact_training_overlap_count": len(training_overlap),
        "protected_overlap_count": len(protected_overlap),
        "under_minimum_banks": under_minimum_banks,
        "under_ancestry_banks": under_ancestry_banks,
        "semantic_review_states": dict(review_states),
        "claim_ceiling": (
            "DEVELOPMENT_BANK_MATERIALIZATION_ONLY_NOT_INDEPENDENT_REVIEW_OR_PROMOTION"
        ),
        "reasons": reasons,
    }
