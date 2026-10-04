from __future__ import annotations

import hashlib
import json
import os
import subprocess
from pathlib import Path

import pytest

from successor.experiments.train_v10r2_dev import (
    DevTrainingHold,
    load_and_validate_dev_spec,
)


ROOT = Path(__file__).resolve().parents[1]
EXP = ROOT / "successor" / "experiments"
TRAIN_JSONL = Path(
    os.environ.get(
        "VERA_V10_TRAIN_JSONL",
        r"D:\VERA\.scratch\v10-qwen512-preflight-20261001-v1\train.jsonl",
    )
)
EXPECTED_RAW_SHA256 = {
    "V10R3_RECIPE_SEMANTICS_ORDER_ROWS0_159_20261004_V2.json":
        "129572aef614e921c92161d9874e9cecdbf40bfbb0de073221562cd09e6172dc",
    "V10R3_STAGED_RESET_CONTROL_STAGE1_SPEC_20261004_V2.json":
        "507d812cd05e3bdf131992acf4ffa947217b8aaab18968d1515b894093688f3c",
    "V10R3_CONTINUOUS20_TRAINING_SPEC_20261004_V2.json":
        "30c1a055ee5228888ab2df83d3af51dc04bc0f3ff598b9d8d51ec088e1ea67e7",
    "V10R3_RECIPE_SEMANTICS_PANEL_ROWS448_511_V1.json":
        "8e5ae8eebf68a2687b9905dc99632d11aeaeb74fad328b38f472db9afe483699",
    "V10R3_STAGED_VS_CONTINUOUS_PROTOCOL_20261004_V2.json":
        "2de024f88f2ecda3cab5af995e45dcb8b6e05545034eb7a051556632c75b29fc",
}


def _json(name: str) -> dict:
    return json.loads((EXP / name).read_text(encoding="utf-8"))


def _sha(name: str) -> str:
    return hashlib.sha256((EXP / name).read_bytes()).hexdigest()


def _git_sha(name: str) -> str:
    raw = subprocess.check_output(
        [
            "git",
            "-C",
            str(ROOT),
            "show",
            f"HEAD:successor/experiments/{name}",
        ]
    )
    return hashlib.sha256(raw).hexdigest()


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
    manifest_sha = _git_sha(manifest_name)
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

def test_raw_committed_file_hash_bindings_are_exact() -> None:
    protocol = _json("V10R3_STAGED_VS_CONTINUOUS_PROTOCOL_20261004_V2.json")
    for name, expected in EXPECTED_RAW_SHA256.items():
        assert _git_sha(name) == expected

    assert protocol["matched_training_subject"]["order_manifest_sha256"] == (
        EXPECTED_RAW_SHA256[
            "V10R3_RECIPE_SEMANTICS_ORDER_ROWS0_159_20261004_V2.json"
        ]
    )
    assert protocol["control"]["stage1_spec_sha256"] == (
        EXPECTED_RAW_SHA256[
            "V10R3_STAGED_RESET_CONTROL_STAGE1_SPEC_20261004_V2.json"
        ]
    )
    assert protocol["candidate"]["spec_sha256"] == (
        EXPECTED_RAW_SHA256[
            "V10R3_CONTINUOUS20_TRAINING_SPEC_20261004_V2.json"
        ]
    )
    assert protocol["evaluation"]["panel_file_sha256"] == (
        EXPECTED_RAW_SHA256[
            "V10R3_RECIPE_SEMANTICS_PANEL_ROWS448_511_V1.json"
        ]
    )
    assert protocol["prospective_gates"][
        "initial_trainable_digest_exact_match_required"
    ] is True


def test_order_manifest_recomputes_from_frozen_train_jsonl() -> None:
    if not TRAIN_JSONL.is_file():
        pytest.skip(f"frozen train JSONL unavailable:{TRAIN_JSONL}")
    raw = TRAIN_JSONL.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == (
        "a232732a7db1f22c7edabb984fb16a3fe5350022e0a152576d80877eb9430300"
    )
    rows = [
        json.loads(line)
        for line in raw.decode("utf-8").splitlines()
        if line.strip()
    ]
    assert len(rows) == 50000
    manifest = _json(
        "V10R3_RECIPE_SEMANTICS_ORDER_ROWS0_159_20261004_V2.json"
    )
    assert manifest["serialization"] == "NEWLINE_UTF8_FINAL_LF"

    def record_id(row: dict, index: int) -> str:
        return (
            row.get("record_id")
            or row.get("case_id")
            or row.get("id")
            or f"bound-train-row-{index}"
        )

    actual_ids = [record_id(rows[i], i) for i in range(160)]
    assert actual_ids == manifest["record_ids"]
    assert hashlib.sha256(
        ("\n".join(actual_ids) + "\n").encode("utf-8")
    ).hexdigest() == manifest["record_ids_sha256"]
