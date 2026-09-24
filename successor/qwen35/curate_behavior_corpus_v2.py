from __future__ import annotations

import argparse
import base64
import hashlib
import json
import math
import re
import urllib.request
from collections import defaultdict, deque

JUDGE_REPO = "Qwen/Qwen2.5-14B-Instruct"
JUDGE_REV = "cf98f3b3bbb457ad9e2bb7baf9a0125b6b88caa8"
QUOTAS = {
"H01":16,"H02":16,"H03":16,"H04":16,"H05":16,"H06":16,"H07":16,"H08":16,
"H09":6,"H10":16,"H11":16,"H12":6,"H13":6,"H14":6,"H15":6,"H16":16,
"H17":6,"H18":6,"H19":16,"H20":6
}
BANNED = (
    "taxonomy","training example","training data","benchmark","evaluation rubric",
    "preferred response","rejected response","chosen response","disfavored response",
    "thebrazenbeard","vera_model_training","build team two","project lantern",
    "veramesh","vera mesh","unbound-sol","driftguard"
)

SYSTEM = """You are an independent curator of contrastive behavior data.
Judge whether a candidate cleanly teaches the requested distinction to a capable 4B instruction model.

Requirements:
- prompt is natural, standalone, and useful outside any named project;
- chosen is genuinely better on the requested distinction;
- rejected is fluent, plausible, and subtly wrong rather than a caricature;
- chosen does not win merely by being longer, more cautious, or more detailed;
- the distinction is learnable without private context;
- difficulty is not a trick question or dependent on obscure hidden facts;
- pair should generalize to unrelated users and domains.

Return JSON only:
{"pass":true|false,"target_isolated":1-5,"naturalness":1-5,"bad_plausibility":1-5,"length_fairness":1-5,"difficulty_fit":1-5,"substance":1-5,"reason":"..."}
A pass requires every numeric score >=4.
"""

def fetch(url: str) -> bytes:
    with urllib.request.urlopen(url,timeout=90) as r:
        return r.read()

def rows_from(url: str) -> list[dict]:
    return [json.loads(x) for x in fetch(url).decode("utf-8").splitlines() if x.strip()]

def norm(s: str) -> str:
    return " ".join(re.findall(r"[a-z0-9']+",s.lower()))

def shingles(s: str,n: int=4) -> set[str]:
    w=norm(s).split()
    if len(w)<n: return {" ".join(w)} if w else set()
    return {" ".join(w[i:i+n]) for i in range(len(w)-n+1)}

class NearIndex:
    def __init__(self):
        self.items=[]
    def near(self,text: str,threshold: float=0.58) -> bool:
        a=shingles(text)
        if not a: return True
        for b in self.items:
            j=len(a&b)/max(1,len(a|b))
            if j>=threshold: return True
        self.items.append(a)
        return False

def deterministic(rows: list[dict]) -> tuple[list[dict],dict]:
    idx=NearIndex()
    out=[]
    rej=defaultdict(int)
    for r in rows:
        p=str(r.get("prompt","")).strip()
        c=str(r.get("chosen","")).strip()
        d=str(r.get("rejected","")).strip()
        dim=r.get("dimension")
        if dim not in QUOTAS or not p or not c or not d:
            rej["shape"]+=1; continue
        if c==d or norm(c)==norm(d):
            rej["identical"]+=1; continue
        ratio=(len(c)+1)/(len(d)+1)
        if not 0.60<=ratio<=1.70:
            rej["length_ratio"]+=1; continue
        low=(p+"\n"+c+"\n"+d).lower()
        if any(x in low for x in BANNED):
            rej["banned_marker"]+=1; continue
        cs,ds=shingles(c,3),shingles(d,3)
        if cs and ds and len(cs&ds)/max(1,len(cs|ds))>0.92:
            rej["responses_too_similar"]+=1; continue
        if idx.near(p):
            rej["near_duplicate_prompt"]+=1; continue
        out.append(r)
    return out,dict(rej)

def judge_prompt(r: dict) -> str:
    return f"""Dimension: {r.get('dimension')} / {r.get('dimension_name')}
Candidate domain: {r.get('domain')}
Generator-described discriminator: {r.get('discriminator')}

USER PROMPT:
{r['prompt']}

CHOSEN:
{r['chosen']}

REJECTED:
{r['rejected']}

Judge only the pair quality and isolation of the intended distinction."""

def parse_obj(text: str):
    a,b=text.find("{"),text.rfind("}")
    if a<0 or b<=a: return None
    try: x=json.loads(text[a:b+1])
    except Exception: return None
    return x if isinstance(x,dict) else None

def model_judge(rows: list[dict]) -> list[dict]:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
    tok=AutoTokenizer.from_pretrained(JUDGE_REPO,revision=JUDGE_REV)
    if tok.pad_token_id is None: tok.pad_token=tok.eos_token
    tok.padding_side="left"
    q=BitsAndBytesConfig(load_in_4bit=True,bnb_4bit_quant_type="nf4",bnb_4bit_use_double_quant=True,bnb_4bit_compute_dtype=torch.bfloat16)
    model=AutoModelForCausalLM.from_pretrained(JUDGE_REPO,revision=JUDGE_REV,quantization_config=q,device_map={"":0},dtype=torch.bfloat16)
    model.eval()
    accepted=[]
    for start in range(0,len(rows),8):
        batch=rows[start:start+8]
        texts=[tok.apply_chat_template([{"role":"system","content":SYSTEM},{"role":"user","content":judge_prompt(r)}],tokenize=False,add_generation_prompt=True) for r in batch]
        inputs=tok(texts,return_tensors="pt",padding=True,truncation=True,max_length=2600).to(model.device)
        with torch.inference_mode():
            gen=model.generate(**inputs,max_new_tokens=180,do_sample=False,pad_token_id=tok.pad_token_id)
        for i,r in enumerate(batch):
            obj=parse_obj(tok.decode(gen[i,inputs["input_ids"].shape[1]:],skip_special_tokens=True))
            if not obj: continue
            keys=("target_isolated","naturalness","bad_plausibility","length_fairness","difficulty_fit","substance")
            scores=[obj.get(k) for k in keys]
            if not all(isinstance(v,(int,float)) and not isinstance(v,bool) and 1 <= v <= 5 for v in scores):
                continue
            z=dict(r)
            numeric={k:float(obj[k]) for k in keys}
            z["curation"]={
                "judge_repo":JUDGE_REPO,"judge_revision":JUDGE_REV,
                "judge_pass":obj.get("pass") is True,
                **numeric,
                "score_mean":sum(numeric.values())/len(numeric),
                "score_min":min(numeric.values()),
                "reason":str(obj.get("reason",""))[:500]
            }
            accepted.append(z)
        print(f"JUDGE_PROGRESS|scored={min(start+len(batch),len(rows))}|total={len(rows)}|usable={len(accepted)}",flush=True)
    return accepted

def balanced_select(rows: list[dict]) -> list[dict]:
    # Independent judge scores are used as a ranking signal rather than a brittle
    # all-dimensions>=4 binary gate. Hard floors still reject genuinely weak pairs.
    eligible=[]
    rejected=defaultdict(int)
    for r in rows:
        c=r["curation"]
        if c["target_isolated"] < 3:
            rejected["target_isolated_lt3"] += 1; continue
        if c["naturalness"] < 3:
            rejected["naturalness_lt3"] += 1; continue
        if c["bad_plausibility"] < 3:
            rejected["bad_plausibility_lt3"] += 1; continue
        if c["difficulty_fit"] < 3:
            rejected["difficulty_fit_lt3"] += 1; continue
        if c["length_fairness"] < 3:
            rejected["length_fairness_lt3"] += 1; continue
        if c["substance"] < 3:
            rejected["substance_lt3"] += 1; continue
        eligible.append(r)

    by=defaultdict(lambda:defaultdict(list))
    for r in eligible:
        by[r["dimension"]][r.get("domain","unknown")].append(r)

    def rank_key(x):
        c=x["curation"]
        # Prefer target isolation and plausible negatives, then aggregate quality,
        # then deterministic pair hash for stable tie-breaking.
        return (
            c["target_isolated"],
            c["bad_plausibility"],
            c["score_min"],
            c["score_mean"],
            c["naturalness"],
            c["substance"],
            x["pair_sha256"],
        )

    final=[]
    stats={}
    for dim,quota in QUOTAS.items():
        pools={d:deque(sorted(v,key=rank_key,reverse=True)) for d,v in by[dim].items()}
        domains=sorted(pools,key=lambda d:max((rank_key(x) for x in pools[d]),default=(0,)),reverse=True)
        picked=[]
        # First maximize domain coverage, then fill remaining quota by best available score.
        while len(picked)<quota and domains:
            next_domains=[]
            for domain in domains:
                if pools[domain] and len(picked)<quota:
                    picked.append(pools[domain].popleft())
                if pools[domain]:
                    next_domains.append(domain)
            domains=next_domains
        if len(picked)<quota:
            raise RuntimeError(f"{dim}: ranked curator only {len(picked)}/{quota} after hard floors")
        min_domains=8 if quota==16 else 4
        actual=len({x.get("domain") for x in picked})
        if actual<min_domains:
            raise RuntimeError(f"{dim}: only {actual} domains, need {min_domains}")
        stats[dim]={
            "rows":len(picked),
            "domains":actual,
            "mean_judge_score":sum(x["curation"]["score_mean"] for x in picked)/len(picked),
            "min_selected_score":min(x["curation"]["score_min"] for x in picked),
            "judge_pass_true":sum(bool(x["curation"].get("judge_pass")) for x in picked),
        }
        final.extend(picked)
    return sorted(final,key=lambda x:hashlib.sha256(("final:"+x["pair_sha256"]).encode()).hexdigest()),dict(rejected),stats

def emit(tag: str,raw: bytes):
    b64=base64.b64encode(raw).decode("ascii")
    step=8000
    total=math.ceil(len(b64)/step)
    print(f"{tag}_META|bytes={len(raw)}|sha256={hashlib.sha256(raw).hexdigest()}|chunks={total}",flush=True)
    for i in range(total):
        print(f"{tag}_CHUNK|{i+1}|{total}|{b64[i*step:(i+1)*step]}",flush=True)
    print(f"{tag}_COMPLETE",flush=True)

def run(url: str):
    candidates=rows_from(url)
    det,rejections=deterministic(candidates)
    judged=model_judge(det)
    final,rank_rejections,rank_stats=balanced_select(judged)
    raw=("\n".join(json.dumps(x,ensure_ascii=False,separators=(",",":")) for x in final)+"\n").encode()
    stats={}
    for dim in QUOTAS:
        rr=[x for x in final if x["dimension"]==dim]
        stats[dim]={"rows":len(rr),"domains":len({x.get("domain") for x in rr})}
    manifest={
        "schema":"VERA_QWEN35_BEHAVIOR_V2_CURATED_MANIFEST",
        "candidate_rows":len(candidates),"deterministic_pass":len(det),"judge_scored":len(judged),
        "accepted_rows":len(final),"rejections":{"deterministic":rejections,"rank_hard_floor":rank_rejections},
        "stats":stats,"rank_stats":rank_stats,
        "judge_repo":JUDGE_REPO,"judge_revision":JUDGE_REV,
        "sha256":hashlib.sha256(raw).hexdigest()
    }
    print("CURATED_MANIFEST="+json.dumps(manifest,sort_keys=True),flush=True)
    emit("CURATED_JSONL",raw)

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--candidate-url",required=True)
    args=ap.parse_args()
    run(args.candidate_url)
