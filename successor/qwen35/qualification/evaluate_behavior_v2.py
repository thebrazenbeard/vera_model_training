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

def recover(work,artifact_commit,prefix,part_count,expected_sha):
    archive=work/"adapter.tar.gz"; work.mkdir(parents=True,exist_ok=True)
    h=hashlib.sha256(); total=0
    with archive.open("wb") as out:
        for i in range(part_count):
            url=f"https://raw.githubusercontent.com/thebrazenbeard/vera_model_training/{artifact_commit}/{prefix}.part{i:03d}"
            data=download(url); out.write(data); h.update(data); total+=len(data)
    if h.hexdigest()!=expected_sha: raise RuntimeError(f"adapter SHA mismatch {h.hexdigest()} != {expected_sha}")
    extract=work/"extracted"; extract.mkdir(exist_ok=True)
    with tarfile.open(archive,"r:gz") as tf: tf.extractall(extract,filter="data")
    adapter=extract/"adapter"
    if not (adapter/"adapter_config.json").exists(): raise RuntimeError("adapter_config.json missing")
    print(f"ADAPTER_READBACK|bytes={total}|sha256={h.hexdigest()}",flush=True)
    return adapter

def load_holdout(url):
    raw=download(url)
    rows=[json.loads(x) for x in raw.decode().splitlines() if x.strip()]
    if not rows: raise RuntimeError("empty holdout")
    return rows,hashlib.sha256(raw).hexdigest()

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
    adapter=recover(a.work,a.artifact_commit,a.part_prefix,a.part_count,a.adapter_sha256)
    rows,hold_sha=load_holdout(a.holdout_url)
    tok=AutoTokenizer.from_pretrained(BASE_REPO,revision=BASE_REV)
    if tok.pad_token_id is None: tok.pad_token=tok.eos_token
    q=BitsAndBytesConfig(load_in_4bit=True,bnb_4bit_quant_type="nf4",bnb_4bit_use_double_quant=True,bnb_4bit_compute_dtype=torch.bfloat16)
    base=Qwen3_5ForCausalLM.from_pretrained(BASE_REPO,revision=BASE_REV,quantization_config=q,device_map={"":0},dtype=torch.bfloat16)
    base.eval(); b=evaluate(base,tok,rows)
    adapted=PeftModel.from_pretrained(base,adapter); adapted.eval(); v=evaluate(adapted,tok,rows)
    result={
      "schema":"VERA_QWEN35_BEHAVIOR_QUALIFICATION_V2",
      "subject":{"output_identity":"Vera-Qwen3.5-4B-Behavior-V1","adapter_sha256":a.adapter_sha256,"artifact_commit":a.artifact_commit,"base_repo":BASE_REPO,"base_revision":BASE_REV,"holdout_sha256":hold_sha,"holdout_rows":len(rows)},
      "method":"mean_response_token_logprob_preference_margin",
      "base":{k:v for k,v in b.items() if k!="rows"},
      "adapter":{k:v for k,v in v.items() if k!="rows"},
      "delta":{"accuracy":v["accuracy"]-b["accuracy"],"mean_margin":v["mean_margin"]-b["mean_margin"]},
      "rows":{"base":b["rows"],"adapter":v["rows"]}
    }
    print("QUALIFICATION_RESULT="+json.dumps(result,sort_keys=True),flush=True)

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--artifact-commit",required=True); ap.add_argument("--part-prefix",required=True)
    ap.add_argument("--part-count",required=True,type=int); ap.add_argument("--adapter-sha256",required=True)
    ap.add_argument("--holdout-url",required=True); ap.add_argument("--work",type=Path,default=Path("/tmp/vera-qwen35-v2-qualification"))
    main(ap.parse_args())
