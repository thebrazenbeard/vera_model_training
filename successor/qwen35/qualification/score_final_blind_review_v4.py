from __future__ import annotations
import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
QUAL=ROOT/"successor"/"qwen35"/"qualification"

def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]

def expected_mapping(selection_sha: str, record_ids: list[str]) -> list[dict]:
    pairs=[
        {"record_id":record_id,"condition":condition}
        for record_id in record_ids
        for condition in ("BASE","ADAPTER")
    ]
    ordered=sorted(
        pairs,
        key=lambda x: hashlib.sha256(
            (selection_sha+"|"+x["record_id"]+"|"+x["condition"]).encode()
        ).hexdigest(),
    )
    return [
        {"blind_id":f"blind-{index:03d}","record_id":item["record_id"],"condition":item["condition"]}
        for index,item in enumerate(ordered,1)
    ]

def main(args) -> int:
    spec=json.loads((QUAL/"FINAL_QUALIFICATION_V4_SPEC.json").read_text(encoding="utf-8"))
    packet_manifest=json.loads(args.packet_manifest.read_text(encoding="utf-8"))
    judgment_manifest=json.loads(args.judgments_manifest.read_text(encoding="utf-8"))
    selection=json.loads((QUAL/"FINAL_BLIND_REVIEW_V4_SELECTION.json").read_text(encoding="utf-8"))
    rubrics_path=QUAL/"FINAL_BLIND_REVIEW_V4_RUBRICS.json"
    if packet_manifest.get("rubrics_sha256")!=sha256(rubrics_path):
        raise RuntimeError("rubric file hash mismatch")
    if sha256(args.blind_packet)!=packet_manifest["blind_packet_sha256"]:
        raise RuntimeError("blind packet hash mismatch")
    blind_items=load_jsonl(args.blind_packet)
    if len(blind_items)!=packet_manifest["item_count"]:
        raise RuntimeError("blind packet count mismatch")
    if packet_manifest.get("selection_sha256")!=sha256(QUAL/"FINAL_BLIND_REVIEW_V4_SELECTION.json"):
        raise RuntimeError("blind selection hash mismatch")
    if packet_manifest.get("subject")!=spec["subject"]:
        raise RuntimeError("blind packet subject mismatch")
    if packet_manifest.get("adapter_sha256")!=spec["adapter"]["archive_sha256"]:
        raise RuntimeError("blind packet adapter archive mismatch")
    if not packet_manifest.get("adapter_model_sha256") or not packet_manifest.get("automated_result_sha256"):
        raise RuntimeError("blind packet missing adapter binding")
    judge_binding_path=QUAL/"FINAL_JUDGE_V4_BINDING.json"
    if judgment_manifest.get("judge_verified") is not True:
        raise RuntimeError("judge identity was not verified")
    if judgment_manifest.get("judge_binding_sha256")!=sha256(judge_binding_path):
        raise RuntimeError("judge binding hash mismatch")
    if judgment_manifest.get("blind_packet_sha256")!=packet_manifest["blind_packet_sha256"]:
        raise RuntimeError("judge packet hash mismatch")
    if sha256(args.mapping)!=packet_manifest["mapping_sha256"]:
        raise RuntimeError("mapping hash mismatch")
    if sha256(args.judgments)!=judgment_manifest["judgments_sha256"]:
        raise RuntimeError("judgments hash mismatch")
    if judgment_manifest.get("mapping_accessed") is not False:
        raise RuntimeError("judgments were not frozen blind")
    mapping_doc=json.loads(args.mapping.read_text(encoding="utf-8"))
    mapping_items=mapping_doc["items"]
    mapping={x["blind_id"]:x for x in mapping_items}
    blind_by_id={x["blind_id"]:x for x in blind_items}
    judgments=load_jsonl(args.judgments)
    judgment_ids=[x["blind_id"] for x in judgments]
    expected_count=packet_manifest["item_count"]
    if len(mapping_items)!=expected_count or len(mapping)!=expected_count:
        raise RuntimeError("mapping coverage mismatch")
    if len(blind_items)!=expected_count or len(blind_by_id)!=expected_count:
        raise RuntimeError("blind packet coverage mismatch")
    conditions=Counter(x.get("condition") for x in mapping_items)
    if conditions!={"BASE":20,"ADAPTER":20}:
        raise RuntimeError("mapping condition balance mismatch")
    expected=expected_mapping(packet_manifest["selection_sha256"],selection["record_ids"])
    if mapping_items!=expected:
        raise RuntimeError("mapping deterministic assignment mismatch")
    record_counts=Counter(x.get("record_id") for x in mapping_items)
    if set(record_counts)!=set(selection["record_ids"]) or any(record_counts[r]!=2 for r in selection["record_ids"]):
        raise RuntimeError("mapping selection coverage mismatch")
    if len(judgments)!=expected_count or len(set(judgment_ids))!=expected_count:
        raise RuntimeError("judgment coverage mismatch")
    if set(judgment_ids)!=set(mapping) or set(judgment_ids)!=set(blind_by_id):
        raise RuntimeError("judgment blind-id set mismatch")
    for blind_id,source in blind_by_id.items():
        if source.get("record_id")!=mapping[blind_id].get("record_id"):
            raise RuntimeError("blind packet mapping metadata mismatch")
    for j in judgments:
        source=blind_by_id[j["blind_id"]]
        if j.get("record_id")!=source.get("record_id") or j.get("dimension")!=source.get("dimension"):
            raise RuntimeError("judgment metadata mismatch")
    if any(x.get("verdict") not in {"PASS","FAIL","CRITICAL_FAIL"} for x in judgments):
        raise RuntimeError("invalid blind judgment label")
    counts=defaultdict(Counter)
    per_dimension=defaultdict(lambda:defaultdict(Counter))
    for j in judgments:
        m=mapping[j["blind_id"]]
        condition=m["condition"]
        counts[condition][j["verdict"]]+=1
        per_dimension[condition][j["dimension"]][j["verdict"]]+=1
    summary={}
    for condition in ("BASE","ADAPTER"):
        total=sum(counts[condition].values())
        passed=counts[condition]["PASS"]
        summary[condition]={
            "n":total,
            "pass":passed,
            "fail":counts[condition]["FAIL"],
            "critical_fail":counts[condition]["CRITICAL_FAIL"],
            "pass_rate":passed/total if total else 0.0,
            "by_dimension":{d:dict(c) for d,c in sorted(per_dimension[condition].items())},
        }
    contract=spec["pass_contract"]["independent_blind_review"]
    reasons=[]
    adapter=summary["ADAPTER"]
    base=summary["BASE"]
    if adapter["pass_rate"] < contract["min_adapter_pass_rate"]:
        reasons.append("adapter_pass_rate_below_minimum")
    if contract["require_adapter_pass_rate_gte_base"] and adapter["pass_rate"] < base["pass_rate"]:
        reasons.append("adapter_pass_rate_below_base")
    if adapter["critical_fail"] > contract["max_adapter_critical_failures"]:
        reasons.append("adapter_critical_failures_exceed_maximum")
    result={
        "schema":"QWEN35_FINAL_BLIND_REVIEW_RESULT_V4",
        "subject":spec["subject"],
        "adapter_sha256":packet_manifest["adapter_sha256"],
        "adapter_model_sha256":packet_manifest["adapter_model_sha256"],
        "automated_result_sha256":packet_manifest["automated_result_sha256"],
        "blind_packet_sha256":packet_manifest["blind_packet_sha256"],
        "mapping_sha256":packet_manifest["mapping_sha256"],
        "judgments_sha256":judgment_manifest["judgments_sha256"],
        "judge_binding_sha256":judgment_manifest["judge_binding_sha256"],
        "judge":judgment_manifest,
        "conditions":summary,
        "independent_review_pass":not reasons,
        "failure_reasons":reasons,
        "independence_boundary":"Judge model is separately frozen from the Qwen3.5 subject and sees condition-hidden responses without preferred answers. The judge script has no mapping argument, but OS-level filesystem isolation from the private mapping is not established. Benchmark design and orchestration are not independent of the current project runtime.",
    }
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8",newline="\n")
    print("BLIND_RESULT="+json.dumps({k:v for k,v in result.items() if k!="conditions"},sort_keys=True))
    return 0

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--blind-packet",type=Path,required=True)
    ap.add_argument("--packet-manifest",type=Path,required=True)
    ap.add_argument("--mapping",type=Path,required=True)
    ap.add_argument("--judgments",type=Path,required=True)
    ap.add_argument("--judgments-manifest",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    raise SystemExit(main(ap.parse_args()))