from __future__ import annotations

import hashlib
import importlib
import importlib.util
import json
from pathlib import Path

import pytest

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


def test_run_recipe_semantics_decision_binds_custody_and_gates(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
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
        "initialization_equivalence_gate": {
            "expected_initial_trainable_parameter_digest": "d" * 64,
        },
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
    monkeypatch.setattr(
        module,
        "FROZEN_PROTOCOL_SHA256",
        module.committed_text_sha(protocol_path),
    )
    monkeypatch.setattr(
        module,
        "validate_recipe_receipt_semantics",
        lambda receipt_path, **kwargs: {
            "status": "PASS",
            "role": kwargs["role"],
            "receipt_path": str(receipt_path),
        },
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



def test_run_decision_rejects_nonfrozen_protocol_hash(tmp_path: Path) -> None:
    from successor.experiments.decide_v10r3_recipe_semantics import (
        RecipeEvalHold,
        run_recipe_semantics_decision,
    )

    evaluation_path = tmp_path / "evaluation.json"
    evaluation_path.write_text(
        json.dumps(
            {
                "schema": "V10R3_RECIPE_SEMANTICS_TRAIN_HOLDOUT_EVAL_V1",
                "status": "DEVELOPMENT_RECIPE_SEMANTICS_DIAGNOSTIC_COMPLETE",
            }
        ),
        encoding="utf-8",
    )
    protocol_path = tmp_path / "protocol.json"
    protocol_path.write_text(
        json.dumps(
            {
                "schema": "V10R3_STAGED_VS_CONTINUOUS_RECIPE_SEMANTICS_PROTOCOL_V2",
                "prospective_gates": {
                    "continuous_minus_staged_token_weighted_nll_max": 999.0,
                },
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(RecipeEvalHold, match="frozen protocol hash mismatch"):
        run_recipe_semantics_decision(
            evaluation_path=evaluation_path,
            protocol_path=protocol_path,
            staged_receipt_path=tmp_path / "missing-staged.json",
            continuous_receipt_path=tmp_path / "missing-continuous.json",
        )



def test_recipe_semantics_validator_rejects_continuous_receipt_as_staged(
    tmp_path: Path,
) -> None:
    from successor.experiments import decide_v10r3_recipe_semantics as module

    validate_semantics = getattr(module, "validate_recipe_receipt_semantics", None)
    assert callable(validate_semantics)

    receipt = {
        "schema": "V10R2_QWEN35_DEV_TRAINING_RECEIPT_V1",
        "status": "DEVELOPMENT_OPTIMIZER_STEP_COMPLETE",
        "train_sha256": "train-a",
        "runtime_binding_sha256": "runtime-a",
        "cumulative_optimizer_steps": 20,
        "experiment_class": "CONTINUOUS_STATE_RECIPE_SEMANTICS",
        "development_window": {
            "start_row": 0,
            "row_count": 160,
            "row_ids": [f"bound-train-row-{i}" for i in range(160)],
        },
        "training_order": {
            "shuffle_dataset": False,
            "train_sampling_strategy": "sequential",
        },
        "optimizer": {
            "backend": "bitsandbytes",
            "module": "bitsandbytes.optim.adamw",
            "optim_bits": 8,
            "is_paged": False,
        },
        "resume_adapter": None,
        "initial_trainable_parameter_digest": "init-a",
        "initialization_equivalence_gate": {
            "expected_digest": "init-a",
            "pass": True,
        },
        "weight_digest_changed": True,
        "weight_digest_after": "weight-after",
    }
    receipt["receipt_sha256"] = hashlib.sha256(canonical_bytes(receipt)).hexdigest()
    path = tmp_path / "DEV_TRAINING_COMPLETE.json"
    path.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )

    with pytest.raises(module.RecipeEvalHold, match="staged receipt experiment class mismatch"):
        validate_semantics(
            path,
            role="staged",
            expected_train_sha="train-a",
            expected_runtime_sha="runtime-a",
            expected_initial_digest="init-a",
        )



def _write_semantic_receipt(
    path: Path,
    *,
    experiment_class: str,
    start_row: int,
    row_count: int,
    cumulative_steps: int,
    train_sha: str,
    runtime_sha: str,
    initial_digest: str,
    resume_adapter: dict | None,
) -> tuple[Path, str, str]:
    path.parent.mkdir(parents=True, exist_ok=True)
    weight_after = hashlib.sha256(
        f"{experiment_class}:{start_row}:{cumulative_steps}".encode("utf-8")
    ).hexdigest()
    receipt = {
        "schema": "V10R2_QWEN35_DEV_TRAINING_RECEIPT_V1",
        "status": "DEVELOPMENT_OPTIMIZER_STEP_COMPLETE",
        "train_sha256": train_sha,
        "runtime_binding_sha256": runtime_sha,
        "cumulative_optimizer_steps": cumulative_steps,
        "experiment_class": experiment_class,
        "development_window": {
            "start_row": start_row,
            "row_count": row_count,
            "row_ids": [
                f"bound-train-row-{i}"
                for i in range(start_row, start_row + row_count)
            ],
        },
        "training_order": {
            "shuffle_dataset": False,
            "train_sampling_strategy": "sequential",
        },
        "optimizer": {
            "backend": "bitsandbytes",
            "module": "bitsandbytes.optim.adamw",
            "optim_bits": 8,
            "is_paged": False,
        },
        "resume_adapter": resume_adapter,
        "initial_trainable_parameter_digest": (
            initial_digest if resume_adapter is None else "resumed-weight"
        ),
        "initialization_equivalence_gate": {
            "expected_digest": initial_digest if resume_adapter is None else None,
            "pass": True,
        },
        "weight_digest_changed": True,
        "weight_digest_after": weight_after,
    }
    receipt["receipt_sha256"] = hashlib.sha256(canonical_bytes(receipt)).hexdigest()
    path.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return path, receipt["receipt_sha256"], weight_after


def test_recipe_semantics_validator_accepts_exact_continuous20(tmp_path: Path) -> None:
    from successor.experiments.decide_v10r3_recipe_semantics import (
        validate_recipe_receipt_semantics,
    )

    receipt_path, _, _ = _write_semantic_receipt(
        tmp_path / "continuous" / "DEV_TRAINING_COMPLETE.json",
        experiment_class="CONTINUOUS_STATE_RECIPE_SEMANTICS",
        start_row=0,
        row_count=160,
        cumulative_steps=20,
        train_sha="train-a",
        runtime_sha="runtime-a",
        initial_digest="init-a",
        resume_adapter=None,
    )
    got = validate_recipe_receipt_semantics(
        receipt_path,
        role="continuous",
        expected_train_sha="train-a",
        expected_runtime_sha="runtime-a",
        expected_initial_digest="init-a",
    )
    assert got["status"] == "PASS"
    assert got["chain"] == ["continuous20"]


def test_recipe_semantics_validator_accepts_exact_staged_4_8_8(tmp_path: Path) -> None:
    from successor.experiments.decide_v10r3_recipe_semantics import (
        validate_recipe_receipt_semantics,
    )

    stage1_path, stage1_sha, stage1_weight = _write_semantic_receipt(
        tmp_path / "stage1" / "DEV_TRAINING_COMPLETE.json",
        experiment_class="STAGED_RESET_RECIPE_SEMANTICS_CONTROL",
        start_row=0,
        row_count=32,
        cumulative_steps=4,
        train_sha="train-a",
        runtime_sha="runtime-a",
        initial_digest="init-a",
        resume_adapter=None,
    )
    stage2_path, stage2_sha, stage2_weight = _write_semantic_receipt(
        tmp_path / "stage2" / "DEV_TRAINING_COMPLETE.json",
        experiment_class="STAGED_RESET_RECIPE_SEMANTICS_CONTROL",
        start_row=32,
        row_count=64,
        cumulative_steps=12,
        train_sha="train-a",
        runtime_sha="runtime-a",
        initial_digest="init-a",
        resume_adapter={
            "source_receipt_path": str(stage1_path),
            "source_receipt_sha256": stage1_sha,
            "source_weight_digest_after": stage1_weight,
            "source_cumulative_optimizer_steps": 4,
            "previous_optimizer_steps": 4,
            "next_train_row": 32,
        },
    )
    stage3_path, _, _ = _write_semantic_receipt(
        tmp_path / "stage3" / "DEV_TRAINING_COMPLETE.json",
        experiment_class="STAGED_RESET_RECIPE_SEMANTICS_CONTROL",
        start_row=96,
        row_count=64,
        cumulative_steps=20,
        train_sha="train-a",
        runtime_sha="runtime-a",
        initial_digest="init-a",
        resume_adapter={
            "source_receipt_path": str(stage2_path),
            "source_receipt_sha256": stage2_sha,
            "source_weight_digest_after": stage2_weight,
            "source_cumulative_optimizer_steps": 12,
            "previous_optimizer_steps": 8,
            "next_train_row": 96,
        },
    )

    got = validate_recipe_receipt_semantics(
        stage3_path,
        role="staged",
        expected_train_sha="train-a",
        expected_runtime_sha="runtime-a",
        expected_initial_digest="init-a",
    )
    assert got["status"] == "PASS"
    assert [item["stage"] for item in got["chain"]] == [1, 2, 3]
