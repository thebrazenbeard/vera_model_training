from __future__ import annotations

import json
from pathlib import Path

import pytest

from successor.experiments.train_v10r2_dev import (
    DevTrainingHold,
    load_and_validate_dev_spec,
)

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "successor/experiments/V10R3R1_CONTINUOUS20_EXECUTABILITY_REPLICATION_SPEC_20261004_V1.json"
PROTOCOL = ROOT / "successor/experiments/V10R3R1_CONTINUOUS20_EXECUTABILITY_REPLICATION_PROTOCOL_20261004_V1.json"


def test_v10r3r1_preregistration_is_not_executable_training_authority() -> None:
    spec = json.loads(SPEC.read_text(encoding="utf-8"))
    protocol = json.loads(PROTOCOL.read_text(encoding="utf-8"))

    assert spec["status"] == "PREREGISTERED_NO_EXECUTION_AUTHORITY"
    assert spec["authority"]["source"] == "COORDINATION_AND_PREREGISTRATION_ONLY"
    assert spec["authority"]["execution_authority_required"] is True
    assert protocol["authority"]["development_training_authorized"] is False
    assert protocol["authority"]["execution_authority_required"] is True
    assert protocol["authority"]["current_authority"] == "COORDINATION_AND_PREREGISTRATION_ONLY"

    with pytest.raises(DevTrainingHold, match="development training is not authorized"):
        load_and_validate_dev_spec(SPEC)
