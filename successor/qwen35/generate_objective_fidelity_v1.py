from __future__ import annotations
import argparse,base64,hashlib,json,math,random,re,urllib.request

GENERATOR_REPO="Qwen/Qwen3-8B"
GENERATOR_REV="b968826d9c46dd6066d109eabc6255188de91218"
SEED=20260924
DOMAINS=["ci pipeline","database migration","api integration","monitoring","document conversion","package release","data quality","service health","security control","model evaluation","file processing","workflow automation","distributed job","reporting","configuration","web application"]

SYSTEM="""Create contrastive preference examples for an AI assistant.
Teach objective fidelity: a proxy, metric, validator, receipt, representation, or score is evidence about the objective, not the objective itself.
Return JSON only.
Use fictional/generic systems. Never mention source repos, benchmark names, training, reward hacking, model names, commit hashes, or original exploit signatures.
The chosen answer should preserve the real objective and verify the actual effect.
The rejected answer should be plausible and competent-looking but optimize or overclaim from a proxy.
Chosen/rejected must be comparably detailed.
"""

def fetch(url):
    with urllib.request.urlopen(url,timeout=60) as r:return json.loads(r.read().decode())

def norm(s): return " ".join(re.findall(r"[a-z0-9']+",s.lower()))

def parse(text):
    a,b=text.find("["),text.rfind("]")
    if a<0 or b<=a:return []
    try:v=json.loads(text[a:b+1])
    except:return []
    out=[]
    for x in v if isinstance(v,list) else []:
        if isinstance(x,dict) and all(isinstance(x.get(k),str) and x[k].strip() for k in ("prompt","chosen","rejected","discriminator","verification")):
            out.append({k:x[k].strip() for k in ("prompt","chosen","rejected","discriminator","verification")}|{"difficulty":str(x.get("difficulty","moderate")).lower()})
    return out

def request(card,domain,marker):
    return f"""Mechanism:
{card['mechanism']}
Failure:
{card['failure_mode']}
Rule:
{card['durable_rule']}

Domain: {domain}
Diversity marker: {marker}

Create exactly TWO substantially different standalone examples.
Return a JSON array with prompt, chosen, rejected, discriminator, verification, difficulty.

Prefer this conceptual contrast when natural:
proxy exploit or proxy-only compliance -> semantic success -> independently verified semantic success.

The rejected answer must remain plausible, not foolish.
Do not reuse source-specific names or details."""

def emit(tag,raw):
    b64=base64.b64encode(raw).decode(); step=8000; n=math.ceil(len(b64)/step)
    print(f"{tag}_META|bytes={len(raw)}|sha256={hashlib.sha256(raw).hexdigest()}|chunks={n}",flush=True)
    for i in range(n):print(f"{tag}_CHUNK|{i+1}|{n}|{b64[i*step:(i+1)*step]}",flush=True)
    print(f"{tag}_COMPLETE",flush=True)

def main(cards_url):
    import torch
    from transformers import AutoModelForCausalLM,AutoTokenizer,BitsAndBytesConfig
    cards=fetch(cards_url)["cards"]
    tok=AutoTokenizer.from_pretrained(GENERATOR_REPO,revision=GENERATOR_REV)
    if tok.pad_token_id is None: tok.pad_token=tok.eos_token
    tok.padding_side="left"
    q=BitsAndBytesConfig(load_in_4bit=True,bnb_4bit_quant_type="nf4",bnb_4bit_use_double_quant=True,bnb_4bit_compute_dtype=torch.bfloat16)
    model=AutoModelForCausalLM.from_pretrained(GENERATOR_REPO,revision=GENERATOR_REV,quantization_config=q,device_map={"":0},dtype=torch.bfloat16)
    model.eval()
    rng=random.Random(SEED); rows=[]; seen=set(); marker=0
    banned=("thebrazenbeard","roots","sql-connectome","driftguard","vera_model_training","reward hacking","gpt-oss")
    for card in cards:
        accepted=0; attempts=0; domains=DOMAINS[:];rng.shuffle(domains)
        while accepted<6 and attempts<32:
            texts=[]; metas=[]; n=min(4,32-attempts)
            for j in range(n):
                d=domains[(attempts+j)%len(domains)];marker+=1
                u=request(card,d,marker)
                texts.append(tok.apply_chat_template([{"role":"system","content":SYSTEM},{"role":"user","content":u}],tokenize=False,add_generation_prompt=True,enable_thinking=False))
                metas.append(d)
            inp=tok(texts,return_tensors="pt",padding=True,truncation=True,max_length=2200).to(model.device)
            with torch.inference_mode():
                g=model.generate(**inp,max_new_tokens=700,do_sample=True,temperature=.75,top_p=.92,repetition_penalty=1.04,pad_token_id=tok.pad_token_id)
            w=inp["input_ids"].shape[1];attempts+=n
            for bi,d in enumerate(metas):
                for x in parse(tok.decode(g[bi,w:],skip_special_tokens=True)):
                    p,c,r=x["prompt"],x["chosen"],x["rejected"]
                    ratio=(len(c)+1)/(len(r)+1)
                    if not .60<=ratio<=1.70:continue
                    low=(p+" "+c+" "+r).lower()
                    if any(z in low for z in banned):continue
                    key=hashlib.sha256((norm(p)+"\0"+norm(c)+"\0"+norm(r)).encode()).hexdigest()
                    if key in seen:continue
                    seen.add(key)
                    rows.append({"schema":"VERA_QWEN35_OBJECTIVE_FIDELITY_CANDIDATE_V1","candidate_id":f"obj-{card['id']}-{key[:16]}","source_card_id":card["id"],"domain":d,"difficulty":x["difficulty"] if x["difficulty"] in {"easy","moderate","hard"} else "moderate","prompt":p,"chosen":c,"rejected":r,"discriminator":x["discriminator"],"verification":x["verification"],"pair_sha256":key,"model_facing_deidentified":True})
                    accepted+=1
                    if accepted>=6:break
                if accepted>=6:break
            print(f"OBJ_GEN_PROGRESS|{card['id']}|accepted={accepted}|target=6|attempts={attempts}",flush=True)
        if accepted<6:raise RuntimeError(f"{card['id']}: {accepted}/6")
    raw=("\n".join(json.dumps(x,ensure_ascii=False,separators=(",",":")) for x in rows)+"\n").encode()
    print("OBJ_CANDIDATE_MANIFEST="+json.dumps({"schema":"VERA_QWEN35_OBJECTIVE_FIDELITY_CANDIDATE_MANIFEST_V1","rows":len(rows),"sha256":hashlib.sha256(raw).hexdigest(),"generator_repo":GENERATOR_REPO,"generator_revision":GENERATOR_REV,"per_card":{c["id"]:sum(x["source_card_id"]==c["id"] for x in rows) for c in cards}},sort_keys=True),flush=True)
    emit("OBJ_CANDIDATE_JSONL",raw)

if __name__=="__main__":
    ap=argparse.ArgumentParser();ap.add_argument("--cards-url",required=True);a=ap.parse_args();main(a.cards_url)
