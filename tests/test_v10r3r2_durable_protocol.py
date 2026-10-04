from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXP = ROOT / "successor" / "experiments"
PROTOCOL = EXP / "V10R3R2_DURABLE_CONTINUOUS20_PROTOCOL_20261004_V1.json"
SPEC_REL = "successor/experiments/V10R3R2_CONTINUOUS20_DURABLE_EXECUTION_SPEC_20261004_V1.json"
HARNESS_REL = "successor/experiments/run_durable_process.py"
LAUNCHER_REL = "successor/experiments/launch_v10r3r2_durable.py"
HOST_GUARD_REL = "successor/experiments/preflight_v10r3r2_host_resources.py"
INCIDENT = EXP / "receipts" / "V10R3R1_EXECUTION_INCIDENT_20261004_V1.json"


def _committed(relative: str) -> bytes:
    return subprocess.check_output(
        ["git", "-C", str(ROOT), "show", f"HEAD:{relative}"]
    )


def _committed_sha(relative: str) -> str:
    return hashlib.sha256(_committed(relative)).hexdigest()


def _blob(relative: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(ROOT), "rev-parse", f"HEAD:{relative}"],
        text=True,
    ).strip()


def test_r2_protocol_binds_exact_recipe_and_launch_subjects() -> None:
    protocol = json.loads(PROTOCOL.read_text(encoding="utf-8"))
    source = protocol["source_subject"]

    assert source["recipe_source_head"] == (
        "4197205466f3213c4d3e3c0e3e7557e4569bc276"
    )
    assert source["metadata_binding_source_head"] == (
        "d8b7cbf1f87855713543a5a85de00427314287dc"
    )

    bindings = (
        (
            SPEC_REL,
            "execution_spec_committed_sha256",
            "execution_spec_git_blob",
        ),
        (
            HARNESS_REL,
            "durable_harness_committed_sha256",
            "durable_harness_git_blob",
        ),
        (
            LAUNCHER_REL,
            "durable_launcher_committed_sha256",
            "durable_launcher_git_blob",
        ),
        (
            HOST_GUARD_REL,
            "host_resource_guard_committed_sha256",
            "host_resource_guard_git_blob",
        ),
    )
    for relative, sha_field, blob_field in bindings:
        assert source[sha_field] == _committed_sha(relative)
        assert source[blob_field] == _blob(relative)

    assert source["execution_spec_path"] == SPEC_REL
    assert source["durable_harness_path"] == HARNESS_REL
    assert source["durable_launcher_path"] == LAUNCHER_REL
    assert source["host_resource_guard_path"] == HOST_GUARD_REL
    assert source["hash_semantics"] == (
        "UTF8_TEXT_LF_NORMALIZED_COMMITTED_CONTENT"
    )


def test_r2_protocol_binds_r1_incident_and_forbids_retry() -> None:
    protocol = json.loads(PROTOCOL.read_text(encoding="utf-8"))
    incident_bytes = INCIDENT.read_bytes().replace(b"\r\n", b"\n")

    assert protocol["predecessor_incident"]["lf_normalized_sha256"] == hashlib.sha256(
        incident_bytes
    ).hexdigest()
    assert protocol["predecessor_incident"]["r1_attempt_limit_exhausted"] is True
    assert protocol["predecessor_incident"]["r1_retry_prohibited"] is True
    assert protocol["execution"]["attempt_limit"] == 1
    assert protocol["execution"]["automatic_retry"] is False
    assert protocol["execution"]["panel_use"] == "PROHIBITED"

    observability = protocol["observability"]
    assert observability["watchdog_latest_optimizer_step_required"] is True
    assert observability["watchdog_progress_sources"] == [
        "stdout.log",
        "stderr.log",
    ]
    assert observability["launch_metadata_required_fields"] == [
        "repo_head",
        "spec_path",
        "spec_sha256",
        "runtime_binding_sha256",
    ]
    assert observability["launch_metadata_format_validation_required"] is True
    assert observability["launch_metadata_exact_subject_binding_required"] is True

    assert protocol["execution"]["host_resource_gate"] == {
        "required": True,
        "min_available_physical_gib": 8.0,
        "min_commit_headroom_gib": 8.0,
        "gpu_memory_used_mib_required": 0,
        "competing_trainer_count_required": 0,
    }
