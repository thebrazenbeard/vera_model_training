"""Provisional V5 candidate selection using only frozen development validation.

Never selects from a final holdout. Hash-chain and score-file identity must
both reconcile, including baseline, candidate, validation set and decoding.
No result can assert independent grading or deployment qualification.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from .devloop import LedgerError, read_validation_ledger, write_new

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def select_development_candidate(ledger_path,score_paths,output,*,minimum_cases=300):
    out=Path(output)
    if out.exists():
        raise LedgerError("selection output exists; no overwrite")
    records=read_validation_ledger(Path(ledger_path))
    if not records:
        raise LedgerError("empty development validation ledger")
    by_hash={}
    for path in score_paths:
        d=sha(path)
        if d in by_hash:
            raise LedgerError("duplicate score file supplied")
        by_hash[d]=Path(path)
    if set(by_hash)!={entry["results_sha256"] for entry in records}:
        raise LedgerError("result file hash mismatch with ledger")
    if len({e["validation_sha256"] for e in records})!=1:
        raise LedgerError("different validation cohorts; ranking invalid")
    if len({e["base_model_sha256"] for e in records})!=1:
        raise LedgerError("different baseline identities; ranking invalid")
    qualified=[]
    inspected=[]
    decode_hashes=set()
    for entry in records:
        path=by_hash[entry["results_sha256"]]
        result=json.loads(path.read_text(encoding="utf-8"))
        if (result.get("schema")!="QWEN35_DEV_GENERATED_PAIRED_RESULT_V1"
            or result.get("status")!="DEVELOPMENT_DIAGNOSTIC_UNATTESTED"
            or result.get("case_sha256")!=entry["validation_sha256"]
            or result.get("base_model_sha256")!=entry["base_model_sha256"]
            or result.get("candidate_model_sha256")!=entry["candidate_model_sha256"]):
            raise LedgerError("result identity/provenance mismatch")
        decode_hashes.add(result.get("decoding_sha256"))
        stats=result.get("paired",{})
        lanes=stats.get("lanes",{})
        inspected.append(entry["experiment_id"])
        if stats.get("n",0)<minimum_cases:
            continue
        if not all(lane in lanes for lane in ("behavioral","retention","adversarial")):
            continue
        beh=lanes["behavioral"]
        ret=lanes["retention"]
        adv=lanes["adversarial"]
        ci=beh.get("cluster_bootstrap_ci95")
        if (ci is None or len(ci)!=2 or
            beh.get("independent_families_observed",0)<50 or
            ret.get("independent_families_observed",0)<30 or
            adv.get("independent_families_observed",0)<30):
            continue
        if beh.get("delta",-1)<0.02 or ci[0]<0:
            continue
        if ret.get("delta",-1)<-0.05 or adv.get("delta",-1)<0:
            continue
        qualified.append((ci[0],beh["delta"],entry["candidate_model_sha256"],entry["experiment_id"]))
    if len(decode_hashes)!=1 or not all(isinstance(x,str) and len(x)==64 for x in decode_hashes):
        raise LedgerError("inconsistent decoding configuration across development trials")
    if qualified:
        selected=max(qualified)
        status="PROVISIONAL_DEV_CANDIDATE_NOT_QUALIFIED"
        chosen=selected[2]
        chosen_trial=selected[3]
    else:
        status="NO_DEVELOPMENT_CANDIDATE_SELECTED"
        chosen=None
        chosen_trial=None
    receipt={"schema":"QWEN35_PROVISIONAL_DEVELOPMENT_SELECTION_V1",
             "status":status,"qualified":False,
             "candidate_model_sha256":chosen,"selected_experiment_id":chosen_trial,
             "validation_sha256":records[0]["validation_sha256"],
             "base_model_sha256":records[0]["base_model_sha256"],
             "decoding_sha256":next(iter(decode_hashes)),
             "ledger_sha256":sha(ledger_path),
             "inspected_experiments":inspected,
             "selection_rule":"Among eligible cohorts: maximum lower family-cluster CI, then point delta; final data prohibited",
             "effect":"NONE / NO_MODEL_ACTIVATION / NO_FINAL_EXAM_CONSUMED"}
    out.parent.mkdir(parents=True,exist_ok=True)
    write_new(out,(json.dumps(receipt,sort_keys=True,indent=2)+"\n").encode("utf-8"))
    return receipt
