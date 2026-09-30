"""Local deterministic direct-response generation, with bound observation records.

This invokes a model's generate method, unlike V4's supplied-answer log-probs.
The record is a LOCAL GENERATION CLAIM, not independent runtime attestation.
"""
from __future__ import annotations
import hashlib
import json
import re
from .observations import canonical_sha

class GenerationError(ValueError):
    pass

def decoding_spec(max_new_tokens=32):
    if not isinstance(max_new_tokens,int) or not 1<=max_new_tokens<=512:
        raise GenerationError("max_new_tokens must be integer in 1..512")
    return {"do_sample":False,"max_new_tokens":max_new_tokens,
            "enable_thinking":False,"system_prompt":None,"add_generation_prompt":True}

def decoding_digest(max_new_tokens=32):
    return canonical_sha(decoding_spec(max_new_tokens))

def generate_record(model,tokenizer,case,*,condition,model_sha,max_new_tokens=32):
    import torch
    cfg=decoding_spec(max_new_tokens)
    if condition not in ("base","candidate"):
        raise GenerationError("condition must be base or candidate")
    if not isinstance(model_sha,str) or re.fullmatch(r"[0-9a-f]{64}",model_sha) is None:
        raise GenerationError("model_sha must bind a SHA-256 artifact")
    msgs=[{"role":"user","content":case["prompt"]}]
    try:
        rendered=tokenizer.apply_chat_template(msgs,tokenize=False,
                                               add_generation_prompt=True,enable_thinking=False)
    except TypeError:
        raise GenerationError("tokenizer chat template does not accept enable_thinking=False")
    encoding=tokenizer(rendered,return_tensors="pt",add_special_tokens=False)
    input_ids=encoding["input_ids"].to(model.device)
    attention=encoding.get("attention_mask")
    if attention is not None:
        attention=attention.to(model.device)
    with torch.inference_mode():
        result=model.generate(input_ids=input_ids,attention_mask=attention,
                              do_sample=False,max_new_tokens=max_new_tokens,
                              pad_token_id=tokenizer.pad_token_id,
                              eos_token_id=tokenizer.eos_token_id)
    completion=result[0,input_ids.shape[1]:]
    response=tokenizer.decode(completion,skip_special_tokens=True).strip()
    if not response:
        raise GenerationError("model produced empty completion")
    return {"schema":"QWEN35_GENERATION_OBSERVATION_V1",
            "case_id":case["case_id"],"condition":condition,"case_sha256":canonical_sha(case),
            "model_sha256":model_sha,
            "rendered_input_sha256":hashlib.sha256(rendered.encode("utf-8")).hexdigest(),
            "decoding_sha256":decoding_digest(max_new_tokens),
            "response":response,
            "response_sha256":hashlib.sha256(response.encode("utf-8")).hexdigest(),
            "origin":"model_generation_claim",
            "generation_evidence_ceiling":"DIRECT_LOCAL_MODEL_CALL / NO_INDEPENDENT_RUNTIME_ATTESTATION"}
