from pathlib import Path
import importlib.util

ROOT=Path(__file__).resolve().parents[1]
MODULE=ROOT/"training"/"stage1_corpus_manifest.py"

def _load():
    assert MODULE.exists(), "Stage-1 deterministic manifest builder must exist"
    spec=importlib.util.spec_from_file_location("stage1_corpus_manifest",MODULE)
    module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module); return module

def _record(record_id, family="identity_stability"):
    return {
        "stable_record_id": record_id,
        "exact_source_provenance": "source:test",
        "construction_commit": "1"*40,
        "capability_family": family,
        "semantic_template_ancestry": "template:test",
        "privacy_class": "PUBLIC",
        "mutable_stable_class": "STABLE",
        "known_confounds": [],
        "intended_custody": "train",
        "content_hash": "a"*64,
        "admissibility_class": "STABLE_GENERAL_BEHAVIOR",
    }

def test_manifest_is_order_independent_and_binds_plan_source():
    m=_load()
    one=m.build_stage1_manifest([_record("r2"),_record("r1")], source_head="2"*40, plan_blob="3"*40)
    two=m.build_stage1_manifest([_record("r1"),_record("r2")], source_head="2"*40, plan_blob="3"*40)
    assert one==two
    assert one["record_count"]==2
    assert one["record_ids"]==["r1","r2"]
    assert len(one["manifest_sha256"])==64

def test_duplicate_record_id_holds():
    import pytest
    m=_load()
    with pytest.raises(m.Stage1ManifestHold, match="duplicate"):
        m.build_stage1_manifest([_record("r1"),_record("r1")], source_head="2"*40, plan_blob="3"*40)
