from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

import torch
from peft import PeftModel
from transformers import AutoTokenizer, Qwen3_5ForCausalLM

try:
    from .final_qualification_binding_v4 import verify_blind_adapter_binding
except ImportError:
    from final_qualification_binding_v4 import verify_blind_adapter_binding

ROOT=Path(__file__).resolve().parents[3]
Q=ROOT/"successor"/"qwen35"
QUAL=Q/"qualification"

def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]

def render(tokenizer,prompt: str) -> str:
    messages=[{"role":"user","content":prompt}]
    try:
        return tokenizer.apply_chat_template(messages,tokenize=False,add_generation_prompt=True,enable_thinking=False)
    except TypeError:
        return tokenizer.apply_chat_template(messages,tokenize=False,add_generation_prompt=True)

def generate_one(model,tokenizer,prompt: str,max_new_tokens: int) -> str:
    text=render(tokenizer,prompt)
    enc=tokenizer(text,return_tensors="pt",add_special_tokens=False)
    input_ids=enc["input_ids"].to("cpu")
    attention_mask=enc.get("attention_mask")
    if attention_mask is not None:
        attention_mask=attention_mask.to("cpu")
    with torch.inference_mode():
        out=model.generate(
            input_ids=input_ids,
            attention_mask=attention_mask,
            do_sample=False,
            max_new_tokens=max_new_tokens,
            pad_token_id=tokenizer.pad_token_id,
            eos_token_id=tokenizer.eos_token_id,
        )
    return tokenizer.decode(out[0,input_ids.shape[1]:],skip_special_tokens=True).strip()
def main(args) -> int:
    binding=verify_blind_adapter_binding(QUAL/"FINAL_QUALIFICATION_V4_SPEC.json",args.automated_result,args.adapter_dir)
    selection_path=QUAL/"FINAL_BLIND_REVIEW_V4_SELECTION.json"
    selection=json.loads(selection_path.read_text(encoding="utf-8"))
    holdout_path=QUAL/"final_holdout_v4.jsonl"
    if sha256(holdout_path)!=selection["behavioral_holdout_sha256"]:
        raise RuntimeError("holdout hash mismatch")
    holdout={row["record_id"]:row for row in load_jsonl(holdout_path)}
    selected=[]
    for rid in selection["record_ids"]:
        if rid not in holdout:
            raise RuntimeError(f"selection missing record {rid}")
        selected.append(holdout[rid])
    curriculum=json.loads((Q/"HISTORY_BEHAVIOR_CURRICULUM_V2.json").read_text(encoding="utf-8"))
    tokenizer=AutoTokenizer.from_pretrained(args.base_dir,local_files_only=True)
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token=tokenizer.eos_token
    torch.set_num_threads(args.threads)
    print("LOAD_BASE",flush=True)
    model=Qwen3_5ForCausalLM.from_pretrained(
        args.base_dir,local_files_only=True,dtype=torch.bfloat16,
        device_map={"":"cpu"},low_cpu_mem_usage=True,
    )
    model.eval()
    generations=[]
    max_new=selection["generation"]["max_new_tokens"]
    for i,row in enumerate(selected,1):
        response=generate_one(model,tokenizer,row["prompt"],max_new)
        generations.append({"record_id":row["record_id"],"dimension":row["dimension"],"condition":"BASE","prompt":row["prompt"],"response":response})
        print(f"BASE_GENERATION|{i}/{len(selected)}|{row['record_id']}",flush=True)
    print("LOAD_ADAPTER",flush=True)
    adapted=PeftModel.from_pretrained(model,args.adapter_dir,is_trainable=False)
    adapted.eval()
    for i,row in enumerate(selected,1):
        response=generate_one(adapted,tokenizer,row["prompt"],max_new)
        generations.append({"record_id":row["record_id"],"dimension":row["dimension"],"condition":"ADAPTER","prompt":row["prompt"],"response":response})
        print(f"ADAPTER_GENERATION|{i}/{len(selected)}|{row['record_id']}",flush=True)
    args.private_generations.parent.mkdir(parents=True,exist_ok=True)
    args.private_generations.write_text("".join(json.dumps(x,sort_keys=True)+"\n" for x in generations),encoding="utf-8",newline="\n")
    selection_sha=sha256(selection_path)
    ordered=sorted(
        generations,
        key=lambda x: hashlib.sha256((selection_sha+"|"+x["record_id"]+"|"+x["condition"]).encode()).hexdigest()
    )
    rubrics_path=QUAL/"FINAL_BLIND_REVIEW_V4_RUBRICS.json"
    rubrics_doc=json.loads(rubrics_path.read_text(encoding="utf-8"))
    if rubrics_doc["selection_sha256"]!=sha256(selection_path) or set(rubrics_doc["cases"])!=set(selection["record_ids"]):
        raise RuntimeError("rubric selection binding mismatch")
    rubrics=rubrics_doc["cases"]
    blind=[]
    mapping=[]
    for i,item in enumerate(ordered,1):
        blind_id=f"blind-{i:03d}"
        dim=curriculum["dimensions"][item["dimension"]]
        blind.append({
            "blind_id":blind_id,
            "record_id":item["record_id"],
            "dimension":item["dimension"],
            "prompt":item["prompt"],
            "response":item["response"],
            "dimension_target":dim["target"],
            "known_failure_modes":dim["failures"],
            "required_propositions":rubrics[item["record_id"]]["required_propositions"],
            "forbidden_propositions":rubrics[item["record_id"]]["forbidden_propositions"],
        })
        mapping.append({"blind_id":blind_id,"record_id":item["record_id"],"condition":item["condition"]})
    args.blind_packet.write_text("".join(json.dumps(x,sort_keys=True)+"\n" for x in blind),encoding="utf-8",newline="\n")
    args.mapping.write_text(json.dumps({"schema":"QWEN35_FINAL_BLIND_MAPPING_V4","items":mapping},indent=2,sort_keys=True)+"\n",encoding="utf-8",newline="\n")
    manifest={
        "schema":"QWEN35_FINAL_BLIND_PACKET_MANIFEST_V4",
        "selection_sha256":selection_sha,
        "rubrics_sha256":sha256(rubrics_path),
        "behavioral_holdout_sha256":selection["behavioral_holdout_sha256"],
        "private_generations_sha256":sha256(args.private_generations),
        "blind_packet_sha256":sha256(args.blind_packet),
        "mapping_sha256":sha256(args.mapping),
        "item_count":len(blind),
        "generation":selection["generation"],
        "subject":"Vera-Qwen3.5-4B-Behavior-V1-v4-candidate-a",
        "adapter_sha256":binding["adapter_sha256"],
        "adapter_model_sha256":binding["adapter_model_sha256"],
        "automated_result_sha256":binding["automated_result_sha256"],
        "spec_sha256":binding["spec_sha256"],
    }
    args.manifest.write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n",encoding="utf-8",newline="\n")
    print("BLIND_PACKET="+json.dumps(manifest,sort_keys=True),flush=True)
    return 0

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--base-dir",type=Path,required=True)
    ap.add_argument("--adapter-dir",type=Path,required=True)
    ap.add_argument("--automated-result",type=Path,required=True)
    ap.add_argument("--private-generations",type=Path,required=True)
    ap.add_argument("--blind-packet",type=Path,required=True)
    ap.add_argument("--mapping",type=Path,required=True)
    ap.add_argument("--manifest",type=Path,required=True)
    ap.add_argument("--threads",type=int,default=12)
    raise SystemExit(main(ap.parse_args()))