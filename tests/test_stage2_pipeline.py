import importlib
import importlib.util


def test_stage2_pipeline_passes_only_when_manifest_eval_and_contamination_all_pass():
    spec = importlib.util.find_spec("training.stage2_pipeline")
    assert spec is not None, "Stage-2 pipeline module is missing"
    s2 = importlib.import_module("training.stage2_pipeline")
    packet = s2.build_stage2_gate_packet(
        baseline_manifest={"status": "PASS", "manifest_sha256": "a" * 64},
        eval_contract={"status": "PASS", "reasons": []},
        contamination_report={"status": "PASS", "reasons": []},
    )
    assert packet["status"] == "PASS"
    assert packet["baseline_manifest_sha256"] == "a" * 64

    held = s2.build_stage2_gate_packet(
        baseline_manifest={"status": "PASS", "manifest_sha256": "a" * 64},
        eval_contract={"status": "HOLD", "reasons": ["missing_eval_banks"]},
        contamination_report={"status": "PASS", "reasons": []},
    )
    assert held["status"] == "HOLD"
    assert "eval_contract:missing_eval_banks" in held["reasons"]
