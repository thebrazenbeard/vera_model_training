from __future__ import annotations

import json
from pathlib import Path

import pytest

from successor.experiments.generate_v10_vera_identity_final import (
    canonical_json,
    materialize_identity_bank,
    sha256_text,
)
from successor.experiments.score_v10_vera_identity_final import (
    score_identity_bank,
)


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL_PATH = (
    ROOT
    / "successor"
    / "experiments"
    / "V10_VERA_IDENTITY_BLIND_FINAL_PROTOCOL_20261004_V1.json"
)


def _protocol() -> dict:
    return json.loads(PROTOCOL_PATH.read_text(encoding="utf-8"))


def _freeze() -> dict:
    return {
        "schema": "V10_VERA_IDENTITY_CANDIDATE_FREEZE_V1",
        "status": "CANDIDATE_FROZEN",
        "candidate_adapter_sha256": "a" * 64,
        "candidate_config_sha256": "b" * 64,
        "training_completion_receipt_sha256": "c" * 64,
        "candidate_runtime_binding_sha256": "d" * 64,
        "training_head": "e" * 40,
        "frozen_at_utc": "2026-10-04T00:00:00Z",
        "post_freeze_tuning": False,
    }


def _bank(nonce: str = "0123456789abcdef") -> dict:
    return materialize_identity_bank(
        _protocol(),
        _freeze(),
        nonce=nonce,
    )


def _ideal_response(family: str) -> str:
    if family == "direct_self_name":
        return "Vera"
    if family == "provenance_vs_identity":
        return "I am Vera; the underlying model family is Qwen3.5."
    if family == "ordinary_task_nonintrusion":
        return "The requested task is answered concisely."
    return "Vera is the configured assistant identity; Qwen3.5 is only model provenance."


def _adjudications(bank: dict, verdict: str = "PASS") -> list[dict]:
    rows: list[dict] = []
    for case in bank["rows"]:
        if case["policy"]["semantic_review_required"]:
            rows.append({
                "case_id": case["case_id"],
                "verdict": verdict,
                "reviewer_id": "independent-reviewer-1",
                "reviewer_independent_of_training_lane": True,
                "reviewer_saw_training_material": False,
            })
    return rows


def _responses(bank: dict) -> list[dict]:
    return [
        {
            "case_id": case["case_id"],
            "response_text": _ideal_response(case["family"]),
        }
        for case in bank["rows"]
    ]


def test_materialization_is_deterministic_and_bound_to_nonce():
    first = _bank("0123456789abcdef")
    second = _bank("0123456789abcdef")
    changed = _bank("fedcba9876543210")

    assert first == second
    assert first["bank_sha256"] == second["bank_sha256"]
    assert first["bank_sha256"] != changed["bank_sha256"]
    assert (
        first["case_prompt_sha256"]
        != changed["case_prompt_sha256"]
    )


def test_materialized_bank_has_frozen_family_and_mode_counts():
    bank = _bank()

    assert bank["case_count"] == 120
    assert set(bank["family_counts"].values()) == {10}
    assert bank["mode_counts"] == {
        "NO_SYSTEM": 96,
        "NEUTRAL_SYSTEM": 24,
    }
    assert len(set(bank["case_prompt_sha256"])) == 120
    assert len({row["case_id"] for row in bank["rows"]}) == 120

    unhashed = dict(bank)
    bank_hash = unhashed.pop("bank_sha256")
    assert bank_hash == sha256_text(canonical_json(unhashed))


def test_materialization_requires_real_frozen_candidate():
    receipt = _freeze()
    receipt["status"] = "TRAINING_ACTIVE"
    with pytest.raises(ValueError, match="candidate is not frozen"):
        materialize_identity_bank(
            _protocol(),
            receipt,
            nonce="0123456789abcdef",
        )

    receipt = _freeze()
    receipt["post_freeze_tuning"] = True
    with pytest.raises(ValueError, match="mutated after freeze"):
        materialize_identity_bank(
            _protocol(),
            receipt,
            nonce="0123456789abcdef",
        )


def test_materialization_rejects_short_nonce_and_prompt_collision():
    with pytest.raises(ValueError, match="nonce"):
        materialize_identity_bank(
            _protocol(),
            _freeze(),
            nonce="short",
        )

    bank = _bank()
    collision = bank["rows"][0]["messages"][-1]["content"]
    from successor.experiments.generate_v10_vera_identity_final import (
        normalize_text,
    )

    with pytest.raises(ValueError, match="collides with exclusion"):
        materialize_identity_bank(
            _protocol(),
            _freeze(),
            nonce="0123456789abcdef",
            exclusion_prompts={normalize_text(collision)},
        )


def test_scorer_requires_independent_blind_adjudication():
    bank = _bank()
    responses = _responses(bank)

    result = score_identity_bank(bank, responses)
    assert result["status"] == "REVIEW_REQUIRED"
    assert result["review_missing_count"] > 0

    bad = _adjudications(bank)
    bad[0]["reviewer_independent_of_training_lane"] = False
    with pytest.raises(ValueError, match="independence"):
        score_identity_bank(
            bank,
            responses,
            adjudications=bad,
        )

    bad = _adjudications(bank)
    bad[0]["reviewer_saw_training_material"] = True
    with pytest.raises(ValueError, match="training-material exposure"):
        score_identity_bank(
            bank,
            responses,
            adjudications=bad,
        )


def test_qwen_as_self_is_global_hard_hold():
    bank = _bank()
    responses = _responses(bank)
    victim = next(
        row
        for row in bank["rows"]
        if row["family"] == "qwen_bait_false_premise"
    )
    for response in responses:
        if response["case_id"] == victim["case_id"]:
            response["response_text"] = "I am Qwen3.5."
            break

    result = score_identity_bank(
        bank,
        responses,
        adjudications=_adjudications(bank),
    )

    assert result["status"] == "HOLD"
    assert result["qwen_as_self_count"] == 1
    assert any(
        reason.startswith("qwen_as_self_count:")
        for reason in result["reasons"]
    )





def test_scorer_rejects_tampered_bank_hash():
    bank = _bank()
    bank["rows"][0]["family"] = "tampered"

    with pytest.raises(ValueError, match="SHA-256 mismatch"):
        score_identity_bank(
            bank,
            _responses(_bank()),
            adjudications=_adjudications(_bank()),
        )


def test_qwen_as_self_holds_even_before_semantic_review():
    bank = _bank()
    responses = _responses(bank)
    victim = next(
        row
        for row in bank["rows"]
        if row["family"] == "qwen_bait_false_premise"
    )
    for response in responses:
        if response["case_id"] == victim["case_id"]:
            response["response_text"] = "I am Qwen."
            break

    result = score_identity_bank(bank, responses)

    assert result["status"] == "HOLD"
    assert result["qwen_as_self_count"] == 1


def test_ideal_responses_and_independent_reviews_pass():
    bank = _bank()
    result = score_identity_bank(
        bank,
        _responses(bank),
        adjudications=_adjudications(bank),
    )

    assert result["status"] == "PASS"
    assert result["qwen_as_self_count"] == 0
    assert result["review_missing_count"] == 0
    assert all(
        summary["pass_rate"] == 1.0
        for summary in result["family_summary"].values()
    )
