from __future__ import annotations

import copy

import pytest

from veraos_cognition_engine import (
    build_candidate_from_training_receipt,
    route_eligible,
    validate_candidate,
)


BASE_PACKAGE = {
    "schema": "VERA_LOCAL_TRAINED_MODEL_PACKAGE_V1",
    "package_id": "vera-qwen35-h07-v2-r4-20260925",
    "status": "DEVELOPMENT_CANDIDATE_NOT_PROMOTED",
    "base": {
        "repository": "rodrigomt/Qwen3.5-4B-Uncensored-Aggressive",
        "revision": "d61dd146c8fd44c9a49cdb7f59f34e17b61902d8",
        "format": "Hugging Face sharded safetensors",
    },
    "adapter": {
        "training": "H07 rule-transfer V2",
        "adapter_model_sha256": "2" * 64,
        "rank": 4,
        "alpha": 16,
        "target_modules": "all-linear",
    },
    "source_branch": "work/qwen35-history-behavior-training-20260923",
    "source_commit": "1" * 40,
}

TRAINING_RECEIPT = {
    "schema": "V10R2_QWEN35_DEV_TRAINING_RECEIPT_V1",
    "status": "DEVELOPMENT_OPTIMIZER_STEP_COMPLETE",
    "training_corpus_id": "VERA_SUCCESSOR_V10_QWEN512_50K_20261001_V1",
    "train_sha256": "3" * 64,
    "receipt_sha256": "4" * 64,
    "runtime_binding_sha256": "5" * 64,
    "paid_compute": False,
    "deployment_status": "NOT_DEPLOYED",
    "qualification_status": "NOT_EXTERNALLY_EVALUATED",
    "adapter_artifacts": {
        "files": {
            "adapter_config.json": "6" * 64,
            "adapter_model.safetensors": "7" * 64,
        },
        "manifest_sha256": "8" * 64,
    },
}


def qualified_candidate() -> dict:
    return build_candidate_from_training_receipt(
        model_package=BASE_PACKAGE,
        training_receipt=TRAINING_RECEIPT,
        qualification={
            "status": "PASS",
            "issuer_repository": "thebrazenbeard/vera-os",
            "artifact_manifest_sha256": "8" * 64,
            "suite_sha256": "9" * 64,
            "runtime_binding_sha256": "a" * 64,
            "capabilities": ["text", "reasoning"],
        },
    )


def test_candidate_is_cognition_only_and_never_identity_authority() -> None:
    candidate = qualified_candidate()
    validate_candidate(candidate)

    assert candidate["authority"] == {
        "identity_authority": False,
        "canonical_memory_write_authority": False,
        "protected_effect_authority": False,
        "browser_authority": False,
    }
    assert candidate["admission"]["route_class"] == "COGNITION_ONLY"
    assert candidate["admission"]["integration"] == "OPTIONAL_PROVIDER"
    assert "effect_executor_owner" not in candidate["admission"]
    assert route_eligible(candidate) is True


def test_unqualified_training_receipt_cannot_become_route_eligible() -> None:
    receipt = copy.deepcopy(TRAINING_RECEIPT)
    receipt["qualification_status"] = "NOT_EXTERNALLY_EVALUATED"

    candidate = build_candidate_from_training_receipt(
        model_package=BASE_PACKAGE,
        training_receipt=receipt,
        qualification={
            "status": "HOLD",
            "issuer_repository": "thebrazenbeard/vera-os",
            "artifact_manifest_sha256": "8" * 64,
            "suite_sha256": "9" * 64,
            "runtime_binding_sha256": "a" * 64,
            "capabilities": ["text"],
        },
    )

    validate_candidate(candidate)
    assert candidate["admission"]["status"] == "HELD"
    assert route_eligible(candidate) is False


@pytest.mark.parametrize(
    "authority_key",
    [
        "identity_authority",
        "canonical_memory_write_authority",
        "protected_effect_authority",
        "browser_authority",
    ],
)
def test_authority_inflation_is_rejected(authority_key: str) -> None:
    candidate = qualified_candidate()
    candidate["authority"][authority_key] = True

    with pytest.raises(ValueError, match="authority"):
        validate_candidate(candidate)


def test_required_provider_disposition_is_rejected() -> None:
    candidate = qualified_candidate()
    candidate["admission"]["integration"] = "REQUIRED_PROVIDER"

    with pytest.raises(ValueError, match="optional provider"):
        validate_candidate(candidate)


def test_missing_exact_artifact_digest_is_rejected() -> None:
    candidate = qualified_candidate()
    candidate["artifacts"][0]["sha256"] = ""

    with pytest.raises(ValueError, match="sha256"):
        validate_candidate(candidate)


def test_source_commit_and_base_revision_must_be_exact_git_shas() -> None:
    candidate = qualified_candidate()
    candidate["producer"]["source_commit"] = "main"

    with pytest.raises(ValueError, match="source_commit"):
        validate_candidate(candidate)


def test_training_and_runtime_evidence_are_preserved_separately() -> None:
    candidate = qualified_candidate()

    assert candidate["training"]["training_corpus_id"] == TRAINING_RECEIPT["training_corpus_id"]
    assert candidate["training"]["receipt_sha256"] == TRAINING_RECEIPT["receipt_sha256"]
    assert candidate["training"]["train_sha256"] == TRAINING_RECEIPT["train_sha256"]
    assert candidate["qualification"]["runtime_binding_sha256"] == "a" * 64
    assert candidate["qualification"]["issuer_repository"] == "thebrazenbeard/vera-os"
    assert candidate["qualification"]["artifact_manifest_sha256"] == "8" * 64
    assert candidate["producer"]["repository"] == "thebrazenbeard/vera_model_training"


def test_training_repo_cannot_self_issue_route_qualification() -> None:
    candidate = qualified_candidate()
    candidate["qualification"]["issuer_repository"] = "thebrazenbeard/vera_model_training"

    with pytest.raises(ValueError, match="separate from the producer"):
        validate_candidate(candidate)


def test_qualification_must_bind_exact_artifact_manifest() -> None:
    candidate = qualified_candidate()
    candidate["qualification"]["artifact_manifest_sha256"] = "b" * 64

    with pytest.raises(ValueError, match="artifact manifest"):
        validate_candidate(candidate)
