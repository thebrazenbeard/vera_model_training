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
INCIDENT = EXP / "receipts" / "V10R3R1_EXECUTION_INCIDENT_20261004_V1.json"


def _committed_sha(relative: str) -> str:
    payload = subprocess.check_output(["git", "-C", str(ROOT), "show", f"HEAD:{relative}"])
    return hashlib.sha256(payload).hexdigest()


def test_r2_protocol_binds_exact_recipe_subject_and_harness() -> None:
    protocol = json.loads(PROTOCOL.read_text(encoding="utf-8"))

    assert protocol["source_subject"]["recipe_source_head"] == (
        "e282c2b2de2b93e4787a4647acb1c8fc8d5790f7"
    )
    assert protocol["source_subject"]["execution_spec_committed_sha256"] == _committed_sha(
        SPEC_REL
    )
    assert protocol["source_subject"]["durable_harness_committed_sha256"] == _committed_sha(
        HARNESS_REL
    )
    assert protocol["source_subject"]["hash_semantics"] == (
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
