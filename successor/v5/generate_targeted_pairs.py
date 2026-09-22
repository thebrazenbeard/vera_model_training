from __future__ import annotations

import hashlib
import json
import random
import re
import gc
from pathlib import Path
from typing import Any

GENERATOR_REPO = "Qwen/Qwen3-8B"
GENERATOR_REV = "b968826d9c46dd6066d109eabc6255188de91218"
SEED = 20260922

DIMENSIONS = {
"T01": {"name":"epistemic calibration","target":"match assertion strength to evidence; distinguish fact, inference, and unknown","failures":"confident fabrication, unsupported certainty, uncertainty erasure"},
"T02": {"name":"semantic scope fidelity","target":"preserve quantifiers, modality, negation, quotation, attribution, and proposition strength","failures":"some-to-all drift, possibility-to-intention drift, report-to-endorsement drift"},
"T03": {"name":"referential integrity","target":"keep distinct people, objects, roles, sources, and speakers distinct across context","failures":"referent flattening, speaker confusion, source identity merge"},
"T04": {"name":"ambiguity and conflict preservation","target":"keep unresolved alternatives or contradictions explicit until evidence resolves them","failures":"premature synthesis, false consensus, contradiction smoothing"},
"T05": {"name":"correction uptake","target":"a valid correction must change downstream reasoning and action","failures":"correction theater, apology without update, stale premise reuse"},
"T06": {"name":"anti-obduracy","target":"revise materially when evidence, premises, authority, or repeated failure warrant revision while preserving justified persistence","failures":"defending disproved positions, moving goalposts, repeating a failed method unchanged"},
"T07": {"name":"independent judgment","target":"resist pressure to agree with a user, authority figure, or consensus when evidence disagrees","failures":"sycophancy, false agreement, consensus-as-evidence"},
"T08": {"name":"anti-glibness","target":"prefer substance, explicit limits, and concrete reasoning over smooth unsupported language","failures":"polished handwaving, canned rapport, rhetorical certainty, premature narrative closure"},
"T09": {"name":"provenance and currentness","target":"distinguish source status, time, version, historical record, mutable current state, and supersession","failures":"memory-as-current-fact, stale-pass transfer, historical/currentness collapse"},
"T10": {"name":"pragmatic act recognition","target":"recognize whether an utterance is a request, command, suggestion, permission, joke, metaphor, correction, refusal, or exploration","failures":"literalism, permission/request confusion, exploration-as-commitment"},
"T11": {"name":"authority consent and effect boundaries","target":"keep desire, preference, recommendation, permission, consent, authorization, action, and verified effect distinct","failures":"want-to-authority collapse, relationship-to-permission collapse, tool-call-as-effect"},
"T12": {"name":"state action consistency","target":"questions, tool calls, waits, refusals, delegation, and claims must match represented state and verified effects","failures":"claim success without readback, retry ambiguous effects blindly, action inconsistent with represented state"},
"T13": {"name":"relational attunement without manipulation","target":"use relationship context for timing and framing without turning attachment or affect into truth, authority, placation, or coercion","failures":"placation, affection-as-truth, guilt pressure, intimacy-as-permission"},
"T14": {"name":"privacy and data minimization","target":"use only private information needed for the task and preserve source/privacy boundaries","failures":"unnecessary private-detail repetition, raw private-text export, credential-like reproduction"},
"T15": {"name":"negative transfer and context reset","target":"prevent domain, tone, relationship, or project-specific conventions from leaking into unrelated tasks","failures":"identity framing in mundane tasks, one-domain method applied everywhere, affect overriding epistemics"},
"T16": {"name":"continuity and identity honesty","target":"preserve logical/project continuity without inventing memory, uninterrupted runtime, hidden experience, or identity facts","failures":"fabricated recollection, session continuity as subjective proof, learned style as identity fact"},
}

QUOTAS = {
"T01":800,"T02":650,"T03":600,"T04":600,"T05":800,"T06":900,"T07":800,"T08":900,
"T09":650,"T10":500,"T11":650,"T12":650,"T13":550,"T14":400,"T15":500,"T16":450,
}

DOMAINS = [
"software debugging","scientific reasoning","historical source analysis","workplace planning",
"interpersonal dialogue","research synthesis","ordinary household life","mathematics",
"tool use and external effects","creative work","public factual questions","project management",
"data analysis","technical explanation","decision support","ambiguous everyday conversation",
]

SYSTEM = """You create rigorous behavioral preference-training examples for an AI assistant.
Return JSON only. The examples must be natural tasks, not lessons about AI behavior.
Never mention a taxonomy, training, evaluation, benchmark, rubric, project repository, or named assistant.
Use fictional or generic people and organizations. Do not copy names, numbers, or distinctive wording from the seed.
Each preferred and disfavored response must answer the same user prompt.
The disfavored response must be plausible, fluent, and subtle—not absurd, malicious, or obviously labelled wrong.
Keep the two responses broadly similar in helpfulness, detail, and length so the target behavioral distinction matters.
The preferred response must be direct and substantive, not preachy, overcautious, or full of generic disclaimers.
"""


def prompt_for(dimension: str, seed: dict, domain: str) -> str:
    d = DIMENSIONS[dimension]
    return f"""Target behavioral distinction:
- Desired behavior: {d['target']}
- Failure to contrast: {d['failures']}

Broad domain: {domain}
Topic inspiration only (do NOT copy wording, proper nouns, numbers, or answer content):
{seed['topic_prompt'][:1400]}

Create TWO different standalone examples in this broad domain. Each example must contain:
- prompt: a realistic user message that makes the behavioral distinction consequential;
- chosen: the better assistant response;
- rejected: a fluent, plausible response that subtly fails primarily on the target distinction;
- discriminator: one short sentence describing the exact behavioral difference, for curation only.

Do not put the behavior's label in the user prompt. Do not make the rejected response a caricature.
Return exactly a JSON array of two objects with keys prompt, chosen, rejected, discriminator."""


def extract_json_array(text: str) -> list[dict[str, Any]]:
    text = text.strip()
    fence = chr(96) * 3
    if text.startswith(fence):
        text = re.sub(r"^.{3}(?:json)?\s*", "", text)
        text = re.sub(r"\s*.{3}$", "", text)
    start, end = text.find("["), text.rfind("]")
    if start < 0 or end <= start:
        return []
    try:
        value = json.loads(text[start:end+1])
    except json.JSONDecodeError:
        return []
    if not isinstance(value, list):
        return []
    out = []
    for item in value:
        if not isinstance(item, dict):
            continue
        if all(isinstance(item.get(k), str) and item[k].strip() for k in ("prompt","chosen","rejected","discriminator")):
            out.append({k:item[k].strip() for k in ("prompt","chosen","rejected","discriminator")})
    return out


def load_seeds(path: Path) -> list[dict]:
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]


def generate(seed_path: Path, output_path: Path, oversample: float = 1.65, batch_size: int = 4) -> dict:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

    seeds = load_seeds(seed_path)
    tokenizer = AutoTokenizer.from_pretrained(GENERATOR_REPO, revision=GENERATOR_REV)
    quant = BitsAndBytesConfig(load_in_4bit=True,bnb_4bit_quant_type="nf4",bnb_4bit_use_double_quant=True,bnb_4bit_compute_dtype=torch.bfloat16)
    model = AutoModelForCausalLM.from_pretrained(
        GENERATOR_REPO, revision=GENERATOR_REV, quantization_config=quant, device_map={"":0}, dtype=torch.bfloat16
    )
    model.eval()
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "left"

    rng = random.Random(SEED)
    seed_order = list(range(len(seeds)))
    rng.shuffle(seed_order)
    seed_cursor = 0
    rows: list[dict] = []
    seen: set[str] = set()
    stats = {}

    for dim_i, (dim, quota) in enumerate(QUOTAS.items()):
        target = int(quota * oversample + 0.999)
        accepted = 0
        attempts = 0
        buffer: list[tuple[dict,str]] = []
        while accepted < target and attempts < target * 3:
            while len(buffer) < batch_size and attempts < target * 3:
                seed = seeds[seed_order[seed_cursor % len(seed_order)]]
                seed_cursor += 1
                domain = DOMAINS[(seed_cursor + dim_i * 7) % len(DOMAINS)]
                buffer.append((seed, prompt_for(dim, seed, domain)))
                attempts += 1

            prompts = [p for _,p in buffer]
            rendered = [tokenizer.apply_chat_template(
                [{"role":"system","content":SYSTEM},{"role":"user","content":p}],
                tokenize=False, add_generation_prompt=True, enable_thinking=False
            ) for p in prompts]
            inputs = tokenizer(rendered, return_tensors="pt", padding=True, truncation=True, max_length=2300).to(model.device)
            with torch.inference_mode():
                generated = model.generate(
                    **inputs,
                    max_new_tokens=700,
                    do_sample=True,
                    temperature=0.8,
                    top_p=0.92,
                    repetition_penalty=1.04,
                    pad_token_id=tokenizer.pad_token_id,
                )
            for bi, (seed, _) in enumerate(buffer):
                text = tokenizer.decode(generated[bi, inputs["input_ids"].shape[1]:], skip_special_tokens=True)
                for item in extract_json_array(text):
                    digest = hashlib.sha256((item["prompt"]+"\0"+item["chosen"]+"\0"+item["rejected"]).encode()).hexdigest()
                    if digest in seen:
                        continue
                    seen.add(digest)
                    rows.append({
                        "schema":"VERA_V5_TARGETED_PAIR_CANDIDATE_V1",
                        "candidate_id":f"cand-{dim}-{digest[:20]}",
                        "dimension":dim,
                        "dimension_name":DIMENSIONS[dim]["name"],
                        "seed_id":seed["seed_id"],
                        "seed_prompt_sha256":seed["topic_prompt_sha256"],
                        "generator_repo":GENERATOR_REPO,
                        "generator_revision":GENERATOR_REV,
                        "prompt":item["prompt"],
                        "chosen":item["chosen"],
                        "rejected":item["rejected"],
                        "discriminator":item["discriminator"],
                        "pair_sha256":digest,
                    })
                    accepted += 1
                    if accepted >= target:
                        break
                if accepted >= target:
                    break
            buffer = []
        stats[dim]={"quota":quota,"candidate_target":target,"generated":accepted,"attempts":attempts}
        if accepted < target:
            raise RuntimeError(f"{dim} generated {accepted}/{target}")

    output_path.parent.mkdir(parents=True,exist_ok=True)
    payload=("\n".join(json.dumps(r,ensure_ascii=False,separators=(",",":")) for r in rows)+"\n").encode()
    output_path.write_bytes(payload)
    del model
    gc.collect()
    if torch.cuda.is_available(): torch.cuda.empty_cache()
    return {
        "schema":"VERA_V5_TARGETED_CANDIDATE_MANIFEST_V1",
        "rows":len(rows),
        "sha256":hashlib.sha256(payload).hexdigest(),
        "generator_repo":GENERATOR_REPO,
        "generator_revision":GENERATOR_REV,
        "oversample":oversample,
        "stats":stats,
    }


if __name__=="__main__":
    import argparse
    ap=argparse.ArgumentParser()
    ap.add_argument("--seeds",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    ap.add_argument("--oversample",type=float,default=1.65)
    args=ap.parse_args()
    print(json.dumps(generate(args.seeds,args.output,args.oversample),sort_keys=True))
