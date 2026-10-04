from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

from successor.experiments.preflight_v10r3r2_host_resources import (
    read_live_metrics,
    validate_host_resources,
)
from successor.experiments.run_durable_process import (
    run_durable_process,
    validate_launch_metadata,
)


SPEC_REL = "successor/experiments/V10R3R2_CONTINUOUS20_DURABLE_EXECUTION_SPEC_20261004_V1.json"
PROTOCOL_REL = "successor/experiments/V10R3R2_DURABLE_CONTINUOUS20_PROTOCOL_20261004_V1.json"
HARNESS_REL = "successor/experiments/run_durable_process.py"
LAUNCHER_REL = "successor/experiments/launch_v10r3r2_durable.py"
HOST_GUARD_REL = "successor/experiments/preflight_v10r3r2_host_resources.py"
TRAIN_JSONL = Path(r"D:VERA.scratch10-qwen512-preflight-20261001-v1	rain.jsonl")
RUNTIME_PYTHON = Path(r"C:ProgramDataProRunmodel-envScriptspython.exe")
LOG_DIR = Path(r"D:VERAlogs	raining10r3r2-cont20-20261004-v1")
EXPECTED_OPTIMIZER_STEPS = 20


class R2LaunchHold(RuntimeError):
    """Fail-closed refusal for the V10R3R2 bound launcher."""


def _git(repo_root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo_root), *args],
        check=False,
        capture_output=True,
        text=True,
        timeout=20,
    )
    if result.returncode != 0:
        raise R2LaunchHold(
            f"git {' '.join(args)} failed:{result.returncode}:{result.stderr[-500:]}"
        )
    return result.stdout.strip()


def _committed_bytes(repo_root: Path, relative: str) -> bytes:
    result = subprocess.run(
        ["git", "-C", str(repo_root), "show", f"HEAD:{relative}"],
        check=False,
        capture_output=True,
        timeout=20,
    )
    if result.returncode != 0:
        raise R2LaunchHold(
            f"unable to read committed subject:{relative}:{result.returncode}"
        )
    if bytes((13, 10)) in result.stdout:
        raise R2LaunchHold(f"committed subject is not LF-normalized:{relative}")
    return result.stdout


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _load_committed_json(repo_root: Path, relative: str) -> dict:
    value = json.loads(_committed_bytes(repo_root, relative).decode("utf-8"))
    if not isinstance(value, dict):
        raise R2LaunchHold(f"committed JSON object required:{relative}")
    return value


def validate_bound_metadata(metadata: dict, expected: dict) -> dict:
    validate_launch_metadata(metadata)
    validate_launch_metadata(expected)
    for key in (
        "repo_head",
        "spec_path",
        "spec_sha256",
        "runtime_binding_sha256",
    ):
        if metadata.get(key) != expected.get(key):
            raise R2LaunchHold(f"bound metadata mismatch:{key}")
    return dict(metadata)


def build_bound_metadata(repo_root: Path) -> dict:
    repo_root = repo_root.resolve()
    head = _git(repo_root, "rev-parse", "HEAD")
    if _git(repo_root, "diff", "--name-only"):
        raise R2LaunchHold("tracked working tree is dirty")
    if _git(repo_root, "diff", "--cached", "--name-only"):
        raise R2LaunchHold("index is dirty")

    protocol = _load_committed_json(repo_root, PROTOCOL_REL)
    spec_bytes = _committed_bytes(repo_root, SPEC_REL)
    harness_bytes = _committed_bytes(repo_root, HARNESS_REL)
    launcher_bytes = _committed_bytes(repo_root, LAUNCHER_REL)
    host_guard_bytes = _committed_bytes(repo_root, HOST_GUARD_REL)
    spec = json.loads(spec_bytes.decode("utf-8"))

    source = protocol.get("source_subject")
    if not isinstance(source, dict):
        raise R2LaunchHold("protocol source_subject missing")

    expected_hashes = {
        "execution_spec_committed_sha256": _sha256(spec_bytes),
        "durable_harness_committed_sha256": _sha256(harness_bytes),
        "durable_launcher_committed_sha256": _sha256(launcher_bytes),
        "host_resource_guard_committed_sha256": _sha256(host_guard_bytes),
    }
    for field, actual in expected_hashes.items():
        if source.get(field) != actual:
            raise R2LaunchHold(f"protocol source binding mismatch:{field}")

    if source.get("execution_spec_path") != SPEC_REL:
        raise R2LaunchHold("protocol execution spec path mismatch")
    if source.get("durable_harness_path") != HARNESS_REL:
        raise R2LaunchHold("protocol durable harness path mismatch")
    if source.get("durable_launcher_path") != LAUNCHER_REL:
        raise R2LaunchHold("protocol durable launcher path mismatch")
    if source.get("host_resource_guard_path") != HOST_GUARD_REL:
        raise R2LaunchHold("protocol host guard path mismatch")

    runtime_binding = (
        spec.get("source_subject", {}).get("runtime_binding_sha256")
        if isinstance(spec.get("source_subject"), dict)
        else None
    )
    metadata = {
        "repo_head": head,
        "spec_path": SPEC_REL,
        "spec_sha256": _sha256(spec_bytes),
        "runtime_binding_sha256": runtime_binding,
    }
    return validate_launch_metadata(metadata)


def verify_r2_subject(repo_root: Path) -> dict:
    metadata = build_bound_metadata(repo_root)
    protocol = _load_committed_json(repo_root, PROTOCOL_REL)
    host_gate = protocol.get("execution", {}).get("host_resource_gate")
    if not isinstance(host_gate, dict) or host_gate.get("required") is not True:
        raise R2LaunchHold("host resource gate is not required")

    output_namespace = _load_committed_json(repo_root, SPEC_REL)["output"]["namespace"]
    output_path = Path(output_namespace)
    if output_path.exists():
        raise R2LaunchHold(f"output namespace already exists:{output_path}")
    if LOG_DIR.exists():
        raise R2LaunchHold(f"log namespace already exists:{LOG_DIR}")

    return {
        "schema": "V10R3R2_BOUND_LAUNCH_VERIFICATION_V1",
        "status": "PASS",
        "metadata": metadata,
        "output_namespace": str(output_path),
        "log_namespace": str(LOG_DIR),
        "host_resource_gate": host_gate,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path)
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args()

    repo_root = (
        args.repo_root.resolve()
        if args.repo_root is not None
        else Path(__file__).resolve().parents[2]
    )
    verification = verify_r2_subject(repo_root)
    if args.verify_only:
        print(json.dumps(verification, indent=2, sort_keys=True))
        return 0

    host_gate = verification["host_resource_gate"]
    metrics = read_live_metrics()
    validate_host_resources(
        metrics,
        min_available_physical_gib=float(
            host_gate["min_available_physical_gib"]
        ),
        min_commit_headroom_gib=float(
            host_gate["min_commit_headroom_gib"]
        ),
    )

    child = [
        str(RUNTIME_PYTHON),
        "successor/experiments/train_v10r2_dev.py",
        "--repo-root",
        str(repo_root),
        "--train-jsonl",
        str(TRAIN_JSONL),
        "--spec",
        SPEC_REL,
    ]
    metadata = verification["metadata"]
    return run_durable_process(
        [
            "--log-dir",
            str(LOG_DIR),
            "--watch-seconds",
            "30",
            "--expected-optimizer-steps",
            str(EXPECTED_OPTIMIZER_STEPS),
            "--metadata-json",
            json.dumps(metadata, sort_keys=True),
            "--cwd",
            str(repo_root),
            "--",
            *child,
        ]
    )


if __name__ == "__main__":
    raise SystemExit(main())
