from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from successor.experiments.v10r3_cross_runtime_parity import assess_parity


ROOT = Path(__file__).parents[1]
PROTOCOL = (
    ROOT
    / "successor"
    / "experiments"
    / "V10R3_CROSS_RUNTIME_PARITY_PROTOCOL_V1.json"
)


def _receipt(runtime_key: str) -> dict:
    return {
        "runtime_key": runtime_key,
        "input_ids_sha256": "a" * 64,
        "labels_sha256": "b" * 64,
        "trainable_layout_sha256": "c" * 64,
        "trainable_parameter_count": 8_116_224,
        "weight_digest_unchanged": True,
        "optimizer_created": False,
        "microbatch_losses": [1.1, 1.2, 1.3, 1.4],
        "mean_loss": 1.25,
        "gradient": {"all_finite": True},
    }


def test_protocol_is_frozen_nonmutating_and_binds_exact_subject() -> None:
    value = json.loads(PROTOCOL.read_text(encoding="utf-8"))
    assert value["schema"] == "V10R3_CROSS_RUNTIME_PARITY_PROTOCOL_V1"
    assert value["status"] == "FROZEN_NOT_EXECUTED"
    assert value["effect"] == (
        "NON_MUTATING_FORWARD_BACKWARD_ONLY_NO_OPTIMIZER_NO_WEIGHT_CHANGE"
    )
    subject = value["common_subject"]
    assert subject["adapter_model_sha256"] == (
        "5a78d4f94d25a0376862ebcb15e528ed6dab30b5b398da9d6af1783a16937eaf"
    )
    assert subject["train_sha256"] == (
        "a232732a7db1f22c7edabb984fb16a3fe5350022e0a152576d80877eb9430300"
    )
    assert subject["row_indices"] == [384, 400, 416, 432]
    assert [row["tokens"] for row in subject["rows"]] == [324, 214, 84, 149]
    assert subject["backend"] == "torch_reference"
    assert subject["optimizer_created"] is False

    runtimes = value["runtimes"]
    assert runtimes["A"]["binding_sha256"] == (
        "44b01efc6c2d0e1716208e04e7132433561b5562430adae821fd29e6a1493224"
    )
    assert runtimes["B"]["binding_sha256"] == (
        "8880dc796d4e0646ee0e061c2b83cc743106067b9955410a6ffb41a2d68fc25f"
    )

    gate = value["prospective_gate"]
    assert gate["gradient_cosine_min"] == 0.999
    assert gate["gradient_relative_l2_max"] == 0.02
    assert gate["gradient_l2_relative_difference_max"] == 0.02
    assert gate["max_microbatch_loss_abs_delta"] == 0.002
    assert gate["mean_loss_abs_delta_max"] == 0.001
    assert value["decision"]["no_threshold_changes_after_execution"] is True
    assert value["authority"]["weight_change_authorized"] is False
    assert value["authority"]["optimizer_step_authorized"] is False
    assert value["authority"]["full_training_authorized"] is False


def test_assess_parity_passes_within_frozen_gates() -> None:
    protocol = json.loads(PROTOCOL.read_text(encoding="utf-8"))
    left = _receipt("A")
    right = _receipt("B")
    right["microbatch_losses"] = [1.1004, 1.1998, 1.3002, 1.3996]
    right["mean_loss"] = sum(right["microbatch_losses"]) / 4
    a = np.array([1.0, 2.0, 3.0, 4.0], dtype=np.float32)
    b = a * np.float32(1.001)
    result = assess_parity(protocol, left, right, a, b)
    assert result["status"] == "PASS_RUNTIME_PARITY"
    assert result["reasons"] == []
    assert result["metrics"]["gradient_cosine"] >= 0.999
    assert result["metrics"]["gradient_relative_l2"] <= 0.02


def test_assess_parity_holds_on_gradient_divergence() -> None:
    protocol = json.loads(PROTOCOL.read_text(encoding="utf-8"))
    left = _receipt("A")
    right = _receipt("B")
    a = np.array([1.0, 0.0, 0.0, 0.0], dtype=np.float32)
    b = np.array([0.9, 0.2, 0.2, 0.2], dtype=np.float32)
    result = assess_parity(protocol, left, right, a, b)
    assert result["status"] == "HOLD_RUNTIME_PROMOTION"
    assert "gradient_cosine_below_gate" in result["reasons"]
    assert "gradient_relative_l2_above_gate" in result["reasons"]


def test_assess_parity_holds_on_token_or_loss_mismatch() -> None:
    protocol = json.loads(PROTOCOL.read_text(encoding="utf-8"))
    left = _receipt("A")
    right = _receipt("B")
    right["input_ids_sha256"] = "d" * 64
    right["microbatch_losses"][2] += 0.01
    right["mean_loss"] = sum(right["microbatch_losses"]) / 4
    a = np.ones(8, dtype=np.float32)
    b = np.ones(8, dtype=np.float32)
    result = assess_parity(protocol, left, right, a, b)
    assert result["status"] == "HOLD_RUNTIME_PROMOTION"
    assert "input_ids_sha256_mismatch" in result["reasons"]
    assert "microbatch_loss_delta_above_gate" in result["reasons"]
