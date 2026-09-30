from __future__ import annotations
import hashlib
import torch
import pytest
from successor.qwen35.measurement_v1.generation import GenerationError, generate_record, decoding_digest
from successor.qwen35.measurement_v1.observations import verify_pair

class Tok:
    pad_token_id=0
    eos_token_id=9
    def apply_chat_template(self,messages,**kwargs):
        return "[USER]"+messages[0]["content"]+"[ASSISTANT]"
    def __call__(self,text,**kwargs):
        return {"input_ids":torch.tensor([[1,2,3]],dtype=torch.long),
                "attention_mask":torch.tensor([[1,1,1]],dtype=torch.long)}
    def decode(self,tokens,**kwargs):
        assert list(tokens)==[42]
        return "READY"

class Model:
    device=torch.device("cpu")
    def __init__(self):self.calls=[]
    def generate(self,**kwargs):
        self.calls.append(kwargs)
        return torch.tensor([[1,2,3,42]],dtype=torch.long)

def case():
    return {"case_id":"live-dev-01","lane":"retention","dimension":None,
            "family_id":"unique","prompt":"Reply READY.","grader":{"kind":"exact","expected":"READY"},
            "origin":{"source_id":"dev0","source_revision":"v1","license":"CC0-1.0",
                      "source_sha256":"a"*64,"privacy":"public","generation_method":"human"}}

def test_generation_calls_model_and_hash_binds_real_completion():
    c=case()
    model=Model()
    r=generate_record(model,Tok(),c,condition="base",model_sha="a"*64,max_new_tokens=12)
    assert r["response"]=="READY" and r["origin"]=="model_generation_claim"
    assert r["response_sha256"]==hashlib.sha256(b"READY").hexdigest()
    assert r["rendered_input_sha256"]==hashlib.sha256(b"[USER]Reply READY.[ASSISTANT]").hexdigest()
    assert model.calls[0]["max_new_tokens"]==12
    assert model.calls[0]["do_sample"] is False

def test_generation_conditions_have_comparable_input_sha():
    c=case()
    b=generate_record(Model(),Tok(),c,condition="base",model_sha="a"*64)
    a=generate_record(Model(),Tok(),c,condition="candidate",model_sha="b"*64)
    assert verify_pair(c,b,a,base_sha="a"*64,candidate_sha="b"*64,
                       decoding_sha=decoding_digest(32))["candidate"]["status"]=="PASS"

def test_generation_rejects_missing_or_invalid_settings():
    with pytest.raises(GenerationError,match="max_new_tokens"):
        generate_record(Model(),Tok(),case(),condition="base",model_sha="a"*64,max_new_tokens=0)
    with pytest.raises(GenerationError,match="condition"):
        generate_record(Model(),Tok(),case(),condition="unknown",model_sha="a"*64)
