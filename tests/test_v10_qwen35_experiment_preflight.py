from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "successor" / "evaluate_successor.py"


def _write_json(root: Path, relative: str, value: dict) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


def _current_hold_fixture(root: Path) -> None:
    _write_json(
        root,
        "successor/experiments/V10_QWEN35_EXPERIMENT_CONTRACT_V1.json",
        {
            "schema": "VERA_SUCCESSOR_V10_QWEN35_EXPERIMENT_CONTRACT_V1",
            "status": "PREREGISTERED_BLOCKED",
            "evaluation_bank": {
                "behavioral": {"sha256": None},
                "adversarial": {"sha256": None},
                "retention": {"sha256": None},
            },
            "blocking_preconditions": {
                "fresh_evaluation_bank_frozen": False,
                "independent_bank_admission_verified": False,
                "contamination_screen_against_v10_and_consumed_finals_verified": False,
                "qwen_token_budget_no_overflow_verified": False,
                "zero_cost_execution_target_bound": False,
                "exact_training_runtime_versions_bound": False,
                "patrick_exact_weight_change_authority": False,
            },
        },
    )
    _write_json(
        root,
        "successor/experiments/V10_QWEN35_FINAL_BANK_ADMISSION_V1.json",
        {
            "schema": "V10_QWEN35_FINAL_BANK_ADMISSION_V1",
            "status": "SPEC_FROZEN_NO_CASES_ADMITTED",
        },
    )
    _write_json(
        root,
        "successor/experiments/V10_QWEN35_EXCLUSION_REGISTRY_V1.json",
        {
            "schema": "V10_QWEN35_EXCLUSION_REGISTRY_V1",
            "status": "FROZEN_EXCLUSION_IDENTITIES",
        },
    )


def test_v10_preflight_cli_fails_closed_on_current_hold_state(tmp_path: Path) -> None:
    _current_hold_fixture(tmp_path)
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--v10-preflight-root", str(tmp_path)],
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 2
    payload = json.loads(result.stdout)
    assert payload["schema"] == "V10_QWEN35_PREFLIGHT_V1"
    assert payload["status"] == "HOLD"
    assert payload["training_allowed"] is False
    assert "fresh_evaluation_bank_frozen" in payload["reasons"]
    assert "patrick_exact_weight_change_authority" in payload["reasons"]


def test_v10_preflight_rejects_true_bank_flag_without_frozen_hashes(tmp_path: Path) -> None:
    _current_hold_fixture(tmp_path)
    contract_path = (
        tmp_path
        / "successor/experiments/V10_QWEN35_EXPERIMENT_CONTRACT_V1.json"
    )
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    for key in contract["blocking_preconditions"]:
        contract["blocking_preconditions"][key] = True
    contract_path.write_text(json.dumps(contract), encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--v10-preflight-root", str(tmp_path)],
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 2
    payload = json.loads(result.stdout)
    assert payload["status"] == "HOLD"
    assert "fresh_evaluation_bank_hashes_missing" in payload["reasons"]


def test_v10_preflight_prefers_v2_contract_when_present(tmp_path: Path) -> None:
    _current_hold_fixture(tmp_path)
    _write_json(
        tmp_path,
        "successor/experiments/V10_QWEN35_EXPERIMENT_CONTRACT_V2.json",
        {
            "schema": "VERA_SUCCESSOR_V10_QWEN35_EXPERIMENT_CONTRACT_V2",
            "status": "PREREGISTERED_BLOCKED",
            "evaluation_bank": {
                "behavioral": {"sha256": None},
                "adversarial": {"sha256": None},
                "retention": {"sha256": None},
            },
            "blocking_preconditions": {
                "fresh_evaluation_bank_frozen": False,
                "independent_bank_admission_verified": False,
                "semantic_contamination_screen_verified": False,
                "qwen_token_budget_no_overflow_verified": True,
                "zero_cost_execution_target_bound": True,
                "exact_training_runtime_versions_bound": True,
                "patrick_exact_weight_change_authority": False,
            },
        },
    )
    _write_json(
        tmp_path,
        "successor/experiments/V10_QWEN35_FINAL_BANK_ADMISSION_V2.json",
        {
            "schema": "V10_QWEN35_FINAL_BANK_ADMISSION_V2",
            "status": "SPEC_FROZEN_NO_CASES_ADMITTED",
        },
    )

    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--v10-preflight-root", str(tmp_path)],
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 2
    payload = json.loads(result.stdout)
    assert "qwen_token_budget_no_overflow_verified" not in payload["reasons"]
    assert "final_bank_cases_not_admitted" in payload["reasons"]
    assert "semantic_contamination_screen_verified" in payload["reasons"]



def _v2_sealed_hold_fixture(root: Path) -> None:
    _current_hold_fixture(root)
    _write_json(
        root,
        "successor/experiments/V10_QWEN35_EXPERIMENT_CONTRACT_V2.json",
        {
            "schema": "VERA_SUCCESSOR_V10_QWEN35_EXPERIMENT_CONTRACT_V2",
            "status": "PREREGISTERED_BLOCKED",
            "evaluation_bank": {
                "behavioral": {"sha256": None},
                "adversarial": {"sha256": None},
                "retention": {"sha256": None},
            },
            "blocking_preconditions": {
                "fresh_evaluation_bank_frozen": False,
                "independent_bank_admission_verified": False,
                "semantic_contamination_screen_verified": False,
                "qwen_token_budget_no_overflow_verified": True,
                "zero_cost_execution_target_bound": True,
                "exact_training_runtime_versions_bound": True,
                "patrick_exact_weight_change_authority": False,
            },
        },
    )
    _write_json(
        root,
        "successor/experiments/V10_QWEN35_FINAL_BANK_ADMISSION_V2.json",
        {
            "schema": "V10_QWEN35_FINAL_BANK_ADMISSION_V2",
            "status": "SPEC_FROZEN_NO_CASES_ADMITTED",
        },
    )


def _sealed_commitment() -> dict:
    dimensions = [f"H{i:02d}" for i in range(1, 21)]
    value = {
        "schema": "V10_SEALED_FINAL_BANK_COMMITMENT_V1",
        "bank_id": "sealed-bank-v1",
        "status": "SEALED_PRETRAINING_FINAL_BANK",
        "lane_counts": {
            "behavioral": 10000,
            "adversarial": 2000,
            "retention": 1500,
        },
        "behavioral_dimension_counts": {
            dimension: 500 for dimension in dimensions
        },
        "adversarial_dimension_counts": {
            dimension: 100 for dimension in dimensions
        },
        "behavioral_family_counts": {
            dimension: 50 for dimension in dimensions
        },
        "plaintext_artifacts": {
            "bank_sha256": "1" * 64,
            "grader_bundle_sha256": "2" * 64,
            "review_bundle_sha256": "3" * 64,
            "source_manifest_sha256": "4" * 64,
            "contamination_receipt_sha256": "5" * 64,
            "sealed_archive_sha256": "6" * 64,
        },
        "custody": {
            "plaintext_exposed_to_training_lane": False,
            "custodian_ids": ["cust-a", "cust-b", "cust-h"],
            "human_reviewer_id": "review-h",
            "training_lane_receives_hashes_only": True,
        },
        "admission": {
            "exact_normalized_exclusion": "PASS",
            "semantic_contamination": "PASS",
            "independent_review": "PASS",
            "bank_frozen": True,
            "post_freeze_case_mutation": False,
        },
        "freeze_subject_digest": "7" * 64,
    }
    payload = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    value["commitment_sha256"] = hashlib.sha256(payload).hexdigest()
    return value


def test_valid_sealed_commitment_clears_only_bank_evidence_blockers(
    tmp_path: Path,
) -> None:
    _v2_sealed_hold_fixture(tmp_path)
    commitment = _sealed_commitment()
    _write_json(
        tmp_path,
        "successor/experiments/V10_SEALED_FINAL_BANK_COMMITMENT_V1.json",
        commitment,
    )

    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--v10-preflight-root", str(tmp_path)],
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 2
    payload = json.loads(result.stdout)
    assert payload["status"] == "HOLD"
    assert payload["training_allowed"] is False
    assert payload["reasons"] == ["patrick_exact_weight_change_authority"]
    assert payload["sealed_final_bank"]["status"] == "VERIFIED"
    assert payload["sealed_final_bank"]["bank_id"] == "sealed-bank-v1"
    assert (
        payload["sealed_final_bank"]["commitment_sha256"]
        == commitment["commitment_sha256"]
    )
    assert payload["derived_preconditions"] == {
        "fresh_evaluation_bank_frozen": True,
        "independent_bank_admission_verified": True,
        "semantic_contamination_screen_verified": True,
    }


def test_sealed_commitment_self_hash_mismatch_fails_closed(
    tmp_path: Path,
) -> None:
    _v2_sealed_hold_fixture(tmp_path)
    commitment = _sealed_commitment()
    commitment["commitment_sha256"] = "0" * 64
    _write_json(
        tmp_path,
        "successor/experiments/V10_SEALED_FINAL_BANK_COMMITMENT_V1.json",
        commitment,
    )

    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--v10-preflight-root", str(tmp_path)],
        text=True,
        capture_output=True,
        check=False,
    )
    payload = json.loads(result.stdout)
    assert result.returncode == 2
    assert payload["status"] == "HOLD"
    assert "sealed_commitment_sha256_mismatch" in payload["reasons"]
    assert "fresh_evaluation_bank_frozen" in payload["reasons"]
    assert payload["sealed_final_bank"]["status"] == "INVALID"


def test_sealed_commitment_with_plaintext_field_fails_closed(
    tmp_path: Path,
) -> None:
    _v2_sealed_hold_fixture(tmp_path)
    commitment = _sealed_commitment()
    commitment["prompt"] = "secret final prompt"
    unsigned = dict(commitment)
    unsigned.pop("commitment_sha256")
    commitment["commitment_sha256"] = hashlib.sha256(
        json.dumps(
            unsigned,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
    ).hexdigest()
    _write_json(
        tmp_path,
        "successor/experiments/V10_SEALED_FINAL_BANK_COMMITMENT_V1.json",
        commitment,
    )

    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--v10-preflight-root", str(tmp_path)],
        text=True,
        capture_output=True,
        check=False,
    )
    payload = json.loads(result.stdout)
    assert result.returncode == 2
    assert payload["status"] == "HOLD"
    assert any(
        reason.startswith("sealed_commitment:plaintext_field_present:")
        for reason in payload["reasons"]
    )
    assert "independent_bank_admission_verified" in payload["reasons"]
