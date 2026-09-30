from __future__ import annotations
import json
from pathlib import Path
import pytest
from successor.qwen35.measurement_v1.local_generate import (
    LocalGenerationError, generate_pair, save_session,
)

class DummyTok:
    pad_token_id=0
    eos_token_id=7
    def apply_chat_template(self,messages,**kwargs):return "USR:"+messages[0]["content"]+":AST"
    def __call__(self,text,**kwargs):
        import torch
        return {"input_ids":torch.tensor([[1,2]])}
    def decode(self,ids,**kwargs):
        return "A" if list(ids)==[3] else "B"

class DummyModel:
    def __init__(self,extra):
        import torch
        self.device=torch.device("cpu")
        self.extra=extra
        self.calls=0
    def generate(self,**kwargs):
        import torch
        self.calls+=1
        return torch.tensor([[1,2,self.extra]])

def case(i):
    return {"case_id":f"test-{i}","prompt":f"Generate token for prompt {i}.",
            "family_id":f"g{i}","lane":"retention","dimension":None,
            "grader":{"kind":"exact","expected":"A"},
            "origin":{"source_id":f"src{i}","source_revision":"v1","license":"CC0-1.0",
                      "source_sha256":"c"*64,"privacy":"public","generation_method":"human"}}

def test_local_pair_calls_models_and_writes_hash_bound_evidence(tmp_path):
    rows=[case(1),case(2)]
    base=DummyModel(3)
    adapted=DummyModel(4)
    b,a=generate_pair(base,adapted,DummyTok(),rows,base_sha="a"*64,candidate_sha="b"*64,
                      max_new_tokens=8)
    assert len(b)==len(a)==2
    assert base.calls==adapted.calls==2
    assert all(r["response"]=="A" for r in b)
    assert all(r["response"]=="B" for r in a)
    output=tmp_path/"generated"
    result=save_session(output,rows,b,a)
    assert result["case_count"]==2
    assert result["status"]=="LOCAL_GENERATIONS_RECORDED_NOT_INDEPENDENTLY_ATTESTED"
    assert (output/"base.jsonl").exists()
    with pytest.raises(LocalGenerationError,match="exists"):
        save_session(output,rows,b,a)

def test_local_pair_rejects_empty_or_same_model_identity():
    with pytest.raises(LocalGenerationError,match="distinct"):
        generate_pair(DummyModel(3),DummyModel(4),DummyTok(),[case(1)],
                      base_sha="a"*64,candidate_sha="a"*64,max_new_tokens=8)
