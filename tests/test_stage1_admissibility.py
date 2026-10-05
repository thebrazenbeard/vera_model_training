from pathlib import Path
import importlib.util

ROOT=Path(__file__).resolve().parents[1]
MODULE=ROOT/"training"/"stage1_admissibility.py"

def _load():
    assert MODULE.exists(), "Stage-1 admissibility firewall must exist"
    spec=importlib.util.spec_from_file_location("stage1_admissibility",MODULE)
    module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module); return module

def _record(admissibility_class="STABLE_GENERAL_BEHAVIOR", custody="train"):
    return {
        "stable_record_id":"r1",
        "exact_source_provenance":"source:test",
        "construction_commit":"1"*40,
        "capability_family":"identity_stability",
        "semantic_template_ancestry":"template:test",
        "privacy_class":"PUBLIC",
        "mutable_stable_class":"STABLE",
        "known_confounds":[],
        "intended_custody":custody,
        "content_hash":"a"*64,
        "admissibility_class":admissibility_class,
    }

def test_stable_general_behavior_can_enter_train():
    m=_load()
    result=m.evaluate_record(_record())
    assert result["status"]=="PASS"
    assert result["training_eligible"] is True

def test_private_mutable_historical_and_identity_crossing_fail_closed_for_train():
    m=_load()
    for cls in ("MUTABLE_EXTERNAL_MEMORY","PRIVATE_NOT_FOR_GENERIC_WEIGHTS","HISTORICAL_AUDIT_ONLY","REJECTED_IDENTITY_CROSSING"):
        result=m.evaluate_record(_record(cls))
        assert result["status"]=="HOLD"
        assert result["training_eligible"] is False

def test_missing_required_metadata_holds():
    m=_load()
    row=_record(); del row["semantic_template_ancestry"]
    result=m.evaluate_record(row)
    assert result["status"]=="HOLD"
    assert any("semantic_template_ancestry" in x for x in result["reasons"])
