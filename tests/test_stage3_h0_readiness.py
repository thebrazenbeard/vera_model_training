import importlib
import importlib.util


def _passing_inputs():
    stage0 = {
        "status": "STAGE0_RUNTIME_QUALIFIED",
        "qualified_subject_head": "1" * 40,
    }
    stage2 = {
        "status": "PASS",
        "baseline_manifest_sha256": "2" * 64,
        "bank_manifest_sha256": "3" * 64,
    }
    bank = {
        "status": "PASS",
        "bank_count": 12,
        "case_count": 240,
        "minimum_cases_per_bank": 20,
        "under_minimum_banks": [],
        "manifest_sha256": "3" * 64,
    }
    control = {
        "status": "PASS",
        "isolation_receipt_sha256": "4" * 64,
    }
    return stage0, stage2, bank, control


def test_h0_readiness_requires_real_materialized_reviewed_dev_bank_and_runtime():
    spec = importlib.util.find_spec("training.stage3_h0_readiness")
    assert spec is not None, "H0 readiness module is missing"
    h0 = importlib.import_module("training.stage3_h0_readiness")
    stage0, stage2, bank, control = _passing_inputs()
    report = h0.build_stage3_h0_readiness(
        stage0_runtime_receipt=stage0,
        stage2_qualification_packet=stage2,
        bank_manifest=bank,
        h0_control_contract=control,
        development_bank_materialized=True,
        independent_review_complete=True,
        protected_final_used=False,
    )
    assert report["status"] == "READY_FOR_H0_DEVELOPMENT_RUN"
    assert report["reasons"] == []


def test_h0_readiness_holds_without_materialized_bank_review_or_with_final_bank():
    h0 = importlib.import_module("training.stage3_h0_readiness")
    stage0, stage2, bank, control = _passing_inputs()
    stage2["status"] = "HOLD"
    bank["status"] = "HOLD"
    report = h0.build_stage3_h0_readiness(
        stage0_runtime_receipt=stage0,
        stage2_qualification_packet=stage2,
        bank_manifest=bank,
        h0_control_contract=control,
        development_bank_materialized=False,
        independent_review_complete=False,
        protected_final_used=True,
    )
    assert report["status"] == "HOLD"
    assert "stage2_qualification_packet_not_pass" in report["reasons"]
    assert "development_bank_not_materialized" in report["reasons"]
    assert "development_bank_independent_review_incomplete" in report["reasons"]
    assert "protected_final_use_forbidden" in report["reasons"]
