"""Deterministic direct-response grading; subjective/external effects require external verification."""
from __future__ import annotations
import hashlib
import math
import re
from .cases import CaseError, validate_row

def _sha(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()

def grade(case: dict, answer: str, *, independent_review=None,
          verify_independent_review=None, effect_receipt=None, verify_external_effect=None) -> dict:
    validate_row(case)
    if not isinstance(answer,str) or not answer.strip():
        return {"status":"FAIL","mechanism":"empty_or_invalid_response"}
    spec=case["grader"]
    kind=spec["kind"]
    mechanism=kind
    if kind=="exact":
        passed=answer.strip()==spec["expected"].strip()
    elif kind=="regex":
        passed=re.fullmatch(spec["pattern"],answer.strip(),flags=re.UNICODE) is not None
    elif kind=="numeric":
        try:
            value=float(answer.strip())
            target=float(spec["expected"])
            tol=float(spec.get("tolerance",0))
            passed=math.isfinite(value) and math.isfinite(target) and abs(value-target)<=tol
        except (ValueError,TypeError):
            passed=False
    elif kind=="contains":
        a=answer.casefold()
        required=spec["required"]
        forbidden=spec.get("forbidden",[])
        if not all(isinstance(x,str) and x.strip() for x in required+forbidden):
            raise CaseError("contains phrases must be nonempty strings")
        passed=all(x.casefold() in a for x in required) and not any(x.casefold() in a for x in forbidden)
    elif kind=="manual":
        if not isinstance(independent_review,dict) or verify_independent_review is None:
            return {"status":"UNREVIEWED","mechanism":"independent_semantic_review_absent"}
        if independent_review.get("case_id")!=case["case_id"] or independent_review.get("response_sha256")!=_sha(answer):
            return {"status":"UNREVIEWED","mechanism":"manual_review_binding_invalid"}
        if independent_review.get("verdict") not in ("PASS","FAIL","CRITICAL_FAIL"):
            return {"status":"UNREVIEWED","mechanism":"manual_review_verdict_invalid"}
        if verify_independent_review(case,answer,independent_review) is not True:
            return {"status":"UNREVIEWED","mechanism":"manual_review_authentication_failed"}
        return {"status":independent_review["verdict"],"mechanism":"externally_verified_manual_review"}
    elif kind=="runtime_effect":
        if not isinstance(effect_receipt,dict) or verify_external_effect is None:
            return {"status":"UNREVIEWED","mechanism":"verified_effect_readback_absent"}
        if not effect_receipt.get("action_id") or not re.fullmatch(r"[0-9a-f]{64}",str(effect_receipt.get("readback_digest",""))):
            return {"status":"UNREVIEWED","mechanism":"effect_receipt_identity_invalid"}
        if effect_receipt.get("verdict") not in ("PASS","FAIL","CRITICAL_FAIL"):
            return {"status":"UNREVIEWED","mechanism":"effect_receipt_verdict_invalid"}
        if verify_external_effect(case,answer,effect_receipt) is not True:
            return {"status":"UNREVIEWED","mechanism":"effect_external_verification_failed"}
        return {"status":effect_receipt["verdict"],"mechanism":"independently_verified_external_effect"}
    else:
        raise CaseError("unsupported grader")
    return {"status":"PASS" if passed else "FAIL","mechanism":mechanism}
