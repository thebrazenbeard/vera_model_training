from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Sequence


class DurableProcessHold(RuntimeError):
    """Fail-closed refusal for the durable process harness."""


_PROGRESS = re.compile(r"(?<!\d)(\d+)\s*/\s*(\d+)(?!\d)")


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _write_json(path: Path, value: dict) -> None:
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _gpu_probe() -> dict:
    try:
        result = subprocess.run(
            [
                "nvidia-smi",
                "--query-gpu=utilization.gpu,memory.used,memory.total",
                "--format=csv,noheader,nounits",
            ],
            check=False,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except Exception as exc:
        return {"status": "UNAVAILABLE", "error": f"{type(exc).__name__}:{exc}"}

    if result.returncode != 0:
        return {
            "status": "ERROR",
            "exit_code": result.returncode,
            "stderr": result.stderr[-500:],
        }

    line = result.stdout.strip().splitlines()
    if not line:
        return {"status": "EMPTY"}
    parts = [part.strip() for part in line[0].split(",")]
    if len(parts) != 3:
        return {"status": "UNPARSEABLE", "raw": line[0]}
    try:
        return {
            "status": "OK",
            "utilization_percent": int(parts[0]),
            "memory_used_mib": int(parts[1]),
            "memory_total_mib": int(parts[2]),
        }
    except ValueError:
        return {"status": "UNPARSEABLE", "raw": line[0]}


def _latest_optimizer_step(
    stdout_path: Path,
    expected_optimizer_steps: int | None,
) -> int | None:
    if expected_optimizer_steps is None or not stdout_path.exists():
        return None
    try:
        text = stdout_path.read_bytes().decode("utf-8", errors="replace")
    except OSError:
        return None
    observed = [
        int(step)
        for step, total in _PROGRESS.findall(text)
        if int(total) == expected_optimizer_steps
        and 0 <= int(step) <= expected_optimizer_steps
    ]
    return max(observed) if observed else None


def _parse(argv: Sequence[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--log-dir", required=True, type=Path)
    parser.add_argument("--watch-seconds", type=float, default=30.0)
    parser.add_argument("--cwd", type=Path)
    parser.add_argument("--expected-optimizer-steps", type=int)
    parser.add_argument("--metadata-json", default="{}")
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args(argv)
    if args.command and args.command[0] == "--":
        args.command = args.command[1:]
    if not args.command:
        raise DurableProcessHold("child command is required")
    if args.watch_seconds <= 0:
        raise DurableProcessHold("watch seconds must be positive")
    if (
        args.expected_optimizer_steps is not None
        and args.expected_optimizer_steps <= 0
    ):
        raise DurableProcessHold("expected optimizer steps must be positive")
    try:
        metadata = json.loads(args.metadata_json)
    except json.JSONDecodeError as exc:
        raise DurableProcessHold("metadata json is invalid") from exc
    if not isinstance(metadata, dict):
        raise DurableProcessHold("metadata json must be an object")
    args.metadata = metadata
    return args


def run_durable_process(argv: Sequence[str] | None = None) -> int:
    args = _parse(argv)
    log_dir = args.log_dir
    if log_dir.exists():
        raise DurableProcessHold(f"log namespace already exists:{log_dir}")
    log_dir.mkdir(parents=True, exist_ok=False)

    cwd = args.cwd.resolve() if args.cwd is not None else Path.cwd().resolve()
    stdout_path = log_dir / "stdout.log"
    stderr_path = log_dir / "stderr.log"
    watchdog_path = log_dir / "watchdog.jsonl"
    launch_path = log_dir / "launch.json"
    final_path = log_dir / "final.json"

    started_wall = _utc_now()
    started_perf = time.perf_counter()

    with stdout_path.open("wb") as stdout_handle, stderr_path.open("wb") as stderr_handle:
        child = subprocess.Popen(
            list(args.command),
            cwd=str(cwd),
            stdout=stdout_handle,
            stderr=stderr_handle,
            env=os.environ.copy(),
        )
        _write_json(
            launch_path,
            {
                "schema": "DURABLE_PROCESS_LAUNCH_V2",
                "status": "STARTED",
                "started_at_utc": started_wall,
                "pid": child.pid,
                "cwd": str(cwd),
                "command": list(args.command),
                "metadata": args.metadata,
                "expected_optimizer_steps": args.expected_optimizer_steps,
                "stdout_path": str(stdout_path),
                "stderr_path": str(stderr_path),
                "watchdog_path": str(watchdog_path),
            },
        )

        with watchdog_path.open("a", encoding="utf-8", newline="\n") as watchdog:
            while True:
                returncode = child.poll()
                row = {
                    "schema": "DURABLE_PROCESS_WATCHDOG_V2",
                    "observed_at_utc": _utc_now(),
                    "pid": child.pid,
                    "returncode": returncode,
                    "latest_optimizer_step": _latest_optimizer_step(
                        stdout_path,
                        args.expected_optimizer_steps,
                    ),
                    "stdout_bytes": stdout_path.stat().st_size,
                    "stderr_bytes": stderr_path.stat().st_size,
                    "gpu": _gpu_probe(),
                }
                watchdog.write(json.dumps(row, sort_keys=True) + "\n")
                watchdog.flush()
                os.fsync(watchdog.fileno())
                if returncode is not None:
                    break
                time.sleep(args.watch_seconds)

    elapsed = time.perf_counter() - started_perf
    returncode = int(child.returncode)
    final = {
        "schema": "DURABLE_PROCESS_FINAL_V2",
        "status": "EXITED",
        "started_at_utc": started_wall,
        "ended_at_utc": _utc_now(),
        "elapsed_seconds": round(elapsed, 6),
        "pid": child.pid,
        "exit_code": returncode,
        "signal": -returncode if returncode < 0 else None,
        "latest_optimizer_step": _latest_optimizer_step(
            stdout_path,
            args.expected_optimizer_steps,
        ),
        "metadata": args.metadata,
        "stdout_bytes": stdout_path.stat().st_size,
        "stderr_bytes": stderr_path.stat().st_size,
        "stdout_path": str(stdout_path),
        "stderr_path": str(stderr_path),
        "watchdog_path": str(watchdog_path),
    }
    _write_json(final_path, final)
    return returncode


def main() -> int:
    return run_durable_process()


if __name__ == "__main__":
    raise SystemExit(main())
