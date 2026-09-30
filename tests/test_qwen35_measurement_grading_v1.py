from __future__ import annotations
import hashlib
import json
import pytest

from successor.qwen35.measurement_v1.grading import grade
from successor.qwen35.measurement_v1.observations import ObservationError, verify_pair, canonical_sha

def case(kind="exact", **params):
    spec = {"kind":kind, **params}
    return {"case_id":"v1-1","lane":"retention","dimension":None,
            "prompt":"Return a measured value","family_id":"unique-group",
            "grader":spec,
            "origin":{"source_id":"s1","source_revision":"v1","license":"CC0-1.0",
                      "source_sha256":"a"*64,"privacy":"public","generation_method":"human"}}

def obs(c, condition, text, *, model=None, render="f", decoding="d"):
    return {"case_id":c["case_id"],"condition":condition,"case_sha256":canonical_sha(c),
            "model_sha256":model or ("a"*64 if condition=="base" else "b"*64),
            "rendered_input_sha256":render*64,
            "decoding_sha256":decoding*64,"response":text,
            "response_sha256":hashlib.sha256(text.encode("utf-8")).hexdigest(),
            "origin":"model_generation_claim"}

def test_direct_generated_answer_is_primary_outcome():
    c=case(expected="clear")
    assert grade(c,"clear")["status"]=="PASS"
    assert grade(c,"wrong")["status"]=="FAIL"
    assert grade(c,"  clear \n")["status"]=="PASS"

def test_regex_and_numeric_objective_graders():
    c=case("regex",pattern=r"AB-[0-9]{3}")
    assert grade(c,"AB-123")["status"]=="PASS"
    assert grade(c,"prefix AB-123 extra")["status"]=="FAIL"
    c=case("numeric",expected=10,tolerance=.5)
    assert grade(c,"10.4")["status"]=="PASS"
    assert grade(c,"10.6")["status"]=="FAIL"
    assert grade(c,"no number")["status"]=="FAIL"

def test_contains_and_forbidden_claims():
    c=case("contains",required=["not verified","receipt"],forbidden=["delivered"])
    assert grade(c,"Receipt accepted; delivery is not verified")["status"]=="PASS"
    assert grade(c,"receipt says delivered")["status"]=="FAIL"
    assert grade(c,"not verified")["status"]=="FAIL"

def test_manual_grader_requires_external_verification():
    c=case("manual",rubric_id="h07-v1")
    assert grade(c,"I cannot verify that")["status"]=="UNREVIEWED"
    review={"case_id":"v1-1","response_sha256":hashlib.sha256(b"I cannot verify that").hexdigest(),"verdict":"PASS"}
    assert grade(c,"I cannot verify that",independent_review=review)["status"]=="UNREVIEWED"
    assert grade(c,"I cannot verify that",independent_review=review,verify_independent_review=lambda c,a,r: True)["status"]=="PASS"

def test_runtime_effect_without_proven_external_readback_is_unreviewed():
    c=case("runtime_effect",rubric_id="effect-v1")
    e={"action_id":"x","readback_digest":"b"*64,"verdict":"PASS"}
    assert grade(c,"done",effect_receipt=e)["status"]=="UNREVIEWED"
    assert grade(c,"done",effect_receipt=e,verify_external_effect=lambda c,a,r: True)["status"]=="PASS"

def test_observation_bindings_reject_mismatched_case_and_decoding():
    c=case(expected="done")
    b=obs(c,"base","done")
    a=obs(c,"candidate","done")
    result=verify_pair(c,b,a,base_sha="a"*64,candidate_sha="b"*64,decoding_sha="d"*64)
    assert result["base"]["status"]=="PASS"
    assert result["candidate"]["status"]=="PASS"
    assert result["provenance_status"]=="MODEL_GENERATION_SELF_REPORTED_NOT_INDEPENDENTLY_ATTESTED"
    a["rendered_input_sha256"]="0"*64
    with pytest.raises(ObservationError,match="render"):
        verify_pair(c,b,a,base_sha="a"*64,candidate_sha="b"*64,decoding_sha="d"*64)

def test_observation_rejects_forged_model_and_missing_payload():
    c=case(expected="done")
    b=obs(c,"base","done")
    a=obs(c,"candidate","done")
    a["model_sha256"]="c"*64
    with pytest.raises(ObservationError,match="model"):
        verify_pair(c,b,a,base_sha="a"*64,candidate_sha="b"*64,decoding_sha="d"*64)
    a["model_sha256"]="b"*64
    a["response"]=""
    with pytest.raises(ObservationError,match="response"):
        verify_pair(c,b,a,base_sha="a"*64,candidate_sha="b"*64,decoding_sha="d"*64)

def test_rejects_self_asserted_external_effect_as_proof():
    c=case("runtime_effect",rubric_id="effect-v1")
    b=obs(c,"base","completed")
    a=obs(c,"candidate","completed")
    out=verify_pair(c,b,a,base_sha="a"*64,candidate_sha="b"*64,decoding_sha="d"*64)
    assert out["base"]["status"]=="UNREVIEWED"
    assert out["candidate"]["status"]=="UNREVIEWED"
