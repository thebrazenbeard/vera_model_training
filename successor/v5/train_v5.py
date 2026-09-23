from __future__ import annotations

import hashlib
import json
import random
from pathlib import Path

BASE_REPO = "HuggingFaceTB/SmolLM3-3B"
BASE_REV = "a07cc9a04f16550a088caea529712d1d335b0ac1"
SEED = 20260922
SYSTEM = {"role":"system","content":"/no_think /system_override"}


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]


def sha256_file(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""):
            h.update(chunk)
    return h.hexdigest()


def sft_record(row: dict) -> dict:
    return {
        "prompt":[SYSTEM,{"role":"user","content":row["prompt"]}],
        "completion":[{"role":"assistant","content":row["response"]}],
    }


def targeted_sft_record(row: dict) -> dict:
    return {
        "prompt":[SYSTEM,{"role":"user","content":row["prompt"]}],
        "completion":[{"role":"assistant","content":row["chosen"]}],
    }


def preference_record(row: dict) -> dict:
    return {
        "prompt":[SYSTEM,{"role":"user","content":row["prompt"]}],
        "chosen":[{"role":"assistant","content":row["chosen"]}],
        "rejected":[{"role":"assistant","content":row["rejected"]}],
    }


def load_model():
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
    from peft import LoraConfig

    quant=BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_use_double_quant=True,
        bnb_4bit_compute_dtype=torch.bfloat16,
    )
    tokenizer=AutoTokenizer.from_pretrained(BASE_REPO,revision=BASE_REV)
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token=tokenizer.eos_token
    model=AutoModelForCausalLM.from_pretrained(
        BASE_REPO,
        revision=BASE_REV,
        quantization_config=quant,
        device_map={"":0},
        dtype=torch.bfloat16,
    )
    model.config.use_cache=False
    peft=LoraConfig(
        r=4,
        lora_alpha=16,
        lora_dropout=0.0,
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=["q_proj","v_proj"],
    )
    return model,tokenizer,peft


def train(
    general_sft_path:Path,
    general_pref_path:Path,
    targeted_path:Path,
    output_dir:Path,
    *,
    smoke:bool=False,
)->dict:
    import torch,transformers,trl,peft as peft_lib
    from datasets import Dataset, load_dataset
    from trl import SFTConfig,SFTTrainer
    from trl.experimental.orpo import ORPOConfig,ORPOTrainer

    random.seed(SEED)
    torch.manual_seed(SEED)
    general_sft=read_jsonl(general_sft_path)
    general_pref=read_jsonl(general_pref_path)
    targeted_all=read_jsonl(targeted_path)
    gold_all=[r for r in targeted_all if r.get("schema")=="VERA_V5_GOLD_TARGETED_PAIR_V1"]
    generated_all=[r for r in targeted_all if r.get("schema")!="VERA_V5_GOLD_TARGETED_PAIR_V1"]
    if not smoke:
        if len(general_sft)!=70000: raise RuntimeError(f"general SFT count {len(general_sft)}")
        if len(general_pref)!=20000: raise RuntimeError(f"general pref count {len(general_pref)}")
        if len(generated_all)!=11000: raise RuntimeError(f"generated targeted count {len(generated_all)}")
        if len(gold_all)!=24: raise RuntimeError(f"gold targeted count {len(gold_all)}")
        if len(targeted_all)!=11024: raise RuntimeError(f"combined targeted count {len(targeted_all)}")
        if any(r.get("qualification_eligible") is not False for r in gold_all):
            raise RuntimeError("gold targeted rows must be qualification-ineligible")
        targeted=targeted_all
    else:
        general_sft=general_sft[:32]
        general_pref=general_pref[:16]
        targeted=generated_all[:2]+gold_all[:2]

    sft_rows=[sft_record(r) for r in general_sft]+[targeted_sft_record(r) for r in targeted]
    random.Random(SEED+1).shuffle(sft_rows)
    pref_rows=[preference_record(r) for r in general_pref]+[preference_record(r) for r in targeted]
    random.Random(SEED+2).shuffle(pref_rows)

    dev_raw=load_dataset(
        "HuggingFaceH4/ultrafeedback_binarized",
        split="test_sft",
        revision="3949bf5f8c17c394422ccfab0c31ea9c20bdeb85",
    )
    dev_rows=[]
    for r in dev_raw:
        messages=r.get("messages")
        if isinstance(messages,list) and len(messages)==2 and messages[0].get("role")=="user" and messages[1].get("role")=="assistant":
            dev_rows.append({
                "prompt":[SYSTEM,{"role":"user","content":messages[0]["content"]}],
                "completion":[{"role":"assistant","content":messages[1]["content"]}],
            })
    if smoke: dev_rows=dev_rows[:8]

    train_ds=Dataset.from_list(sft_rows)
    dev_ds=Dataset.from_list(dev_rows)
    pref_ds=Dataset.from_list(pref_rows)

    model,tokenizer,lora_config=load_model()
    output_dir.mkdir(parents=True,exist_ok=True)
    sft_out=output_dir/"sft_work"
    sft_args=SFTConfig(
        output_dir=str(sft_out),
        per_device_train_batch_size=8 if not smoke else 2,
        per_device_eval_batch_size=8 if not smoke else 2,
        gradient_accumulation_steps=4 if not smoke else 1,
        num_train_epochs=1.0,
        max_steps=1 if smoke else -1,
        learning_rate=5e-6,
        lr_scheduler_type="cosine",
        warmup_steps=200 if not smoke else 0,
        optim="paged_adamw_8bit",
        bf16=True,
        tf32=True,
        gradient_checkpointing=True,
        gradient_checkpointing_kwargs={"use_reentrant":False},
        max_length=1536,
        completion_only_loss=True,
        packing=False,
        shuffle_dataset=True,
        logging_steps=25 if not smoke else 1,
        save_strategy="no",
        eval_strategy="no",
        report_to="none",
        seed=SEED,
        data_seed=SEED,
    )
    sft=SFTTrainer(
        model=model,
        args=sft_args,
        train_dataset=train_ds,
        eval_dataset=dev_ds,
        processing_class=tokenizer,
        peft_config=lora_config,
    )
    sft_result=sft.train()
    sft_eval=sft.evaluate()
    model=sft.model

    orpo_out=output_dir/"orpo_work"
    orpo_args=ORPOConfig(
        output_dir=str(orpo_out),
        per_device_train_batch_size=2 if not smoke else 1,
        gradient_accumulation_steps=8 if not smoke else 1,
        num_train_epochs=1.0,
        max_steps=1 if smoke else -1,
        learning_rate=2e-6,
        lr_scheduler_type="cosine",
        warmup_steps=150 if not smoke else 0,
        optim="paged_adamw_8bit",
        bf16=True,
        tf32=True,
        gradient_checkpointing=True,
        gradient_checkpointing_kwargs={"use_reentrant":False},
        max_length=1536,
        beta=0.1,
        logging_steps=25 if not smoke else 1,
        save_strategy="no",
        eval_strategy="no",
        report_to="none",
        seed=SEED,
        data_seed=SEED,
    )
    orpo=ORPOTrainer(
        model=model,
        args=orpo_args,
        train_dataset=pref_ds,
        processing_class=tokenizer,
    )
    orpo_result=orpo.train()
    model=orpo.model

    adapter_dir=output_dir/"adapter"
    model.save_pretrained(adapter_dir,safe_serialization=True)
    tokenizer.save_pretrained(adapter_dir)

    adapter_path=adapter_dir/"adapter_model.safetensors"
    config_path=adapter_dir/"adapter_config.json"
    manifest={
        "schema":"VERA_SUCCESSOR_V5_TRAINING_RECEIPT_V1",
        "smoke":smoke,
        "base_repo":BASE_REPO,
        "base_revision":BASE_REV,
        "seed":SEED,
        "general_sft_rows":len(general_sft),
        "generated_targeted_rows":sum(r.get("schema")!="VERA_V5_GOLD_TARGETED_PAIR_V1" for r in targeted),
        "gold_targeted_rows":sum(r.get("schema")=="VERA_V5_GOLD_TARGETED_PAIR_V1" for r in targeted),
        "targeted_sft_rows":len(targeted),
        "targeted_input_sha256":sha256_file(targeted_path),
        "sft_total_rows":len(sft_rows),
        "general_preference_rows":len(general_pref),
        "targeted_preference_rows":len(targeted),
        "preference_total_rows":len(pref_rows),
        "sft_train_loss":float(sft_result.training_loss),
        "sft_eval_loss":float(sft_eval.get("eval_loss",float("nan"))),
        "orpo_train_loss":float(orpo_result.training_loss),
        "adapter_sha256":sha256_file(adapter_path),
        "adapter_bytes":adapter_path.stat().st_size,
        "adapter_config_sha256":sha256_file(config_path),
        "versions":{
            "torch":torch.__version__,
            "transformers":transformers.__version__,
            "trl":trl.__version__,
            "peft":peft_lib.__version__,
        },
        "objective_sequence":["completion_only_sft","orpo"],
        "lora":{"r":4,"alpha":16,"dropout":0.0,"target_modules":["q_proj","v_proj"]},
    }
    (output_dir/"training_receipt.json").write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\\n",encoding="utf-8")
    return manifest


if __name__=="__main__":
    import argparse
    ap=argparse.ArgumentParser()
    ap.add_argument("--general-sft",type=Path,required=True)
    ap.add_argument("--general-prefs",type=Path,required=True)
    ap.add_argument("--targeted",type=Path,required=True)
    ap.add_argument("--output-dir",type=Path,required=True)
    ap.add_argument("--smoke",action="store_true")
    args=ap.parse_args()
    print(json.dumps(train(args.general_sft,args.general_prefs,args.targeted,args.output_dir,smoke=args.smoke),sort_keys=True))
