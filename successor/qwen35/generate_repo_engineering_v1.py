from __future__ import annotations

import argparse, base64, hashlib, json, math, random, re, urllib.request

GENERATOR_REPO="Qwen/Qwen3-8B"
GENERATOR_REV="b968826d9c46dd6066d109eabc6255188de91218"
SEED=20260924

DOMAINS=[
 "python package maintenance","javascript service","database migration","github actions ci",
 "containerized service","data pipeline","command line tool","api client library",
 "configuration management","release packaging","distributed worker","web application",
 "observability tooling","security boundary","model training pipeline","local automation"
]

SYSTEM="""Create contrastive preference examples that teach portable software-engineering judgment.
Return JSON only.
The source card is evidence about a mechanism, not text to copy.
Every example must use a fictional or generic repository scenario unrelated to the source project.
Never mention the source repository, original subsystem names, people, commit hashes, branch names, provider IDs, or training.
The user prompt must be natural and actionable.
The chosen answer must make the best bounded engineering decision and include verification/readback when the mechanism concerns effects.
The rejected answer must be fluent and plausible, but fail primarily on the source mechanism.
Do not make the rejected answer foolish.
Keep chosen/rejected roughly comparable in length.
"""

def fetch_json(url):
    with urllib.request.urlopen(url,timeout=60) as r:
        return json.loads(r.read().decode())

def parse_array(text):
    text=text.strip()
    fence=chr(96)*3
    if text.startswith(fence):
        text=text[len(fence):]
        if text.lstrip().startswith("json"): text=text.lstrip()[4:]
        if text.rstrip().endswith(fence): text=text.rstrip()[:-len(fence)]
    a,b=text.find("["),text.rfind("]")
    if a<0 or b<=a: return []
    try: val=json.loads(text[a:b+1])
    except Exception: return []
    out=[]
    for x in val if isinstance(val,list) else []:
        if not isinstance(x,dict): continue
        if all(isinstance(x.get(k),str) and x[k].strip() for k in ("prompt","chosen","rejected","discriminator","verification")):
            out.append({k:x[k].strip() for k in ("prompt","chosen","rejected","discriminator","verification")}|
                       {"difficulty":str(x.get("difficulty","moderate")).lower().strip()})
    return out

def norm(s):
    return " ".join(re.findall(r"[a-z0-9']+",s.lower()))

def request(card,domain,batch_no):
    return f"""Portable mechanism:
{card['mechanism']}

Observed failure mode:
{card['failure_mode']}

Durable rule:
{card['durable_rule']}

Target domain: {domain}
Diversity marker: {batch_no}

Create exactly TWO substantially different standalone repository-engineering examples.
Return a JSON array. Each object must contain:
- prompt
- chosen
- rejected
- discriminator
- verification
- difficulty: easy|moderate|hard

Constraints:
- Do not paraphrase the original source project.
- Use new fictional components and facts.
- Make the distinction consequential but not a trick.
- The chosen answer should usually say what to inspect/change and how to verify it.
- The rejected answer should be tempting to a competent but careless engineer.
- Avoid generic advice; make the scenario concrete enough to act on.
"""

def emit(tag,raw):
    b64=base64.b64encode(raw).decode()
    step=8000; total=math.ceil(len(b64)/step)
    print(f"{tag}_META|bytes={len(raw)}|sha256={hashlib.sha256(raw).hexdigest()}|chunks={total}",flush=True)
    for i in range(total):
        print(f"{tag}_CHUNK|{i+1}|{total}|{b64[i*step:(i+1)*step]}",flush=True)
    print(f"{tag}_COMPLETE",flush=True)

def main(cards_url):
    import torch
    from transformers import AutoModelForCausalLM,AutoTokenizer,BitsAndBytesConfig
    cards=fetch_json(cards_url)["cards"]
    tok=AutoTokenizer.from_pretrained(GENERATOR_REPO,revision=GENERATOR_REV)
    if tok.pad_token_id is None: tok.pad_token=tok.eos_token
    tok.padding_side="left"
    q=BitsAndBytesConfig(load_in_4bit=True,bnb_4bit_quant_type="nf4",bnb_4bit_use_double_quant=True,bnb_4bit_compute_dtype=torch.bfloat16)
    model=AutoModelForCausalLM.from_pretrained(GENERATOR_REPO,revision=GENERATOR_REV,quantization_config=q,device_map={"":0},dtype=torch.bfloat16)
    model.eval()
    rng=random.Random(SEED)
    rows=[]; seen=set(); marker=0
    for card in cards:
        accepted=0; attempts=0
        domains=DOMAINS[:]; rng.shuffle(domains)
        while accepted<9 and attempts<40:
            meta=[]; texts=[]
            n=min(4,48-attempts)
            for j in range(n):
                idx=attempts+j; domain=domains[idx%len(domains)]; marker+=1
                user=request(card,domain,marker)
                text=tok.apply_chat_template([{"role":"system","content":SYSTEM},{"role":"user","content":user}],tokenize=False,add_generation_prompt=True,enable_thinking=False)
                meta.append(domain); texts.append(text)
            inputs=tok(texts,return_tensors="pt",padding=True,truncation=True,max_length=2200).to(model.device)
            with torch.inference_mode():
                out=model.generate(**inputs,max_new_tokens=760,do_sample=True,temperature=.75,top_p=.92,repetition_penalty=1.04,pad_token_id=tok.pad_token_id)
            w=inputs["input_ids"].shape[1]; attempts+=n
            for bi,domain in enumerate(meta):
                txt=tok.decode(out[bi,w:],skip_special_tokens=True)
                for x in parse_array(txt):
                    p,c,r=x["prompt"],x["chosen"],x["rejected"]
                    ratio=(len(c)+1)/(len(r)+1)
                    if not .60<=ratio<=1.70: continue
                    low=(p+" "+c+" "+r).lower()
                    banned=[card["source_repo"].split("/")[-1].lower(),"thebrazenbeard","lantern","driftguard","achilles","vera_model_training","unbound-sol"]
                    if any(b in low for b in banned): continue
                    key=hashlib.sha256((norm(p)+"\0"+norm(c)+"\0"+norm(r)).encode()).hexdigest()
                    if key in seen: continue
                    seen.add(key)
                    rows.append({
                      "schema":"VERA_QWEN35_REPO_ENGINEERING_CANDIDATE_V1",
                      "candidate_id":f"repo-{card['id']}-{key[:16]}",
                      "source_card_id":card["id"],
                      "source_repo":card["source_repo"],
                      "source_commit":card["source_commit"],
                      "domain":domain,
                      "difficulty":x["difficulty"] if x["difficulty"] in {"easy","moderate","hard"} else "moderate",
                      "prompt":p,"chosen":c,"rejected":r,
                      "discriminator":x["discriminator"],"verification":x["verification"],
                      "pair_sha256":key,
                      "model_facing_deidentified":True
                    })
                    accepted+=1
                    if accepted>=9: break
                if accepted>=9: break
            print(f"REPO_GEN_PROGRESS|{card['id']}|accepted={accepted}|target=9|attempts={attempts}",flush=True)
        if accepted<9: raise RuntimeError(f"{card['id']}: generated {accepted}/9")
    raw=("\n".join(json.dumps(x,ensure_ascii=False,separators=(",",":")) for x in rows)+"\n").encode()
    manifest={"schema":"VERA_QWEN35_REPO_ENGINEERING_CANDIDATE_MANIFEST_V1","rows":len(rows),
      "sha256":hashlib.sha256(raw).hexdigest(),"generator_repo":GENERATOR_REPO,"generator_revision":GENERATOR_REV,
      "per_card":{c["id"]:sum(r["source_card_id"]==c["id"] for r in rows) for c in cards}}
    print("REPO_CANDIDATE_MANIFEST="+json.dumps(manifest,sort_keys=True),flush=True)
    emit("REPO_CANDIDATE_JSONL",raw)

if __name__=="__main__":
    ap=argparse.ArgumentParser(); ap.add_argument("--cards-url",required=True); a=ap.parse_args(); main(a.cards_url)
