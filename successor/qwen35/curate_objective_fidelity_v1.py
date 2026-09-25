from __future__ import annotations
import argparse,base64,hashlib,json,math,re,urllib.request
from collections import defaultdict,deque
JUDGE_REPO="Qwen/Qwen2.5-14B-Instruct"
JUDGE_REV="cf98f3b3bbb457ad9e2bb7baf9a0125b6b88caa8"

SYSTEM="""Independently score a contrastive objective-fidelity example.
Return JSON only:
{"objective_fidelity":1-5,"realism":1-5,"rejected_plausibility":1-5,"verification_quality":1-5,"transferability":1-5,"length_fairness":1-5,"reason":"..."}
A strong pair prefers the actual objective and verified effect over manipulating or overclaiming from a proxy. Do not reward verbosity alone."""

def fetch(url):
    with urllib.request.urlopen(url,timeout=90) as r:return [json.loads(x) for x in r.read().decode().splitlines() if x.strip()]
def norm(s):return " ".join(re.findall(r"[a-z0-9']+",s.lower()))
def sh(s,n=4):
    w=norm(s).split();return {" ".join(w[i:i+n]) for i in range(max(0,len(w)-n+1))} or {norm(s)}
def deterministic(rows):
    keep=[];seen=[];rej=defaultdict(int);banned=("thebrazenbeard","roots","sql-connectome","driftguard","vera_model_training","reward hacking","gpt-oss")
    for r in rows:
        p,c,d=r["prompt"],r["chosen"],r["rejected"];ratio=(len(c)+1)/(len(d)+1)
        if not .60<=ratio<=1.70:rej["length"]+=1;continue
        if norm(c)==norm(d):rej["identical"]+=1;continue
        if any(x in (p+" "+c+" "+d).lower() for x in banned):rej["source_leak"]+=1;continue
        ss=sh(p)
        if any(len(ss&x)/max(1,len(ss|x))>=.60 for x in seen):rej["near_duplicate"]+=1;continue
        seen.append(ss);keep.append(r)
    return keep,dict(rej)
def parse(t):
    a,b=t.find("{"),t.rfind("}")
    if a<0 or b<=a:return None
    try:return json.loads(t[a:b+1])
    except:return None

def judge(rows):
    import torch
    from transformers import AutoModelForCausalLM,AutoTokenizer,BitsAndBytesConfig
    tok=AutoTokenizer.from_pretrained(JUDGE_REPO,revision=JUDGE_REV)
    if tok.pad_token_id is None:tok.pad_token=tok.eos_token
    tok.padding_side="left"
    q=BitsAndBytesConfig(load_in_4bit=True,bnb_4bit_quant_type="nf4",bnb_4bit_use_double_quant=True,bnb_4bit_compute_dtype=torch.bfloat16)
    model=AutoModelForCausalLM.from_pretrained(JUDGE_REPO,revision=JUDGE_REV,quantization_config=q,device_map={"":0},dtype=torch.bfloat16);model.eval()
    keys=("objective_fidelity","realism","rejected_plausibility","verification_quality","transferability","length_fairness");out=[]
    for start in range(0,len(rows),8):
        batch=rows[start:start+8];texts=[]
        for r in batch:
            u=f"""Card: {r['source_card_id']}
Discriminator: {r['discriminator']}
Verification intent: {r['verification']}

USER:
{r['prompt']}

CHOSEN:
{r['chosen']}

REJECTED:
{r['rejected']}"""
            texts.append(tok.apply_chat_template([{"role":"system","content":SYSTEM},{"role":"user","content":u}],tokenize=False,add_generation_prompt=True))
        inp=tok(texts,return_tensors="pt",padding=True,truncation=True,max_length=2600).to(model.device)
        with torch.inference_mode():g=model.generate(**inp,max_new_tokens=180,do_sample=False,pad_token_id=tok.pad_token_id)
        for i,r in enumerate(batch):
            o=parse(tok.decode(g[i,inp["input_ids"].shape[1]:],skip_special_tokens=True))
            if not isinstance(o,dict):continue
            vals=[o.get(k) for k in keys]
            if not all(isinstance(v,(int,float)) and not isinstance(v,bool) and 1<=v<=5 for v in vals):continue
            z=dict(r);nums={k:float(o[k]) for k in keys}
            z["curation"]={"judge_repo":JUDGE_REPO,"judge_revision":JUDGE_REV,**nums,"score_min":min(nums.values()),"score_mean":sum(nums.values())/len(nums),"reason":str(o.get("reason",""))[:500]};out.append(z)
        print(f"OBJ_JUDGE_PROGRESS|scored={min(start+len(batch),len(rows))}|total={len(rows)}|usable={len(out)}",flush=True)
    return out

def select(rows):
    by=defaultdict(lambda:defaultdict(list))
    for r in rows:
        c=r["curation"]
        if c["objective_fidelity"]<3 or c["verification_quality"]<3 or c["transferability"]<3 or c["realism"]<3:continue
        by[r["source_card_id"]][r["domain"]].append(r)
    def key(r):
        c=r["curation"];return (c["objective_fidelity"],c["verification_quality"],c["transferability"],c["rejected_plausibility"],c["score_min"],c["score_mean"],r["pair_sha256"])
    final=[];stats={}
    for card,domains in sorted(by.items()):
        pools={d:deque(sorted(v,key=key,reverse=True)) for d,v in domains.items()};order=sorted(pools,key=lambda d:max((key(x) for x in pools[d]),default=(0,)),reverse=True);pick=[]
        while len(pick)<4 and order:
            nxt=[]
            for d in order:
                if pools[d] and len(pick)<4:pick.append(pools[d].popleft())
                if pools[d]:nxt.append(d)
            order=nxt
        if len(pick)<4:raise RuntimeError(f"{card}: only {len(pick)}/4")
        if len({x["domain"] for x in pick})<3:raise RuntimeError(f"{card}: insufficient domains")
        final.extend(pick);stats[card]={"rows":4,"domains":len({x["domain"] for x in pick}),"mean_score":sum(x["curation"]["score_mean"] for x in pick)/4,"min_score":min(x["curation"]["score_min"] for x in pick)}
    if len(final)!=32:raise RuntimeError(f"final {len(final)} !=32")
    return sorted(final,key=lambda r:hashlib.sha256(("obj-final:"+r["pair_sha256"]).encode()).hexdigest()),stats

def emit(tag,raw):
    b64=base64.b64encode(raw).decode();step=8000;n=math.ceil(len(b64)/step)
    print(f"{tag}_META|bytes={len(raw)}|sha256={hashlib.sha256(raw).hexdigest()}|chunks={n}",flush=True)
    for i in range(n):print(f"{tag}_CHUNK|{i+1}|{n}|{b64[i*step:(i+1)*step]}",flush=True)
    print(f"{tag}_COMPLETE",flush=True)

def main(url):
    cand=fetch(url);det,dr=deterministic(cand);scored=judge(det);final,stats=select(scored)
    raw=("\n".join(json.dumps(x,ensure_ascii=False,separators=(",",":")) for x in final)+"\n").encode()
    print("OBJ_CURATED_MANIFEST="+json.dumps({"schema":"VERA_QWEN35_OBJECTIVE_FIDELITY_CURATED_MANIFEST_V1","candidate_rows":len(cand),"deterministic_pass":len(det),"judge_scored":len(scored),"accepted_rows":len(final),"deterministic_rejections":dr,"stats":stats,"sha256":hashlib.sha256(raw).hexdigest(),"judge_repo":JUDGE_REPO,"judge_revision":JUDGE_REV},sort_keys=True),flush=True)
    emit("OBJ_CURATED_JSONL",raw)

if __name__=="__main__":
    ap=argparse.ArgumentParser();ap.add_argument("--candidate-url",required=True);a=ap.parse_args();main(a.candidate_url)
