from __future__ import annotations

import json
from pathlib import Path

import pytest

from successor.experiments.train_v10r2_dev import (
    DevTrainingHold,
    effect_label,
    load_and_validate_dev_spec,
    summarize_optimizer,
)


def _write_spec(path: Path, *, optimizer: str = "adamw_bnb_8bit") -> Path:
    value = {
        "schema": "V10R2_QWEN35_DEV_TRAINING_SPEC_V1",
        "status": "AUTHORIZED_LOCAL_DEVELOPMENT_TRAINING",
        "authority": {
            "actor_id": "PATRICK_USER_AUTHORITY",
            "source": "EXPLICIT_CURRENT_USER_INSTRUCTION",
            "scope": "CHANGE_TRAINING_METHOD_AND_CONTINUE_LOCAL_MODEL_TRAINING",
            "paid_compute_authorized": False,
            "merge_authorized": False,
            "deploy_activate_authorized": False,
        },
        "source_subject": {
            "parent_revision": "a" * 40,
            "training_corpus_id": "corpus",
            "train_sha256": "b" * 64,
            "train_rows": 50000,
            "runtime_binding_sha256": "c" * 64,
        },
        "trainer": {
            "max_optimizer_steps": 1,
            "optimizer": optimizer,
            "gradient_accumulation_steps": 8,
            "per_device_train_batch_size": 1,
            "max_length": 512,
            "learning_rate": 2e-5,
            "lr_scheduler_type": "cosine",
            "warmup_optimizer_steps": 0,
            "completion_only_loss": True,
            "packing": False,
            "shuffle_dataset": True,
            "gradient_checkpointing": True,
            "bf16": True,
            "tf32": True,
            "gradient_checkpointing_use_reentrant": False,
            "logging_steps": 1,
            "save_strategy": "no",
            "eval_strategy": "no",
            "report_to": "none",
            "seed": 20261001,
        },
        "quantization": {
            "load_in_4bit": True,
            "type": "nf4",
            "double_quant": True,
            "compute_dtype": "bfloat16",
        },
        "lora": {
            "r": 4,
            "alpha": 16,
            "dropout": 0,
            "target_modules": "all-linear",
            "bias": "none",
            "task_type": "CAUSAL_LM",
        },
        "model_load": {
            "device_map": {"": 0},
            "dtype": "bfloat16",
            "use_cache": False,
            "prepare_model_for_kbit_training_use_gradient_checkpointing": True,
        },
        "output": {
            "namespace": str(path.parent / "adapter"),
            "save_final_adapter": True,
            "overwrite_forbidden": True,
        },
        "qualification": {
            "external_final_bank_required_for_qualification": True,
            "development_training_may_precede_external_qualification": True,
            "claim_ceiling": "LOCAL_DEVELOPMENT_ADAPTER_ONLY_NOT_EXTERNALLY_QUALIFIED",
        },
    }
    path.write_text(json.dumps(value), encoding="utf-8")
    return path


def test_dev_spec_accepts_nonpaged_bnb_8bit(tmp_path: Path) -> None:
    spec = load_and_validate_dev_spec(_write_spec(tmp_path / "spec.json"))
    assert spec["trainer"]["optimizer"] == "adamw_bnb_8bit"
    assert spec["trainer"]["max_optimizer_steps"] == 1


def test_dev_spec_accepts_nonpaged_torchao_8bit(tmp_path: Path) -> None:
    path = _write_spec(tmp_path / "spec.json", optimizer="adamw_torch_8bit")
    spec = load_and_validate_dev_spec(path)
    assert spec["trainer"]["optimizer"] == "adamw_torch_8bit"


def test_dev_spec_accepts_four_step_staged_window(tmp_path: Path) -> None:
    path = _write_spec(tmp_path / "spec.json")
    value = json.loads(path.read_text())
    value["trainer"]["max_optimizer_steps"] = 4
    value["development_window"] = {"start_row": 0, "row_count": 32}
    path.write_text(json.dumps(value), encoding="utf-8")
    spec = load_and_validate_dev_spec(path)
    assert spec["trainer"]["max_optimizer_steps"] == 4
    assert spec["development_window"]["row_count"] == 32


def test_dev_spec_rejects_misaligned_staged_window(tmp_path: Path) -> None:
    path = _write_spec(tmp_path / "spec.json")
    value = json.loads(path.read_text())
    value["trainer"]["max_optimizer_steps"] = 4
    value["development_window"] = {"start_row": 0, "row_count": 24}
    path.write_text(json.dumps(value), encoding="utf-8")
    with pytest.raises(DevTrainingHold, match="staged optimizer window"):
        load_and_validate_dev_spec(path)


def test_dev_spec_rejects_paged_optimizer(tmp_path: Path) -> None:
    path = _write_spec(tmp_path / "spec.json", optimizer="paged_adamw_8bit")
    with pytest.raises(DevTrainingHold, match="paged optimizers are forbidden"):
        load_and_validate_dev_spec(path)


def test_dev_spec_rejects_plain_adamw_torch(tmp_path: Path) -> None:
    path = _write_spec(tmp_path / "spec.json", optimizer="adamw_torch")
    with pytest.raises(DevTrainingHold, match="approved non-paged 8-bit"):
        load_and_validate_dev_spec(path)


def test_dev_spec_rejects_paid_compute_or_deploy_authority(tmp_path: Path) -> None:
    path = _write_spec(tmp_path / "spec.json")
    value = json.loads(path.read_text())
    value["authority"]["paid_compute_authorized"] = True
    path.write_text(json.dumps(value), encoding="utf-8")
    with pytest.raises(DevTrainingHold, match="paid compute"):
        load_and_validate_dev_spec(path)


def test_dev_spec_requires_external_bank_for_qualification(tmp_path: Path) -> None:
    path = _write_spec(tmp_path / "spec.json")
    value = json.loads(path.read_text())
    value["qualification"]["external_final_bank_required_for_qualification"] = False
    path.write_text(json.dumps(value), encoding="utf-8")
    with pytest.raises(DevTrainingHold, match="external final bank"):
        load_and_validate_dev_spec(path)


def test_optimizer_summary_identifies_nonpaged_bnb_8bit_optimizer() -> None:
    class Args:
        optim_bits = 8
        min_8bit_size = 4096

    class FakeOptimizer:
        is_paged = False
        args = Args()

    FakeOptimizer.__module__ = "bitsandbytes.optim.adamw"
    FakeOptimizer.__name__ = "AdamW"

    result = summarize_optimizer(FakeOptimizer())
    assert result["class"] == "AdamW"
    assert result["module"] == "bitsandbytes.optim.adamw"
    assert result["backend"] == "bitsandbytes"
    assert result["is_paged"] is False
    assert result["optim_bits"] == 8
    assert result["min_8bit_size"] == 4096



def test_optimizer_summary_unwraps_accelerate_wrapper() -> None:
    class Args:
        optim_bits = 8
        min_8bit_size = 4096

    class Inner:
        is_paged = False
        args = Args()

    Inner.__module__ = "bitsandbytes.optim.adamw"
    Inner.__name__ = "AdamW"

    class Wrapper:
        def __init__(self):
            self.optimizer = Inner()

    result = summarize_optimizer(Wrapper())
    assert result["class"] == "AdamW"
    assert result["module"] == "bitsandbytes.optim.adamw"
    assert result["is_paged"] is False
    assert result["optim_bits"] == 8
    assert result["wrapper_chain"] == ["Wrapper"]


def test_optimizer_summary_identifies_nonpaged_torchao_8bit_optimizer() -> None:
    class FakeOptimizer:
        block_size = 256

    FakeOptimizer.__module__ = "torchao.optim.adam"
    FakeOptimizer.__name__ = "AdamW8bit"

    result = summarize_optimizer(FakeOptimizer())
    assert result["class"] == "AdamW8bit"
    assert result["module"] == "torchao.optim.adam"
    assert result["backend"] == "torchao"
    assert result["is_paged"] is False
    assert result["optim_bits"] == 8


def test_effect_label_tracks_step_count_and_backend() -> None:
    assert effect_label("adamw_bnb_8bit", 1) == "ONE_LOCAL_BNB_ADAMW_8BIT_OPTIMIZER_STEP"
    assert effect_label("adamw_bnb_8bit", 4) == "FOUR_LOCAL_BNB_ADAMW_8BIT_OPTIMIZER_STEPS"
    assert effect_label("adamw_torch_8bit", 1) == "ONE_LOCAL_TORCHAO_ADAMW_8BIT_OPTIMIZER_STEP"


def test_effect_label_rejects_unknown_backend_or_count() -> None:
    with pytest.raises(DevTrainingHold, match="effect label"):
        effect_label("paged_adamw_8bit", 1)
    with pytest.raises(DevTrainingHold, match="effect label"):
        effect_label("adamw_bnb_8bit", 0)
