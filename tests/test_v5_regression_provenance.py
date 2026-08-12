import json

import audit_gate_v5


def test_exported_regression_suggestions_are_labeled_unverified(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    spec = {"identity": "SB", "function": "Supabase Platform Specialist", "target": "practitioner", "rounds": 1}
    qual = {
        "training_package_ready": False,
        "condition": "repair",
        "capability_proxy_evidence": [],
    }

    audit_gate_v5.write_outputs(
        spec,
        "# capsule",
        qual,
        ["same-model proposed regression"],
        [],
        [],
        [],
        [],
    )

    payload = json.loads((tmp_path / "out" / "REGRESSION_SET.json").read_text())
    assert payload["cases"] == [{
        "case": "same-model proposed regression",
        "status": "PROPOSED_UNVERIFIED",
        "provenance": "SAME_LOCAL_MODEL_EXAMINER",
    }]
