from __future__ import annotations

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
