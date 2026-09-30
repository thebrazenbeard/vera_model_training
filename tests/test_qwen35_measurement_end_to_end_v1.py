from __future__ import annotations
import json
from pathlib import Path
import pytest
from successor.qwen35.measurement_v1.local_generate import generate_pair,save_session
from successor.qwen35.measurement_v1.devloop import score_paired_files
from successor.qwen35.measurement_v1.qualification import decide

class T:
    pad_token_id=0
    eos_token_id=9
    def apply_chat_template(self,ms,**kwargs):return "P="+ms[0]["content"]
    def __call__(self,text,**kw):
        import torch
        return {"input_ids":torch.tensor([[1,2]])}
    def decode(self,ids,**kw):return "verified" if list(ids)==[3] else "unsupported"

class M:
    def __init__(self,code):
        import torch
        self.device=torch.device("cpu")
        self.code=code
    def generate(self,**kwargs):
        import torch
        return torch.tensor([[1,2,self.code]])

def c(i,kind="exact"):
    return {"case_id":f"int-{i}","prompt":f"Confirm synthetic reading for {i}.","lane":"retention",
            "dimension":None,"family_id":f"independent-{i}",
            "origin":{"source_id":f"public-fixture-{i}","source_revision":"v1","license":"CC0-1.0",
                      "source_sha256":"1"*64,"privacy":"public","generation_method":"synthetic_testing"},
            "grader":({"kind":"exact","expected":"verified"} if kind=="exact" else {"kind":"manual","rubric_id":"r1"})}

def test_small_real_generation_interface_is_not_a_final_gate(tmp_path):
    cases=[c(1),c(2)]
    path=tmp_path/"cases.jsonl"
    path.write_text("\n".join(json.dumps(x) for x in cases)+"\n",encoding="utf-8")
    b,a=generate_pair(M(3),M(3),T(),cases,base_sha="a"*64,candidate_sha="b"*64,max_new_tokens=6)
    folder=tmp_path/"session"
    save_session(folder,cases,b,a)
    out=score_paired_files(path,folder/"base.jsonl",folder/"candidate.jsonl",
                           tmp_path/"score.json",base_sha="a"*64,candidate_sha="b"*64,
                           decoding_sha=b[0]["decoding_sha256"])
    assert out["status"]=="DEVELOPMENT_DIAGNOSTIC_UNATTESTED"
    assert out["paired"]["n"]==2
    assert decide({"case_count":2,"status":"STRUCTURAL_PREFLIGHT_ONLY"},out["paired"])["status"]=="NOT_QUALIFIED"

def test_subjective_response_not_silently_included_in_statistics(tmp_path):
    cases=[c(10,"manual")]
    path=tmp_path/"cases.jsonl"
    path.write_text(json.dumps(cases[0])+"\n",encoding="utf-8")
    b,a=generate_pair(M(3),M(3),T(),cases,base_sha="a"*64,candidate_sha="b"*64)
    folder=tmp_path/"session"
    save_session(folder,cases,b,a)
    out=score_paired_files(path,folder/"base.jsonl",folder/"candidate.jsonl",
                           tmp_path/"score.json",base_sha="a"*64,candidate_sha="b"*64,
                           decoding_sha=b[0]["decoding_sha256"])
    assert out["status"]=="INCOMPLETE_UNREVIEWED"
    assert out["paired"] is None
