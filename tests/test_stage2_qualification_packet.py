import importlib
import importlib.util


def test_stage2_qualification_packet_requires_all_six_components():
    spec = importlib.util.find_spec("training.stage2_qualification_packet")
    assert spec is not None, "Stage-2 qualification packet module is missing"
    s2 = importlib.import_module("training.stage2_qualification_packet")

    packet = s2.build_stage2_qualification_packet(
        baseline_manifest={"status": "PASS", "manifest_sha256": "a" * 64},
        eval_contract={"status": "PASS", "reasons": []},
        contamination_report={"status": "PASS", "reasons": []},
        bank_manifest={"status": "PASS", "manifest_sha256": "b" * 64, "reasons": []},
        paired_inference={"status": "PASS", "reasons": []},
        custody_report={"status": "PASS", "reasons": []},
    )
    assert packet["status"] == "PASS"
    assert packet["bank_manifest_sha256"] == "b" * 64

    held = s2.build_stage2_qualification_packet(
        baseline_manifest={"status": "PASS", "manifest_sha256": "a" * 64},
        eval_contract={"status": "PASS", "reasons": []},
        contamination_report={"status": "PASS", "reasons": []},
        bank_manifest={"status": "PASS", "manifest_sha256": "b" * 64, "reasons": []},
        paired_inference={"status": "HOLD", "reasons": ["required_promotion_family_missing"]},
        custody_report={"status": "PASS", "reasons": []},
    )
    assert held["status"] == "HOLD"
    assert "paired_inference:required_promotion_family_missing" in held["reasons"]
