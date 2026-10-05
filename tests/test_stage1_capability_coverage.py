from pathlib import Path
import importlib.util

ROOT=Path(__file__).resolve().parents[1]
MODULE=ROOT/"training"/"stage1_capability_coverage.py"

def _load():
    assert MODULE.exists(), "Stage-1 capability coverage evaluator must exist"
    spec=importlib.util.spec_from_file_location("stage1_capability_coverage",MODULE)
    module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module); return module

def test_report_requires_all_plan_families_and_tracks_ancestry():
    m=_load()
    rows=[{"stable_record_id":f"r{i}","capability_family":family,"semantic_template_ancestry":f"t{i}","counterfactual_twin_group":f"g{i}"} for i,family in enumerate(m.REQUIRED_CAPABILITY_FAMILIES)]
    report=m.build_coverage_report(rows)
    assert report["status"]=="PASS"
    assert report["missing_families"]==[]
    assert set(report["family_counts"])==set(m.REQUIRED_CAPABILITY_FAMILIES)
    assert report["records_with_template_ancestry"]==len(rows)
    assert report["records_with_counterfactual_twin_group"]==len(rows)

def test_missing_family_holds():
    m=_load()
    rows=[{"stable_record_id":"r1","capability_family":"identity_stability","semantic_template_ancestry":"t1"}]
    report=m.build_coverage_report(rows)
    assert report["status"]=="HOLD"
    assert "instruction_following" in report["missing_families"]
