from __future__ import annotations

import argparse,base64,hashlib,json,math,re,urllib.request
from collections import defaultdict,deque

JUDGE_REPO="Qwen/Qwen2.5-14B-Instruct"
JUDGE_REV="cf98f3b3bbb457ad9e2bb7baf9a0125b6b88caa8"

SYSTEM="""Independently score a contrastive software-engineering preference pair.
The intended portable mechanism is supplied as metadata.
Judge whether the pair teaches that mechanism in a realistic new repository scenario.

Return JSON only:
{"mechanism_isolation":1-5,"engineering_realism":1-5,"bad_plausibility":1-5,"verification_specificity":1-5,"transferability":1-5,"length_fairness":1-5,"reason":"..."}

A good pair has a natural task, a clearly better chosen answer, a plausible rejected answer, and a verification step that matches the claimed effect. Do not reward verbosity by itself.
"""

def fetch(url):
    with urllib.request.urlopen(url,timeout=90) as r: return r.read()

def rows(url):
    return [json.loads(x) for x in fetch(url).decode().splitlines() if x.strip()]

def norm(s): return " ".join(re.findall(r"[a-z0-9']+",s.lower()))
def shingles(s,n=4):
    w=norm(s).split()
    return {" ".join(w[i:i+n]) for i in range(max(0,len(w)-n+1))} or {norm(s)}

def deterministic(rs):
    kept=[]; seen=[]; reject=defaultdict(int)
    banned=("thebrazenbeard","driftguard","achilles","vera_model_training","lantern","unbound-sol")
    for r in rs:
        p,c,d=r["prompt"],r["chosen"],r["rejected"]
        ratio=(len(c)+1)/(len(d)+1)
        if not .60<=ratio<=1.70: reject["length"]+=1; continue
        if norm(c)==norm(d): reject["identical"]+=1; continue
        if any(x in (p+" "+c+" "+d).lower() for x in banned): reject["source_leak"]+=1; continue
        sh=shingles(p)
        if any(len(sh&x)/max(1,len(sh|x))>=.60 for x in seen): reject["near_duplicate"]+=1; continue
        seen.append(sh); kept.append(r)
    return kept,dict(reject)

def parse(text):
    a,b=text.find("{"),text.rfind("}")
    if a<0 or b<=a:return None
    try:return json.loads(text[a:b+1])
    except:return None

def judge(rs):
    import torch
    from transformers import AutoModelForCausalLM,AutoTokenizer,BitsAndBytesConfig
    tok=AutoTokenizer.from_pretrained(JUDGE_REPO,revision=JUDGE_REV)
    if tok.pad_token_id is None: tok.pad_token=tok.eos_token
    tok.padding_side="left"
    q=BitsAndBytesConfig(load_in_4bit=True,bnb_4bit_quant_type="nf4",bnb_4bit_use_double_quant=True,bnb_4bit_compute_dtype=torch.bfloat16)
    model=AutoModelForCausalLM.from_pretrained(JUDGE_REPO,revision=JUDGE_REV,quantization_config=q,device_map={"":0},dtype=torch.bfloat16)
    model.eval(); out=[]
    keys=("mechanism_isolation","engineering_realism","bad_plausibility","verification_specificity","transferability","length_fairness")
    for start in range(0,len(rs),8):
        batch=rs[start:start+8]; texts=[]
        for r in batch:
            user=f"""Source-card id: {r['source_card_id']}
Discriminator: {r['discriminator']}
Verification intent: {r['verification']}

USER:
{r['prompt']}

CHOSEN:
{r['chosen']}

REJECTED:
{r['rejected']}"""
            texts.append(tok.apply_chat_template([{"role":"system","content":SYSTEM},{"role":"user","content":user}],tokenize=False,add_generation_prompt=True))
        inp=tok(texts,return_tensors="pt",padding=True,truncation=True,max_length=2600).to(model.device)
        with torch.inference_mode():
            gen=model.generate(**inp,max_new_tokens=180,do_sample=False,pad_token_id=tok.pad_token_id)
        for i,r in enumerate(batch):
            obj=parse(tok.decode(gen[i,inp["input_ids"].shape[1]:],skip_special_tokens=True))
            if not isinstance(obj,dict):continue
            vals=[obj.get(k) for k in keys]
            if not all(isinstance(v,(int,float)) and not isinstance(v,bool) and 1<=v<=5 for v in vals):continue
            z=dict(r); numeric={k:float(obj[k]) for k in keys}
            z["curation"]={"judge_repo":JUDGE_REPO,"judge_revision":JUDGE_REV,**numeric,
              "score_min":min(numeric.values()),"score_mean":sum(numeric.values())/len(numeric),
              "reason":str(obj.get("reason",""))[:500]}
            out.append(z)
        print(f"REPO_JUDGE_PROGRESS|scored={min(start+len(batch),len(rs))}|total={len(rs)}|usable={len(out)}",flush=True)
    return out

def select(rs):
    eligible=[]; reject=defaultdict(int)
    for r in rs:
        c=r["curation"]
        if c["mechanism_isolation"]<3: reject["mechanism_lt3"]+=1; continue
        if c["engineering_realism"]<3: reject["realism_lt3"]+=1; continue
        if c["bad_plausibility"]<3: reject["bad_plausibility_lt3"]+=1; continue
        if c["verification_specificity"]<3: reject["verification_lt3"]+=1; continue
        if c["transferability"]<3: reject["transfer_lt3"]+=1; continue
        if c["length_fairness"]<3: reject["length_fairness_lt3"]+=1; continue
        eligible.append(r)
    by=defaultdict(lambda:defaultdict(list))
    for r in eligible: by[r["source_card_id"]][r["domain"]].append(r)
    final=[]; stats={}
    def key(r):
        c=r["curation"]
        return (c["mechanism_isolation"],c["verification_specificity"],c["bad_plausibility"],c["score_min"],c["score_mean"],r["pair_sha256"])
    for card,domains in sorted(by.items()):
        pools={d:deque(sorted(v,key=key,reverse=True)) for d,v in domains.items()}
        order=sorted(pools,key=lambda d:max((key(x) for x in pools[d]),default=(0,)),reverse=True)
        pick=[]
        while len(pick)<8 and order:
            nxt=[]
            for d in order:
                if pools[d] and len(pick)<8: pick.append(pools[d].popleft())
                if pools[d]: nxt.append(d)
            order=nxt
        if len(pick)<8: raise RuntimeError(f"{card}: only {len(pick)}/8 after curation")
        if len({x["domain"] for x in pick})<6: raise RuntimeError(f"{card}: insufficient domain diversity")
        final.extend(pick)
        stats[card]={"rows":8,"domains":len({x["domain"] for x in pick}),
          "mean_score":sum(x["curation"]["score_mean"] for x in pick)/8,
          "min_score":min(x["curation"]["score_min"] for x in pick)}
    if len(final)!=96: raise RuntimeError(f"final {len(final)} !=96")
    return sorted(final,key=lambda r:hashlib.sha256(("repo-final:"+r["pair_sha256"]).encode()).hexdigest()),dict(reject),stats

def emit(tag,raw):
    b64=base64.b64encode(raw).decode(); step=8000; total=math.ceil(len(b64)/step)
    print(f"{tag}_META|bytes={len(raw)}|sha256={hashlib.sha256(raw).hexdigest()}|chunks={total}",flush=True)
    for i in range(total): print(f"{tag}_CHUNK|{i+1}|{total}|{b64[i*step:(i+1)*step]}",flush=True)
    print(f"{tag}_COMPLETE",flush=True)

def main(url):
    cand=rows(url); det,dr=deterministic(cand); scored=judge(det); final,hr,stats=select(scored)
    raw=("\n".join(json.dumps(x,ensure_ascii=False,separators=(",",":")) for x in final)+"\n").encode()
    manifest={"schema":"VERA_QWEN35_REPO_ENGINEERING_CURATED_MANIFEST_V1","candidate_rows":len(cand),
      "deterministic_pass":len(det),"judge_scored":len(scored),"accepted_rows":len(final),
      "rejections":{"deterministic":dr,"hard_floor":hr},"stats":stats,
      "sha256":hashlib.sha256(raw).hexdigest(),"judge_repo":JUDGE_REPO,"judge_revision":JUDGE_REV}
    print("REPO_CURATED_MANIFEST="+json.dumps(manifest,sort_keys=True),flush=True); emit("REPO_CURATED_JSONL",raw)

if __name__=="__main__":
    ap=argparse.ArgumentParser();ap.add_argument("--candidate-url",required=True);a=ap.parse_args();main(a.candidate_url)
