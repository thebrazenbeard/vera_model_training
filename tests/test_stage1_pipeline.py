from pathlib import Path
import importlib.util

ROOT=Path(__file__).resolve().parents[1]
MODULE=ROOT/"training"/"stage1_pipeline.py"

def _load():
    assert MODULE.exists(), "Stage-1 integrated gate must exist"
    spec=importlib.util.spec_from_file_location("stage1_pipeline",MODULE)
    module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module); return module

def _rows():
    from training.stage1_capability_coverage import REQUIRED_CAPABILITY_FAMILIES
    rows=[]
    for i,family in enumerate(REQUIRED_CAPABILITY_FAMILIES):
        rows.append({
            "stable_record_id":f"r{i:02d}",
            "exact_source_provenance":f"source:{i}",
            "construction_commit":"1"*40,
            "capability_family":family,
            "semantic_template_ancestry":f"template:{i}",
            "privacy_class":"PUBLIC",
            "mutable_stable_class":"STABLE",
            "known_confounds":[],
            "intended_custody":"train",
            "content_hash":f"{i+1:064x}"[-64:],
            "admissibility_class":"STABLE_GENERAL_BEHAVIOR",
            "counterfactual_twin_group":f"g{i}",
        })
    return rows

def test_integrated_stage1_gate_passes_only_after_all_three_lane_checks():
    m=_load()
    packet=m.build_stage1_packet(_rows(),source_head="2"*40,plan_blob="3"*40)
    assert packet["status"]=="PASS"
    assert packet["coverage"]["status"]=="PASS"
    assert packet["manifest"]["record_count"]==13
    assert all(result["status"]=="PASS" for result in packet["admissibility"])

def test_integrated_stage1_gate_holds_private_training_record():
    m=_load()
    rows=_rows()
    rows[0]["admissibility_class"]="PRIVATE_NOT_FOR_GENERIC_WEIGHTS"
    packet=m.build_stage1_packet(rows,source_head="2"*40,plan_blob="3"*40)
    assert packet["status"]=="HOLD"
    assert packet["manifest"] is None
