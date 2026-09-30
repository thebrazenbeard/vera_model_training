from __future__ import annotations
import hashlib,json
import pytest
from successor.qwen35.measurement_v1.devloop import append_validation,LedgerError
from successor.qwen35.measurement_v1.selection import select_development_candidate
from successor.qwen35.measurement_v1.statistics import paired_statistics

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def score(validation="b",candidate="d",improvement=.07,lower=.03):
    gains=round(250*improvement)
    cases=[]
    for i in range(400):
        lane="behavioral" if i<250 else ("retention" if i<330 else "adversarial")
        base_correct=not (lane=="behavioral" and i<gains)
        record={"case_id":f"dev-{i:04d}","family_id":f"source-group-{i:04d}",
                "lane":lane,"dimension":"H01" if lane=="behavioral" else None,
                "case_sha256":"1"*64,"decoding_sha256":"f"*64,
                "base":{"status":"PASS" if base_correct else "FAIL",
                        "response_sha256":"2"*64,"model_sha256":"a"*64},
                "candidate":{"status":"PASS","response_sha256":"3"*64,
                             "model_sha256":candidate*64}}
        cases.append(record)
    result=paired_statistics(cases,seed=20260930,replicates=160)
    return {"schema":"QWEN35_DEV_GENERATED_PAIRED_RESULT_V1",
            "status":"DEVELOPMENT_DIAGNOSTIC_UNATTESTED",
            "case_sha256":validation*64,"base_model_sha256":"a"*64,
            "candidate_model_sha256":candidate*64,"decoding_sha256":"f"*64,
            "per_case":cases,"paired":result}

def setup(tmp_path):
    ledger=tmp_path/"ledger.jsonl";scores=[]
    for i,(id,improve,low) in enumerate([("c",.01,-.01),("d",.09,.05)]):
        p=tmp_path/f"score_{id}.json"
        p.write_text(json.dumps(score(candidate=id,improvement=improve,lower=low)),encoding="utf-8")
        entry={"experiment_id":f"trial-{i}","stage":"development_validation",
               "source_commit":"1"*40,"recipe_sha256":"9"*64,"train_sha256":"e"*64,
               "validation_sha256":"b"*64,"results_sha256":sha(p),
               "base_model_sha256":"a"*64,"candidate_model_sha256":id*64}
        append_validation(ledger,entry,blocked_final_digests=set())
        scores.append(p)
    return ledger,scores

def test_select_uses_verified_same_validation_and_never_qualifies(tmp_path):
    ledger,scores=setup(tmp_path)
    out=tmp_path/"candidate.json"
    d=select_development_candidate(ledger,scores,out)
    assert d["status"]=="PROVISIONAL_DEV_CANDIDATE_NOT_QUALIFIED"
    assert d["candidate_model_sha256"]=="d"*64
    assert d["qualified"] is False
    with pytest.raises(LedgerError,match="exists"):
        select_development_candidate(ledger,scores,out)

def test_tampered_result_cannot_be_ranked(tmp_path):
    ledger,scores=setup(tmp_path)
    scores[1].write_text(scores[1].read_text(encoding="utf-8")+" ",encoding="utf-8")
    with pytest.raises(LedgerError,match="hash"):
        select_development_candidate(ledger,scores,tmp_path/"out.json")

def test_result_claim_without_matching_validation_data_rejected(tmp_path):
    ledger,scores=setup(tmp_path)
    r=json.loads(scores[1].read_text(encoding="utf-8"))
    r["case_sha256"]="0"*64
    scores[1].write_text(json.dumps(r),encoding="utf-8")
    with pytest.raises(LedgerError):
        select_development_candidate(ledger,scores,tmp_path/"out.json")

def test_selection_rejects_too_few_dev_cases(tmp_path):
    ledger,scores=setup(tmp_path)
    for p in scores:
        r=json.loads(p.read_text(encoding="utf-8"));r["paired"]["n"]=4
        p.write_text(json.dumps(r),encoding="utf-8")
    with pytest.raises(LedgerError,match="hash"):
        select_development_candidate(ledger,scores,tmp_path/"out.json")

def test_self_authored_paired_percentage_cannot_be_laundered_through_matching_ledger(tmp_path):
    forged=score(candidate="d",improvement=.03)
    forged["paired"]["lanes"]["behavioral"]["delta"]=.99
    p=tmp_path/"forged.json"
    p.write_text(json.dumps(forged),encoding="utf-8")
    ledger=tmp_path/"ledger.jsonl"
    append_validation(ledger,{"experiment_id":"forged-1","stage":"development_validation",
         "source_commit":"1"*40,"recipe_sha256":"9"*64,
         "train_sha256":"e"*64,"validation_sha256":"b"*64,
         "results_sha256":sha(p),
         "base_model_sha256":"a"*64,"candidate_model_sha256":"d"*64},
         blocked_final_digests=set())
    with pytest.raises(LedgerError,match="summary"):
        select_development_candidate(ledger,[p],tmp_path/"selected.json")

def test_dev_selection_rejects_missing_case_level_evidence_even_with_hash_bound_summary(tmp_path):
    forged=score(candidate="d")
    del forged["per_case"]
    p=tmp_path/"forged.json";p.write_text(json.dumps(forged),encoding="utf-8")
    ledger=tmp_path/"ledger.jsonl"
    append_validation(ledger,{"experiment_id":"forged-2","stage":"development_validation",
         "source_commit":"1"*40,"recipe_sha256":"9"*64,
         "train_sha256":"e"*64,"validation_sha256":"b"*64,
         "results_sha256":sha(p),"base_model_sha256":"a"*64,
         "candidate_model_sha256":"d"*64},blocked_final_digests=set())
    with pytest.raises(LedgerError,match="case-level"):
        select_development_candidate(ledger,[p],tmp_path/"selection.json")
