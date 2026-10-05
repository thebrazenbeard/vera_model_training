from __future__ import annotations

REQUIRED_RECORD_FIELDS = (
    "stable_record_id","exact_source_provenance","construction_commit",
    "capability_family","semantic_template_ancestry","privacy_class",
    "mutable_stable_class","known_confounds","intended_custody",
    "content_hash","admissibility_class",
)
ADMISSIBILITY_CLASSES = (
    "STABLE_GENERAL_BEHAVIOR",
    "MUTABLE_EXTERNAL_MEMORY",
    "PRIVATE_NOT_FOR_GENERIC_WEIGHTS",
    "HISTORICAL_AUDIT_ONLY",
    "REJECTED_IDENTITY_CROSSING",
)

def evaluate_record(record: dict) -> dict:
    reasons=[]
    if not isinstance(record,dict):
        return {"status":"HOLD","training_eligible":False,"reasons":["record_not_object"]}
    for field in REQUIRED_RECORD_FIELDS:
        if field not in record:
            reasons.append(f"missing_required_metadata:{field}")
    cls=record.get("admissibility_class")
    if cls not in ADMISSIBILITY_CLASSES:
        reasons.append(f"invalid_admissibility_class:{cls}")
    custody=record.get("intended_custody")
    training_eligible=(cls=="STABLE_GENERAL_BEHAVIOR" and custody=="train" and not reasons)
    if custody=="train" and cls!="STABLE_GENERAL_BEHAVIOR":
        reasons.append(f"train_forbidden_for_admissibility_class:{cls}")
    if cls=="REJECTED_IDENTITY_CROSSING":
        reasons.append("rejected_identity_crossing")
    return {
        "schema":"STAGE1_ADMISSIBILITY_RESULT_V1",
        "status":"PASS" if not reasons else "HOLD",
        "training_eligible":training_eligible,
        "admissibility_class":cls,
        "reasons":reasons,
    }
