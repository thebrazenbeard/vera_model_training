from __future__ import annotations

import json
from pathlib import Path

import pytest

from successor.experiments.run_v10_hf_q1 import (
    HfQ1Hold,
    assert_paid_launch_authority,
    build_dry_run_plan,
    load_and_validate_protocol,
)


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = (
    ROOT
    / "successor"
    / "experiments"
    / "V10_HF_Q1_R2_CLOUD_PROTOCOL_20261004_V1.json"
)


def test_protocol_binds_exact_r2_subject_and_base_model() -> None:
    protocol = load_and_validate_protocol(PROTOCOL)

    assert protocol["source_subject"]["r2_training_head"] == (
        "bc8c4c997aae11ef9b80a899d273bf18283dbf8c"
    )
    assert protocol["source_subject"]["r2_execution_spec_sha256"] == (
        "caaecf6309aee0ff5279c42b48118065d156228e22c614a5347bf489951b290d"
    )
    assert protocol["base_model"] == {
        "repo": "rodrigomt/Qwen3.5-4B-Uncensored-Aggressive",
        "revision": "d61dd146c8fd44c9a49cdb7f59f34e17b61902d8",
        "mutable_revision_allowed": False,
    }


def test_protocol_preserves_r2_training_semantics() -> None:
    protocol = load_and_validate_protocol(PROTOCOL)
    recipe = protocol["recipe_equivalence"]

    assert recipe["train_rows"] == [0, 159]
    assert recipe["max_optimizer_steps"] == 20
    assert recipe["seed"] == 20261001
    assert recipe["learning_rate"] == 2e-5
    assert recipe["gradient_accumulation_steps"] == 8
    assert recipe["max_length"] == 512
    assert recipe["optimizer"] == "adamw_bnb_8bit"
    assert recipe["train_sampling_strategy"] == "sequential"
    assert recipe["shuffle_dataset"] is False
    assert recipe["lora"] == {
        "r": 4,
        "alpha": 16,
        "dropout": 0,
        "target_modules": "all-linear",
        "bias": "none",
        "task_type": "CAUSAL_LM",
    }


def test_cloud_plan_is_dry_run_and_budget_bounded() -> None:
    plan = build_dry_run_plan(load_and_validate_protocol(PROTOCOL))

    assert plan["status"] == "DRY_RUN_ONLY"
    assert plan["paid_compute_authorized"] is False
    assert plan["hardware"]["flavor"] == "a10g-small"
    assert plan["hardware"]["minimum_vram_gib"] == 24
    assert plan["limits"]["timeout_seconds"] == 1800
    assert plan["limits"]["proposed_budget_cap_usd"] == 0.50
    assert plan["evaluation"]["final_bank"] == "PROHIBITED"
    assert plan["evaluation"]["one_time_panel"] == "PROHIBITED"


def test_paid_launch_refuses_without_separate_exact_authority() -> None:
    with pytest.raises(HfQ1Hold, match="paid compute"):
        assert_paid_launch_authority(None)


def test_paid_launch_refuses_current_no_spend_protocol() -> None:
    protocol = load_and_validate_protocol(PROTOCOL)
    with pytest.raises(HfQ1Hold, match="paid compute"):
        assert_paid_launch_authority(protocol["authority"])


def test_protocol_declares_hardware_variance_not_recipe_variance() -> None:
    protocol = load_and_validate_protocol(PROTOCOL)
    equivalence = protocol["environment_equivalence"]

    assert set(equivalence["allowed_variance"]) == {
        "gpu_model",
        "gpu_vram",
        "driver_version",
        "cuda_driver_runtime",
        "host_os",
        "device_map",
    }
    assert {
        "base_model_bytes",
        "training_data_bytes",
        "row_order",
        "seed",
        "optimizer",
        "scheduler",
        "learning_rate",
        "batching",
        "max_length",
        "quantization",
        "lora_geometry",
        "python_version",
        "python_package_versions",
    }.issubset(set(equivalence["forbidden_variance"]))


def test_protocol_requires_receipts_but_no_quality_claim() -> None:
    protocol = json.loads(PROTOCOL.read_text(encoding="utf-8"))

    assert protocol["required_receipts"] == [
        "environment_receipt",
        "input_hash_receipt",
        "initial_trainable_digest_receipt",
        "training_receipt",
        "artifact_hash_manifest",
        "job_cost_duration_receipt",
    ]
    assert protocol["claim_ceiling"] == (
        "CLOUD_EXECUTABILITY_AND_ENVIRONMENT_ISOLATION_ONLY_"
        "NOT_RECIPE_WINNER_NOT_BEHAVIOR_QUALIFICATION_NOT_FINAL_TRAINING"
    )


def test_protocol_carries_reviewed_r2_omitted_semantics() -> None:
    protocol = load_and_validate_protocol(PROTOCOL)
    recipe = protocol["recipe_equivalence"]

    assert recipe["gradient_checkpointing_use_reentrant"] is False
    assert recipe["lora"]["bias"] == "none"
    assert recipe["lora"]["task_type"] == "CAUSAL_LM"
    assert recipe["model_load"] == {
        "dtype": "bfloat16",
        "use_cache": False,
        "prepare_model_for_kbit_training_use_gradient_checkpointing": True,
    }
    assert protocol["environment_equivalence"]["device_map_policy"] == (
        "MAY_VARY_IF_EXPLICITLY_RECORDED_IN_ENVIRONMENT_RECEIPT"
    )


def test_protocol_requires_reviewed_environment_and_training_receipts() -> None:
    protocol = load_and_validate_protocol(PROTOCOL)
    contract = protocol["receipt_contract"]

    assert set(contract["environment_required_fields"]) == {
        "gpu_compute_capability",
        "gpu_model",
        "gpu_vram_gib",
        "driver_version",
        "cuda_driver_runtime",
        "torch_build",
        "bitsandbytes_backend",
        "bitsandbytes_binary",
        "device_map",
        "tf32_enabled",
        "deterministic_algorithms_enabled",
        "rng_state_digest",
        "environment_digest",
    }
    assert set(contract["training_required_fields"]) == {
        "final_adapter_sha256",
        "final_loss_finite",
        "final_learning_rate_finite",
        "final_grad_norm_finite",
        "weight_digest_changed_true",
    }
    assert set(contract["cost_required_fields"]) == {
        "live_rate_usd_per_hour",
        "timeout_seconds",
        "worst_case_timeout_cost_usd",
        "budget_cap_usd",
        "within_budget",
    }


def test_live_rate_budget_guard_fails_closed() -> None:
    from successor.experiments import run_v10_hf_q1 as hf

    receipt = hf.assert_live_rate_within_budget(
        live_rate_usd_per_hour=1.0,
        timeout_seconds=1800,
        budget_cap_usd=0.50,
    )
    assert receipt["worst_case_timeout_cost_usd"] == pytest.approx(0.50)
    assert receipt["within_budget"] is True

    with pytest.raises(HfQ1Hold, match="budget"):
        hf.assert_live_rate_within_budget(
            live_rate_usd_per_hour=1.01,
            timeout_seconds=1800,
            budget_cap_usd=0.50,
        )


def test_dry_run_plan_exposes_launch_preflight_and_receipt_contract() -> None:
    protocol = load_and_validate_protocol(PROTOCOL)
    plan = build_dry_run_plan(protocol)

    assert plan["launch_preflight"] == protocol["launch_preflight"]
    assert plan["receipt_contract"] == protocol["receipt_contract"]


def _write_protocol_variant(tmp_path: Path, mutate) -> Path:
    value = json.loads(PROTOCOL.read_text(encoding="utf-8"))
    mutate(value)
    path = tmp_path / "protocol.json"
    path.write_text(json.dumps(value), encoding="utf-8")
    return path


def test_protocol_rejects_missing_receipt_contract(tmp_path: Path) -> None:
    path = _write_protocol_variant(
        tmp_path,
        lambda value: value.pop("receipt_contract"),
    )
    with pytest.raises(HfQ1Hold, match="receipt contract"):
        load_and_validate_protocol(path)


def test_protocol_rejects_tampered_launch_preflight(tmp_path: Path) -> None:
    def mutate(value: dict) -> None:
        value["launch_preflight"]["network_launch_present"] = True

    path = _write_protocol_variant(tmp_path, mutate)
    with pytest.raises(HfQ1Hold, match="launch preflight"):
        load_and_validate_protocol(path)


def test_protocol_rejects_unrecorded_device_map_variance(tmp_path: Path) -> None:
    def mutate(value: dict) -> None:
        value["environment_equivalence"]["device_map_policy"] = "UNRECORDED"

    path = _write_protocol_variant(tmp_path, mutate)
    with pytest.raises(HfQ1Hold, match="device map"):
        load_and_validate_protocol(path)
