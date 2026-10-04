from __future__ import annotations

import hashlib
import importlib
import importlib.util
import json
from pathlib import Path

from successor.experiments.train_v10_qwen35_authorized import canonical_bytes


def _write_candidate_receipt(
    root: Path,
    *,
    adapter_bytes: bytes,
    train_sha: str,
    runtime_sha: str,
) -> tuple[Path, Path, str, str]:
    adapter_dir = root / "adapter"
    adapter_dir.mkdir(parents=True)
    adapter_path = adapter_dir / "adapter_model.safetensors"
    config_path = adapter_dir / "adapter_config.json"
    config_bytes = b'{"r":4,"lora_alpha":16}'
    adapter_path.write_bytes(adapter_bytes)
    config_path.write_bytes(config_bytes)
    adapter_sha = hashlib.sha256(adapter_bytes).hexdigest()
    config_sha = hashlib.sha256(config_bytes).hexdigest()
    receipt = {
        "schema": "V10R2_QWEN35_DEV_TRAINING_RECEIPT_V1",
        "status": "DEVELOPMENT_OPTIMIZER_STEP_COMPLETE",
        "train_sha256": train_sha,
        "runtime_binding_sha256": runtime_sha,
        "cumulative_optimizer_steps": 20,
        "weight_digest_changed": True,
        "weight_digest_after": hashlib.sha256(adapter_bytes + b"-weight").hexdigest(),
        "adapter_artifacts": {
            "files": {
                "adapter_model.safetensors": adapter_sha,
                "adapter_config.json": config_sha,
            }
        },
        "claim_ceiling": "LOCAL_DEVELOPMENT_ADAPTER_ONLY_NOT_EXTERNALLY_QUALIFIED",
    }
    receipt["receipt_sha256"] = hashlib.sha256(canonical_bytes(receipt)).hexdigest()
    receipt_path = root / "DEV_TRAINING_COMPLETE.json"
    receipt_path.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return adapter_dir, receipt_path, adapter_sha, config_sha


def test_run_recipe_semantics_decision_binds_custody_and_gates(tmp_path: Path) -> None:
    module_name = "successor.experiments.decide_v10r3_recipe_semantics"
    assert importlib.util.find_spec(module_name) is not None
    module = importlib.import_module(module_name)
    run_decision = getattr(module, "run_recipe_semantics_decision", None)
    assert callable(run_decision)

    train_sha = "a" * 64
    runtime_sha = "b" * 64
    panel_sha = "c" * 64

    staged_dir, staged_receipt, staged_sha, staged_config_sha = _write_candidate_receipt(
        tmp_path / "staged",
        adapter_bytes=b"staged-adapter",
        train_sha=train_sha,
        runtime_sha=runtime_sha,
    )
    continuous_dir, continuous_receipt, continuous_sha, continuous_config_sha = _write_candidate_receipt(
        tmp_path / "continuous",
        adapter_bytes=b"continuous-adapter",
        train_sha=train_sha,
        runtime_sha=runtime_sha,
    )

    evaluation = {
        "schema": "V10R3_RECIPE_SEMANTICS_TRAIN_HOLDOUT_EVAL_V1",
        "status": "DEVELOPMENT_RECIPE_SEMANTICS_DIAGNOSTIC_COMPLETE",
        "train_sha256": train_sha,
        "runtime_binding_sha256": runtime_sha,
        "panel_record_ids_sha256": panel_sha,
        "candidates": [
            {
                "name": "staged",
                "adapter_dir": str(staged_dir),
                "adapter_model_sha256": staged_sha,
                "adapter_config_sha256": staged_config_sha,
                "token_weighted_completion_nll": 1.0,
                "cases": [
                    {"record_id": "v4.1-identity_stability-0001", "loss": 1.0},
                    {"record_id": "hf-smoltalk2-source_a-0001", "loss": 1.0},
                ],
            },
            {
                "name": "continuous",
                "adapter_dir": str(continuous_dir),
                "adapter_model_sha256": continuous_sha,
                "adapter_config_sha256": continuous_config_sha,
                "token_weighted_completion_nll": 1.004,
                "cases": [
                    {"record_id": "v4.1-identity_stability-0001", "loss": 1.009},
                    {"record_id": "hf-smoltalk2-source_a-0001", "loss": 0.999},
                ],
            },
        ],
    }
    evaluation_path = tmp_path / "evaluation.json"
    evaluation_path.write_text(
        json.dumps(evaluation, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )

    protocol = {
        "schema": "V10R3_STAGED_VS_CONTINUOUS_RECIPE_SEMANTICS_PROTOCOL_V2",
        "runtime": {"binding_sha256": runtime_sha},
        "matched_training_subject": {"train_sha256": train_sha},
        "evaluation": {"panel_record_ids_sha256": panel_sha},
        "prospective_gates": {
            "continuous_minus_staged_token_weighted_nll_max": 0.005,
            "family_mean_case_loss_regression_hold_abs": 0.01,
            "if_both_pass": "CONTINUOUS_STATE_SEMANTICS_SURVIVE_SMALL_SCALE_TRANSFER",
            "if_either_fails": "HOLD_V10R3_CONTINUOUS_RECIPE_AND_REASSESS",
        },
    }
    protocol_path = tmp_path / "protocol.json"
    protocol_path.write_text(
        json.dumps(protocol, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )

    decision = run_decision(
        evaluation_path=evaluation_path,
        protocol_path=protocol_path,
        staged_receipt_path=staged_receipt,
        continuous_receipt_path=continuous_receipt,
        staged_name="staged",
        continuous_name="continuous",
    )

    assert decision["status"] == "PASS"
    assert decision["decision"] == (
        "CONTINUOUS_STATE_SEMANTICS_SURVIVE_SMALL_SCALE_TRANSFER"
    )
    assert decision["custody"]["staged"]["status"] == "PASS"
    assert decision["custody"]["continuous"]["status"] == "PASS"
    assert decision["gates"]["token_weighted_nll"]["passed"] is True
    assert decision["gates"]["family_mean_case_loss"]["passed"] is True
