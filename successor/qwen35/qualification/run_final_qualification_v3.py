from __future__ import annotations
import argparse
import hashlib
import json
import platform
from collections import Counter, defaultdict
from pathlib import Path

import torch
from peft import PeftModel
from transformers import AutoTokenizer, Qwen3_5ForCausalLM

ROOT = Path(__file__).resolve().parents[3]
Q = ROOT / "successor" / "qwen35" / "qualification"

def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]

def prefix_ids(tokenizer, prompt: str) -> list[int]:
    messages=[{"role":"user","content":prompt}]
    try:
        text=tokenizer.apply_chat_template(messages,tokenize=False,add_generation_prompt=True,enable_thinking=False)
    except TypeError:
        text=tokenizer.apply_chat_template(messages,tokenize=False,add_generation_prompt=True)
    return tokenizer(text,add_special_tokens=False)["input_ids"]

def sequence(tokenizer, prompt: str, answer: str, max_length: int) -> tuple[list[int], int]:
    pre=prefix_ids(tokenizer,prompt)
    ans=tokenizer(answer,add_special_tokens=False)["input_ids"]
    if tokenizer.eos_token_id is not None and (not ans or ans[-1] != tokenizer.eos_token_id):
        ans.append(tokenizer.eos_token_id)
    ids=pre+ans
    if len(ids)>max_length:
        raise RuntimeError(f"sequence exceeds max_length={max_length}")
    return ids,len(pre)
def score_rows(model, tokenizer, rows: list[dict], max_length: int, progress_label: str, batch_rows: int) -> dict:
    by_dimension=defaultdict(list)
    scored=[]
    pad=tokenizer.pad_token_id if tokenizer.pad_token_id is not None else tokenizer.eos_token_id
    for chunk_start in range(0,len(rows),batch_rows):
        chunk=rows[chunk_start:chunk_start+batch_rows]
        seqs=[]
        starts=[]
        row_meta=[]
        for row in chunk:
            chosen,start_c=sequence(tokenizer,row["prompt"],row["chosen"],max_length)
            rejected,start_r=sequence(tokenizer,row["prompt"],row["rejected"],max_length)
            row_meta.append(row)
            seqs.extend((chosen,rejected))
            starts.extend((start_c,start_r))
        max_len=max(map(len,seqs))
        input_ids=[]
        masks=[]
        for ids in seqs:
            n=max_len-len(ids)
            input_ids.append(ids+[pad]*n)
            masks.append([1]*len(ids)+[0]*n)
        x=torch.tensor(input_ids,dtype=torch.long,device="cpu")
        mask=torch.tensor(masks,dtype=torch.long,device="cpu")
        with torch.inference_mode():
            logits=model(input_ids=x,attention_mask=mask,use_cache=False).logits
        sequence_scores=[]
        for batch_idx,(ids,start) in enumerate(zip(seqs,starts)):
            positions=torch.arange(start,len(ids),device=logits.device)
            step_logits=logits[batch_idx,positions-1,:]
            targets=torch.tensor([ids[t] for t in range(start,len(ids))],device=logits.device,dtype=torch.long)
            target_logits=step_logits.gather(1,targets[:,None]).squeeze(1).float()
            log_norm=torch.logsumexp(step_logits.float(),dim=-1)
            sequence_scores.append(float((target_logits-log_norm).mean().item()))
        for local_index,row in enumerate(row_meta):
            chosen_score=sequence_scores[2*local_index]
            rejected_score=sequence_scores[2*local_index+1]
            margin=chosen_score-rejected_score
            item={
                "record_id":row["record_id"],
                "dimension":row.get("dimension") or row.get("category"),
                "chosen_logp":chosen_score,
                "rejected_logp":rejected_score,
                "margin":margin,
                "correct":margin>0,
            }
            scored.append(item)
            by_dimension[item["dimension"]].append(item)
            index=chunk_start+local_index+1
            print(f"{progress_label}|{index}/{len(rows)}|{item['record_id']}|margin={margin:.6f}|correct={item['correct']}",flush=True)
        del logits,x,mask
    summary={
        "n":len(scored),
        "accuracy":sum(x["correct"] for x in scored)/len(scored),
        "mean_margin":sum(x["margin"] for x in scored)/len(scored),
        "by_dimension":{
            d:{
                "n":len(xs),
                "accuracy":sum(x["correct"] for x in xs)/len(xs),
                "mean_margin":sum(x["margin"] for x in xs)/len(xs),
            } for d,xs in sorted(by_dimension.items())
        },
        "rows":scored,
    }
    return summary
def suite_pass(name: str, base: dict, adapter: dict, contract: dict) -> tuple[bool,list[str]]:
    reasons=[]
    accuracy_delta=adapter["accuracy"]-base["accuracy"]
    margin_delta=adapter["mean_margin"]-base["mean_margin"]
    if adapter["accuracy"] < contract["min_adapter_accuracy"]:
        reasons.append("adapter_accuracy_below_minimum")
    if accuracy_delta < contract["min_accuracy_delta"]:
        reasons.append("accuracy_delta_below_minimum")
    if margin_delta < contract["min_mean_margin_delta"]:
        reasons.append("mean_margin_delta_below_minimum")
    if name=="behavioral":
        max_reg=contract["max_per_dimension_accuracy_regression"]
        min_dim=contract["min_per_dimension_adapter_accuracy"]
        for dimension,a in adapter["by_dimension"].items():
            b=base["by_dimension"][dimension]
            if b["accuracy"]-a["accuracy"] > max_reg + 1e-12:
                reasons.append(f"dimension_regression:{dimension}")
            if a["accuracy"] < min_dim:
                reasons.append(f"dimension_accuracy_below_minimum:{dimension}")
    return not reasons,reasons

def verify_suite(path: Path, expected: dict) -> list[dict]:
    raw=path.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=expected["sha256"]:
        raise RuntimeError(f"suite hash mismatch: {path}")
    rows=load_jsonl(path)
    if len(rows)!=expected["rows"]:
        raise RuntimeError(f"suite row mismatch: {path}")
    return rows

def verify_base_shards(base_dir: Path, spec: dict) -> None:
    for shard in spec["base"]["local_shards"]:
        path=base_dir/shard["file"]
        if path.stat().st_size!=shard["bytes"] or sha256(path)!=shard["sha256"]:
            raise RuntimeError(f"base shard mismatch: {path}")

def main(args) -> int:
    spec_path=Q/"FINAL_QUALIFICATION_V3_SPEC.json"
    spec=json.loads(spec_path.read_text(encoding="utf-8"))
    verify_base_shards(args.base_dir,spec)
    if sha256(args.adapter_archive)!=spec["adapter"]["archive_sha256"]:
        raise RuntimeError("adapter archive mismatch")
    suites={}
    for name in ("behavioral","retention","adversarial_proxy"):
        meta=spec["suites"][name]
        suites[name]=verify_suite(ROOT/meta["path"],meta)
    tokenizer=AutoTokenizer.from_pretrained(args.base_dir,local_files_only=True)
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token=tokenizer.eos_token
    torch.set_num_threads(args.threads)
    print(f"LOAD_BASE|path={args.base_dir}|threads={args.threads}",flush=True)
    model=Qwen3_5ForCausalLM.from_pretrained(args.base_dir,local_files_only=True,dtype=torch.bfloat16,device_map={"":"cpu"},low_cpu_mem_usage=True)
    model.eval()
    base_results={}
    for name,rows in suites.items():
        use_rows=rows[:args.limit] if args.limit else rows
        base_results[name]=score_rows(model,tokenizer,use_rows,spec["evaluation"]["max_length"],f"BASE_{name.upper()}",args.batch_rows)
    print(f"LOAD_ADAPTER|path={args.adapter_dir}",flush=True)
    adapted=PeftModel.from_pretrained(model,args.adapter_dir,is_trainable=False)
    adapted.eval()
    adapter_results={}
    for name,rows in suites.items():
        use_rows=rows[:args.limit] if args.limit else rows
        adapter_results[name]=score_rows(adapted,tokenizer,use_rows,spec["evaluation"]["max_length"],f"ADAPTER_{name.upper()}",args.batch_rows)
    if args.limit:
        result={"schema":"QWEN35_FINAL_QUALIFICATION_SMOKE_V3","limit":args.limit,"base":base_results,"adapter":adapter_results}
    else:
        passes={}
        all_reasons={}
        for name in ("behavioral","retention","adversarial_proxy"):
            ok,reasons=suite_pass(name,base_results[name],adapter_results[name],spec["pass_contract"][name])
            passes[name]=ok
            all_reasons[name]=reasons
        result={
            "schema":"QWEN35_FINAL_QUALIFICATION_AUTOMATED_RESULT_V3",
            "subject":spec["subject"],
            "output_identity":spec["output_identity"],
            "spec_sha256":sha256(spec_path),
            "adapter_sha256":spec["adapter"]["archive_sha256"],
            "adapter_model_sha256":sha256(args.adapter_dir/"adapter_model.safetensors"),
            "base_repo":spec["base"]["repo"],
            "base_revision":spec["base"]["revision"],
            "runtime":{
                "python":platform.python_version(),
                "torch":torch.__version__,
                "transformers":__import__("transformers").__version__,
                "peft":__import__("peft").__version__,
                "device":"cpu",
                "dtype":"bfloat16",
                "threads":args.threads,
            },
            "suites":{},
            "behavioral_pass":passes["behavioral"],
            "retention_pass":passes["retention"],
            "adversarial_proxy_pass":passes["adversarial_proxy"],
            "automated_pass":all(passes.values()),
        }
        for name in passes:
            result["suites"][name]={
                "base":base_results[name],
                "adapter":adapter_results[name],
                "delta":{
                    "accuracy":adapter_results[name]["accuracy"]-base_results[name]["accuracy"],
                    "mean_margin":adapter_results[name]["mean_margin"]-base_results[name]["mean_margin"],
                },
                "pass":passes[name],
                "failure_reasons":all_reasons[name],
            }
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8",newline="\n")
    print("RESULT="+json.dumps({k:v for k,v in result.items() if k not in ("suites","base","adapter")},sort_keys=True),flush=True)
    return 0

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--base-dir",type=Path,required=True)
    ap.add_argument("--adapter-dir",type=Path,required=True)
    ap.add_argument("--adapter-archive",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    ap.add_argument("--threads",type=int,default=8)
    ap.add_argument("--batch-rows",type=int,default=4)
    ap.add_argument("--limit",type=int)
    raise SystemExit(main(ap.parse_args()))