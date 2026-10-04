from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from successor.experiments.train_v10r2_dev import (
    DevTrainingHold,
    load_and_validate_dev_spec,
)


ROOT = Path(__file__).resolve().parents[1]
EXP = ROOT / "successor" / "experiments"


def _json(name: str) -> dict:
    return json.loads((EXP / name).read_text(encoding="utf-8"))


def _sha(name: str) -> str:
    return hashlib.sha256((EXP / name).read_bytes()).hexdigest()


def test_recipe_semantics_order_manifest_is_exact_and_unique() -> None:
    manifest = _json(
        "V10R3_RECIPE_SEMANTICS_ORDER_ROWS0_159_20261004_V2.json"
    )
    assert manifest["schema"] == "V10R3_RECIPE_SEMANTICS_ORDER_MANIFEST_V2"
    assert manifest["row_count"] == 160
    assert manifest["row_indices"] == list(range(160))
    ids = manifest["record_ids"]
    assert len(ids) == 160
    assert len(set(ids)) == 160
    digest = hashlib.sha256(
        ("\n".join(ids) + "\n").encode("utf-8")
    ).hexdigest()
    assert digest == manifest["record_ids_sha256"]
    assert digest == (
        "904ac73c903a3878f950215d004a7d4a17af45a002d2637cba3b3a7995974142"
    )

    groups = manifest["optimizer_step_groups"]
    assert len(groups) == 20
    assert [g["optimizer_step"] for g in groups] == list(range(1, 21))
    assert [i for g in groups for i in g["row_indices"]] == list(range(160))
    assert all(len(g["row_indices"]) == 8 for g in groups)
    assert manifest["shuffle_dataset"] is False
    assert manifest["train_sampling_strategy"] == "sequential"
    assert manifest["invariants"]["each_selected_row_exactly_once"] is True
    assert manifest["invariants"]["same_effective_row_order_both_arms"] is True


def test_matched_specs_share_fresh_initialization_and_order_policy() -> None:
    stage1 = load_and_validate_dev_spec(
        EXP / "V10R3_STAGED_RESET_CONTROL_STAGE1_SPEC_20261004_V2.json"
    )
    continuous = load_and_validate_dev_spec(
        EXP / "V10R3_CONTINUOUS20_TRAINING_SPEC_20261004_V2.json"
    )

    assert "resume_adapter" not in stage1
    assert "resume_adapter" not in continuous
    for key in ("source_subject", "quantization", "lora", "model_load"):
        assert stage1[key] == continuous[key]

    common_trainer_fields = (
        "seed",
        "learning_rate",
        "lr_scheduler_type",
        "warmup_optimizer_steps",
        "per_device_train_batch_size",
        "gradient_accumulation_steps",
        "max_length",
        "optimizer",
        "completion_only_loss",
        "packing",
        "shuffle_dataset",
        "train_sampling_strategy",
        "gradient_checkpointing",
        "bf16",
        "tf32",
        "gradient_checkpointing_use_reentrant",
    )
    for key in common_trainer_fields:
        assert stage1["trainer"][key] == continuous["trainer"][key]

    assert stage1["trainer"]["shuffle_dataset"] is False
    assert stage1["trainer"]["train_sampling_strategy"] == "sequential"
    assert continuous["trainer"]["shuffle_dataset"] is False
    assert continuous["trainer"]["train_sampling_strategy"] == "sequential"
    assert stage1["development_window"] == {"start_row": 0, "row_count": 32}
    assert continuous["development_window"] == {
        "start_row": 0,
        "row_count": 160,
    }
    assert stage1["trainer"]["max_optimizer_steps"] == 4
    assert continuous["trainer"]["max_optimizer_steps"] == 20
    assert stage1["output"]["namespace"] != continuous["output"]["namespace"]


def test_protocol_and_specs_bind_same_order_manifest() -> None:
    manifest_name = "V10R3_RECIPE_SEMANTICS_ORDER_ROWS0_159_20261004_V2.json"
    manifest = _json(manifest_name)
    manifest_sha = _sha(manifest_name)
    protocol = _json("V10R3_STAGED_VS_CONTINUOUS_PROTOCOL_20261004_V2.json")
    stage1 = _json("V10R3_STAGED_RESET_CONTROL_STAGE1_SPEC_20261004_V2.json")
    continuous = _json("V10R3_CONTINUOUS20_TRAINING_SPEC_20261004_V2.json")

    assert protocol["matched_training_subject"]["order_manifest_sha256"] == manifest_sha
    assert protocol["matched_training_subject"]["ordered_record_ids_sha256"] == (
        manifest["record_ids_sha256"]
    )
    for spec in (stage1, continuous):
        assert spec["comparison"]["order_manifest_sha256"] == manifest_sha
        assert spec["comparison"]["full_matched_order_record_ids_sha256"] == (
            manifest["record_ids_sha256"]
        )

    namespaces = {
        stage1["output"]["namespace"],
        continuous["output"]["namespace"],
        protocol["control"]["final_namespace"],
    }
    assert len(namespaces) == 3


def test_superseded_v1_global_shuffle_candidate_is_not_executable() -> None:
    with pytest.raises(
        DevTrainingHold,
        match="shuffle_dataset=false|sequential sampling",
    ):
        load_and_validate_dev_spec(
            EXP / "V10R3_CONTINUOUS20_TRAINING_SPEC_20261004_V1.json"
        )