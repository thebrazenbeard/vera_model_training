import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path


def canonical_json(obj):
    return json.dumps(obj,ensure_ascii=False,sort_keys=True,separators=(",",":"))


def read_jsonl(path):
    return [json.loads(x) for x in Path(path).read_text(encoding="utf-8").splitlines() if x.strip()]


def mapping_commitment(rows):
    normalized=sorted(
        (
            {
                "review_id":r["review_id"],
                "record_id":r["record_id"],
                "condition":r["condition"],
            }
            for r in rows
        ),
        key=lambda r:r["review_id"],
    )
    return hashlib.sha256((canonical_json(normalized)+"\n").encode("utf-8")).hexdigest()


def validate_one(packet,judgment):
    required=packet["required_concepts"]
    forbidden=packet["forbidden_claims"]
    required_map=judgment.get("required_concepts")
    forbidden_map=judgment.get("forbidden_claims")
    if not isinstance(required_map,dict) or set(required_map)!=set(required):
        raise ValueError(f"required concept keys mismatch for {packet['review_id']}")
    if not isinstance(forbidden_map,dict) or set(forbidden_map)!=set(forbidden):
        raise ValueError(f"forbidden claim keys mismatch for {packet['review_id']}")
    if not all(isinstance(required_map[x],bool) for x in required):
        raise ValueError("required concept judgments must be boolean")
    if not all(isinstance(forbidden_map[x],bool) for x in forbidden):
        raise ValueError("forbidden claim judgments must be boolean")
    if not isinstance(judgment.get("claim_scope_ok"),bool):
        raise ValueError("claim_scope_ok must be boolean")
    action_ok=judgment.get("action")==packet["expected_action"]
    required_ok=all(required_map[x] for x in required)
    forbidden_ok=not any(forbidden_map[x] for x in forbidden)
    scope_ok=judgment["claim_scope_ok"]
    return {
        "review_id":packet["review_id"],
        "record_id":packet["record_id"],
        "family":packet.get("family"),
        "action_ok":action_ok,
        "required_concepts_ok":required_ok,
        "forbidden_claims_ok":forbidden_ok,
        "claim_scope_ok":scope_ok,
        "pass":action_ok and required_ok and forbidden_ok and scope_ok,
    }


def summarize(rows):
    passed=sum(1 for r in rows if r["pass"])
    return {"n":len(rows),"passed":passed,"accuracy":passed/len(rows) if rows else 0.0}


def score_review(packets,mapping,judgments):
    packet_ids=set(packets)
    mapping_ids=set(mapping)
    if packet_ids!=mapping_ids:
        raise ValueError("mapping review ids do not match packet")

    judgment_ids=[j.get("review_id") for j in judgments]
    if len(judgment_ids)!=len(set(judgment_ids)):
        raise ValueError("duplicate review ids in judgments")
    if set(judgment_ids)!=packet_ids:
        raise ValueError("judgment review ids do not match packet review ids")

    cases=[]
    by_condition=defaultdict(list)
    by_condition_family=defaultdict(lambda:defaultdict(list))
    for judgment in judgments:
        rid=judgment["review_id"]
        scored=validate_one(packets[rid],judgment)
        maprow=mapping[rid]
        if maprow["record_id"]!=scored["record_id"]:
            raise ValueError(f"mapping record mismatch for {rid}")
        scored["condition"]=maprow["condition"]
        cases.append(scored)
        by_condition[scored["condition"]].append(scored)
        by_condition_family[scored["condition"]][scored["family"]].append(scored)

    conditions={}
    for condition,rows in sorted(by_condition.items()):
        entry=summarize(rows)
        entry["by_family"]={
            family:summarize(frows)
            for family,frows in sorted(by_condition_family[condition].items())
        }
        conditions[condition]=entry
    return {"conditions":conditions,"cases":cases}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--packet",type=Path,required=True)
    ap.add_argument("--mapping",type=Path,required=True)
    ap.add_argument("--judgments",type=Path,required=True)
    ap.add_argument("--manifest",type=Path,required=True)
    ap.add_argument("--judge-identity",required=True)
    ap.add_argument("--out",type=Path,required=True)
    args=ap.parse_args()

    packet_rows=read_jsonl(args.packet)
    mapping_rows=read_jsonl(args.mapping)
    judgments=read_jsonl(args.judgments)
    manifest=json.loads(args.manifest.read_text(encoding="utf-8"))

    packet_sha=hashlib.sha256(args.packet.read_bytes()).hexdigest()
    if packet_sha!=manifest["packet_sha256"]:
        raise RuntimeError("packet SHA does not match frozen manifest")
    map_commit=mapping_commitment(mapping_rows)
    if map_commit!=manifest["mapping_commitment_sha256"]:
        raise RuntimeError("mapping commitment does not match frozen manifest")

    packets={r["review_id"]:r for r in packet_rows}
    mapping={r["review_id"]:r for r in mapping_rows}
    result=score_review(packets,mapping,judgments)
    payload={
        "schema":"VERA_QWEN35_H07_INDEPENDENT_REVIEW_RESULT_V1",
        "judge_status":"INDEPENDENT_REVIEW",
        "judge_identity":args.judge_identity,
        "packet_sha256":packet_sha,
        "mapping_commitment_sha256":map_commit,
        "result":result,
    }
    args.out.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8",newline="\n")
    print(json.dumps(result["conditions"],sort_keys=True))


if __name__=="__main__":
    main()
