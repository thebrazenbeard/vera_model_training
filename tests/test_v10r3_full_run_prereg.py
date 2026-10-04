from __future__ import annotations

import json

import pytest
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
    assert value["status"] == "DRAFT_RECIPE_SEMANTICS_PENDING"
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
    assert recipe["warmup_basis"] == "V2_MINIMAL_CHANGE_PENDING_RECIPE_SEMANTICS_FINAL_REVIEW"
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
    assert backend["status"] == "TORCH_REFERENCE_SELECTED_RUNTIME_A_SELECTED"
    assert backend["runtime_binding_sha256"] == (
        "44b01efc6c2d0e1716208e04e7132433561b5562430adae821fd29e6a1493224"
    )
    assert backend["control"] == "torch_reference"
    assert backend["candidate"] == "fla_triton"
    assert backend["selected"] == "torch_reference"
    assert backend["runtime_host_status"] == "CONSERVATIVE_RUNTIME_A_SELECTED_CANDIDATE_B_PARITY_FAILED"
    assert backend["backend_quality_ab_result"]["decision_sha256"] == (
        "8d13652488f5955b67e83ee00654c0465b633bf8696b89a0bc89dd09e99b4688"
    )
    assert backend["backend_quality_ab_result"]["disposition"] == (
        "REJECT_FLA_PROMOTION_SELECT_TORCH_REFERENCE_MATH"
    )
    parity = backend["cross_runtime_parity"]
    assert parity["status"] == "COMPLETE_FAIL_CANDIDATE_RUNTIME_B_REJECTED"
    assert parity["decision_sha256"] == (
        "bbde91ccaaa5b72f02826db99578281af6fc7275c744fc69051bf259fc486698"
    )
    assert parity["runtime_a_receipt_sha256"] == (
        "f1eb89d3e87e6d1f9e07e5c7d04301bdf11f0fea7531e547abaf6548f035a162"
    )
    assert parity["runtime_b_receipt_sha256"] == (
        "0b5d2c44b557d72b59b4c0943a523384f937ea34ce2d18d5cc0132e1148a1ff4"
    )
    assert parity["gradient_cosine"] == pytest.approx(0.9911159340965399)
    assert parity["gradient_relative_l2"] == pytest.approx(0.13300203789055962)
    assert parity["disposition"] == "KEEP_CONSERVATIVE_RUNTIME_A"

    semantics = value["recipe_semantics"]
    assert semantics["status"] == "PENDING_FRESH_MATCHED_STAGED_VS_CONTINUOUS_V2_FREEZE"
    assert semantics["runtime"] == "A_CONSERVATIVE"
    assert semantics["exact_order"] == "NATURAL_SEQUENTIAL_NO_SHUFFLE_BOTH_ARMS"
    assert semantics["fresh_eval_record_ids_sha256"] == (
        "6a6e7b942222308ebae4209331450579f3b4c526ff47be9016487fa63b44b57f"
    )
    assert semantics["answers_full_run_warmup3"] is False

    conv = value["runtime_research"]["causal_conv"]
    assert conv["disposition"] == "NOT_PRIMARY_FULL_RUN_BOTTLENECK"
    assert conv["receipt_file_sha256"] == (
        "24171cb705e518893b0c2350c89e0c82598b907d1173c88053e686fda7477488"
    )

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
    assert gates["backend_quality_ab_verified"] is True
    assert gates["cross_runtime_parity_verified"] is True
    assert gates["candidate_runtime_b_promoted"] is False
    assert gates["recipe_semantics_verified"] is False
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
