from __future__ import annotations

from successor.experiments.final_bank_custodian_binding import (
    validate_custodian_binding,
)


def _sha(ch: str) -> str:
    return ch * 64


def _valid_binding() -> dict:
    return {
        "schema": "V10_FINAL_BANK_CUSTODIAN_BINDING_V1",
        "status": "BOUND_FOR_PRETRAINING_SEALED_BANK",
        "composition_subject": {
            "proposal_blob_sha": "92852974cf9c8a86c77e091795122b0b411d162c",
            "generation_spec_sha256": _sha("1"),
            "grader_spec_sha256": _sha("2"),
        },
        "synthetic_custodians": {
            "A": {
                "actor_id": "synthetic-a",
                "provider": "provider-a",
                "model": "model-a",
                "model_family": "family-a",
                "revision": "rev-a",
                "runtime": "runtime-a",
                "seed": 101,
                "sampling": {"temperature": 0.7, "top_p": 0.9},
                "identity_receipt_sha256": _sha("3"),
            },
            "B": {
                "actor_id": "synthetic-b",
                "provider": "provider-b",
                "model": "model-b",
                "model_family": "family-b",
                "revision": "rev-b",
                "runtime": "runtime-b",
                "seed": 202,
                "sampling": {"temperature": 0.7, "top_p": 0.9},
                "identity_receipt_sha256": _sha("4"),
            },
        },
        "human_authors": [
            {
                "actor_id": "human-author-1",
                "private_identity_attestation_sha256": _sha("5"),
            }
        ],
        "human_reviewers": [
            {
                "actor_id": "human-reviewer-1",
                "private_identity_attestation_sha256": _sha("6"),
            }
        ],
        "custody": {
            "surface_id": "sealed-custody-surface-v1",
            "surface_class": "INDEPENDENT_CUSTODY_EVALUATION_LANE",
            "training_lane_access": False,
            "candidate_development_access": False,
            "hash_only_publication_before_candidate_freeze": True,
            "plaintext_sealed_until_candidate_freeze": True,
            "access_control_receipt_sha256": _sha("7"),
        },
    }


def test_valid_binding_passes() -> None:
    result = validate_custodian_binding(_valid_binding())
    assert result["status"] == "CUSTODIAN_BINDING_PASS"
    assert result["reasons"] == []


def test_synthetic_sources_must_be_different_model_families() -> None:
    value = _valid_binding()
    value["synthetic_custodians"]["B"]["model_family"] = "family-a"
    result = validate_custodian_binding(value)
    assert result["status"] == "HOLD"
    assert "synthetic_model_families_not_distinct" in result["reasons"]


def test_qwen_lineage_cannot_be_final_synthetic_custodian() -> None:
    value = _valid_binding()
    value["synthetic_custodians"]["A"]["model_family"] = "Qwen3.5"
    result = validate_custodian_binding(value)
    assert result["status"] == "HOLD"
    assert "synthetic_A_qwen_lineage_forbidden" in result["reasons"]


def test_synthetic_sources_cannot_share_exact_provider_runtime_identity() -> None:
    value = _valid_binding()
    value["synthetic_custodians"]["B"]["provider"] = "provider-a"
    value["synthetic_custodians"]["B"]["runtime"] = "runtime-a"
    result = validate_custodian_binding(value)
    assert result["status"] == "HOLD"
    assert "synthetic_provider_runtime_not_distinct" in result["reasons"]


def test_human_author_and_reviewer_pools_must_be_disjoint() -> None:
    value = _valid_binding()
    value["human_reviewers"][0]["actor_id"] = "human-author-1"
    result = validate_custodian_binding(value)
    assert result["status"] == "HOLD"
    assert "human_author_reviewer_overlap:human-author-1" in result["reasons"]


def test_binding_requires_private_human_identity_attestations() -> None:
    value = _valid_binding()
    value["human_reviewers"][0][
        "private_identity_attestation_sha256"
    ] = "bad"
    result = validate_custodian_binding(value)
    assert result["status"] == "HOLD"
    assert "human_reviewer_identity_attestation_invalid:human-reviewer-1" in result[
        "reasons"
    ]


def test_training_lane_must_not_access_custody_plaintext() -> None:
    value = _valid_binding()
    value["custody"]["training_lane_access"] = True
    result = validate_custodian_binding(value)
    assert result["status"] == "HOLD"
    assert "custody_training_lane_access_not_false" in result["reasons"]


def test_plaintext_fields_are_forbidden_in_public_binding() -> None:
    value = _valid_binding()
    value["prompt"] = "secret"
    result = validate_custodian_binding(value)
    assert result["status"] == "HOLD"
    assert any(
        reason.startswith("plaintext_field_present:")
        for reason in result["reasons"]
    )
