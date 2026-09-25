from __future__ import annotations

import argparse
import base64
import hashlib
import io
import json
import math
import random
import tarfile
import urllib.request
from pathlib import Path

BASE_REPO="rodrigomt/Qwen3.5-4B-Uncensored-Aggressive"
BASE_REV="d61dd146c8fd44c9a49cdb7f59f34e17b61902d8"
OUTPUT_IDENTITY="Vera-Qwen3.5-4B-Behavior-V1-recipe-v3"
SEED=20260924
MAX_LENGTH=1024
SFT_LR=2e-5
ORPO_LR=1e-6

def read_jsonl_source(source):
    path=Path(source)
    if path.exists():
        raw=path.read_bytes()
    else:
        with urllib.request.urlopen(str(source),timeout=120) as r: raw=r.read()
    rows=[json.loads(x) for x in raw.decode("utf-8").splitlines() if x.strip()]
    return rows,hashlib.sha256(raw).hexdigest()

def runtime_profile(device):
    if device=="cpu":
        return {"device_map":{"":"cpu"},"compute_dtype":"float32","bf16":False,"tf32":False}
    if device=="cuda":
        return {"device_map":{"":0},"compute_dtype":"bfloat16","bf16":True,"tf32":True}
    raise ValueError(f"unsupported device {device}")

def balanced_targeted(rows,per_dimension):
    if per_dimension < 1:
        raise ValueError("per_dimension must be positive")
    by_dimension={}
    for row in rows:
        if not str(row.get("source","")).startswith("targeted_"): continue
        dimension=row.get("dimension")
        if dimension is None: continue
        by_dimension.setdefault(dimension,[]).append(row)
    selected=[]
    for dimension in sorted(by_dimension):
        candidates=by_dimension[dimension]
        if len(candidates)<per_dimension:
            raise RuntimeError(f"not enough targeted rows for {dimension}: {len(candidates)} < {per_dimension}")
        selected.extend(candidates[:per_dimension])
    return selected

def validate_corpus_counts(sft_rows,pref_rows,experiment_steps):
    if sft_rows < 1 or pref_rows < 1:
        raise RuntimeError("training corpora must be non-empty")
    if experiment_steps is None and (sft_rows!=760 or pref_rows!=648):
        raise RuntimeError(f"corpus count mismatch sft={sft_rows} pref={pref_rows}")

def training_schedule(smoke,experiment_steps,skip_orpo):
    if smoke and experiment_steps is not None:
        raise ValueError("smoke and experiment_steps are mutually exclusive")
    if experiment_steps is not None and experiment_steps < 1:
        raise ValueError("experiment_steps must be positive")
    max_steps=1 if smoke else (experiment_steps if experiment_steps is not None else -1)
    gradient_accumulation_steps=1 if (smoke or experiment_steps is not None) else 8
    return {
      "max_steps":max_steps,
      "gradient_accumulation_steps":gradient_accumulation_steps,
      "run_orpo":not skip_orpo
    }

def generation_prefix(tok,prompt):
    try:
        return tok.apply_chat_template([{"role":"user","content":prompt}],tokenize=False,add_generation_prompt=True,enable_thinking=False)
    except TypeError:
        return tok.apply_chat_template([{"role":"user","content":prompt}],tokenize=False,add_generation_prompt=True)

def sft_row(tok,prompt,response):
    return {
      "prompt":generation_prefix(tok,prompt),
      "completion":response+(tok.eos_token or "")
    }

def pref_row(tok,r):
    return {
      "prompt":generation_prefix(tok,r["prompt"]),
      "chosen":r["chosen"]+(tok.eos_token or ""),
      "rejected":r["rejected"]+(tok.eos_token or "")
    }

def load_model(device):
    import torch
    from transformers import AutoTokenizer,BitsAndBytesConfig,Qwen3_5ForCausalLM
    from peft import LoraConfig,prepare_model_for_kbit_training

    profile=runtime_profile(device)
    compute_dtype=getattr(torch,profile["compute_dtype"])
    tok=AutoTokenizer.from_pretrained(BASE_REPO,revision=BASE_REV)
    if tok.pad_token_id is None: tok.pad_token=tok.eos_token
    q=BitsAndBytesConfig(
      load_in_4bit=True,bnb_4bit_quant_type="nf4",
      bnb_4bit_use_double_quant=True,bnb_4bit_compute_dtype=compute_dtype
    )
    model=Qwen3_5ForCausalLM.from_pretrained(
      BASE_REPO,revision=BASE_REV,quantization_config=q,
      device_map=profile["device_map"],dtype=compute_dtype
    )
    model.config.use_cache=False

    types=list(getattr(model.config,"layer_types",[]))
    if len(types)!=32 or types.count("linear_attention")!=24 or types.count("full_attention")!=8:
        raise RuntimeError(f"unexpected Qwen3.5 topology: layers={len(types)} types={types}")

    names=[n for n,_ in model.named_modules()]
    expected=["q_proj","k_proj","v_proj","o_proj","in_proj_qkv","in_proj_z","in_proj_b","in_proj_a","out_proj","gate_proj","up_proj","down_proj"]
    counts={x:sum(n.endswith(x) for n in names) for x in expected}
    required={"q_proj":8,"k_proj":8,"v_proj":8,"o_proj":8,"in_proj_qkv":24,"in_proj_z":24,"in_proj_b":24,"in_proj_a":24}
    for k,v in required.items():
        if counts[k]!=v: raise RuntimeError(f"module topology mismatch {k}: {counts[k]} != {v}")
    if any("vision" in n.lower() or ".visual" in n.lower() for n in names):
        raise RuntimeError("vision modules present in text-only Qwen3_5ForCausalLM")
    print("BASE_TOPOLOGY="+json.dumps({"layers":32,"linear_attention":24,"full_attention":8,"module_counts":counts},sort_keys=True),flush=True)

    model=prepare_model_for_kbit_training(model,use_gradient_checkpointing=True)
    lora=LoraConfig(
      r=4,lora_alpha=16,lora_dropout=0.0,bias="none",task_type="CAUSAL_LM",
      target_modules="all-linear"
    )
    return model,tok,lora

def archive_dir(path):
    bio=io.BytesIO()
    with tarfile.open(fileobj=bio,mode="w:gz",compresslevel=6) as tf:
        for p in sorted(path.rglob("*")):
            if p.is_file(): tf.add(p,arcname=str(p.relative_to(path.parent)))
    return bio.getvalue()

def emit(tag,raw,chunk=65536):
    b64=base64.b64encode(raw).decode("ascii"); total=math.ceil(len(b64)/chunk)
    print(f"{tag}_META|bytes={len(raw)}|sha256={hashlib.sha256(raw).hexdigest()}|chunks={total}",flush=True)
    for i in range(total): print(f"{tag}_CHUNK|{i+1}|{total}|{b64[i*chunk:(i+1)*chunk]}",flush=True)
    print(f"{tag}_COMPLETE",flush=True)

def run(
    sft_source,pref_source,out,smoke,device,emit_archive,
    balanced_targeted_per_dimension=None,experiment_steps=None,skip_orpo=False
):
    import torch,transformers,trl,peft as peft_lib
    from datasets import Dataset
    from trl import SFTConfig,SFTTrainer
    from trl.experimental.orpo import ORPOConfig,ORPOTrainer

    random.seed(SEED); torch.manual_seed(SEED)
    profile=runtime_profile(device)
    sft_rows,sft_sha=read_jsonl_source(sft_source)
    pref_rows,pref_sha=read_jsonl_source(pref_source)
    validate_corpus_counts(len(sft_rows),len(pref_rows),experiment_steps)

    schedule=training_schedule(smoke,experiment_steps,skip_orpo)
    train_sft_rows=sft_rows
    train_pref_rows=pref_rows
    if balanced_targeted_per_dimension is not None:
        train_sft_rows=balanced_targeted(sft_rows,balanced_targeted_per_dimension)
        train_pref_rows=balanced_targeted(pref_rows,balanced_targeted_per_dimension)
        sft_dimensions={r.get("dimension") for r in sft_rows if str(r.get("source","")).startswith("targeted_") and r.get("dimension")}
        pref_dimensions={r.get("dimension") for r in pref_rows if str(r.get("source","")).startswith("targeted_") and r.get("dimension")}
        if sft_dimensions!=pref_dimensions:
            raise RuntimeError(f"targeted dimension mismatch sft={sorted(sft_dimensions)} pref={sorted(pref_dimensions)}")
        expected=len(sft_dimensions)*balanced_targeted_per_dimension
        if len(train_sft_rows)!=expected or len(train_pref_rows)!=expected:
            raise RuntimeError(
              f"balanced targeted selection incomplete: "
              f"sft={len(train_sft_rows)} pref={len(train_pref_rows)} expected={expected}"
            )

    model,tok,lora=load_model(device)
    sft_data=[sft_row(tok,r["prompt"],r["response"]) for r in train_sft_rows]
    pref_data=[pref_row(tok,r) for r in train_pref_rows]
    if smoke:
        sft_data=sft_data[:24]; pref_data=pref_data[:12]

    out.mkdir(parents=True,exist_ok=True)
    sargs=SFTConfig(
      output_dir=str(out/"sft_work"),per_device_train_batch_size=1,
      gradient_accumulation_steps=schedule["gradient_accumulation_steps"],
      num_train_epochs=1.0,max_steps=schedule["max_steps"],
      learning_rate=SFT_LR,lr_scheduler_type="cosine",warmup_steps=0 if smoke else 3,
      optim="paged_adamw_8bit",bf16=profile["bf16"],tf32=profile["tf32"],gradient_checkpointing=True,
      gradient_checkpointing_kwargs={"use_reentrant":False},max_length=MAX_LENGTH,
      completion_only_loss=True,packing=False,shuffle_dataset=True,logging_steps=1 if smoke else 10,
      save_strategy="no",eval_strategy="no",report_to="none",seed=SEED,data_seed=SEED
    )
    sft=SFTTrainer(model=model,args=sargs,train_dataset=Dataset.from_list(sft_data),processing_class=tok,peft_config=lora)
    sr=sft.train(); model=sft.model
    targets=list(getattr(model,"targeted_module_names",[]))
    if not targets: raise RuntimeError("PEFT reported no targeted modules")
    if any("vision" in n.lower() or ".visual" in n.lower() for n in targets):
        raise RuntimeError("vision target detected")
    prefixes={
      "linear_attn":sum(".linear_attn." in n for n in targets),
      "self_attn":sum(".self_attn." in n for n in targets),
      "mlp":sum(".mlp." in n for n in targets)
    }
    if prefixes["linear_attn"]==0 or prefixes["self_attn"]==0 or prefixes["mlp"]==0:
        raise RuntimeError(f"all-linear coverage incomplete: {prefixes}")
    print("LORA_COVERAGE="+json.dumps({"targeted_modules":len(targets),"families":prefixes,"sample":targets[:30]},sort_keys=True),flush=True)

    rr=None
    if schedule["run_orpo"]:
        oargs=ORPOConfig(
          output_dir=str(out/"orpo_work"),per_device_train_batch_size=1,
          gradient_accumulation_steps=schedule["gradient_accumulation_steps"],
          num_train_epochs=1.0,max_steps=schedule["max_steps"],
          learning_rate=ORPO_LR,lr_scheduler_type="cosine",warmup_steps=0 if smoke else 3,
          optim="paged_adamw_8bit",bf16=profile["bf16"],tf32=profile["tf32"],gradient_checkpointing=True,
          gradient_checkpointing_kwargs={"use_reentrant":False},max_length=MAX_LENGTH,beta=0.1,
          logging_steps=1 if smoke else 10,save_strategy="no",eval_strategy="no",report_to="none",
          seed=SEED,data_seed=SEED
        )
        orpo=ORPOTrainer(model=model,args=oargs,train_dataset=Dataset.from_list(pref_data),processing_class=tok)
        rr=orpo.train(); model=orpo.model

    adapter=out/"adapter"
    # Persist only the LoRA artifact; the tokenizer is frozen with BASE_REPO/BASE_REV
    # and need not be duplicated into the adapter archive.
    for name,param in model.named_parameters():
        if param.requires_grad and param.is_floating_point():
            param.data = param.data.to(torch.bfloat16)
    model.save_pretrained(adapter,safe_serialization=True)
    arc=archive_dir(adapter)
    receipt={
      "schema":"VERA_QWEN35_BEHAVIOR_TRAINING_RECEIPT_V1",
      "output_identity":OUTPUT_IDENTITY,"smoke":smoke,"device":device,
      "recipe":{
        "sft_completion_only_loss":True,"sft_learning_rate":SFT_LR,
        "orpo_learning_rate":ORPO_LR,"run_orpo":schedule["run_orpo"],
        "experiment_steps":experiment_steps,
        "balanced_targeted_per_dimension":balanced_targeted_per_dimension
      },
      "base_repo":BASE_REPO,"base_revision":BASE_REV,
      "sft_sha256":sft_sha,"preference_sha256":pref_sha,
      "sft_rows":len(sft_rows),"preference_rows":len(pref_rows),
      "trained_sft_rows":len(sft_data),
      "trained_preference_rows":len(pref_data) if schedule["run_orpo"] else 0,
      "seed":SEED,"max_length":MAX_LENGTH,
      "sft_loss":float(sr.training_loss),
      "orpo_loss":None if rr is None else float(rr.training_loss),
      "lora":{"r":4,"alpha":16,"target_modules":"all-linear","targeted_module_count":len(targets),"families":prefixes,"saved_dtype":"bfloat16"},
      "adapter_archive_bytes":len(arc),"adapter_archive_sha256":hashlib.sha256(arc).hexdigest(),"artifact_transport_chunk_chars":65536,
      "versions":{"torch":torch.__version__,"transformers":transformers.__version__,"trl":trl.__version__,"peft":peft_lib.__version__}
    }
    receipt_path=out/"training_receipt.json"
    receipt_path.write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n",encoding="utf-8",newline="\n")
    print("TRAINING_RECEIPT="+json.dumps(receipt,sort_keys=True),flush=True)
    if emit_archive: emit("ADAPTER_ARCHIVE",arc)

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--sft-source",required=True); ap.add_argument("--pref-source",required=True)
    ap.add_argument("--output-dir",type=Path,default=Path("/tmp/Vera-Qwen3.5-4B-Behavior-V1-recipe-v3"))
    ap.add_argument("--device",choices=["cuda","cpu"],default="cuda")
    ap.add_argument("--smoke",action="store_true")
    ap.add_argument("--balanced-targeted-per-dimension",type=int)
    ap.add_argument("--experiment-steps",type=int)
    ap.add_argument("--skip-orpo",action="store_true")
    ap.add_argument("--emit-archive",action="store_true")
    a=ap.parse_args()
    run(
      a.sft_source,a.pref_source,a.output_dir,a.smoke,a.device,a.emit_archive,
      balanced_targeted_per_dimension=a.balanced_targeted_per_dimension,
      experiment_steps=a.experiment_steps,skip_orpo=a.skip_orpo
    )
