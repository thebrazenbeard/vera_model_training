from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from successor.experiments.run_durable_process import DurableProcessHold, run_durable_process


def test_durable_process_persists_stdout_stderr_watchdog_and_exit(tmp_path: Path) -> None:
    log_dir = tmp_path / "logs"
    code = (
        "import sys,time;"
        "print('OUT_MARK', flush=True);"
        "print('ERR_MARK', file=sys.stderr, flush=True);"
        "time.sleep(0.12);"
        "sys.exit(7)"
    )

    rc = run_durable_process(
        [
            "--log-dir",
            str(log_dir),
            "--watch-seconds",
            "0.05",
            "--cwd",
            str(tmp_path),
            "--",
            sys.executable,
            "-c",
            code,
        ]
    )

    assert rc == 7
    assert (log_dir / "stdout.log").read_text(encoding="utf-8").strip() == "OUT_MARK"
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
    assert final["status"] == "EXITED"
    assert final["exit_code"] == 7
    assert final["stdout_bytes"] > 0
    assert final["stderr_bytes"] > 0
    assert watchdog
    assert all(row["pid"] == launch["pid"] for row in watchdog)


def test_durable_process_refuses_existing_log_namespace(tmp_path: Path) -> None:
    log_dir = tmp_path / "logs"
    log_dir.mkdir()

    with pytest.raises(DurableProcessHold, match="log namespace already exists"):
        run_durable_process(
            [
                "--log-dir",
                str(log_dir),
                "--",
                sys.executable,
                "-c",
                "print('x')",
            ]
        )
