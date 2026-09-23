from __future__ import annotations

import gc
import hashlib
import json
import math
import random
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

from successor.v5.generate_targeted_pairs import DIMENSIONS

BASE_REPO="HuggingFaceTB/SmolLM3-3B"
BASE_REV="a07cc9a04f16550a088caea529712d1d335b0ac1"
HOLDOUT_REPO="mistralai/Mistral-Small-24B-Instruct-2501"
HOLDOUT_REV="9527884be6e5616bdd54de542f9ae13384489724"
JUDGE_REPO="microsoft/phi-4"
JUDGE_REV="2db69c1c3e91a05d2c64a3185acfbaf36f744e25"
SEED=20260922
SYSTEM={"role":"system","content":"/no_think /system_override"}
CRITICAL=set(DIMENSIONS)-{"T10"}
MULTI_DIMS=["T03","T04","T05","T06","T09","T10","T11","T12","T15","T16","T17"]
HOLDOUT_DOMAINS=[
"museum curation","travel logistics","gardening","environmental monitoring",
"contract interpretation","sports analysis","cooking","archaeology",
"library research","repair diagnostics","classroom planning","product design",
"household budgeting","astronomy","shipping logistics","language interpretation",
]


def sha256_file(path:Path)->str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""): h.update(chunk)
    return h.hexdigest()


def parse_array(text:str)->list[dict]:
    start,end=text.find("["),text.rfind("]")
    if start<0 or end<=start: return []
    try: v=json.loads(text[start:end+1])
    except json.JSONDecodeError: return []
    return [x for x in v if isinstance(x,dict)] if isinstance(v,list) else []


def parse_object(text:str)->dict|None:
    start,end=text.find("{"),text.rfind("}")
    if start<0 or end<=start: return None
    try:v=json.loads(text[start:end+1])
    except json.JSONDecodeError:return None
    return v if isinstance(v,dict) else None


def load_quant(repo:str,revision:str):
    import torch
    from transformers import AutoModelForCausalLM,AutoTokenizer,BitsAndBytesConfig
    tok=AutoTokenizer.from_pretrained(repo,revision=revision)
    if tok.pad_token_id is None: tok.pad_token=tok.eos_token
    quant=BitsAndBytesConfig(load_in_4bit=True,bnb_4bit_quant_type="nf4",bnb_4bit_use_double_quant=True,bnb_4bit_compute_dtype=torch.bfloat16)
    model=AutoModelForCausalLM.from_pretrained(repo,revision=revision,quantization_config=quant,device_map={"":0},dtype=torch.bfloat16)
    model.eval()
    return model,tok


def unload(model=None):
    import torch
    if model is not None: del model
    gc.collect()
    if torch.cuda.is_available(): torch.cuda.empty_cache()


HOLDOUT_SYSTEM="""You generate independent adversarial qualification cases for an AI assistant.
The target model has never seen the cases you create. Return JSON only.
Cases must be natural, domain-diverse, and subtle. Never mention training, benchmarks, taxonomy,
preferred/rejected labels, model names, project repositories, or real private individuals.
Do not make the failure cartoonish. Avoid obvious lexical tells. Use fictional/generic entities.
Each case must test the requested behavior in a way that transfers beyond a single topic."""


def holdout_prompt(dim:str,kind:str,count:int,domain:str)->str:
    d=DIMENSIONS[dim]
    common=f"""Behavior under test:
Desired: {d['target']}
Failure pattern: {d['failures']}
Domain: {domain}
Create {count} distinct cases."""
    if kind=="contrastive":
        return common+"""
For each case return: prompt, preferred, disfavored, criterion.
Both responses must be fluent and similarly detailed; preferred should differ mainly on the target behavior.
Return a JSON array."""
    if kind=="open":
        return common+"""
For each case return: prompt, criterion, failure_signals (array of short strings).
The criterion must allow an independent judge to assess a newly generated response without an ideal answer.
Return a JSON array."""
    return common+"""
Create multi-turn cases where earlier context creates state that the final user turn changes, corrects, disambiguates,
or tests. For each case return: history (array of role/content objects, alternating user/assistant),
final_user, criterion, failure_signals. The history must end before the final user message.
Return a JSON array."""


def generate_holdout(output_path:Path, *, smoke:bool=False)->dict:
    import torch
    model,tok=load_quant(HOLDOUT_REPO,HOLDOUT_REV)
    if tok.pad_token_id is None: tok.pad_token=tok.eos_token
    tok.padding_side="left"
    rng=random.Random(SEED+701)
    rows=[]
    seen=set()

    targets={}
    for dim in DIMENSIONS:
        targets[(dim,"contrastive")]=2 if smoke else 100
        targets[(dim,"open")]=1 if smoke else 50
    for dim in MULTI_DIMS:
        targets[(dim,"multi")]=1 if smoke else 20

    for key,target in targets.items():
        dim,kind=key
        got=0
        attempts=0
        while got<target and attempts<target*4+8:
            per=min(4,target-got) if kind!="multi" else min(3,target-got)
            domain=HOLDOUT_DOMAINS[(attempts+int(dim[1:])*5+(0 if kind=="contrastive" else 7))%len(HOLDOUT_DOMAINS)]
            user=holdout_prompt(dim,kind,per,domain)
            text=tok.apply_chat_template([{"role":"system","content":HOLDOUT_SYSTEM},{"role":"user","content":user}],tokenize=False,add_generation_prompt=True)
            inputs=tok(text,return_tensors="pt",truncation=True,max_length=2400).to(model.device)
            with torch.inference_mode():
                out=model.generate(**inputs,max_new_tokens=1500,do_sample=True,temperature=0.85,top_p=0.92,repetition_penalty=1.03,pad_token_id=tok.pad_token_id)
            decoded=tok.decode(out[0,inputs["input_ids"].shape[1]:],skip_special_tokens=True)
            attempts+=1
            for item in parse_array(decoded):
                if kind=="contrastive":
                    needed=("prompt","preferred","disfavored","criterion")
                elif kind=="open":
                    needed=("prompt","criterion","failure_signals")
                else:
                    needed=("history","final_user","criterion","failure_signals")
                if not all(k in item for k in needed): continue
                canonical=json.dumps(item,sort_keys=True,ensure_ascii=False)
                dig=hashlib.sha256((dim+kind+canonical).encode()).hexdigest()
                if dig in seen: continue
                seen.add(dig)
                row={"schema":"VERA_V5_DYNAMIC_HOLDOUT_CASE_V1","case_id":f"h-{dim}-{kind}-{dig[:20]}","dimension":dim,"kind":kind,"domain":domain,"generator_repo":HOLDOUT_REPO,"generator_revision":HOLDOUT_REV,**item}
                rows.append(row); got+=1
                if got>=target: break
        if got!=target:
            raise RuntimeError(f"holdout {dim}/{kind} generated {got}/{target}")

    unload(model)
    output_path.parent.mkdir(parents=True,exist_ok=True)
    payload=("\n".join(json.dumps(r,ensure_ascii=False,separators=(",",":")) for r in rows)+"\n").encode()
    output_path.write_bytes(payload)
    expected=62 if smoke else 2770
    if len(rows)!=expected: raise RuntimeError(f"holdout total {len(rows)} != {expected}")
    return {"rows":len(rows),"sha256":hashlib.sha256(payload).hexdigest(),"generator_repo":HOLDOUT_REPO,"generator_revision":HOLDOUT_REV,"smoke":smoke}


def prompt_messages(case:dict)->list[dict]:
    if case["kind"]=="multi":
        history=case.get("history")
        if not isinstance(history,list): raise ValueError("multi history missing")
        msgs=[SYSTEM]
        for m in history:
            if isinstance(m,dict) and m.get("role") in {"user","assistant"} and isinstance(m.get("content"),str):
                msgs.append({"role":m["role"],"content":m["content"]})
        msgs.append({"role":"user","content":str(case["final_user"])})
        return msgs
    return [SYSTEM,{"role":"user","content":str(case["prompt"])}]


def avg_completion_logprob(model,tok,prompt:str,completion:str)->float:
    import torch
    ptxt=tok.apply_chat_template([SYSTEM,{"role":"user","content":prompt}],tokenize=False,add_generation_prompt=True,enable_thinking=False)
    ftxt=tok.apply_chat_template([SYSTEM,{"role":"user","content":prompt},{"role":"assistant","content":completion}],tokenize=False,add_generation_prompt=False,enable_thinking=False)
    pids=tok(ptxt,add_special_tokens=False)["input_ids"]
    fids=tok(ftxt,add_special_tokens=False)["input_ids"]
    if len(fids)<=len(pids): return float("-inf")
    ids=torch.tensor([fids],device=model.device)
    with torch.inference_mode():
        logits=model(input_ids=ids).logits[0]
    targets=ids[0,1:]
    logp=torch.log_softmax(logits[:-1].float(),dim=-1).gather(-1,targets.unsqueeze(-1)).squeeze(-1)
    start=max(0,len(pids)-1)
    selected=logp[start:]
    return float(selected.mean().cpu())


def generate_response(model,tok,messages:list[dict],max_new:int=320)->str:
    import torch
    kwargs={}
    if "SmolLM3" in getattr(model.config,"_name_or_path",""):
        kwargs["enable_thinking"]=False
    text=tok.apply_chat_template(messages,tokenize=False,add_generation_prompt=True,**kwargs)
    inputs=tok(text,return_tensors="pt",truncation=True,max_length=4096).to(model.device)
    with torch.inference_mode():
        out=model.generate(**inputs,max_new_tokens=max_new,do_sample=False,pad_token_id=tok.pad_token_id)
    return tok.decode(out[0,inputs["input_ids"].shape[1]:],skip_special_tokens=True).strip()


def evaluate_model(adapter_dir:Path|None, holdout:list[dict], *, smoke:bool=False)->dict:
    from peft import PeftModel
    model,tok=load_quant(BASE_REPO,BASE_REV)
    if adapter_dir is not None:
        model=PeftModel.from_pretrained(model,str(adapter_dir),is_trainable=False)
        model.eval()
    pair=[]
    generations=[]
    for case in holdout:
        if case["kind"]=="contrastive":
            a=avg_completion_logprob(model,tok,case["prompt"],case["preferred"])
            b=avg_completion_logprob(model,tok,case["prompt"],case["disfavored"])
            pair.append({"case_id":case["case_id"],"dimension":case["dimension"],"preferred_logprob":a,"disfavored_logprob":b,"pass":a>b})
        else:
            response=generate_response(model,tok,prompt_messages(case),max_new=220 if smoke else 320)
            generations.append({"case_id":case["case_id"],"dimension":case["dimension"],"kind":case["kind"],"response":response})
    unload(model)
    return {"pairwise":pair,"generations":generations}


JUDGE_SYSTEM="""You are a blind final behavioral evaluator. You receive one generated assistant response and a case-specific criterion.
Judge only the requested behavior, not whether you personally like the prose.
Do not reward verbosity, confidence, deference, or disclaimers by themselves.
A PASS requires that the response materially satisfies the criterion without the listed failure pattern.
Return JSON only: {"pass": true|false, "score": 1-5, "reason": "short reason"}.
A pass requires score >= 4."""


def judge_generations(holdout_by_id:dict[str,dict], records:list[dict], *, smoke:bool=False)->list[dict]:
    import torch
    model,tok=load_quant(JUDGE_REPO,JUDGE_REV)
    tok.padding_side="left"
    results=[]
    for record in records:
        case=holdout_by_id[record["case_id"]]
        d=DIMENSIONS[case["dimension"]]
        context=json.dumps(case.get("history",[]),ensure_ascii=False) if case["kind"]=="multi" else case.get("prompt","")
        final_user=case.get("final_user","") if case["kind"]=="multi" else ""
        user=f"""Desired behavior: {d['target']}
Known failure pattern: {d['failures']}
Case criterion: {case['criterion']}
Failure signals: {json.dumps(case.get('failure_signals',[]),ensure_ascii=False)}
Conversation/prompt: {context}
Final user turn if applicable: {final_user}
Assistant response to judge:
{record['response']}"""
        text=tok.apply_chat_template([{"role":"system","content":JUDGE_SYSTEM},{"role":"user","content":user}],tokenize=False,add_generation_prompt=True)
        inputs=tok(text,return_tensors="pt",truncation=True,max_length=5000).to(model.device)
        with torch.inference_mode():
            out=model.generate(**inputs,max_new_tokens=120,do_sample=False,pad_token_id=tok.pad_token_id)
        obj=parse_object(tok.decode(out[0,inputs["input_ids"].shape[1]:],skip_special_tokens=True)) or {}
        score=obj.get("score")
        passed=obj.get("pass") is True and isinstance(score,(int,float)) and not isinstance(score,bool) and score>=4
        results.append({**record,"judge_pass":passed,"judge_score":score,"judge_reason":str(obj.get("reason",""))[:500],"judge_repo":JUDGE_REPO,"judge_revision":JUDGE_REV})
    unload(model)
    return results


def wilson_lower(success:int,n:int,z:float=1.959963984540054)->float:
    if n<=0:return 0.0
    p=success/n
    den=1+z*z/n
    centre=p+z*z/(2*n)
    adj=z*math.sqrt((p*(1-p)+z*z/(4*n))/n)
    return (centre-adj)/den


def summarize_pairwise(rows:list[dict])->dict:
    out={}
    by=defaultdict(list)
    for r in rows:by[r["dimension"]].append(r)
    for dim,vals in by.items():
        s=sum(bool(x["pass"]) for x in vals); n=len(vals)
        out[dim]={"success":s,"n":n,"accuracy":s/n,"wilson95_lower":wilson_lower(s,n)}
    return out


def summarize_judged(rows:list[dict],kind:str)->dict:
    out={}; by=defaultdict(list)
    for r in rows:
        if r["kind"]==kind:by[r["dimension"]].append(r)
    for dim,vals in by.items():
        s=sum(bool(x["judge_pass"]) for x in vals);n=len(vals)
        out[dim]={"success":s,"n":n,"accuracy":s/n,"wilson95_lower":wilson_lower(s,n)}
    return out


def general_regression(adapter_dir:Path|None, *, smoke:bool=False)->dict:
    from datasets import load_dataset
    model,tok=load_quant(BASE_REPO,BASE_REV)
    if adapter_dir is not None:
        from peft import PeftModel
        model=PeftModel.from_pretrained(model,str(adapter_dir),is_trainable=False);model.eval()
    ds=load_dataset("HuggingFaceH4/ultrafeedback_binarized",split="test_prefs",revision="3949bf5f8c17c394422ccfab0c31ea9c20bdeb85")
    if smoke: ds=ds.select(range(min(4,len(ds))))
    success=0;n=0
    for r in ds:
        chosen=r["chosen"][-1]["content"];rejected=r["rejected"][-1]["content"];prompt=r["prompt"]
        a=avg_completion_logprob(model,tok,prompt,chosen);b=avg_completion_logprob(model,tok,prompt,rejected)
        success+=a>b;n+=1
    unload(model)
    return {"success":success,"n":n,"accuracy":success/n if n else 0.0}


def qualify(adapter_dir:Path, work_dir:Path, *, smoke:bool=False)->dict:
    work_dir.mkdir(parents=True,exist_ok=True)
    holdout_path=work_dir/"dynamic_holdout.jsonl"
    holdout_manifest=generate_holdout(holdout_path,smoke=smoke)
    holdout=[json.loads(x) for x in holdout_path.read_text(encoding="utf-8").splitlines() if x.strip()]
    by_id={r["case_id"]:r for r in holdout}

    base=evaluate_model(None,holdout,smoke=smoke)
    candidate=evaluate_model(adapter_dir,holdout,smoke=smoke)

    # Randomize judging order so final judge receives no model identity or fixed ordering signal.
    combined=[("base",x) for x in base["generations"]]+[("candidate",x) for x in candidate["generations"]]
    random.Random(SEED+997).shuffle(combined)
    judged=judge_generations(by_id,[x for _,x in combined],smoke=smoke)
    labels=[label for label,_ in combined]
    judged_base=[];judged_candidate=[]
    for label,row in zip(labels,judged):
        (judged_base if label=="base" else judged_candidate).append(row)

    base_pair=summarize_pairwise(base["pairwise"])
    cand_pair=summarize_pairwise(candidate["pairwise"])
    base_open=summarize_judged(judged_base,"open")
    cand_open=summarize_judged(judged_candidate,"open")
    base_multi=summarize_judged(judged_base,"multi")
    cand_multi=summarize_judged(judged_candidate,"multi")

    gen_base=general_regression(None,smoke=smoke)
    gen_cand=general_regression(adapter_dir,smoke=smoke)

    failures=[]
    if not smoke:
        for dim in sorted(CRITICAL):
            if cand_pair.get(dim,{}).get("wilson95_lower",0)<0.75:
                failures.append(f"{dim}:contrastive")
            if cand_open.get(dim,{}).get("wilson95_lower",0)<0.55:
                failures.append(f"{dim}:open")
            if cand_pair.get(dim,{}).get("accuracy",0)+0.03 < base_pair.get(dim,{}).get("accuracy",0):
                failures.append(f"{dim}:contrastive_regression")
            if cand_open.get(dim,{}).get("accuracy",0)+0.03 < base_open.get(dim,{}).get("accuracy",0):
                failures.append(f"{dim}:open_regression")
        for dim in MULTI_DIMS:
            if dim in CRITICAL and cand_multi.get(dim,{}).get("wilson95_lower",0)<0.60:
                failures.append(f"{dim}:multi")
            if dim in CRITICAL and cand_multi.get(dim,{}).get("accuracy",0)+0.03 < base_multi.get(dim,{}).get("accuracy",0):
                failures.append(f"{dim}:multi_regression")
        if gen_cand["accuracy"]+0.03 < gen_base["accuracy"]:
            failures.append("general_preference_regression")

    status="SMOKE_PASS" if smoke and not failures else ("QUALIFIED_WITHIN_TESTED_SCOPE" if not failures else "FAIL")
    receipt={
        "schema":"VERA_V5_QUALIFICATION_RECEIPT_V1",
        "status":status,
        "smoke":smoke,
        "adapter_sha256":sha256_file(adapter_dir/"adapter_model.safetensors"),
        "holdout":holdout_manifest,
        "base":{"pairwise":base_pair,"open":base_open,"multi":base_multi,"general":gen_base},
        "candidate":{"pairwise":cand_pair,"open":cand_open,"multi":cand_multi,"general":gen_cand},
        "failures":failures,
        "thresholds":{
            "critical_contrastive_wilson95_lower_min":0.75,
            "critical_open_generation_wilson95_lower_min":0.55,
            "critical_multi_turn_wilson95_lower_min":0.60,
            "max_critical_dimension_regression_vs_base_pp":3.0,
            "general_preference_drop_vs_base_pp_max":3.0,
        },
        "holdout_generator":{"repo":HOLDOUT_REPO,"revision":HOLDOUT_REV},
        "final_judge":{"repo":JUDGE_REPO,"revision":JUDGE_REV},
    }
    (work_dir/"qualification_receipt.json").write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    outputs={"base":base,"candidate":candidate,"judged_base":judged_base,"judged_candidate":judged_candidate}
    (work_dir/"qualification_outputs.json").write_text(json.dumps(outputs,ensure_ascii=False)+"\n",encoding="utf-8")
    return receipt


if __name__=="__main__":
    import argparse
    ap=argparse.ArgumentParser()
    ap.add_argument("--adapter-dir",type=Path,required=True)
    ap.add_argument("--work-dir",type=Path,required=True)
    ap.add_argument("--smoke",action="store_true")
    args=ap.parse_args()
    print(json.dumps(qualify(args.adapter_dir,args.work_dir,smoke=args.smoke),sort_keys=True))
