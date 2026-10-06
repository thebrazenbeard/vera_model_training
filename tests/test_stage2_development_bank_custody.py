import importlib
import importlib.util


def _cases():
    return [
        {"case_id": "ordinary-1", "intended_custody": "dev", "lane_c_target": False},
        {"case_id": "c-target-1", "intended_custody": "dev", "lane_c_target": True},
    ]


def test_dev_bank_pre_freeze_custody_keeps_c_targets_away_from_lane_c_config():
    spec = importlib.util.find_spec("training.stage2_development_bank_custody")
    assert spec is not None, "development bank custody module is missing"
    c = importlib.import_module("training.stage2_development_bank_custody")
    report = c.build_development_bank_custody_report(
        _cases(),
        c_freeze_complete=False,
        custody_owner="IndependentCustodian",
        c_config_visible_case_ids=set(),
    )
    assert report["status"] == "PASS"
    assert report["c_target_config_overlap"] == []


def test_dev_bank_custody_holds_if_lane_c_custodies_or_sees_target_pre_freeze():
    c = importlib.import_module("training.stage2_development_bank_custody")
    report = c.build_development_bank_custody_report(
        _cases(),
        c_freeze_complete=False,
        custody_owner="Lane-C",
        c_config_visible_case_ids={"c-target-1"},
    )
    assert report["status"] == "HOLD"
    assert "pre_freeze_custodian_must_be_independent_of_lane_c" in report["reasons"]
    assert "c_target_visible_to_lane_c_before_freeze" in report["reasons"]
