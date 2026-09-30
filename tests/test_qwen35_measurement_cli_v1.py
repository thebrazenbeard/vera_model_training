import json
from pathlib import Path
from successor.qwen35.measurement_v1.cli import main

def r(i):
    return {"case_id":f"d-{i}","lane":"retention","dimension":None,
            "prompt":f"Display code {i} exactly.","family_id":f"family-{i//2}",
            "origin":{"source_id":f"source-{i}","source_revision":"v1","license":"CC0-1.0",
                      "source_sha256":"c"*64,"privacy":"public","generation_method":"human"},
            "grader":{"kind":"exact","expected":str(i)}}

def test_cli_split_dev_produces_readable_manifest(tmp_path,capsys):
    path=tmp_path/"all.jsonl"
    path.write_text("\n".join(json.dumps(r(i)) for i in range(50))+"\n",encoding="utf-8")
    dst=tmp_path/"split"
    assert main(["split-dev","--cases",str(path),"--out",str(dst)])==0
    report=json.loads(capsys.readouterr().out.strip())
    assert report["stage"]=="DEVELOPMENT_NOT_FINAL"
    assert report["train_rows"]+report["validation_rows"]==50
    assert (dst/"manifest.json").is_file()
    assert main(["split-dev","--cases",str(path),"--out",str(dst)])!=0

def test_cli_final_preflight_fails_closed_with_tiny_bank(tmp_path,capsys):
    path=tmp_path/"tiny.jsonl";path.write_text(json.dumps(r(1))+"\n",encoding="utf-8")
    out=tmp_path/"gate.json"
    assert main(["final-preflight","--cases",str(path),"--out",str(out)])==3
    decision=json.loads(out.read_text(encoding="utf-8"))
    assert decision["qualified"] is False
    assert decision["status"]=="NOT_QUALIFIED"
    assert "10,000" in decision["reasons"][0]
    assert "independent_review" in decision["remaining_requirements"]
    assert main(["final-preflight","--cases",str(path),"--out",str(out)])==2

def test_cli_validation_ledger_persists_receipt(tmp_path):
    entry={"experiment_id":"experiment-1","stage":"development_validation","source_commit":"1"*40,
           "recipe_sha256":"a"*64,"train_sha256":"c"*64,"validation_sha256":"b"*64,
           "results_sha256":"d"*64,"base_model_sha256":"e"*64,"candidate_model_sha256":"f"*64}
    p=tmp_path/"candidate.json"
    p.write_text(json.dumps(entry),encoding="utf-8")
    ledger=tmp_path/"ledger.jsonl"
    assert main(["record-validation","--entry",str(p),"--ledger",str(ledger)])==0
    items=[json.loads(x) for x in ledger.read_text(encoding="utf-8").splitlines()]
    assert len(items)==1
    assert items[0]["chain_index"]==1
    assert main(["record-validation","--entry",str(p),"--ledger",str(ledger)])==2

def test_cli_select_dev_never_claims_qualification(tmp_path,capsys):
    import hashlib
    from successor.qwen35.measurement_v1.devloop import append_validation
    ledger=tmp_path/"validation.jsonl"
    scores=tmp_path/"scores.json"
    from successor.qwen35.measurement_v1.statistics import paired_statistics
    cases=[]
    for i in range(350):
        lane="behavioral" if i<200 else ("retention" if i<280 else "adversarial")
        gain=lane=="behavioral" and i<28
        cases.append({"case_id":f"cli-{i:04d}","family_id":f"family-{i:04d}",
          "lane":lane,"dimension":f"H{(i%20)+1:02d}" if lane=="behavioral" else None,
          "case_sha256":"1"*64,"decoding_sha256":"d"*64,
          "base":{"status":"FAIL" if gain else "PASS","model_sha256":"a"*64,"response_sha256":"2"*64},
          "candidate":{"status":"PASS","model_sha256":"c"*64,"response_sha256":"3"*64}})
    payload={"schema":"QWEN35_DEV_GENERATED_PAIRED_RESULT_V1",
      "status":"DEVELOPMENT_DIAGNOSTIC_UNATTESTED",
      "case_sha256":"b"*64,"base_model_sha256":"a"*64,
      "candidate_model_sha256":"c"*64,"decoding_sha256":"d"*64,
      "per_case":cases,"paired":paired_statistics(cases,seed=20260930,replicates=160)}
    scores.write_text(json.dumps(payload),encoding="utf-8")
    entry={"experiment_id":"trial-dev","stage":"development_validation",
      "source_commit":"1"*40,"recipe_sha256":"9"*64,
      "train_sha256":"e"*64,"validation_sha256":"b"*64,
      "results_sha256":hashlib.sha256(scores.read_bytes()).hexdigest(),
      "base_model_sha256":"a"*64,"candidate_model_sha256":"c"*64}
    append_validation(ledger,entry,blocked_final_digests=set())
    output=tmp_path/"selected.json"
    exit_code=main(["select-dev","--ledger",str(ledger),"--score",str(scores),"--out",str(output)])
    assert exit_code==0
    receipt=json.loads(output.read_text(encoding="utf-8"))
    assert receipt["qualified"] is False
    assert receipt["status"]=="PROVISIONAL_DEV_CANDIDATE_NOT_QUALIFIED"
    assert main(["select-dev","--ledger",str(ledger),"--score",str(scores),"--out",str(output)])==2
