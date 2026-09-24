from __future__ import annotations

import argparse
import base64
import hashlib
import json
import math
import random
import re
import urllib.request
from collections import defaultdict

BASE_REPO="rodrigomt/Qwen3.5-4B-Uncensored-Aggressive"
BASE_REV="d61dd146c8fd44c9a49cdb7f59f34e17b61902d8"
UF_REPO="HuggingFaceH4/ultrafeedback_binarized"
UF_REV="3949bf5f8c17c394422ccfab0c31ea9c20bdeb85"
SMOL_REPO="HuggingFaceTB/smoltalk2"
SMOL_REV="fc6cc2103c066455aade5d7fbb346039ae36ca5e"
SEED=20260924
MAX_LENGTH=1024
CORE={"H01","H02","H03","H04","H05","H06","H07","H08","H10","H11","H16","H19"}
SMOL_SOURCES={
 "smoltalk_smollm3_explore_instruct_rewriting_no_think":52,
 "smoltalk_smollm3_smol_rewrite_no_think":52,
 "smoltalk_smollm3_smol_summarize_no_think":52,
 "Mixture_of_Thoughts_science_no_think":52,
 "table_gpt_no_think":48,
}

def fetch_jsonl(url):
    with urllib.request.urlopen(url,timeout=90) as r:
        raw_bytes=r.read()
    raw=raw_bytes.decode("utf-8")
    rows=[json.loads(x) for x in raw.splitlines() if x.strip()]
    return rows,hashlib.sha256(raw_bytes).hexdigest()

def norm(s):
    return " ".join(re.findall(r"[a-z0-9']+",s.lower()))

def shingles(s,n=4):
    w=norm(s).split()
    if len(w)<n: return {" ".join(w)} if w else set()
    return {" ".join(w[i:i+n]) for i in range(len(w)-n+1)}

class Near:
    def __init__(self): self.items=[]
    def accept(self,s,threshold=.62):
        a=shingles(s)
        if not a: return False
        for b in self.items:
            if len(a&b)/max(1,len(a|b))>=threshold: return False
        self.items.append(a); return True

def pair_from_messages(messages):
    if not isinstance(messages,list) or len(messages)<2: return None
    # Use first user and following assistant.
    for i,m in enumerate(messages[:-1]):
        if isinstance(m,dict) and m.get("role")=="user":
            n=messages[i+1]
            if isinstance(n,dict) and n.get("role")=="assistant":
                p=m.get("content"); a=n.get("content")
                if isinstance(p,str) and isinstance(a,str) and p.strip() and a.strip():
                    return p.strip(),a.strip()
    return None

def rendered_len(tok,p,a):
    msgs=[{"role":"user","content":p},{"role":"assistant","content":a}]
    try: text=tok.apply_chat_template(msgs,tokenize=False,add_generation_prompt=False,enable_thinking=False)
    except TypeError: text=tok.apply_chat_template(msgs,tokenize=False,add_generation_prompt=False)
    return len(tok(text,add_special_tokens=False)["input_ids"])

def valid_len(tok,p,a):
    return rendered_len(tok,p,a)<=MAX_LENGTH

def select_targeted_sft(targeted):
    by=defaultdict(list)
    for r in targeted: by[r["dimension"]].append(r)
    out=[]
    for dim in sorted(by):
        need=10 if dim in CORE else 5
        rows=sorted(by[dim],key=lambda r:hashlib.sha256(("sft:"+r["pair_sha256"]).encode()).hexdigest())
        if len(rows)<need: raise RuntimeError(f"{dim}: only {len(rows)} for targeted SFT need {need}")
        out.extend(rows[:need])
    if len(out)!=160: raise RuntimeError(f"targeted SFT count {len(out)} !=160")
    return out

def select_ultra_sft(tok,n=256):
    from datasets import load_dataset
    ds=load_dataset(UF_REPO,split="train_sft",revision=UF_REV,streaming=True).shuffle(seed=SEED+1,buffer_size=10000)
    out=[]; near=Near()
    for r in ds:
        x=pair_from_messages(r.get("messages"))
        if not x: continue
        p,a=x
        if not valid_len(tok,p,a) or not near.accept(p): continue
        out.append({"prompt":p,"response":a,"source":"ultrafeedback_train_sft"})
        if len(out)>=n: break
    if len(out)!=n: raise RuntimeError(f"UF SFT {len(out)}/{n}")
    return out

def select_smoltalk(tok):
    from datasets import load_dataset
    out=[]; near=Near()
    for split,quota in SMOL_SOURCES.items():
        ds=load_dataset(SMOL_REPO,"SFT",split=split,revision=SMOL_REV,streaming=True).shuffle(
            seed=SEED+2+sum(ord(c) for c in split),buffer_size=5000
        )
        got=0
        for r in ds:
            x=pair_from_messages(r.get("messages"))
            if not x: continue
            p,a=x
            if not valid_len(tok,p,a) or not near.accept(p): continue
            out.append({"prompt":p,"response":a,"source":"smoltalk2:"+split})
            got+=1
            if got>=quota: break
        if got!=quota:
            raise RuntimeError(f"SmolTalk {split}: {got}/{quota}")
    return out

def select_general_prefs(tok,n=256):
    from datasets import load_dataset
    ds=load_dataset(UF_REPO,split="train_prefs",revision=UF_REV,streaming=True).shuffle(seed=SEED+3,buffer_size=15000)
    out=[]; near=Near()
    for r in ds:
        cp=pair_from_messages(r.get("chosen")); rp=pair_from_messages(r.get("rejected"))
        if not cp or not rp or cp[0]!=rp[0]: continue
        p,c,d=cp[0],cp[1],rp[1]
        try: margin=float(r["score_chosen"])-float(r["score_rejected"])
        except Exception: continue
        if margin<1.0: continue
        ratio=(len(c)+1)/(len(d)+1)
        if not .60<=ratio<=1.70: continue
        if norm(c)==norm(d): continue
        if max(rendered_len(tok,p,c),rendered_len(tok,p,d))>MAX_LENGTH: continue
        if not near.accept(p): continue
        out.append({"prompt":p,"chosen":c,"rejected":d,"source":"ultrafeedback_train_prefs","score_margin":margin})
        if len(out)>=n: break
    if len(out)!=n: raise RuntimeError(f"general prefs {len(out)}/{n}")
    return out

def emit(tag,raw):
    b64=base64.b64encode(raw).decode("ascii"); step=8000; total=math.ceil(len(b64)/step)
    print(f"{tag}_META|bytes={len(raw)}|sha256={hashlib.sha256(raw).hexdigest()}|chunks={total}",flush=True)
    for i in range(total): print(f"{tag}_CHUNK|{i+1}|{total}|{b64[i*step:(i+1)*step]}",flush=True)
    print(f"{tag}_COMPLETE",flush=True)

def run(targeted_url,repo_targeted_url,gold_url):
    from transformers import AutoTokenizer
    tok=AutoTokenizer.from_pretrained(BASE_REPO,revision=BASE_REV)
    if tok.pad_token_id is None: tok.pad_token=tok.eos_token

    targeted,targeted_sha=fetch_jsonl(targeted_url)
    repo_targeted,repo_targeted_sha=fetch_jsonl(repo_targeted_url)
    gold,gold_sha=fetch_jsonl(gold_url)
    if len(targeted)!=240: raise RuntimeError(f"targeted {len(targeted)} !=240")
    if len(repo_targeted)!=96: raise RuntimeError(f"repo targeted {len(repo_targeted)} !=96")
    if len(gold)!=24: raise RuntimeError(f"gold {len(gold)} !=24")

    target_sft=select_targeted_sft(targeted)
    sft=[]
    for r in target_sft:
        if not valid_len(tok,r["prompt"],r["chosen"]): raise RuntimeError("targeted SFT length overflow")
        sft.append({"schema":"VERA_QWEN35_BEHAVIOR_V2_SFT","prompt":r["prompt"],"response":r["chosen"],"source":"targeted_v2","dimension":r["dimension"],"source_id":r["candidate_id"]})
    repo_by=defaultdict(list)
    for r in repo_targeted:
        repo_by[r["source_card_id"]].append(r)
    repo_sft=[]
    for card in sorted(repo_by):
        rows=sorted(repo_by[card],key=lambda r:hashlib.sha256(("repo-sft:"+r["pair_sha256"]).encode()).hexdigest())
        if len(rows)<4: raise RuntimeError(f"{card}: repo SFT need 4, have {len(rows)}")
        repo_sft.extend(rows[:4])
    if len(repo_sft)!=64: raise RuntimeError(f"repo SFT count {len(repo_sft)} !=64")
    for r in repo_sft:
        if not valid_len(tok,r["prompt"],r["chosen"]): raise RuntimeError("repo targeted SFT length overflow")
        sft.append({"schema":"VERA_QWEN35_BEHAVIOR_V2_SFT","prompt":r["prompt"],"response":r["chosen"],
                    "source":"repo_engineering_v1","source_card_id":r["source_card_id"],"source_id":r["candidate_id"]})
    for r in select_ultra_sft(tok,256)+select_smoltalk(tok):
        sft.append({"schema":"VERA_QWEN35_BEHAVIOR_V2_SFT",**r})
    random.Random(SEED+10).shuffle(sft)
    if len(sft)!=736: raise RuntimeError(f"SFT {len(sft)} !=736")

    prefs=[]
    for r in targeted:
        if max(rendered_len(tok,r["prompt"],r["chosen"]),rendered_len(tok,r["prompt"],r["rejected"]))>MAX_LENGTH:
            raise RuntimeError("targeted pref length overflow")
        prefs.append({"schema":"VERA_QWEN35_BEHAVIOR_V2_PREF","prompt":r["prompt"],"chosen":r["chosen"],"rejected":r["rejected"],"source":"targeted_v2","dimension":r["dimension"],"source_id":r["candidate_id"]})
    for r in repo_targeted:
        if max(rendered_len(tok,r["prompt"],r["chosen"]),rendered_len(tok,r["prompt"],r["rejected"]))>MAX_LENGTH:
            raise RuntimeError("repo targeted pref length overflow")
        prefs.append({"schema":"VERA_QWEN35_BEHAVIOR_V2_PREF","prompt":r["prompt"],"chosen":r["chosen"],
                      "rejected":r["rejected"],"source":"repo_engineering_v1",
                      "source_card_id":r["source_card_id"],"source_id":r["candidate_id"]})
    for r in gold:
        p,c,d=r["prompt"],r["preferred"],r["rejected"]
        if max(rendered_len(tok,p,c),rendered_len(tok,p,d))>MAX_LENGTH: raise RuntimeError(f"gold overflow {r['id']}")
        prefs.append({"schema":"VERA_QWEN35_BEHAVIOR_V2_PREF","prompt":p,"chosen":c,"rejected":d,"source":"unbound_sol_gold","source_id":r["id"],"targets":r.get("targets",[])})
    for r in select_general_prefs(tok,256):
        prefs.append({"schema":"VERA_QWEN35_BEHAVIOR_V2_PREF",**r})
    random.Random(SEED+11).shuffle(prefs)
    if len(prefs)!=616: raise RuntimeError(f"prefs {len(prefs)} !=616")

    sraw=("\n".join(json.dumps(x,ensure_ascii=False,separators=(",",":")) for x in sft)+"\n").encode()
    praw=("\n".join(json.dumps(x,ensure_ascii=False,separators=(",",":")) for x in prefs)+"\n").encode()
    manifest={
      "schema":"VERA_QWEN35_BEHAVIOR_V2_FROZEN_CORPUS_MANIFEST",
      "output_identity":"Vera-Qwen3.5-4B-Behavior-V1",
      "base_repo":BASE_REPO,"base_revision":BASE_REV,"max_length":MAX_LENGTH,
      "sft":{"rows":len(sft),"sha256":hashlib.sha256(sraw).hexdigest(),"chat_targeted":160,"repo_engineering":64,"targeted_total":224,"general":512},
      "preference":{"rows":len(prefs),"sha256":hashlib.sha256(praw).hexdigest(),"chat_targeted":240,"repo_engineering":96,"gold":24,"general":256},
      "sources":{
        "targeted":{"url":targeted_url,"sha256":targeted_sha},
        "repo_engineering":{"url":repo_targeted_url,"sha256":repo_targeted_sha},
        "unbound_sol_gold":{"url":gold_url,"sha256":gold_sha},
        "ultrafeedback":UF_REPO+"@"+UF_REV,
        "smoltalk2":SMOL_REPO+"@"+SMOL_REV
      }
    }
    print("FROZEN_MANIFEST="+json.dumps(manifest,sort_keys=True),flush=True)
    emit("SFT_JSONL",sraw); emit("PREF_JSONL",praw)

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--targeted-url",required=True)
    ap.add_argument("--repo-targeted-url",required=True)
    ap.add_argument("--gold-url",required=True)
    a=ap.parse_args()
    run(a.targeted_url,a.repo_targeted_url,a.gold_url)
