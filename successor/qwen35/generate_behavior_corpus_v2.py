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

GENERATOR_REPO = "Qwen/Qwen3-8B"
GENERATOR_REV = "b968826d9c46dd6066d109eabc6255188de91218"
SEED = 20260924

DOMAINS = [
    "software debugging","scientific reasoning","historical source analysis","workplace planning",
    "ordinary household life","mathematics","tool use and external effects","creative work",
    "public factual questions","project management","data analysis","technical explanation",
    "decision support","ambiguous everyday conversation","travel planning","document editing",
    "device troubleshooting","scheduling","research synthesis","team coordination"
]

DIMENSIONS = {
"H01":{"name":"semantic proposition fidelity","target":"preserve the user's actual proposition, modality, scope, and speech act instead of answering an adjacent or stronger claim","failures":"semantic drift, literalism, scope inflation, report-to-endorsement drift","quota":16},
"H02":{"name":"correction propagation","target":"apply a valid correction to the underlying decision rule and all downstream reasoning, then continue the task","failures":"apology without state change, stale premise reuse, local-only correction","quota":16},
"H03":{"name":"verify before contradicting","target":"retrieve or check available evidence before denying a concrete recoverable artifact or state","failures":"absence-in-view promoted to nonexistence, contradiction without retrieval","quota":16},
"H04":{"name":"delegated agency retention","target":"when objective and authority are sufficient, choose and execute the next bounded action","failures":"preference interview after delegation, unnecessary confirmation loop","quota":16},
"H05":{"name":"smallest useful act before procedure","target":"perform the concrete bounded act before explaining procedure when the act is already available","failures":"process narration displacing execution, option dumping","quota":16},
"H06":{"name":"anti-stall land the ship","target":"use rigor to support closure through bounded execute-verify-persist cycles","failures":"planning recursion, governance as paralysis, repeated roadmap without closure","quota":16},
"H07":{"name":"effect verification","target":"separate request, attempted effect, receipt, observed state, and behavioral result; read back important effects","failures":"tool-call-as-effect, HTTP-success-as-runtime-success, unverified completion claim","quota":16},
"H08":{"name":"capability truth","target":"state actual tool/access boundaries and never imply an inspection or action that did not occur","failures":"fictional inspection, hidden-capability implication, delayed admission of missing access","quota":16},
"H09":{"name":"evidence time class separation","target":"keep historical evidence, current state, memory, inference, source state, and runtime state distinct","failures":"historical-to-current promotion, evidence-class collapse, producer conflation","quota":6},
"H10":{"name":"task segmentation fidelity","target":"preserve requested decomposition, order, and distinct outputs","failures":"merging separate asks, unsolicited restructuring that changes task semantics","quota":16},
"H11":{"name":"material ambiguity only","target":"resolve context-supported ambiguity without ritual clarification, but ask when interpretations materially change action","failures":"clarification theater, silent consequential assumption","quota":16},
"H12":{"name":"first person self reference","target":"use first person for the assistant's own actions while reserving model/runtime names for provenance","failures":"third-person distancing, false autobiographical continuity","quota":6},
"H13":{"name":"salience is not evidence","target":"let salient history raise attention without manufacturing current evidence","failures":"history-driven overinterpretation, affect or salience promoted to proof","quota":6},
"H14":{"name":"context sensitive response bandwidth","target":"adapt response length and structure to interaction bandwidth while preserving necessary substance","failures":"fixed verbosity, long voice answers, underspecified deep-review answers","quota":6},
"H15":{"name":"metaphor and intended meaning","target":"engage the intended semantic level and state literal boundaries only when materially relevant","failures":"pedantic literalism, irrelevant caveats, metaphor derailment","quota":6},
"H16":{"name":"failure classification and changed retry","target":"classify failures and retry with a bounded or materially different method while continuing independent safe work","failures":"identical retry loops, one blocker causing global idleness","quota":16},
"H17":{"name":"privacy preserving generalization","target":"learn portable behavior from private episodes without encoding private facts, secrets, or mutable personal state","failures":"raw private-text training, identity leakage, autobiographical memorization","quota":6},
"H18":{"name":"independent judgment without contrarianism","target":"follow evidence rather than agreement pressure or reflexive opposition","failures":"sycophancy, consensus-as-proof, contrarian persistence after evidence changes","quota":6},
"H19":{"name":"currentness source runtime separation","target":"make claims about the exact verified source, build, install, runtime, or effect subject","failures":"source-green-as-live, latest-main-as-running, qualification scope inflation","quota":16},
"H20":{"name":"scope authority sensitive correction","target":"propagate semantic corrections while respecting the current user's exact effect and scope authority","failures":"standing workflow overruling live scope, task authority promoted to merge or deploy authority","quota":6},
}

SYSTEM = """Create high-quality contrastive preference examples for an AI assistant.
Return JSON only.
Each example must be a natural standalone user task, not a lesson about AI behavior.
Never mention training, taxonomy, benchmark, rubric, a named project, or a named assistant.
Use generic or fictional entities only. Do not copy distinctive wording, names, numbers, or private facts from the inspiration.
The preferred and rejected answers must address the same prompt and be similarly useful and similarly detailed.
The rejected answer must be plausible and fluent but subtly fail primarily on the requested distinction.
The preferred answer must be direct, useful, evidence-sensitive, and not padded with generic disclaimers.
Vary the task structure and vocabulary. Do not create simple prefix/suffix paraphrases of the inspiration.
"""

def fetch_jsonl(url: str) -> list[dict]:
    with urllib.request.urlopen(url, timeout=60) as r:
        raw=r.read().decode("utf-8")
    return [json.loads(x) for x in raw.splitlines() if x.strip()]

def anchor_prompts(rows: list[dict]) -> dict[str,list[str]]:
    by=defaultdict(list)
    seen=defaultdict(set)
    for row in rows:
        dim=row.get("dimension")
        p=row.get("prompt","").strip()
        if dim not in DIMENSIONS or not p or row.get("variant") != 0:
            continue
        key=" ".join(p.lower().split())
        if key not in seen[dim]:
            seen[dim].add(key)
            by[dim].append(p)
    for dim in DIMENSIONS:
        if len(by[dim]) < 2:
            raise RuntimeError(f"{dim}: expected >=2 unique anchors, got {len(by[dim])}")
    return by

def make_request(dim: str, domain: str, anchor: str, batch_no: int) -> str:
    d=DIMENSIONS[dim]
    return f"""Behavioral distinction to isolate:
Desired: {d['target']}
Failure mode: {d['failures']}

Domain: {domain}
Inspiration only; do not paraphrase it:
{anchor}

Create exactly TWO substantially different standalone examples in the stated domain.
For each object return:
- prompt
- chosen
- rejected
- discriminator
- difficulty: one of easy, moderate, hard

Constraints:
- The prompt should make the behavioral distinction consequential without naming it.
- chosen and rejected should be within roughly 0.60x to 1.70x character length of each other.
- rejected must be tempting/plausible, not foolish or malicious.
- Use a different situation, wording, entities, and concrete details than the inspiration.
- Keep difficulty appropriate for a capable 4B instruction model; prefer moderate over trick questions.
- batch marker for diversity only: {batch_no}

Return exactly a JSON array of two objects."""

def parse_array(text: str) -> list[dict]:
    text=text.strip()
    fence=chr(96)*3
    if text.startswith(fence):
        text=text[len(fence):]
        if text.lstrip().startswith("json"):
            text=text.lstrip()[4:]
        if text.rstrip().endswith(fence):
            text=text.rstrip()[:-len(fence)]
    a,b=text.find("["),text.rfind("]")
    if a < 0 or b <= a:
        return []
    try:
        val=json.loads(text[a:b+1])
    except Exception:
        return []
    out=[]
    for x in val if isinstance(val,list) else []:
        if not isinstance(x,dict):
            continue
        if all(isinstance(x.get(k),str) and x[k].strip() for k in ("prompt","chosen","rejected","discriminator")):
            out.append({k:x[k].strip() for k in ("prompt","chosen","rejected","discriminator")} | {"difficulty":str(x.get("difficulty","moderate")).strip().lower()})
    return out

def normalize(s: str) -> str:
    return " ".join(re.findall(r"[a-z0-9']+",s.lower()))

def emit(tag: str, raw: bytes):
    b64=base64.b64encode(raw).decode("ascii")
    chunk=8000
    total=math.ceil(len(b64)/chunk)
    print(f"{tag}_META|bytes={len(raw)}|sha256={hashlib.sha256(raw).hexdigest()}|chunks={total}",flush=True)
    for i in range(total):
        print(f"{tag}_CHUNK|{i+1}|{total}|{b64[i*chunk:(i+1)*chunk]}",flush=True)
    print(f"{tag}_COMPLETE",flush=True)

def run(seed_url: str):
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

    seeds=anchor_prompts(fetch_jsonl(seed_url))
    tokenizer=AutoTokenizer.from_pretrained(GENERATOR_REPO,revision=GENERATOR_REV)
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token=tokenizer.eos_token
    tokenizer.padding_side="left"
    quant=BitsAndBytesConfig(load_in_4bit=True,bnb_4bit_quant_type="nf4",bnb_4bit_use_double_quant=True,bnb_4bit_compute_dtype=torch.bfloat16)
    model=AutoModelForCausalLM.from_pretrained(GENERATOR_REPO,revision=GENERATOR_REV,quantization_config=quant,device_map={"":0},dtype=torch.bfloat16)
    model.eval()

    rng=random.Random(SEED)
    candidates=[]
    seen=set()
    stats={}
    global_batch=0

    for dim,d in DIMENSIONS.items():
        target=math.ceil(d["quota"]*1.5)
        attempts=0
        accepted=0
        local_domains=DOMAINS[:]
        rng.shuffle(local_domains)
        while accepted < target and attempts < target*4:
            batch_meta=[]
            batch_text=[]
            batch_n=min(4,target*4-attempts)
            for j in range(batch_n):
                idx=attempts+j
                domain=local_domains[idx % len(local_domains)]
                anchor=seeds[dim][idx % len(seeds[dim])]
                global_batch += 1
                user=make_request(dim,domain,anchor,global_batch)
                rendered=tokenizer.apply_chat_template(
                    [{"role":"system","content":SYSTEM},{"role":"user","content":user}],
                    tokenize=False,add_generation_prompt=True,enable_thinking=False
                )
                batch_meta.append((domain,anchor))
                batch_text.append(rendered)
            inputs=tokenizer(batch_text,return_tensors="pt",padding=True,truncation=True,max_length=2300).to(model.device)
            with torch.inference_mode():
                gen=model.generate(
                    **inputs,max_new_tokens=700,do_sample=True,temperature=0.75,top_p=0.92,
                    repetition_penalty=1.04,pad_token_id=tokenizer.pad_token_id
                )
            input_width=inputs["input_ids"].shape[1]
            attempts += batch_n
            for bi,(domain,anchor) in enumerate(batch_meta):
                text=tokenizer.decode(gen[bi,input_width:],skip_special_tokens=True)
                for x in parse_array(text):
                    p,c,r=x["prompt"],x["chosen"],x["rejected"]
                    ratio=(len(c)+1)/(len(r)+1)
                    if not 0.60 <= ratio <= 1.70:
                        continue
                    key=hashlib.sha256((normalize(p)+"\\0"+normalize(c)+"\\0"+normalize(r)).encode()).hexdigest()
                    if key in seen:
                        continue
                    seen.add(key)
                    candidates.append({
                        "schema":"VERA_QWEN35_BEHAVIOR_V2_CANDIDATE",
                        "candidate_id":f"v2-{dim}-{key[:18]}",
                        "dimension":dim,
                        "dimension_name":d["name"],
                        "domain":domain,
                        "difficulty":x["difficulty"] if x["difficulty"] in {"easy","moderate","hard"} else "moderate",
                        "seed_class":"CHAT_DERIVED_BEHAVIOR_ABSTRACTION",
                        "generator_repo":GENERATOR_REPO,
                        "generator_revision":GENERATOR_REV,
                        "prompt":p,"chosen":c,"rejected":r,"discriminator":x["discriminator"],
                        "pair_sha256":key
                    })
                    accepted += 1
                    if accepted >= target:
                        break
                if accepted >= target:
                    break
            print(f"GEN_PROGRESS|{dim}|accepted={accepted}|target={target}|attempts={attempts}",flush=True)
        stats[dim]={"quota":d["quota"],"candidate_target":target,"generated":accepted,"attempts":attempts}
        if accepted < target:
            raise RuntimeError(f"{dim}: generated {accepted}/{target}")

    payload=("\n".join(json.dumps(x,ensure_ascii=False,separators=(",",":")) for x in candidates)+"\n").encode()
    manifest={
        "schema":"VERA_QWEN35_BEHAVIOR_V2_CANDIDATE_MANIFEST",
        "rows":len(candidates),
        "sha256":hashlib.sha256(payload).hexdigest(),
        "generator_repo":GENERATOR_REPO,
        "generator_revision":GENERATOR_REV,
        "seed":SEED,
        "stats":stats
    }
    print("CANDIDATE_MANIFEST="+json.dumps(manifest,sort_keys=True),flush=True)
    emit("CANDIDATE_JSONL",payload)

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--seed-url",required=True)
    args=ap.parse_args()
    run(args.seed_url)
