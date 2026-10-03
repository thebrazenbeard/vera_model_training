from __future__ import annotations

import json
from pathlib import Path

import pytest

from successor.experiments.train_v10r2_lane_b import (
    CLAIM_CEILING,
    DevTrainingHold,
    effect_label,
    load_and_validate_dev_spec,
)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _lane_b_spec() -> Path:
    return (
        _repo_root()
        / 'successor'
        / 'experiments'
        / 'V10R2_LANE_B_DEV_SPEC_FLA_BNB8_STEP1_20261003_V1.json'
    )


def test_lane_b_bound_spec_validates() -> None:
    spec = load_and_validate_dev_spec(_lane_b_spec())
    assert spec['qualification']['claim_ceiling'] == CLAIM_CEILING
    assert spec['trainer']['optimizer'] == 'adamw_bnb_8bit'
    assert spec['development_window'] == {'start_row': 4096, 'row_count': 8}
    assert spec['trainer']['pad_to_multiple_of'] == 512


def test_effect_labels_are_nonpaged_lane_b_backends() -> None:
    assert effect_label('adamw_bnb_8bit', 1) == 'ONE_LOCAL_BNB_ADAMW_8BIT_OPTIMIZER_STEP'
    assert effect_label('adamw_torch_8bit', 2) == 'TWO_LOCAL_TORCHAO_ADAMW_8BIT_OPTIMIZER_STEPS'


def test_lane_b_spec_rejects_paged_optimizer(tmp_path: Path) -> None:
    value = json.loads(_lane_b_spec().read_text(encoding='utf-8'))
    value['trainer']['optimizer'] = 'paged_adamw_8bit'
    path = tmp_path / 'spec.json'
    path.write_text(json.dumps(value), encoding='utf-8')
    with pytest.raises(DevTrainingHold, match='paged'):
        load_and_validate_dev_spec(path)


def test_lane_b_spec_rejects_window_mismatch(tmp_path: Path) -> None:
    value = json.loads(_lane_b_spec().read_text(encoding='utf-8'))
    value['development_window']['row_count'] = 16
    path = tmp_path / 'spec.json'
    path.write_text(json.dumps(value), encoding='utf-8')
    with pytest.raises(DevTrainingHold, match='staged optimizer window'):
        load_and_validate_dev_spec(path)