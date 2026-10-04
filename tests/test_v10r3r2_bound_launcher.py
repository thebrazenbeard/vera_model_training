from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from successor.experiments import run_v10r3r2_durable as r2


def _lf_sha(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _subject(tmp_path: Path) -> tuple[Path, Path]:
    repo = tmp_path / "repo"
    exp = repo / "successor" / "experiments"
    exp.mkdir(parents=True)
    train = tmp_path / "train.jsonl"
    train.write_text('{"prompt":"p","response":"r"}\n', encoding="utf-8")
    train_sha = hashlib.sha256(train.read_bytes()).hexdigest()

    (repo / r2.TRAINER_REL).write_text(
        "raise SystemExit(0)\n",
        encoding="utf-8",
    )
    spec_path = repo / r2.SPEC_REL
    spec = {
        "source_subject": {
            "runtime_binding_sha256": "d" * 64,
            "train_sha256": train_sha,
        },
        "trainer": {"max_optimizer_steps": 20},
        "output": {
            "namespace": str(tmp_path / "candidate"),
        },
    }
    spec_path.write_text(
        json.dumps(spec, indent=2) + "\n",
        encoding="utf-8",
    )

    protocol_path = repo / r2.PROTOCOL_REL
    protocol = {
        "source_subject": {
            "execution_spec_path": r2.SPEC_REL,
            "execution_spec_committed_sha256": _lf_sha(spec_path),
        },
        "execution": {
            "attempt_limit": 1,
            "automatic_retry": False,
            "panel_use": "PROHIBITED",
            "host_resource_gate": {
                "required": True,
                "min_available_physical_gib": 8.0,
                "min_commit_headroom_gib": 8.0,
            },
        },
        "observability": {
            "log_namespace": str(tmp_path / "logs"),
            "watch_seconds": 30.0,
        },
    }
    protocol_path.write_text(
        json.dumps(protocol, indent=2) + "\n",
        encoding="utf-8",
    )
    return repo, train


def _safe_metrics() -> dict:
    return {
        "available_physical_gib": 12.0,
        "commit_headroom_gib": 12.0,
        "committed_percent": 50.0,
        "gpu_memory_used_mib": 0,
        "gpu_memory_total_mib": 4096,
        "gpu_utilization_percent": 0,
        "competing_trainers": [],
    }


def _patch_git(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(r2, "_git_head", lambda repo: "a" * 40)
    monkeypatch.setattr(
        r2,
        "_require_clean_tracked_worktree",
        lambda repo: None,
    )


def test_r2_launcher_derives_subject_metadata_from_actual_files(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repo, train = _subject(tmp_path)
    _patch_git(monkeypatch)

    launch = r2.derive_r2_launch(
        repo,
        train,
        python_executable="python.exe",
        live_metrics=_safe_metrics(),
    )

    metadata = launch["metadata"]
    assert metadata["repo_head"] == "a" * 40
    assert metadata["spec_path"] == r2.SPEC_REL
    assert metadata["spec_sha256"] == _lf_sha(repo / r2.SPEC_REL)
    assert metadata["runtime_binding_sha256"] == "d" * 64
    assert metadata["train_sha256"] == hashlib.sha256(
        train.read_bytes()
    ).hexdigest()
    assert launch["child_command"][-2:] == ["--spec", r2.SPEC_REL]
    assert launch["expected_optimizer_steps"] == 20


def test_r2_launcher_rejects_protocol_spec_hash_mismatch(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repo, train = _subject(tmp_path)
    _patch_git(monkeypatch)
    protocol_path = repo / r2.PROTOCOL_REL
    protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
    protocol["source_subject"]["execution_spec_committed_sha256"] = "f" * 64
    protocol_path.write_text(json.dumps(protocol), encoding="utf-8")

    with pytest.raises(r2.R2LaunchHold, match="protocol/spec SHA-256"):
        r2.derive_r2_launch(
            repo,
            train,
            python_executable="python.exe",
            live_metrics=_safe_metrics(),
        )


def test_r2_launcher_rejects_wrong_training_jsonl(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repo, train = _subject(tmp_path)
    _patch_git(monkeypatch)
    train.write_text("changed\n", encoding="utf-8")

    with pytest.raises(r2.R2LaunchHold, match="training JSONL SHA-256"):
        r2.derive_r2_launch(
            repo,
            train,
            python_executable="python.exe",
            live_metrics=_safe_metrics(),
        )


@pytest.mark.parametrize(
    ("field", "value", "reason"),
    [
        ("attempt_limit", 2, "attempt limit"),
        ("automatic_retry", True, "automatic retry"),
        ("panel_use", "ALLOWED", "panel-use"),
    ],
)
def test_r2_launcher_rejects_governance_drift(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    field: str,
    value: object,
    reason: str,
) -> None:
    repo, train = _subject(tmp_path)
    _patch_git(monkeypatch)
    protocol_path = repo / r2.PROTOCOL_REL
    protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
    protocol["execution"][field] = value
    protocol_path.write_text(json.dumps(protocol), encoding="utf-8")

    with pytest.raises(r2.R2LaunchHold, match=reason):
        r2.derive_r2_launch(
            repo,
            train,
            python_executable="python.exe",
            live_metrics=_safe_metrics(),
        )


def test_r2_launcher_rejects_existing_output_or_log_namespace(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repo, train = _subject(tmp_path)
    _patch_git(monkeypatch)
    candidate = tmp_path / "candidate"
    candidate.mkdir()

    with pytest.raises(r2.R2LaunchHold, match="output namespace"):
        r2.derive_r2_launch(
            repo,
            train,
            python_executable="python.exe",
            live_metrics=_safe_metrics(),
        )

    candidate.rmdir()
    (tmp_path / "logs").mkdir()
    with pytest.raises(r2.R2LaunchHold, match="log namespace"):
        r2.derive_r2_launch(
            repo,
            train,
            python_executable="python.exe",
            live_metrics=_safe_metrics(),
        )


def test_r2_launcher_propagates_host_resource_hold(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repo, train = _subject(tmp_path)
    _patch_git(monkeypatch)
    metrics = _safe_metrics()
    metrics["gpu_memory_used_mib"] = 128

    with pytest.raises(Exception, match="gpu memory is not free"):
        r2.derive_r2_launch(
            repo,
            train,
            python_executable="python.exe",
            live_metrics=metrics,
        )
