"""Frozen V5 SFT training preflight, separate train/validation, no final data usage.

A frozen recipe is source evidence only. It is not a trained checkpoint or a
claim that TRL, CUDA, or an evaluator executed.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from .cases import normalized_prompt, legacy_consumed_fingerprints
from .devloop import LedgerError, write_new

class TrainingContractError(ValueError):
    pass

def _read_sft(path):
    rows=[]
    for i,line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(),1):
        if not line.strip():continue
        try:r=json.loads(line)
        except json.JSONDecodeError as exc:raise TrainingContractError(f"invalid SFT row {i}") from exc
        if not isinstance(r,dict) or any(not isinstance(r.get(k),str) or not r[k].strip()
                                          for k in ("record_id","family_id","prompt","response")):
            raise TrainingContractError(f"incomplete SFT row {i}")
        origin=r.get("origin")
        if not isinstance(origin,dict):
            raise TrainingContractError(f"missing source provenance {i}")
        for key in ("source_id","source_revision","license","source_sha256","generation_method"):
            if not isinstance(origin.get(key),str) or not origin[key].strip():
                raise TrainingContractError(f"origin {key} missing on row {i}")
        if origin.get("privacy")!="public":
            raise TrainingContractError("private material forbidden for SFT training")
        if not re.fullmatch("[0-9a-f]{64}",origin["source_sha256"]):
            raise TrainingContractError("source SHA256 invalid")
        rows.append(r)
    return rows

def _digest(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def verify_sft_partitions(train_path,validation_path,*,consumed_prompt_fingerprints,
                          minimum_train=100,minimum_validation=30):
    train=_read_sft(train_path)
    validation=_read_sft(validation_path)
    if len(train)<minimum_train or len(validation)<minimum_validation:
        raise TrainingContractError("insufficient SFT train or validation rows")
    consumed_prompt_fingerprints=set(consumed_prompt_fingerprints) | legacy_consumed_fingerprints()
    seen_ids=set()
    seen_prompts=set()
    for row in train+validation:
        if row["record_id"] in seen_ids:
            raise TrainingContractError("duplicate SFT record_id across partitions")
        seen_ids.add(row["record_id"])
        prompt=normalized_prompt(row["prompt"])
        if not prompt or prompt in seen_prompts:
            raise TrainingContractError("duplicate normalized SFT prompt")
        seen_prompts.add(prompt)
        if prompt in consumed_prompt_fingerprints:
            raise TrainingContractError("consumed final text prohibited in SFT")
    train_families={r["family_id"] for r in train}
    val_families={r["family_id"] for r in validation}
    if train_families & val_families:
        raise TrainingContractError("train/validation family overlap")
    train_sources={r["origin"]["source_id"] for r in train}
    validation_sources={r["origin"]["source_id"] for r in validation}
    if train_sources & validation_sources:
        raise TrainingContractError("train/validation source overlap")
    return {"status":"SFT_PARTITIONS_VERIFIED_NOT_TRAINED",
            "train_rows":len(train),"validation_rows":len(validation),
            "train_sha256":_digest(train_path),"validation_sha256":_digest(validation_path),
            "train_families":len(train_families),"validation_families":len(val_families),
            "source_sha256s":len({r["origin"]["source_sha256"] for r in train+validation}),
            "generalization_status":"UNKNOWN_REQUIRES_LIVE_VALIDATION"}

def build_trainer_config(*,batch_size=1,gradient_accumulation_steps=8,epochs=2,
                         eval_steps=12,learning_rate=0.0001,seed=20260930):
    if (not 0<batch_size<=8 or not 0<gradient_accumulation_steps<=64 or
            not 0<epochs<=10 or not 0<eval_steps<=10000 or not 0<learning_rate<.01):
        raise TrainingContractError("invalid training hyperparameters")
    return {"per_device_train_batch_size":batch_size,
            "gradient_accumulation_steps":gradient_accumulation_steps,
            "num_train_epochs":float(epochs),"learning_rate":learning_rate,
            "lr_scheduler_type":"cosine","warmup_ratio":0.05,
            "eval_strategy":"steps","eval_steps":eval_steps,
            "save_strategy":"steps","save_steps":eval_steps,
            "load_best_model_at_end":True,"metric_for_best_model":"eval_loss",
            "greater_is_better":False,"save_total_limit":2,
            "early_stopping_patience":3,
            "completion_only_loss":True,"packing":False,
            "max_length":512,"overflow":"error",
            "seed":seed,"data_seed":seed,
            "report_to":"none"}

def freeze_training_recipe(train_path,validation_path,output,*,base_revision,source_commit,
                           consumed_prompt_fingerprints):
    if Path(output).exists():
        raise TrainingContractError("frozen recipe output already exists")
    if not re.fullmatch(r"[0-9a-f]{40}",base_revision) or not re.fullmatch(r"[0-9a-f]{40}",source_commit):
        raise TrainingContractError("unpinned base or source commit")
    partition=verify_sft_partitions(train_path,validation_path,
                                    consumed_prompt_fingerprints=consumed_prompt_fingerprints)
    manifest={"schema":"QWEN35_V5_VALIDATION_TRAINING_RECIPE_V1",
              "source_commit":source_commit,
              "base_repo":"rodrigomt/Qwen3.5-4B-Uncensored-Aggressive",
              "base_revision":base_revision,
              "train_path":str(Path(train_path).resolve()),
              "validation_path":str(Path(validation_path).resolve()),
              "train_sha256":partition["train_sha256"],
              "validation_sha256":partition["validation_sha256"],
              "train_rows":partition["train_rows"],
              "validation_rows":partition["validation_rows"],
              "training":build_trainer_config(),
              "checkpoint_status":"RECIPE_FROZEN / TRAINING_NOT_STARTED",
              "claims":"NO_FINAL_HOLDOUT_ACCESS / NO_LIVE_MODEL_TRAINING / NO_QUALIFICATION"}
    Path(output).parent.mkdir(parents=True,exist_ok=True)
    try:write_new(Path(output),(json.dumps(manifest,sort_keys=True,indent=2)+"\n").encode("utf-8"))
    except LedgerError as exc:raise TrainingContractError(str(exc)) from exc
    return manifest
