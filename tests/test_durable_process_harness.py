from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from successor.experiments.run_durable_process import DurableProcessHold, run_durable_process


def test_durable_process_persists_subject_step_logs_and_exit(tmp_path: Path) -> None:
    log_dir = tmp_path / "logs"
    metadata = {
        "repo_head": "a" * 40,
        "spec_path": "successor/experiments/example.json",
        "spec_sha256": "b" * 64,
        "runtime_binding_sha256": "c" * 64,
    }
    code = (
        "import sys,time;"
        "print('  5%|x| 1/20', flush=True);"
        "print('ERR_MARK', file=sys.stderr, flush=True);"
        "time.sleep(0.08);"
        "print(' 10%|x| 2/20', flush=True);"
        "time.sleep(0.08);"
        "sys.exit(7)"
    )

    rc = run_durable_process(
        [
            "--log-dir", str(log_dir),
            "--watch-seconds", "0.04",
            "--expected-optimizer-steps", "20",
            "--metadata-json", json.dumps(metadata),
            "--cwd", str(tmp_path),
            "--", sys.executable, "-c", code,
        ]
    )

    assert rc == 7
    stdout = (log_dir / "stdout.log").read_text(encoding="utf-8")
    assert "1/20" in stdout
    assert "2/20" in stdout
    assert (log_dir / "stderr.log").read_text(encoding="utf-8").strip() == "ERR_MARK"

    launch = json.loads((log_dir / "launch.json").read_text(encoding="utf-8"))
    final = json.loads((log_dir / "final.json").read_text(encoding="utf-8"))
    watchdog = [
        json.loads(line)
        for line in (log_dir / "watchdog.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    assert launch["status"] == "STARTED"
    assert launch["pid"] > 0
    assert launch["metadata"] == metadata
    assert launch["expected_optimizer_steps"] == 20
    assert final["status"] == "EXITED"
    assert final["exit_code"] == 7
    assert final["signal"] is None
    assert final["latest_optimizer_step"] == 2
    assert final["stdout_bytes"] > 0
    assert final["stderr_bytes"] > 0
    assert watchdog
    assert all(row["pid"] == launch["pid"] for row in watchdog)
    assert max(row["latest_optimizer_step"] or 0 for row in watchdog) == 2


def test_durable_process_refuses_existing_log_namespace(tmp_path: Path) -> None:
    log_dir = tmp_path / "logs"
    log_dir.mkdir()

    with pytest.raises(DurableProcessHold, match="log namespace already exists"):
        run_durable_process(
            [
                "--log-dir", str(log_dir),
                "--metadata-json", json.dumps({
                    "repo_head": "a" * 40,
                    "spec_path": "successor/experiments/example.json",
                    "spec_sha256": "b" * 64,
                    "runtime_binding_sha256": "c" * 64,
                }),
                "--", sys.executable, "-c", "print('x')",
            ]
        )


def test_durable_process_rejects_invalid_metadata_json(tmp_path: Path) -> None:
    with pytest.raises(DurableProcessHold, match="metadata json"):
        run_durable_process(
            [
                "--log-dir", str(tmp_path / "logs"),
                "--metadata-json", "[]",
                "--", sys.executable, "-c", "print('x')",
            ]
        )


def test_durable_process_reads_optimizer_progress_from_stderr(tmp_path: Path) -> None:
    log_dir = tmp_path / "logs"
    metadata = {
        "repo_head": "a" * 40,
        "spec_path": "successor/experiments/example.json",
        "spec_sha256": "b" * 64,
        "runtime_binding_sha256": "c" * 64,
    }
    code = (
        "import sys,time;"
        "print(' 15%|x| 3/20', file=sys.stderr, flush=True);"
        "time.sleep(0.08);"
        "print(' 20%|x| 4/20', file=sys.stderr, flush=True);"
    )

    rc = run_durable_process(
        [
            "--log-dir", str(log_dir),
            "--watch-seconds", "0.04",
            "--expected-optimizer-steps", "20",
            "--metadata-json", json.dumps(metadata),
            "--", sys.executable, "-c", code,
        ]
    )

    assert rc == 0
    final = json.loads((log_dir / "final.json").read_text(encoding="utf-8"))
    assert final["latest_optimizer_step"] == 4


def test_durable_process_requires_bound_launch_metadata(tmp_path: Path) -> None:
    incomplete = {
        "repo_head": "a" * 40,
        "spec_path": "successor/experiments/example.json",
    }

    with pytest.raises(DurableProcessHold, match="required metadata"):
        run_durable_process(
            [
                "--log-dir", str(tmp_path / "logs"),
                "--metadata-json", json.dumps(incomplete),
                "--", sys.executable, "-c", "print('x')",
            ]
        )


@pytest.mark.parametrize(
    "missing_key",
    ["repo_head", "spec_path", "spec_sha256", "runtime_binding_sha256"],
)
def test_durable_process_rejects_each_missing_metadata_key(
    tmp_path: Path,
    missing_key: str,
) -> None:
    metadata = {
        "repo_head": "a" * 40,
        "spec_path": "successor/experiments/example.json",
        "spec_sha256": "b" * 64,
        "runtime_binding_sha256": "c" * 64,
    }
    metadata.pop(missing_key)

    with pytest.raises(DurableProcessHold, match="required metadata"):
        run_durable_process(
            [
                "--log-dir", str(tmp_path / f"logs-{missing_key}"),
                "--metadata-json", json.dumps(metadata),
                "--", sys.executable, "-c", "print('x')",
            ]
        )


@pytest.mark.parametrize(
    ("key", "value", "message"),
    [
        ("repo_head", "f" * 39, "repo_head"),
        ("repo_head", "g" * 40, "repo_head"),
        ("spec_sha256", "a" * 63, "spec_sha256"),
        ("spec_sha256", "g" * 64, "spec_sha256"),
        ("runtime_binding_sha256", "a" * 63, "runtime_binding_sha256"),
        ("runtime_binding_sha256", "g" * 64, "runtime_binding_sha256"),
        ("spec_path", "../outside.json", "spec_path"),
        ("spec_path", r"successor\experiments\example.json", "spec_path"),
    ],
)
def test_durable_process_rejects_malformed_metadata(
    tmp_path: Path,
    key: str,
    value: str,
    message: str,
) -> None:
    metadata = {
        "repo_head": "a" * 40,
        "spec_path": "successor/experiments/example.json",
        "spec_sha256": "b" * 64,
        "runtime_binding_sha256": "c" * 64,
    }
    metadata[key] = value

    with pytest.raises(DurableProcessHold, match=message):
        run_durable_process(
            [
                "--log-dir", str(tmp_path / f"logs-{key}"),
                "--metadata-json", json.dumps(metadata),
                "--", sys.executable, "-c", "print('x')",
            ]
        )
