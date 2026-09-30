from __future__ import annotations
import hashlib,json,pathlib,collections
import pytest
ROOT=pathlib.Path(__file__).resolve().parents[1]
Q=ROOT/"successor/qwen35/qualification"
C=ROOT/"successor/qwen35/corpus"
A=ROOT/"successor/qwen35/artifacts"
SUBJECT="Vera-Qwen3.5-4B-Behavior-V1-v4-candidate-a"
FILES={"behavioral":("final_holdout_v4.jsonl",100),"retention":("final_retention_v4.jsonl",20),"adversarial_proxy":("final_adversarial_proxy_v4.jsonl",20)}
def rows(path):
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]
def test_v4_subject_is_trained_and_frozen_before_new_data():
    m=json.loads((A/"Vera-Qwen3.5-4B-Behavior-V1-v4-adapter-manifest.json").read_text())
    assert m["source_head"]=="7a76320525fe8550282fff281a565f22de90723b"
    assert m["qualification_status"]=="NOT_YET_RUN"
    assert m["adapter_files"]["adapter_model.safetensors"]["bytes"]>0
    assert m["corpus_sha256"]==hashlib.sha256((C/"vera_qwen35_behavior_v4_sft.jsonl").read_bytes()).hexdigest()
def test_fresh_v4_suite_counts_balanced_and_unique():
    collected=[]
    for name,(file,count) in FILES.items():
        sample=rows(Q/file)
        assert len(sample)==count
        assert all({"record_id","prompt","chosen","rejected"}<=set(r) for r in sample)
        assert all(r["chosen"].strip()!=r["rejected"].strip() for r in sample)
        collected.extend(sample)
    assert len({x["record_id"] for x in collected})==140
    assert len({x["prompt"] for x in collected})==140
    assert collections.Counter(x["dimension"] for x in rows(Q/"final_holdout_v4.jsonl"))=={f"H{i:02d}":5 for i in range(1,21)}
def test_v4_spec_and_freeze_bind_new_bytes():
    spec_path=Q/"FINAL_QUALIFICATION_V4_SPEC.json"
    spec=json.loads(spec_path.read_text(encoding="utf-8"))
    freeze=json.loads((Q/"FINAL_QUALIFICATION_V4_FREEZE.json").read_text(encoding="utf-8"))
    assert spec["subject"]==SUBJECT and freeze["evaluation_started"] is False
    assert hashlib.sha256(spec_path.read_bytes()).hexdigest()==freeze["spec_sha256"]
    assert spec["adapter"]["adapter_model_sha256"]==json.loads((A/"Vera-Qwen3.5-4B-Behavior-V1-v4-adapter-manifest.json").read_text())["adapter_files"]["adapter_model.safetensors"]["sha256"]
    for key,(name,count) in FILES.items():
        assert spec["suites"][key]["rows"]==count
        assert spec["suites"][key]["sha256"]==hashlib.sha256((Q/name).read_bytes()).hexdigest()
        assert freeze["suite_sha256"][key]==spec["suites"][key]["sha256"]
    assert freeze["screening"]["lexical_sequence"]["failures"]==0
    assert freeze["screening"]["embedding"]["failures"]==0
def test_v4_automated_thresholds_match_predeclared_v3():
    old=json.loads((Q/"FINAL_QUALIFICATION_V3_SPEC.json").read_text(encoding="utf-8"))["pass_contract"]
    new=json.loads((Q/"FINAL_QUALIFICATION_V4_SPEC.json").read_text(encoding="utf-8"))["pass_contract"]
    assert new==old
def test_v4_evaluation_is_not_old_holdout_repackaged():
    consumed=json.loads((C/"v4_consumed_evidence_registry.json").read_text(encoding="utf-8"))["entries"]
    prior=set()
    for entry in consumed:
        p=ROOT/entry["path"]
        if p.suffix==".jsonl":
            prior.update(" ".join(x["prompt"].casefold().split()) for x in rows(p) if "prompt" in x)
    for name,_ in FILES.values():
        assert all(" ".join(r["prompt"].casefold().split()) not in prior for r in rows(Q/name))
