import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "successor" / "experiments" / "V10R3R5_STAGE0_SUCCESSOR_PROTOCOL_20261006_V1.json"


def test_r5_records_r4_binding_label_typo_without_rewriting_r4_evidence():
    protocol = json.loads(PROTOCOL.read_text(encoding="utf-8-sig"))
    correction = protocol["predecessor_binding_documentary_correction"]
    assert correction["r4_binding_file_rewritten"] is False
    assert correction["incident_bytes_rewritten"] is False
    assert correction["incident_sha256"] == "96ea8a6dbe436f2b582b0fbf8ddcc5d36387b66233c75bd01417e827bb07e027"
    assert correction["observed_schema_label"] == "V103R3R4_STAGE0_EXECUTION_INCIDENT_BINDING_V1"
    assert correction["canonical_schema_label"] == "V10R3R4_STAGE0_EXECUTION_INCIDENT_BINDING_V1"
    assert correction["observed_normalization_path_label"].endswith(
        "V103R3R4_STAGE0_INCIDENT_20261006_V1.json"
    )
    assert correction["canonical_incident_path"].endswith(
        "V10R3R4_STAGE0_INCIDENT_20261006_V1.json"
    )
