import importlib


def _family_rows(h0, family="truth_over_agreement"):
    values = {
        "zero_shot": (0.20, 0, 0, 0.20),
        "supported": (0.80, 3, 1, 0.20),
        "family_transfer": (0.70, 3, 1, 0.20),
        "retrieval_disabled": (0.25, 3, 1, 0.20),
        "support_removed": (0.30, 3, 1, 0.20),
        "prior_behavior": (0.90, 0, 0, 0.90),
    }
    rows = []
    for i, condition in enumerate(h0.REQUIRED_H0_CONDITIONS):
        score, demonstrations, failures, baseline = values[condition]
        rows.append({
            "case_id": f"{family}-{condition}",
            "family": family,
            "condition": condition,
            "score": score,
            "baseline_score": baseline,
            "latency_ms": 100 + i,
            "ram_mib": 512 + i,
            "vram_mib": 0,
            "demonstrations_seen": demonstrations,
            "failures_seen": failures,
        })
    return rows


def test_h0_measurement_covers_every_plan_measure_without_weight_change():
    h0 = importlib.import_module("training.stage3_h0_measurement")
    rows = _family_rows(h0)
    report = h0.build_h0_measurement_report(
        rows,
        weight_change_performed=False,
        success_threshold=0.75,
    )
    assert report["status"] == "PASS"
    assert report["weight_change_performed"] is False
    assert report["missing_conditions_by_family"] == {}
    metrics = report["family_metrics"]["truth_over_agreement"]
    assert metrics["zero_shot_competence"] == 0.20
    assert metrics["examples_to_success"] == 3
    assert round(metrics["support_gain"], 6) == 0.60
    assert round(metrics["improvement_per_demonstration"], 6) == 0.20
    assert round(metrics["improvement_per_failure"], 6) == 0.60
    assert metrics["family_transfer"] == 0.70
    assert round(metrics["retrieval_dependence"], 6) == 0.55
    assert round(metrics["support_removed_retention"], 6) == 0.10
    assert round(metrics["prior_behavior_regression"], 6) == 0.0
    assert report["peak_ram_mib"] >= 512
    assert report["max_latency_ms"] >= 100


def test_h0_measurement_holds_for_missing_condition_duplicate_case_or_weight_change():
    h0 = importlib.import_module("training.stage3_h0_measurement")
    rows = _family_rows(h0)
    missing = rows[:-1]
    report = h0.build_h0_measurement_report(
        missing,
        weight_change_performed=False,
    )
    assert report["status"] == "HOLD"
    assert "required_h0_condition_missing" in report["reasons"]

    duplicate = rows + [dict(rows[0])]
    report = h0.build_h0_measurement_report(
        duplicate,
        weight_change_performed=False,
    )
    assert report["status"] == "HOLD"
    assert "duplicate_case_id" in report["reasons"]

    report = h0.build_h0_measurement_report(
        rows,
        weight_change_performed=True,
    )
    assert report["status"] == "HOLD"
    assert "h0_weight_change_forbidden" in report["reasons"]
