"""Binding actual response-text claims to cases, model digests and decoding.

Cryptographic hashes verify byte identity, not that a model actually generated
the response. Independent runtime attestation is needed before a live claim.
"""
from __future__ import annotations
import hashlib
import json
import re
from .grading import grade

class ObservationError(ValueError):
    pass

def canonical_sha(value: dict) -> str:
    raw=json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()

def _require_digest(value,name):
    if not isinstance(value,str) or not re.fullmatch("[0-9a-f]{64}",value):
        raise ObservationError(name+" invalid SHA256")

def _validate(case,record,condition,model_sha,decoding_sha):
    if not isinstance(record,dict):
        raise ObservationError("observation missing")
    if record.get("condition")!=condition:
        raise ObservationError("condition binding mismatch")
    if record.get("case_id")!=case["case_id"] or record.get("case_sha256")!=canonical_sha(case):
        raise ObservationError("case binding mismatch")
    _require_digest(record.get("model_sha256"),"model")
    if record["model_sha256"]!=model_sha:
        raise ObservationError("model hash mismatch")
    _require_digest(record.get("decoding_sha256"),"decoding")
    if record["decoding_sha256"]!=decoding_sha:
        raise ObservationError("decoding config mismatch")
    _require_digest(record.get("rendered_input_sha256"),"render")
    if record.get("origin")!="model_generation_claim":
        raise ObservationError("observation origin is not model generation")
    answer=record.get("response")
    if not isinstance(answer,str) or not answer.strip():
        raise ObservationError("response missing/empty")
    digest=hashlib.sha256(answer.encode("utf-8")).hexdigest()
    if record.get("response_sha256")!=digest:
        raise ObservationError("response digest mismatch")

def verify_pair(case,base,candidate,*,base_sha,candidate_sha,decoding_sha,
                human_reviews=None,external_effect_receipts=None,
                verify_human=None,verify_effect=None):
    for name,d in [("base",base_sha),("candidate",candidate_sha),("decoding",decoding_sha)]:
        _require_digest(d,name)
    if base_sha==candidate_sha:
        raise ObservationError("base and candidate artifact digest identical; no distinct comparison")
    _validate(case,base,"base",base_sha,decoding_sha)
    _validate(case,candidate,"candidate",candidate_sha,decoding_sha)
    if base["rendered_input_sha256"]!=candidate["rendered_input_sha256"]:
        raise ObservationError("rendered input differs between conditions")
    result={"case_id":case["case_id"],"family_id":case["family_id"],"lane":case["lane"],
            "dimension":case["dimension"],"case_sha256":canonical_sha(case),
            "decoding_sha256":decoding_sha,
            "provenance_status":"MODEL_GENERATION_SELF_REPORTED_NOT_INDEPENDENTLY_ATTESTED"}
    for name,ob in (("base",base),("candidate",candidate)):
        review=(human_reviews or {}).get(name)
        receipt=(external_effect_receipts or {}).get(name)
        result[name]=grade(case,ob["response"],independent_review=review,
                           verify_independent_review=verify_human,effect_receipt=receipt,
                           verify_external_effect=verify_effect)
        result[name]["response_sha256"]=ob["response_sha256"]
        result[name]["model_sha256"]=ob["model_sha256"]
    return result
