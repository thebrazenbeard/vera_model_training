"""Persistent group-disjoint development workflow with hash-chained experiment evidence.

This module does not train weights, independently attest model generation, or
read final holdout answers for candidate selection.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
from pathlib import Path
from .cases import read_cases, split_dev_cases, legacy_consumed_fingerprints, normalized_prompt
from .observations import verify_pair
from .statistics import paired_statistics

class LedgerError(ValueError):
    pass

def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()

def canonical(value: dict) -> bytes:
    return (json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False)).encode("utf-8")

def write_new(path: Path, contents: bytes) -> None:
    try:
        with Path(path).open("xb") as file:
            file.write(contents)
            file.flush()
            os.fsync(file.fileno())
    except FileExistsError as exc:
        raise LedgerError(f"destination already exists: {path}") from exc

def encode_jsonl(rows) -> bytes:
    return b"".join(canonical(x)+b"\n" for x in rows)

def write_dev_split(input_file: Path, directory: Path, *, seed: int=20260930) -> dict:
    rows=read_cases(input_file)
    blocked=legacy_consumed_fingerprints()
    if any(normalized_prompt(row["prompt"]) in blocked for row in rows):
        raise LedgerError("consumed V3/V4 final prompt forbidden in development split")
    train, validation=split_dev_cases(rows,seed=seed)
    dst=Path(directory)
    if dst.exists():
        raise LedgerError(f"output directory exists: {dst}")
    dst.mkdir(parents=True,exist_ok=False)
    trainbytes=encode_jsonl(train)
    valbytes=encode_jsonl(validation)
    write_new(dst/"train.jsonl",trainbytes)
    write_new(dst/"validation.jsonl",valbytes)
    manifest={
        "schema":"QWEN35_DEV_SPLIT_MANIFEST_V1",
        "source_sha256":digest(Path(input_file).read_bytes()),
        "seed":seed,"train_rows":len(train),"validation_rows":len(validation),
        "train_sha256":digest(trainbytes),"validation_sha256":digest(valbytes),
        "train_families":len({r["family_id"] for r in train}),
        "validation_families":len({r["family_id"] for r in validation}),
        "stage":"DEVELOPMENT_NOT_FINAL",
        "claim_ceiling":"DATA_PARTITION_ONLY_NOT_MODEL_TRAINING_OR_QUALIFICATION",
    }
    write_new(dst/"manifest.json",json.dumps(manifest,sort_keys=True,indent=2).encode("utf-8")+b"\n")
    return manifest

def _chain_entry(payload):
    return digest(canonical({k:v for k,v in payload.items() if k!="entry_sha256"}))

def read_validation_ledger(path: Path) -> list[dict]:
    if not Path(path).exists():
        return []
    records=[]
    previous="0"*64
    for line_index,line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(),1):
        try:
            item=json.loads(line)
        except json.JSONDecodeError as exc:
            raise LedgerError(f"ledger JSON hash chain unreadable on line {line_index}") from exc
        if (item.get("entry_sha256")!=_chain_entry(item)
                or item.get("previous_entry_sha256")!=previous
                or item.get("chain_index")!=line_index):
            raise LedgerError(f"ledger hash chain failure on line {line_index}")
        if item.get("stage")!="development_validation":
            raise LedgerError("ledger contains non-development stage")
        previous=item["entry_sha256"]
        records.append(item)
    return records

def append_validation(path: Path, entry: dict, *, blocked_final_digests: set[str], budget: int=3) -> dict:
    required=("experiment_id","stage","source_commit","recipe_sha256","train_sha256","validation_sha256",
              "results_sha256","base_model_sha256","candidate_model_sha256")
    if not isinstance(entry,dict) or any(not isinstance(entry.get(x),str) or not entry[x] for x in required):
        raise LedgerError("incomplete validation entry")
    if entry["stage"]!="development_validation":
        raise LedgerError("validation ledger stage must be development_validation")
    if any(key.startswith("final") for key in entry):
        raise LedgerError("final evaluation details forbidden in development entry")
    for field in ("recipe_sha256","train_sha256","validation_sha256","results_sha256","base_model_sha256","candidate_model_sha256"):
        if re.fullmatch(r"[0-9a-f]{64}",entry[field]) is None:
            raise LedgerError(f"invalid {field}")
    if re.fullmatch(r"[0-9a-f]{40}",entry["source_commit"]) is None:
        raise LedgerError("invalid source commit")
    if entry["validation_sha256"] in blocked_final_digests or entry["train_sha256"] in blocked_final_digests:
        raise LedgerError("consumed final digest forbidden in development selection")
    if entry["train_sha256"]==entry["validation_sha256"]:
        raise LedgerError("training and validation digests cannot be the same")
    if entry["candidate_model_sha256"]==entry["base_model_sha256"]:
        raise LedgerError("baseline and candidate SHA may not be identical")
    path=Path(path)
    path.parent.mkdir(parents=True,exist_ok=True)
    lock=path.with_suffix(path.suffix+".lock")
    try:
        with lock.open("x",encoding="ascii") as f:
            f.write("exclusive append lock\n")
    except FileExistsError as exc:
        raise LedgerError("ledger locked: reconcile writer before retry") from exc
    try:
        prior=read_validation_ledger(path)
        if len(prior)>=budget:
            raise LedgerError(f"development validation budget exhausted ({budget})")
        if any(x["experiment_id"]==entry["experiment_id"] for x in prior):
            raise LedgerError("duplicate experiment_id")
        next_item=dict(entry)
        next_item["chain_index"]=len(prior)+1
        next_item["previous_entry_sha256"]=prior[-1]["entry_sha256"] if prior else "0"*64
        next_item["entry_sha256"]=_chain_entry(next_item)
        with path.open("ab") as f:
            f.write(canonical(next_item)+b"\n")
            f.flush()
            os.fsync(f.fileno())
        assert read_validation_ledger(path)[-1]["entry_sha256"]==next_item["entry_sha256"]
        return next_item
    finally:
        lock.unlink(missing_ok=True)

def _read_observations(path: Path, condition: str) -> dict[str,dict]:
    try:
        lines=Path(path).read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise LedgerError(f"observation file unreadable: {condition}") from exc
    result={}
    for i,line in enumerate(lines,1):
        if not line.strip():continue
        try:r=json.loads(line)
        except json.JSONDecodeError as exc:raise LedgerError(f"invalid observation JSON at {i}") from exc
        if r.get("condition")!=condition:
            raise LedgerError(f"observation has wrong condition {condition}")
        cid=r.get("case_id")
        if cid in result:
            raise LedgerError(f"duplicate {condition} observation {cid}")
        result[cid]=r
    return result

def score_paired_files(cases_file: Path, base_file: Path, candidate_file: Path, output: Path,
                       *,base_sha:str,candidate_sha:str,decoding_sha:str,seed:int=20260930) -> dict:
    dst=Path(output)
    if dst.exists():
        raise LedgerError(f"output already exists: {dst}")
    cases=read_cases(cases_file)
    blocked=legacy_consumed_fingerprints()
    if any(normalized_prompt(row["prompt"]) in blocked for row in cases):
        raise LedgerError("consumed final prompt forbidden in development scoring")
    base=_read_observations(base_file,"base")
    candidate=_read_observations(candidate_file,"candidate")
    expected={c["case_id"] for c in cases}
    if expected!=set(base) or expected!=set(candidate):
        raise LedgerError("missing or extra paired observations")
    scored=[verify_pair(c,base[c["case_id"]],candidate[c["case_id"]],
                        base_sha=base_sha,candidate_sha=candidate_sha,decoding_sha=decoding_sha)
            for c in cases]
    if any(x[condition]["status"]=="UNREVIEWED" for x in scored for condition in ("base","candidate")):
        summary={"status":"INCOMPLETE_UNREVIEWED","paired":None}
    else:
        summary={"status":"DEVELOPMENT_DIAGNOSTIC_UNATTESTED","paired":paired_statistics(scored,seed=seed)}
    result={"schema":"QWEN35_DEV_GENERATED_PAIRED_RESULT_V1",
            "case_sha256":digest(Path(cases_file).read_bytes()),
            "base_observations_sha256":digest(Path(base_file).read_bytes()),
            "candidate_observations_sha256":digest(Path(candidate_file).read_bytes()),
            "base_model_sha256":base_sha,"candidate_model_sha256":candidate_sha,"decoding_sha256":decoding_sha,
            "score_limit":"MODEL_GENERATION_CLAIM_NOT_INDEPENDENTLY_OBSERVED",
            "per_case":scored,**summary}
    dst.parent.mkdir(parents=True,exist_ok=True)
    write_new(dst,(json.dumps(result,sort_keys=True,indent=2)+"\n").encode("utf-8"))
    return result
