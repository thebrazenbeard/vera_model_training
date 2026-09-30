"""Paired local Qwen generation runner, development only; no installation/deployment."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from .cases import read_cases
from .generation import generate_record
from .observations import canonical_sha, verify_pair
from .devloop import write_new, encode_jsonl

class LocalGenerationError(ValueError):
    pass

def generate_pair(base_model,adapter_model,tokenizer,cases,*,base_sha,candidate_sha,max_new_tokens=32):
    if base_sha==candidate_sha:
        raise LocalGenerationError("base and candidate must have distinct artifact identity")
    if not cases:
        raise LocalGenerationError("cases missing")
    base=[generate_record(base_model,tokenizer,c,condition="base",
                          model_sha=base_sha,max_new_tokens=max_new_tokens) for c in cases]
    candidate=[generate_record(adapter_model,tokenizer,c,condition="candidate",
                               model_sha=candidate_sha,max_new_tokens=max_new_tokens) for c in cases]
    return base,candidate

def save_session(directory,cases,base,candidate):
    dst=Path(directory)
    if dst.exists():
        raise LocalGenerationError("output directory exists; refuse overwrite")
    if not len(cases)==len(base)==len(candidate):
        raise LocalGenerationError("generation count mismatch")
    if not cases:
        raise LocalGenerationError("empty session")
    try:
        for c,b,a in zip(cases,base,candidate):
            verify_pair(c,b,a,base_sha=base[0]["model_sha256"],
                        candidate_sha=candidate[0]["model_sha256"],
                        decoding_sha=base[0]["decoding_sha256"])
    except Exception as exc:
        raise LocalGenerationError("generated record verification failed: "+str(exc)) from exc
    dst.mkdir(parents=True,exist_ok=False)
    base_bytes=encode_jsonl(base)
    cand_bytes=encode_jsonl(candidate)
    write_new(dst/"base.jsonl",base_bytes)
    write_new(dst/"candidate.jsonl",cand_bytes)
    manifest={"schema":"QWEN35_LOCAL_PAIRED_GENERATION_RECEIPT_V1",
              "status":"LOCAL_GENERATIONS_RECORDED_NOT_INDEPENDENTLY_ATTESTED",
              "case_count":len(cases),
              "case_set_sha256":canonical_sha({"cases":[canonical_sha(c) for c in cases]}),
              "base_model_sha256":base[0]["model_sha256"],
              "candidate_model_sha256":candidate[0]["model_sha256"],
              "decoding_sha256":base[0]["decoding_sha256"],
              "base_observations_sha256":hashlib.sha256(base_bytes).hexdigest(),
              "candidate_observations_sha256":hashlib.sha256(cand_bytes).hexdigest(),
              "method":"actual_local_model.generate() calls; no external observer signature",
              "qualification":"NONE"}
    write_new(dst/"generation_manifest.json",
              (json.dumps(manifest,sort_keys=True,indent=2)+"\n").encode("utf-8"))
    return manifest

def _hash_file(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda:f.read(8*1024*1024),b""):
            h.update(chunk)
    return h.hexdigest()

def main(argv=None):
    parser=argparse.ArgumentParser()
    parser.add_argument("--cases",type=Path,required=True)
    parser.add_argument("--base-dir",type=Path,required=True)
    parser.add_argument("--adapter-dir",type=Path,required=True)
    parser.add_argument("--out",type=Path,required=True)
    parser.add_argument("--limit",type=int,default=None)
    parser.add_argument("--max-new-tokens",type=int,default=32)
    parser.add_argument("--run",action="store_true",help="load and generate; without flag preflight only")
    a=parser.parse_args(argv)
    try:
        rows=read_cases(a.cases)
        if a.limit is not None:
            if not 1<=a.limit<=len(rows):
                raise LocalGenerationError("invalid limit")
            rows=rows[:a.limit]
        if a.out.exists():
            raise LocalGenerationError("output already exists")
        root=Path(__file__).resolve().parents[1]
        spec=json.loads((root/"qualification/FINAL_QUALIFICATION_V4_SPEC.json").read_text(encoding="utf-8"))
        for shard in spec["base"]["local_shards"]:
            if _hash_file(a.base_dir/shard["file"])!=shard["sha256"]:
                raise LocalGenerationError("base shard mismatch")
        if _hash_file(a.adapter_dir/"adapter_model.safetensors")!=spec["adapter"]["adapter_model_sha256"]:
            raise LocalGenerationError("adapter file mismatch")
        if _hash_file(a.adapter_dir/"adapter_config.json")!=spec["adapter"]["adapter_config_sha256"]:
            raise LocalGenerationError("adapter config mismatch")
        base_sha=canonical_sha({"revision":spec["base"]["revision"],"shards":spec["base"]["local_shards"]})
        candidate_sha=spec["adapter"]["adapter_model_sha256"]
        if not a.run:
            print(json.dumps({"status":"PREFLIGHT_ONLY_NO_GENERATION","case_count":len(rows),
                              "base_model_sha256":base_sha,"candidate_model_sha256":candidate_sha},sort_keys=True))
            return 0
        import torch
        from transformers import AutoTokenizer, Qwen3_5ForCausalLM
        from peft import PeftModel
        torch.set_num_threads(8)
        tok=AutoTokenizer.from_pretrained(a.base_dir,local_files_only=True)
        if tok.pad_token_id is None:tok.pad_token=tok.eos_token
        model=Qwen3_5ForCausalLM.from_pretrained(a.base_dir,local_files_only=True,
                                                   dtype=torch.bfloat16,device_map={"":"cpu"},
                                                   low_cpu_mem_usage=True)
        model.eval()
        base=[]
        for i,c in enumerate(rows,1):
            base.append(generate_record(model,tok,c,condition="base",model_sha=base_sha,
                                        max_new_tokens=a.max_new_tokens))
            print(f"BASE_GENERATED|{i}/{len(rows)}|{c['case_id']}",flush=True)
        adapted=PeftModel.from_pretrained(model,a.adapter_dir,is_trainable=False)
        adapted.eval()
        candidate=[]
        for i,c in enumerate(rows,1):
            candidate.append(generate_record(adapted,tok,c,condition="candidate",model_sha=candidate_sha,
                                             max_new_tokens=a.max_new_tokens))
            print(f"CANDIDATE_GENERATED|{i}/{len(rows)}|{c['case_id']}",flush=True)
        manifest=save_session(a.out,rows,base,candidate)
        manifest["subset_status"]="DEVELOPMENT_SMOKE_ONLY" if a.limit else "GENERATED_BUT_NOT_QUALIFIED"
        print(json.dumps(manifest,sort_keys=True))
        return 0
    except (LocalGenerationError,ValueError,KeyError,OSError) as exc:
        print(json.dumps({"status":"ERROR","reason":str(exc)},sort_keys=True))
        return 2

if __name__=="__main__":
    raise SystemExit(main())
