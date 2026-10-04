from __future__ import annotations

import pytest

from successor.experiments.launch_v10r3r2_durable import (
    R2LaunchHold,
    validate_bound_metadata,
)


def _expected() -> dict:
    return {
        "repo_head": "a" * 40,
        "spec_path": "successor/experiments/V10R3R2_CONTINUOUS20_DURABLE_EXECUTION_SPEC_20261004_V1.json",
        "spec_sha256": "b" * 64,
        "runtime_binding_sha256": "c" * 64,
    }


def test_bound_metadata_accepts_exact_subject() -> None:
    expected = _expected()
    assert validate_bound_metadata(dict(expected), expected) == expected


@pytest.mark.parametrize(
    ("key", "wrong_value"),
    [
        ("repo_head", "d" * 40),
        ("spec_path", "successor/experiments/V10R3R2_WRONG_SPEC.json"),
        ("spec_sha256", "d" * 64),
        ("runtime_binding_sha256", "e" * 64),
    ],
)
def test_bound_metadata_rejects_well_formed_wrong_subject(
    key: str,
    wrong_value: str,
) -> None:
    expected = _expected()
    candidate = dict(expected)
    candidate[key] = wrong_value

    with pytest.raises(R2LaunchHold, match=key):
        validate_bound_metadata(candidate, expected)


def test_r2_launcher_uses_exact_windows_paths() -> None:
    from successor.experiments.launch_v10r3r2_durable import (
        LOG_DIR,
        RUNTIME_PYTHON,
        TRAIN_JSONL,
    )

    assert TRAIN_JSONL.as_posix() == (
        "D:/VERA/.scratch/v10-qwen512-preflight-20261001-v1/train.jsonl"
    )
    assert RUNTIME_PYTHON.as_posix() == (
        "C:/ProgramData/ProRun/model-env/Scripts/python.exe"
    )
    assert LOG_DIR.as_posix() == (
        "D:/VERA/logs/training/v10r3r2-cont20-20261004-v1"
    )
