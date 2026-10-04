from __future__ import annotations

import json
from pathlib import Path


CONTRACT = (
    Path(__file__).parents[1]
    / "successor"
    / "experiments"
    / "V10_QWEN35_EXPERIMENT_CONTRACT_V3_DRAFT.json"
)


def test_v3_draft_is_fail_closed_and_binds_decided_full_run_invariants() -> None:
    value = json.loads(CONTRACT.read_text(encoding="utf-8"))

    assert value["schema"] == "VERA_SUCCESSOR_V10_QWEN35_EXPERIMENT_CONTRACT_V3_DRAFT"
    assert value["status"] == "DRAFT_BACKEND_QUALITY_AB_PENDING"
    assert value["executable_training_allowed"] is False
    assert value["supersedes_v2"] is False

    source = value["source_subject"]
    assert source["training_corpus_id"] == "VERA_SUCCESSOR_V10_QWEN512_50K_20261001_V1"
    assert source["train_rows"] == 50_000
    assert source["train_sha256"] == (
        "a232732a7db1f22c7edabb984fb16a3fe5350022e0a152576d80877eb9430300"
    )
    assert source["validation_rows"] == 2_500
    assert source["validation_sha256"] == (
        "ccc57ad20e8dfbc826ce49f064e692e0eab3fa396ed602dfba54ad9e252bd6d7"
    )

    recipe = value["training_recipe"]
    assert recipe["method"] == "QLORA_SFT_ONLY"
    assert recipe["fresh_adapter_required"] is True
    assert recipe["parent_adapter"] is None
    assert recipe["epochs"] == 1
    assert recipe["per_device_train_batch_size"] == 1
    assert recipe["gradient_accumulation_steps"] == 8
    assert recipe["expected_optimizer_steps"] == 6_250
    assert recipe["optimizer"] == "adamw_bnb_8bit"
    assert recipe["optimizer_paged"] is False
    assert recipe["continuous_optimizer_state"] is True
    assert recipe["continuous_scheduler_state"] is True
    assert recipe["learning_rate"] == 2e-5
    assert recipe["lr_scheduler_type"] == "cosine"
    assert recipe["warmup_optimizer_steps"] == 3
    assert recipe["warmup_basis"] == "V2_MINIMAL_CHANGE_PENDING_V3_FINAL_REVIEW"
    assert recipe["max_length"] == 512
    assert recipe["overflow_policy"] == "ERROR_NO_TRUNCATION"
    assert recipe["completion_only_loss"] is True
    assert recipe["packing"] is False
    assert recipe["shuffle_dataset"] is True
    assert recipe["seed"] == 20261001
    assert recipe["gradient_checkpointing"] is True

    quant = recipe["quantization"]
    assert quant == {
        "load_in_4bit": True,
        "type": "nf4",
        "double_quant": True,
        "compute_dtype": "bfloat16",
    }
    lora = recipe["lora"]
    assert lora == {
        "r": 4,
        "alpha": 16,
        "dropout": 0,
        "target_modules": "all-linear",
        "bias": "none",
    }

    backend = value["backend_selection"]
    assert backend["status"] == "PENDING_BACKEND_QUALITY_AB"
    assert backend["runtime_binding_sha256"] == (
        "8880dc796d4e0646ee0e061c2b83cc743106067b9955410a6ffb41a2d68fc25f"
    )
    assert backend["control"] == "torch_reference"
    assert backend["candidate"] == "fla_triton"
    assert backend["selected"] is None

    ab = backend["prospective_gate"]
    assert ab["start_adapter_sha256"] == (
        "5a78d4f94d25a0376862ebcb15e528ed6dab30b5b398da9d6af1783a16937eaf"
    )
    assert ab["rows"] == "384-447"
    assert ab["steps_per_arm"] == 8
    assert ab["optimizer"] == "adamw_bnb_8bit_nonpaged"
    assert ab["update_cosine_min"] == 0.995
    assert ab["update_relative_l2_max"] == 0.05
    assert ab["aggregate_nll_regression_abs_max"] == 0.005
    assert ab["family_mean_case_loss_regression_hold_abs"] == 0.01
    assert ab["min_speedup_pct"] == 20

    gates = value["blocking_preconditions"]
    assert gates["backend_quality_ab_verified"] is False
    assert gates["fresh_evaluation_bank_frozen"] is False
    assert gates["independent_bank_admission_verified"] is False
    assert gates["semantic_contamination_screen_verified"] is False
    assert gates["sealed_final_bank_commitment_bound"] is False
    assert gates["patrick_exact_weight_change_authority"] is False

    authority = value["authority"]
    assert authority["weight_change_authorized"] is False
    assert authority["merge_authorized"] is False
    assert authority["paid_compute_authorized"] is False
    assert authority["install_activate_deploy_authorized"] is False
