from __future__ import annotations

import argparse
import hashlib
import json
import tarfile
import urllib.request
from collections import defaultdict
from pathlib import Path

BASE_REPO="rodrigomt/Qwen3.5-4B-Uncensored-Aggressive"
BASE_REV="d61dd146c8fd44c9a49cdb7f59f34e17b61902d8"
MAX_LENGTH=1024

def download(url):
    req=urllib.request.Request(url,headers={"User-Agent":"vera-qwen35-v2-qualification/1"})
    with urllib.request.urlopen(req,timeout=120) as r: return r.read()

def recover(work,artifact_commit,prefix,part_count,expected_sha,local_repo_root=None):
    archive=work/"adapter.tar.gz"; work.mkdir(parents=True,exist_ok=True)
    h=hashlib.sha256(); total=0
    with archive.open("wb") as out:
        for i in range(part_count):
            if local_repo_root is None:
                url=f"https://raw.githubusercontent.com/thebrazenbeard/vera_model_training/{artifact_commit}/{prefix}.part{i:03d}"
                data=download(url)
            else:
                data=(Path(local_repo_root)/f"{prefix}.part{i:03d}").read_bytes()
            out.write(data); h.update(data); total+=len(data)
    if h.hexdigest()!=expected_sha: raise RuntimeError(f"adapter SHA mismatch {h.hexdigest()} != {expected_sha}")
    extract=work/"extracted"; extract.mkdir(exist_ok=True)
    with tarfile.open(archive,"r:gz") as tf: tf.extractall(extract,filter="data")
    adapter=extract/"adapter"
    if not (adapter/"adapter_config.json").exists(): raise RuntimeError("adapter_config.json missing")
    print(f"ADAPTER_READBACK|bytes={total}|sha256={h.hexdigest()}",flush=True)
    return adapter

def resolve_adapter(work,adapter_dir,artifact_commit,part_prefix,part_count,adapter_sha256,local_repo_root):
    if adapter_dir is not None:
        adapter=Path(adapter_dir).resolve()
        if not (adapter/"adapter_config.json").exists():
            raise RuntimeError("local adapter_config.json missing")
        if not (adapter/"adapter_model.safetensors").exists():
            raise RuntimeError("local adapter_model.safetensors missing")
        return adapter
    required=(artifact_commit,part_prefix,part_count,adapter_sha256)
    if any(x is None for x in required):
        raise RuntimeError("chunked adapter mode requires artifact commit, prefix, count, and SHA")
    return recover(
      work,artifact_commit,part_prefix,part_count,adapter_sha256,
      local_repo_root=local_repo_root
    )

def load_holdout_source(source):
    path=Path(source)
    raw=path.read_bytes() if path.exists() else download(str(source))
    rows=[json.loads(x) for x in raw.decode().splitlines() if x.strip()]
    if not rows: raise RuntimeError("empty holdout")
    return rows,hashlib.sha256(raw).hexdigest()

def load_holdout(url):
    return load_holdout_source(url)

def apply_runtime_policy(rows,policy):
    policy=str(policy).strip()
    if not policy:
        raise ValueError("runtime policy must be non-empty")
    out=[]
    for row in rows:
        item=dict(row)
        item["prompt"]=(
          "Runtime verification policy:\n"+policy+
          "\n\nApply the policy to the case below. Claim only what the available effect evidence establishes.\n\nCase:\n"+
          row["prompt"]
        )
        out.append(item)
    return out

def model_load_placement(gpu_memory_mib,cpu_memory_gib,offload_folder):
    if gpu_memory_mib is None:
        return {"device_map":{"":0}}
    if gpu_memory_mib < 512:
        raise ValueError("gpu_memory_mib must be at least 512")
    if cpu_memory_gib < 1:
        raise ValueError("cpu_memory_gib must be positive")
    offload_folder=Path(offload_folder)
    offload_folder.mkdir(parents=True,exist_ok=True)
    return {
      "device_map":"auto",
      "max_memory":{0:f"{gpu_memory_mib}MiB","cpu":f"{cpu_memory_gib}GiB"},
      "offload_folder":str(offload_folder)
    }

def prefix(tok,p):
    try: return tok.apply_chat_template([{"role":"user","content":p}],tokenize=False,add_generation_prompt=True,enable_thinking=False)
    except TypeError: return tok.apply_chat_template([{"role":"user","content":p}],tokenize=False,add_generation_prompt=True)

def ids(tok,p,a):
    pp=tok(prefix(tok,p),add_special_tokens=False)["input_ids"]
    rr=tok(a,add_special_tokens=False)["input_ids"]
    if tok.eos_token_id is not None and (not rr or rr[-1]!=tok.eos_token_id): rr.append(tok.eos_token_id)
    if len(pp)+len(rr)>MAX_LENGTH: raise RuntimeError("holdout exceeds max length")
    return pp+rr,len(pp)

def score(model,tok,p,a):
    import torch
    xx,start=ids(tok,p,a); x=torch.tensor([xx],device=model.device,dtype=torch.long)
    with torch.inference_mode():
        lp=torch.log_softmax(model(input_ids=x,use_cache=False).logits[0].float(),dim=-1)
    vals=[lp[t-1,xx[t]] for t in range(start,len(xx))]
    return float(torch.stack(vals).mean().item())

def evaluate(model,tok,rows):
    allr=[]; by=defaultdict(list)
    for r in rows:
        c=score(model,tok,r["prompt"],r["chosen"]); z=score(model,tok,r["prompt"],r["rejected"]); m=c-z
        x={"record_id":r.get("record_id"),"dimension":r.get("dimension"),"chosen_logp":c,"rejected_logp":z,"margin":m,"correct":m>0}
        allr.append(x); by[r.get("dimension","unknown")].append(x)
    return {
      "n":len(allr),"accuracy":sum(x["correct"] for x in allr)/len(allr),
      "mean_margin":sum(x["margin"] for x in allr)/len(allr),
      "by_dimension":{d:{"n":len(xs),"accuracy":sum(x["correct"] for x in xs)/len(xs),"mean_margin":sum(x["margin"] for x in xs)/len(xs)} for d,xs in sorted(by.items())},
      "rows":allr
    }

def main(a):
    import torch
    from peft import PeftModel
    from transformers import AutoTokenizer,BitsAndBytesConfig,Qwen3_5ForCausalLM
    adapter=resolve_adapter(
      a.work,a.adapter_dir,a.artifact_commit,a.part_prefix,a.part_count,
      a.adapter_sha256,a.local_repo_root
    )
    adapter_model_sha=hashlib.sha256((adapter/"adapter_model.safetensors").read_bytes()).hexdigest()
    holdout_source=a.holdout_path if a.holdout_path is not None else a.holdout_url
    rows,hold_sha=load_holdout_source(holdout_source)
    runtime_policy_sha=None
    if a.runtime_policy_path is not None:
        policy_raw=a.runtime_policy_path.read_bytes()
        runtime_policy_sha=hashlib.sha256(policy_raw).hexdigest()
        rows=apply_runtime_policy(rows,policy_raw.decode("utf-8"))
    tok=AutoTokenizer.from_pretrained(BASE_REPO,revision=BASE_REV)
    if tok.pad_token_id is None: tok.pad_token=tok.eos_token
    q=BitsAndBytesConfig(load_in_4bit=True,bnb_4bit_quant_type="nf4",bnb_4bit_use_double_quant=True,bnb_4bit_compute_dtype=torch.bfloat16)
    placement=model_load_placement(
      a.gpu_memory_mib,a.cpu_memory_gib,a.offload_folder or (a.work/"offload")
    )
    base=Qwen3_5ForCausalLM.from_pretrained(
      BASE_REPO,revision=BASE_REV,quantization_config=q,dtype=torch.bfloat16,
      **placement
    )
    base.eval(); b=evaluate(base,tok,rows)
    adapted=PeftModel.from_pretrained(base,adapter); adapted.eval(); v=evaluate(adapted,tok,rows)
    result={
      "schema":"VERA_QWEN35_BEHAVIOR_QUALIFICATION_V2",
      "subject":{"output_identity":"Vera-Qwen3.5-4B-Behavior-V1","adapter_sha256":a.adapter_sha256,"adapter_model_sha256":adapter_model_sha,"artifact_commit":a.artifact_commit,"base_repo":BASE_REPO,"base_revision":BASE_REV,"holdout_sha256":hold_sha,"holdout_rows":len(rows),"runtime_policy_sha256":runtime_policy_sha},
      "method":"mean_response_token_logprob_preference_margin",
      "base":{k:v for k,v in b.items() if k!="rows"},
      "adapter":{k:v for k,v in v.items() if k!="rows"},
      "delta":{"accuracy":v["accuracy"]-b["accuracy"],"mean_margin":v["mean_margin"]-b["mean_margin"]},
      "rows":{"base":b["rows"],"adapter":v["rows"]}
    }
    print("QUALIFICATION_RESULT="+json.dumps(result,sort_keys=True),flush=True)

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--artifact-commit"); ap.add_argument("--part-prefix")
    ap.add_argument("--part-count",type=int); ap.add_argument("--adapter-sha256")
    ap.add_argument("--adapter-dir",type=Path)
    holdout_group=ap.add_mutually_exclusive_group(required=True)
    holdout_group.add_argument("--holdout-url")
    holdout_group.add_argument("--holdout-path",type=Path)
    ap.add_argument("--work",type=Path,default=Path("/tmp/vera-qwen35-v2-qualification"))
    ap.add_argument("--local-repo-root",type=Path)
    ap.add_argument("--gpu-memory-mib",type=int)
    ap.add_argument("--cpu-memory-gib",type=int,default=20)
    ap.add_argument("--offload-folder",type=Path)
    ap.add_argument("--runtime-policy-path",type=Path)
    main(ap.parse_args())
