import importlib
import importlib.util


def test_stage2_c_target_rows_remain_separately_custodied_before_c_freeze():
    spec = importlib.util.find_spec("training.stage2_custody")
    assert spec is not None, "Stage-2 custody module is missing"
    s2 = importlib.import_module("training.stage2_custody")
    report = s2.build_stage2_custody_report(
        c_target_record_ids={"c-1", "c-2"},
        training_record_ids={"train-1"},
        config_visible_record_ids={"config-1"},
        c_freeze_complete=False,
        custody_owner="Lane-C",
    )
    assert report["status"] == "PASS"
    assert report["c_target_training_overlap"] == []
    assert report["c_target_config_overlap"] == []
    assert report["custody_owner"] == "Lane-C"


def test_stage2_custody_requires_exact_freeze_evidence_before_release():
    s2 = importlib.import_module("training.stage2_custody")
    held = s2.build_stage2_custody_report(
        c_target_record_ids={"c-1"},
        training_record_ids=set(),
        config_visible_record_ids={"c-1"},
        c_freeze_complete=True,
        custody_owner="Lane-C",
    )
    assert held["status"] == "HOLD"
    assert "c_freeze_subject_missing_or_invalid" in held["reasons"]
    assert "custody_receipt_sha256_missing_or_invalid" in held["reasons"]

    released = s2.build_stage2_custody_report(
        c_target_record_ids={"c-1"},
        training_record_ids=set(),
        config_visible_record_ids={"c-1"},
        c_freeze_complete=True,
        custody_owner="Lane-C",
        c_freeze_subject="1" * 40,
        custody_receipt_sha256="2" * 64,
    )
    assert released["status"] == "PASS"
    assert released["c_freeze_subject"] == "1" * 40
