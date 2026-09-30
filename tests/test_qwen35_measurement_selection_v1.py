from __future__ import annotations
import hashlib,json
import pytest
from successor.qwen35.measurement_v1.devloop import append_validation,LedgerError
from successor.qwen35.measurement_v1.selection import select_development_candidate

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def score(validation="b",candidate="d",improvement=.07,lower=.03):
    return {"schema":"QWEN35_DEV_GENERATED_PAIRED_RESULT_V1",
            "status":"DEVELOPMENT_DIAGNOSTIC_UNATTESTED",
            "case_sha256":validation*64,"base_model_sha256":"a"*64,
            "candidate_model_sha256":candidate*64,"decoding_sha256":"f"*64,
            "paired":{"n":400,"lanes":{
                "behavioral":{"n":250,"delta":improvement,"cluster_bootstrap_ci95":[lower,improvement+.05],
                              "independent_families_observed":180},
                "retention":{"n":80,"delta":-.01,"cluster_bootstrap_ci95":[-.04,.02],
                              "independent_families_observed":60},
                "adversarial":{"n":70,"delta":.03,"cluster_bootstrap_ci95":[-.01,.06],
                              "independent_families_observed":55}}}}
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
