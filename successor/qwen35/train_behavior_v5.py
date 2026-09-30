"""Validation-enabled Qwen3.5 V5 candidate training entrypoint.

Preflight by default. Explicit --execute trains on *development* SFT train
with separate, hash-frozen validation data. No final test is read to choose
epochs, checkpoint or hyperparameters. No model activation or deployment.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

from .measurement_v1.training import verify_sft_partitions, _read_sft

BASE_REVISION="d61dd146c8fd44c9a49cdb7f59f34e17b61902d8"

class TrainingEntrypointError(ValueError):
    pass

def _sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def read_frozen_recipe(recipe_path,*,consumed_prompt_fingerprints):
    spec=json.loads(Path(recipe_path).read_text(encoding="utf-8"))
    if spec.get("schema")!="QWEN35_V5_VALIDATION_TRAINING_RECIPE_V1":
        raise TrainingEntrypointError("invalid recipe schema")
    if spec.get("base_revision")!=BASE_REVISION:
        raise TrainingEntrypointError("unpinned base revision")
    if spec.get("checkpoint_status")!="RECIPE_FROZEN / TRAINING_NOT_STARTED":
        raise TrainingEntrypointError("unexpected training recipe state")
    c=spec.get("training",{})
    if not (c.get("eval_strategy")=="steps" and c.get("save_strategy")=="steps"
            and c.get("eval_steps")==c.get("save_steps")
            and c.get("load_best_model_at_end") is True
            and c.get("metric_for_best_model")=="eval_loss"
            and c.get("greater_is_better") is False
            and c.get("completion_only_loss") is True
            and c.get("packing") is False):
        raise TrainingEntrypointError("recipe violates V5 validation contract")
    train=Path(spec["train_path"]);validation=Path(spec["validation_path"])
    if _sha(train)!=spec["train_sha256"] or _sha(validation)!=spec["validation_sha256"]:
        raise TrainingEntrypointError("source data changed since recipe freeze")
    try:
        evidence=verify_sft_partitions(train,validation,
                                       consumed_prompt_fingerprints=consumed_prompt_fingerprints)
    except Exception as exc:
        raise TrainingEntrypointError("partition preflight failed: "+str(exc)) from exc
    if evidence["train_rows"]!=spec["train_rows"] or evidence["validation_rows"]!=spec["validation_rows"]:
        raise TrainingEntrypointError("partition counts changed")
    return spec

def make_trainer(factory,*,model,training_args,tokenizer,lora_config,train_dataset,validation_dataset):
    if not train_dataset or not validation_dataset:
        raise TrainingEntrypointError("nonempty separate training and validation required")
    return factory(model=model,args=training_args,processing_class=tokenizer,
                   peft_config=lora_config,train_dataset=train_dataset,eval_dataset=validation_dataset)

def run_training(recipe,base_dir,output):
    from datasets import Dataset
    from transformers import EarlyStoppingCallback
    from trl import SFTConfig,SFTTrainer
    from .train_behavior_v4 import load_model,load_tokenizer,sft_row,validate_token_budget

    # QLoRA and local hardware constraints are inherited from V4 without making
    # V4's historical trainer/reports mutable.
    out=Path(output)
    if out.exists():
        raise TrainingEntrypointError("training output already exists")
    train=_read_sft(recipe["train_path"])
    val=_read_sft(recipe["validation_path"])
    tok=load_tokenizer(str(base_dir))
    tr=[sft_row(tok,r["prompt"],r["response"]) for r in train]
    ev=[sft_row(tok,r["prompt"],r["response"]) for r in val]
    validate_token_budget(tok,tr+ev,int(recipe["training"]["max_length"]))
    model,lora,module_counts=load_model("cuda",tok,base_dir=str(base_dir))
    training=dict(recipe["training"])
    patience=training.pop("early_stopping_patience")
    training.pop("overflow")
    out.mkdir(parents=True,exist_ok=False)
    cfg=SFTConfig(output_dir=str(out/"checkpoint_work"),
                  **training,
                  bf16=True,tf32=True,gradient_checkpointing=True,
                  gradient_checkpointing_kwargs={"use_reentrant":False},
                  optim="adamw_torch",logging_steps=10,save_safetensors=True)
    trainer=make_trainer(SFTTrainer,model=model,training_args=cfg,tokenizer=tok,
                         lora_config=lora,
                         train_dataset=Dataset.from_list(tr),
                         validation_dataset=Dataset.from_list(ev))
    trainer.add_callback(EarlyStoppingCallback(early_stopping_patience=patience))
    outstate={"schema":"QWEN35_V5_DEVELOPMENT_TRAINING_V1","status":"INCOMPLETE","base_revision":BASE_REVISION,
              "train_sha256":recipe["train_sha256"],"validation_sha256":recipe["validation_sha256"],
              "evaluation_policy":"eval_loss_checkpoints_steps_not_final_holdout"}
    (out/"training_status.json").write_text(json.dumps(outstate,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    result=trainer.train()
    trainer.save_model(str(out/"adapter"))
    outstate.update({"status":"TRAINED_NOT_QUALIFIED","training_loss":float(result.training_loss),
                     "best_model_checkpoint":str(trainer.state.best_model_checkpoint),
                     "global_steps":int(trainer.state.global_step),
                     "parameter_family_counts":module_counts})
    (out/"training_status.json").write_text(json.dumps(outstate,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    return outstate

def main(argv=None):
    parser=argparse.ArgumentParser()
    parser.add_argument("--recipe",type=Path,required=True)
    parser.add_argument("--base-dir",type=Path,required=True)
    parser.add_argument("--output-dir",type=Path,required=True)
    parser.add_argument("--execute",action="store_true",help="actually train; default performs preflight only")
    args=parser.parse_args(argv)
    from .measurement_v1.cli import consumed_evidence
    try:
        _,blocked=consumed_evidence()
        spec=read_frozen_recipe(args.recipe,consumed_prompt_fingerprints=blocked)
        if args.output_dir.exists():
            raise TrainingEntrypointError("output already exists; no overwrite")
        if not args.base_dir.is_dir():
            raise TrainingEntrypointError("local base directory missing")
        # Validate the two full base shard identities against the frozen V4 base
        old=json.loads((Path(__file__).parent/"qualification/FINAL_QUALIFICATION_V4_SPEC.json").read_text(encoding="utf-8"))
        for item in old["base"]["local_shards"]:
            if _sha(args.base_dir/item["file"])!=item["sha256"]:
                raise TrainingEntrypointError("base shard digest mismatch")
        if not args.execute:
            print(json.dumps({"status":"PREFLIGHT_ONLY_NO_WEIGHT_CHANGE",
                              "train_rows":spec["train_rows"],
                              "validation_rows":spec["validation_rows"]},sort_keys=True))
            return 0
        print(json.dumps(run_training(spec,args.base_dir,args.output_dir),sort_keys=True))
        return 0
    except (TrainingEntrypointError,KeyError,OSError,ValueError) as exc:
        print(json.dumps({"status":"ERROR","reason":str(exc)},sort_keys=True))
        return 2

if __name__=="__main__":
    raise SystemExit(main())
