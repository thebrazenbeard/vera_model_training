from __future__ import annotations
import importlib.util
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
QUAL=ROOT/"successor"/"qwen35"/"qualification"

def load(name: str, path: Path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module

def test_review_chain_binds_packet_mapping_judgments_and_selection():
    m=load("chain_v2",QUAL/"finalize_final_qualification_v3.py")
    h=lambda c:c*64
    packet={
      "automated_result_sha256":h("a"),"blind_packet_sha256":h("b"),
      "mapping_sha256":h("c"),"selection_sha256":h("s")
    }
    judgment={
      "blind_packet_sha256":h("b"),"judgments_sha256":h("d"),
      "mapping_accessed":False,"judge_verified":True,"judge_binding_sha256":h("e")
    }
    blind={
      "blind_packet_sha256":h("b"),"mapping_sha256":h("c"),
      "judgments_sha256":h("d"),"judge_binding_sha256":h("e")
    }
    reasons=m.verify_review_chain(h("a"),blind,packet,judgment,h("b"),h("c"),h("d"),h("s"),h("e"))
    assert reasons==[]
    reasons=m.verify_review_chain(h("a"),blind,packet,judgment,h("0"),h("c"),h("d"),h("s"),h("e"))
    assert "packet_blind_file_mismatch" in reasons
