"""CLI for measurable development work, not an automatic model-promotion mechanism."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from .cases import CaseError, normalized_prompt, preflight_final_bank, read_cases
from .devloop import LedgerError, append_validation, score_paired_files, write_dev_split, write_new

ROOT=Path(__file__).resolve().parents[3]
Q=ROOT/"successor/qwen35/qualification"
CONSUMED_FINAL_FILES=[
    "final_holdout_v3.jsonl","final_retention_v3.jsonl","final_adversarial_proxy_v3.jsonl",
    "final_holdout_v4.jsonl","final_retention_v4.jsonl","final_adversarial_proxy_v4.jsonl",
    "history_behavior_holdout_v1.jsonl","h07_final_holdout_v1.jsonl",
]

def consumed_evidence():
    digests=set()
    prompts=set()
    for name in CONSUMED_FINAL_FILES:
        path=Q/name
        if not path.exists():
            raise CaseError("consumed-final source missing: "+name)
        digests.add(hashlib.sha256(path.read_bytes()).hexdigest())
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                item=json.loads(line)
                if "prompt" in item:
                    prompts.add(normalized_prompt(item["prompt"]))
    return digests,prompts

def main(argv=None):
    ap=argparse.ArgumentParser(prog="qwen35.measurement_v1")
    sub=ap.add_subparsers(dest="command",required=True)
    split=sub.add_parser("split-dev",help="freeze grouped development and validation partitions")
    split.add_argument("--cases",type=Path,required=True)
    split.add_argument("--out",type=Path,required=True)
    split.add_argument("--seed",type=int,default=20260930)
    record=sub.add_parser("record-validation",help="append validation receipt; maximum three per ledger")
    record.add_argument("--entry",type=Path,required=True)
    record.add_argument("--ledger",type=Path,required=True)
    paired=sub.add_parser("score-paired",help="grade claimed generated responses, model-only diagnostic")
    for name in ("cases","base","candidate","out"):
        paired.add_argument("--"+name,type=Path,required=True)
    for name in ("base-sha","candidate-sha","decoding-sha"):
        paired.add_argument("--"+name,required=True)
    final=sub.add_parser("final-preflight",help="fail-closed structural final-bank review (never promotes)")
    final.add_argument("--cases",type=Path,required=True)
    final.add_argument("--out",type=Path,required=True)
    a=ap.parse_args(argv)
    try:
        if a.command=="split-dev":
            result=write_dev_split(a.cases,a.out,seed=a.seed)
        elif a.command=="record-validation":
            blocked,_=consumed_evidence()
            entry=json.loads(a.entry.read_text(encoding="utf-8"))
            result=append_validation(a.ledger,entry,blocked_final_digests=blocked)
        elif a.command=="score-paired":
            result=score_paired_files(a.cases,a.base,a.candidate,a.out,
                                      base_sha=a.base_sha,candidate_sha=a.candidate_sha,
                                      decoding_sha=a.decoding_sha)
            result={"status":result["status"],"case_count":len(result["per_case"]),
                    "artifact":str(a.out),"claim_ceiling":result["score_limit"]}
        elif a.command=="final-preflight":
            if a.out.exists():
                raise LedgerError("output already exists")
            rows=read_cases(a.cases)
            _,excluded=consumed_evidence()
            try:
                preflight_final_bank(rows,consumed_prompt_fingerprints=excluded)
                raise CaseError("independent evidence adapter missing; no final promotion")
            except CaseError as error:
                result={"schema":"QWEN35_FINAL_PREFLIGHT_RECEIPT_V1","status":"NOT_QUALIFIED",
                        "qualified":False,"case_count":len(rows),"reasons":[str(error)],
                        "remaining_requirements":["independent_review","representative_10k_vetted_bank",
                                                  "generation_trace_attestation","runtime_effects_separate"]}
            write_new(a.out,(json.dumps(result,sort_keys=True,indent=2)+"\n").encode("utf-8"))
            print(json.dumps(result,sort_keys=True))
            return 3
        else:
            raise ValueError("unsupported command")
        print(json.dumps(result,sort_keys=True,default=str))
        return 0
    except (CaseError,LedgerError,ValueError,OSError,KeyError,TypeError) as exc:
        print(json.dumps({"status":"ERROR","reason":str(exc)},sort_keys=True))
        return 2

if __name__=="__main__":
    raise SystemExit(main())
