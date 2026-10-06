import importlib
import importlib.util


def _rows(s2, families):
    rows = []
    for family in families:
        for i in range(80):
            rows.append({
                "case_id": f"{family}-{i:03d}",
                "family": family,
                "control_score": 0,
                "candidate_score": 1,
            })
    return rows


def test_stage2_paired_inference_contract_requires_80_pairs_for_every_required_family():
    spec = importlib.util.find_spec("training.stage2_paired_inference")
    assert spec is not None, "Stage-2 paired inference module is missing"
    s2 = importlib.import_module("training.stage2_paired_inference")
    rows = _rows(s2, s2.REQUIRED_PROMOTION_FAMILIES)
    report = s2.build_paired_inference_contract(
        rows,
        minimum_pairs_per_family=80,
        power_preregistered=True,
    )
    assert report["status"] == "PASS"
    assert report["paired_design"] is True
    assert report["minimum_pairs_per_family"] == 80
    assert report["missing_families"] == []
    assert min(report["family_pair_counts"].values()) == 80


def test_stage2_paired_inference_holds_if_any_required_family_is_missing():
    s2 = importlib.import_module("training.stage2_paired_inference")
    rows = _rows(s2, s2.REQUIRED_PROMOTION_FAMILIES[:-1])
    report = s2.build_paired_inference_contract(
        rows,
        minimum_pairs_per_family=80,
        power_preregistered=True,
    )
    assert report["status"] == "HOLD"
    assert s2.REQUIRED_PROMOTION_FAMILIES[-1] in report["missing_families"]
    assert "required_promotion_family_missing" in report["reasons"]
