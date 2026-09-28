from __future__ import annotations
import importlib.util
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/"successor"/"qwen35"/"qualification"/"score_final_blind_review_v3.py"

def module():
    spec=importlib.util.spec_from_file_location("blind_score",SCRIPT)
    m=importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(m)
    return m

def test_expected_mapping_is_deterministic_and_balanced():
    m=module()
    ids=[f"final-H{i:02d}-1" for i in range(1,21)]
    a=m.expected_mapping("a"*64,ids)
    b=m.expected_mapping("a"*64,ids)
    assert a==b
    assert len(a)==40
    assert sum(x["condition"]=="BASE" for x in a)==20
    assert sum(x["condition"]=="ADAPTER" for x in a)==20
    assert {x["blind_id"] for x in a}=={f"blind-{i:03d}" for i in range(1,41)}

def test_expected_mapping_changes_when_selection_hash_changes():
    m=module()
    ids=[f"final-H{i:02d}-1" for i in range(1,21)]
    assert m.expected_mapping("a"*64,ids)!=m.expected_mapping("b"*64,ids)
