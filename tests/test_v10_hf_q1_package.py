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
