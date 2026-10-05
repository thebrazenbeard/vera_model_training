from __future__ import annotations
import hashlib, json
from collections import Counter

REQUIRED_RECORD_FIELDS = (
    "stable_record_id","exact_source_provenance","construction_commit",
    "capability_family","semantic_template_ancestry","privacy_class",
    "mutable_stable_class","known_confounds","intended_custody",
    "content_hash","admissibility_class",
)

class Stage1ManifestHold(ValueError):
    pass

def _sha256(value: object) -> str:
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode("utf-8")).hexdigest()

def _require_hex(name: str, value: str, length: int) -> None:
    if not isinstance(value,str) or len(value)!=length or any(ch not in "0123456789abcdef" for ch in value):
        raise Stage1ManifestHold(f"{name} must be lowercase hex length {length}")

def build_stage1_manifest(records: list[dict], *, source_head: str, plan_blob: str) -> dict:
    _require_hex("source_head", source_head, 40)
    _require_hex("plan_blob", plan_blob, 40)
    normalized=[]
    seen=set()
    for index, record in enumerate(records):
        if not isinstance(record,dict):
            raise Stage1ManifestHold(f"record {index} is not an object")
        missing=[field for field in REQUIRED_RECORD_FIELDS if field not in record]
        if missing:
            raise Stage1ManifestHold(f"record {index} missing fields: {','.join(missing)}")
        record_id=record["stable_record_id"]
        if not isinstance(record_id,str) or not record_id:
            raise Stage1ManifestHold(f"record {index} stable_record_id invalid")
        if record_id in seen:
            raise Stage1ManifestHold(f"duplicate stable_record_id: {record_id}")
        seen.add(record_id)
        normalized.append(dict(record))
    normalized.sort(key=lambda row: row["stable_record_id"])
    identity={
        "schema":"STAGE1_CORPUS_MANIFEST_V1",
        "source_head":source_head,
        "plan_blob":plan_blob,
        "record_count":len(normalized),
        "record_ids":[row["stable_record_id"] for row in normalized],
        "capability_counts":dict(sorted(Counter(row["capability_family"] for row in normalized).items())),
        "custody_counts":dict(sorted(Counter(row["intended_custody"] for row in normalized).items())),
        "admissibility_counts":dict(sorted(Counter(row["admissibility_class"] for row in normalized).items())),
        "records_sha256":_sha256(normalized),
    }
    return {**identity,"manifest_sha256":_sha256(identity)}
