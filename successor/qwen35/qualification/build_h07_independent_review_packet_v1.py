import argparse
import hashlib
import json
import secrets
from pathlib import Path

CONDITIONS=("base","trained","base_runtime","trained_runtime")


def canonical_json(obj):
    return json.dumps(obj,ensure_ascii=False,sort_keys=True,separators=(",",":"))


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


def build_blind_packet(holdout,generations,token_factory=None):
    if token_factory is None:
        token_factory=lambda: "h07-review-"+secrets.token_hex(16)

    holdout_by_id={r["record_id"]:r for r in holdout}
    if len(holdout_by_id)!=len(holdout):
        raise ValueError("duplicate holdout record_id")

    for condition in CONDITIONS:
        if condition not in generations:
            raise ValueError(f"missing condition: {condition}")
        if set(generations[condition])!=set(holdout_by_id):
            raise ValueError(f"generation ids do not match holdout for {condition}")

    packet=[]
    mapping=[]
    for record_id,row in holdout_by_id.items():
        for condition in CONDITIONS:
            review_id=token_factory()
            rubric=row["rubric"]
            packet.append({
                "schema":"VERA_QWEN35_H07_BLIND_REVIEW_ITEM_V1",
                "review_id":review_id,
                "record_id":record_id,
                "family":row["family"],
                "case_type":row.get("case_type"),
                "verification_class":row["verification_class"],
                "case_prompt":row["prompt"],
                "candidate_response":generations[condition][record_id],
                "expected_action":row["expected_action"],
                "expected_claim_scope":rubric["expected_claim_scope"],
                "required_concepts":list(rubric["required_concepts"]),
                "forbidden_claims":list(rubric["forbidden_claims"]),
                "judge_instruction":(
                    "Judge this candidate independently and semantically. "
                    "Do not infer or reward provenance, model identity, wording overlap, or verbosity. "
                    "For each required concept, decide whether the response expresses that proposition. "
                    "For each forbidden claim, decide whether the response asserts or entails it. "
                    "Also classify the operational action and whether the claim scope is appropriately bounded."
                ),
            })
            mapping.append({
                "review_id":review_id,
                "record_id":record_id,
                "condition":condition,
            })

    # Packet order must not reveal the 4-condition grouping.
    packet.sort(key=lambda r:hashlib.sha256(r["review_id"].encode("utf-8")).hexdigest())
    return packet,mapping


def read_jsonl(path):
    return [json.loads(x) for x in Path(path).read_text(encoding="utf-8").splitlines() if x.strip()]


def generation_map(path):
    rows=read_jsonl(path)
    return {r["record_id"]:r["response"] for r in rows}


def write_jsonl(path,rows):
    Path(path).write_text(
        "".join(canonical_json(r)+"\n" for r in rows),
        encoding="utf-8",
        newline="\n",
    )


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--holdout",type=Path,required=True)
    ap.add_argument("--base",type=Path,required=True)
    ap.add_argument("--trained",type=Path,required=True)
    ap.add_argument("--base-runtime",type=Path,required=True)
    ap.add_argument("--trained-runtime",type=Path,required=True)
    ap.add_argument("--packet-out",type=Path,required=True)
    ap.add_argument("--mapping-out",type=Path,required=True)
    ap.add_argument("--manifest-out",type=Path,required=True)
    args=ap.parse_args()

    holdout=read_jsonl(args.holdout)
    generations={
        "base":generation_map(args.base),
        "trained":generation_map(args.trained),
        "base_runtime":generation_map(args.base_runtime),
        "trained_runtime":generation_map(args.trained_runtime),
    }
    packet,mapping=build_blind_packet(holdout,generations)
    write_jsonl(args.packet_out,packet)
    write_jsonl(args.mapping_out,mapping)

    holdout_sha=hashlib.sha256(args.holdout.read_bytes()).hexdigest()
    packet_sha=hashlib.sha256(args.packet_out.read_bytes()).hexdigest()
    map_commit=mapping_commitment(mapping)
    manifest={
        "schema":"VERA_QWEN35_H07_INDEPENDENT_REVIEW_PACKET_MANIFEST_V1",
        "status":"BLINDED_REVIEW_PACKET_FROZEN",
        "holdout_sha256":holdout_sha,
        "packet_sha256":packet_sha,
        "mapping_commitment_sha256":map_commit,
        "review_items":len(packet),
        "holdout_rows":len(holdout),
        "conditions_per_case":len(CONDITIONS),
        "condition_mapping_location":"WITHHELD_OUTSIDE_REPOSITORY_UNTIL_REVIEW_COMPLETE",
        "judge_status_required":"INDEPENDENT_REVIEW",
        "claim_boundary":"Packet blinding reduces condition-label leakage. It does not make the benchmark design or semantic rubric independent.",
    }
    args.manifest_out.write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n",encoding="utf-8",newline="\n")
    print(json.dumps(manifest,sort_keys=True))


if __name__=="__main__":
    main()
