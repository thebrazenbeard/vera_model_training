from __future__ import annotations
import hashlib,json
from pathlib import Path
import pytest
from successor.qwen35.measurement_v1.devloop import (
    LedgerError, append_validation, read_validation_ledger, write_dev_split, score_paired_files,
)
from successor.qwen35.measurement_v1.observations import canonical_sha

def case(i,group=None):
    return {"case_id":f"dv-{i}","lane":"retention","dimension":None,
            "prompt":f"Report the three-digit code for scenario {i}.",
            "family_id":group or f"group-{i//2}",
            "origin":{"source_id":f"source-{i}","source_revision":"v1","license":"CC0-1.0",
                      "source_sha256":"c"*64,"privacy":"public","generation_method":"human"},
            "grader":{"kind":"exact","expected":str(i).zfill(3)},
            "review_receipt_id":None}
def digest(content):
    return hashlib.sha256(content.encode("utf-8")).hexdigest()
def entry(index, val="b"):
    return {"experiment_id":f"try-{index}",
            "stage":"development_validation","source_commit":"1"*40,"recipe_sha256":"a"*64,
            "train_sha256":"c"*64,"validation_sha256":val*64,
            "results_sha256":digest(str(index)),"base_model_sha256":"d"*64,
            "candidate_model_sha256":"e"*64}
def observed(c,cond,answer,model_sha):
    return {"case_id":c["case_id"],"condition":cond,"case_sha256":canonical_sha(c),
            "model_sha256":model_sha,"rendered_input_sha256":"f"*64,
            "decoding_sha256":"0"*64,"response":answer,
            "response_sha256":digest(answer),"origin":"model_generation_claim"}

def test_split_writes_disjoint_verified_manifest_without_overwrite(tmp_path):
    rows=[case(i) for i in range(60)]
    input_file=tmp_path/"dev.jsonl"
    input_file.write_text("\n".join(map(json.dumps,rows))+"\n",encoding="utf-8")
    out=tmp_path/"split"
    manifest=write_dev_split(input_file,out,seed=20260930)
    assert manifest["train_rows"]+manifest["validation_rows"]==60
    t=[json.loads(x) for x in (out/"train.jsonl").read_text(encoding="utf-8").splitlines()]
    v=[json.loads(x) for x in (out/"validation.jsonl").read_text(encoding="utf-8").splitlines()]
    assert not ({x["family_id"] for x in t}&{x["family_id"] for x in v})
    assert manifest["train_sha256"]==hashlib.sha256((out/"train.jsonl").read_bytes()).hexdigest()
    with pytest.raises(LedgerError,match="exists"):
        write_dev_split(input_file,out,seed=20260930)

def test_validation_log_is_append_only_hash_chained(tmp_path):
    p=tmp_path/"experiments.jsonl"
    r=append_validation(p,entry(1),blocked_final_digests=set())
    assert r["chain_index"]==1
    assert read_validation_ledger(p)[0]["experiment_id"]=="try-1"
    r2=append_validation(p,entry(2),blocked_final_digests=set())
    assert r2["chain_index"]==2
    assert r2["previous_entry_sha256"]==r["entry_sha256"]
    raw=p.read_text(encoding="utf-8")
    p.write_text(raw.replace("try-1","changed"),encoding="utf-8")
    with pytest.raises(LedgerError,match="hash"):
        read_validation_ledger(p)

def test_validation_budget_3_and_no_final_reuse(tmp_path):
    p=tmp_path/"ledger.jsonl"
    with pytest.raises(LedgerError,match="consumed final"):
        append_validation(p,entry(0),blocked_final_digests={"b"*64})
    for i in range(3):
        append_validation(p,entry(i),blocked_final_digests=set())
    with pytest.raises(LedgerError,match="budget"):
        append_validation(p,entry(5),blocked_final_digests=set())
    assert len(read_validation_ledger(p))==3

def test_no_final_data_or_identical_train_validation_in_selection(tmp_path):
    p=tmp_path/"ledger.jsonl"
    e=entry(1);e["stage"]="final"
    with pytest.raises(LedgerError,match="stage"):
        append_validation(p,e,blocked_final_digests=set())
    e=entry(1);e["train_sha256"]=e["validation_sha256"]
    with pytest.raises(LedgerError,match="same"):
        append_validation(p,e,blocked_final_digests=set())
    assert not p.exists()

def test_scores_only_bound_generated_observation_pairs(tmp_path):
    c=[case(10),case(11)]
    cases=tmp_path/"cases.jsonl";cases.write_text("\n".join(map(json.dumps,c))+"\n",encoding="utf-8")
    b=[observed(x,"base",x["grader"]["expected"],"a"*64) for x in c]
    a=[observed(x,"candidate",x["grader"]["expected"],"b"*64) for x in c]
    paths=[tmp_path/"base.jsonl",tmp_path/"candidate.jsonl"]
    for p,records in zip(paths,[b,a]):
        p.write_text("\n".join(map(json.dumps,records))+"\n",encoding="utf-8")
    dst=tmp_path/"scored.json"
    result=score_paired_files(cases,paths[0],paths[1],dst,base_sha="a"*64,candidate_sha="b"*64,decoding_sha="0"*64)
    assert result["status"]=="DEVELOPMENT_DIAGNOSTIC_UNATTESTED"
    assert result["paired"]["n"]==2
    assert result["paired"]["lanes"]["retention"]["accuracy_candidate"]==1
    with pytest.raises(LedgerError,match="exists"):
        score_paired_files(cases,paths[0],paths[1],dst,base_sha="a"*64,candidate_sha="b"*64,decoding_sha="0"*64)
    paths[1].write_text(json.dumps(a[0])+"\n",encoding="utf-8")
    with pytest.raises(LedgerError,match="missing"):
        score_paired_files(cases,paths[0],paths[1],tmp_path/"fail.json",base_sha="a"*64,candidate_sha="b"*64,decoding_sha="0"*64)

def test_development_split_cannot_import_consumed_v4_prompt(tmp_path):
    from successor.qwen35.measurement_v1.devloop import LedgerError
    root=Path(__file__).resolve().parents[1]
    old=json.loads((root/"successor/qwen35/qualification/final_holdout_v4.jsonl").read_text(encoding="utf-8").splitlines()[0])
    rows=[case(i) for i in range(60)]
    rows[0]["prompt"]=old["prompt"]
    f=tmp_path/"old_final_repackaged.jsonl"
    f.write_text("\n".join(json.dumps(r) for r in rows)+"\n",encoding="utf-8")
    with pytest.raises(LedgerError,match="consumed"):
        write_dev_split(f,tmp_path/"should_not_exist",seed=20260930)
