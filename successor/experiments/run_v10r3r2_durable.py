from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

from successor.experiments.preflight_v10r3r2_host_resources import (
    read_live_metrics,
    validate_host_resources,
)
from successor.experiments.run_durable_process import (
    DurableProcessHold,
    run_durable_process,
)


SPEC_REL = (
    "successor/experiments/"
    "V10R3R2_CONTINUOUS20_DURABLE_EXECUTION_SPEC_20261004_V1.json"
)
PROTOCOL_REL = (
    "successor/experiments/"
    "V10R3R2_DURABLE_CONTINUOUS20_PROTOCOL_20261004_V1.json"
)
TRAINER_REL = "successor/experiments/train_v10r2_dev.py"
_SHA40 = re.compile(r"^[0-9a-f]{40}$")
_SHA64 = re.compile(r"^[0-9a-f]{64}$")


class R2LaunchHold(RuntimeError):
    """Fail-closed refusal before the R2 durable child is created."""


def _lf_sha256(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def _file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _git(repo_root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo_root), *args],
        capture_output=True,
        text=True,
        check=False,
        timeout=15,
    )
    if result.returncode != 0:
        raise R2LaunchHold(
            "git command failed:"
            + " ".join(args)
            + ":"
            + result.stderr[-300:]
        )
    return result.stdout.strip()


def _git_head(repo_root: Path) -> str:
    head = _git(repo_root, "rev-parse", "HEAD")
    if not _SHA40.fullmatch(head):
        raise R2LaunchHold("git HEAD is not a 40-hex commit")
    return head


def _require_clean_tracked_worktree(repo_root: Path) -> None:
    unstaged = subprocess.run(
        ["git", "-C", str(repo_root), "diff", "--quiet", "HEAD", "--"],
        check=False,
        timeout=15,
    )
    staged = subprocess.run(
        ["git", "-C", str(repo_root), "diff", "--cached", "--quiet", "HEAD", "--"],
        check=False,
        timeout=15,
    )
    if unstaged.returncode != 0 or staged.returncode != 0:
        raise R2LaunchHold("tracked worktree is not clean at launch")


def _load_json(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise R2LaunchHold(f"{label} is unreadable or invalid") from exc
    if not isinstance(value, dict):
        raise R2LaunchHold(f"{label} must be a JSON object")
    return value


def derive_r2_launch(
    repo_root: Path,
    train_jsonl: Path,
    *,
    python_executable: str,
    live_metrics: dict[str, Any],
) -> dict[str, Any]:
    repo_root = repo_root.resolve()
    train_jsonl = train_jsonl.resolve()
    spec_path = repo_root / SPEC_REL
    protocol_path = repo_root / PROTOCOL_REL
    trainer_path = repo_root / TRAINER_REL

    if not spec_path.is_file():
        raise R2LaunchHold("frozen R2 spec is missing")
    if not protocol_path.is_file():
        raise R2LaunchHold("frozen R2 protocol is missing")
    if not trainer_path.is_file():
        raise R2LaunchHold("R2 trainer entrypoint is missing")
    if not train_jsonl.is_file():
        raise R2LaunchHold("training JSONL is missing")

    _require_clean_tracked_worktree(repo_root)
    repo_head = _git_head(repo_root)
    spec = _load_json(spec_path, "R2 spec")
    protocol = _load_json(protocol_path, "R2 protocol")

    subject = protocol.get("source_subject")
    if not isinstance(subject, dict):
        raise R2LaunchHold("protocol source_subject missing")
    if subject.get("execution_spec_path") != SPEC_REL:
        raise R2LaunchHold("protocol does not bind the frozen R2 spec path")

    spec_sha = _lf_sha256(spec_path)
    claimed_spec_sha = subject.get("execution_spec_committed_sha256")
    if not isinstance(claimed_spec_sha, str) or not _SHA64.fullmatch(
        claimed_spec_sha
    ):
        raise R2LaunchHold("protocol spec SHA-256 is invalid")
    if spec_sha != claimed_spec_sha:
        raise R2LaunchHold("protocol/spec SHA-256 binding mismatch")

    spec_source = spec.get("source_subject")
    if not isinstance(spec_source, dict):
        raise R2LaunchHold("spec source_subject missing")
    runtime_sha = spec_source.get("runtime_binding_sha256")
    train_sha = spec_source.get("train_sha256")
    if not isinstance(runtime_sha, str) or not _SHA64.fullmatch(runtime_sha):
        raise R2LaunchHold("spec runtime binding SHA-256 is invalid")
    if not isinstance(train_sha, str) or not _SHA64.fullmatch(train_sha):
        raise R2LaunchHold("spec train SHA-256 is invalid")
    if _file_sha256(train_jsonl) != train_sha:
        raise R2LaunchHold("training JSONL SHA-256 does not match frozen spec")

    execution = protocol.get("execution")
    observability = protocol.get("observability")
    if not isinstance(execution, dict) or not isinstance(observability, dict):
        raise R2LaunchHold("R2 execution/observability policy missing")
    if execution.get("attempt_limit") != 1:
        raise R2LaunchHold("R2 attempt limit drift")
    if execution.get("automatic_retry") is not False:
        raise R2LaunchHold("R2 automatic retry must remain false")
    if execution.get("panel_use") != "PROHIBITED":
        raise R2LaunchHold("R2 panel-use prohibition drift")

    gate = execution.get("host_resource_gate")
    if not isinstance(gate, dict) or gate.get("required") is not True:
        raise R2LaunchHold("R2 host resource gate missing")
    preflight = validate_host_resources(
        live_metrics,
        min_available_physical_gib=float(
            gate["min_available_physical_gib"]
        ),
        min_commit_headroom_gib=float(gate["min_commit_headroom_gib"]),
    )

    output = spec.get("output")
    if not isinstance(output, dict):
        raise R2LaunchHold("R2 output policy missing")
    output_namespace = Path(str(output.get("namespace", "")))
    if output_namespace.exists():
        raise R2LaunchHold("R2 output namespace already exists")

    log_dir = Path(str(observability.get("log_namespace", "")))
    if not log_dir.is_absolute():
        raise R2LaunchHold("R2 log namespace must be absolute")
    if log_dir.exists():
        raise R2LaunchHold("R2 log namespace already exists")

    trainer = spec.get("trainer")
    if not isinstance(trainer, dict):
        raise R2LaunchHold("R2 trainer policy missing")
    expected_steps = trainer.get("max_optimizer_steps")
    if expected_steps != 20:
        raise R2LaunchHold("R2 optimizer-step count drift")

    metadata = {
        "repo_head": repo_head,
        "spec_path": SPEC_REL,
        "spec_sha256": spec_sha,
        "runtime_binding_sha256": runtime_sha,
        "train_sha256": train_sha,
        "protocol_path": PROTOCOL_REL,
        "protocol_sha256": _lf_sha256(protocol_path),
        "preflight": preflight,
    }
    child_command = [
        python_executable,
        str(trainer_path),
        "--repo-root",
        str(repo_root),
        "--train-jsonl",
        str(train_jsonl),
        "--spec",
        SPEC_REL,
    ]
    return {
        "repo_root": repo_root,
        "log_dir": log_dir,
        "watch_seconds": float(observability["watch_seconds"]),
        "expected_optimizer_steps": expected_steps,
        "metadata": metadata,
        "child_command": child_command,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--train-jsonl", type=Path, required=True)
    args = parser.parse_args()

    try:
        launch = derive_r2_launch(
            args.repo_root,
            args.train_jsonl,
            python_executable=sys.executable,
            live_metrics=read_live_metrics(),
        )
        return run_durable_process(
            [
                "--log-dir",
                str(launch["log_dir"]),
                "--watch-seconds",
                str(launch["watch_seconds"]),
                "--expected-optimizer-steps",
                str(launch["expected_optimizer_steps"]),
                "--metadata-json",
                json.dumps(launch["metadata"], sort_keys=True),
                "--cwd",
                str(launch["repo_root"]),
                "--",
                *launch["child_command"],
            ]
        )
    except (R2LaunchHold, DurableProcessHold) as exc:
        print(f"HOLD:{exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
