from __future__ import annotations

import argparse
import base64
import gc
import gzip
import hashlib
import json
import shutil
from pathlib import Path

from successor.v5 import build_public_corpus as public
from successor.v5 import generate_targeted_pairs as generator
from successor.v5 import curate_targeted_pairs as curator
from successor.v5 import train_v5 as trainer
from successor.v5 import qualify_v5 as qualifier

CHUNK_CHARS=15000


def sha256_file(path:Path)->str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""): h.update(chunk)
    return h.hexdigest()


def gzip_copy(src:Path,dst:Path)->dict:
    dst.parent.mkdir(parents=True,exist_ok=True)
    with src.open("rb") as fin,gzip.open(dst,"wb",compresslevel=9) as fout:
        shutil.copyfileobj(fin,fout)
    return {"bytes":dst.stat().st_size,"sha256":sha256_file(dst)}


def emit_file(path:Path,label:str)->dict:
    data=path.read_bytes()
    sha=hashlib.sha256(data).hexdigest()
    b64=base64.b64encode(data).decode("ascii")
    chunks=[b64[i:i+CHUNK_CHARS] for i in range(0,len(b64),CHUNK_CHARS)]
    meta={"label":label,"bytes":len(data),"sha256":sha,"base64_chars":len(b64),"chunks":len(chunks),"chunk_chars":CHUNK_CHARS}
    print("ARTIFACT_META|"+json.dumps(meta,sort_keys=True),flush=True)
    for i,chunk in enumerate(chunks):
        print(f"ARTIFACT_CHUNK|{label}|{i:05d}|{chunk}",flush=True)
    print(f"ARTIFACT_END|{label}|{sha}",flush=True)
    return meta


def emit_json(label:str,value:dict)->None:
    print("RECEIPT|"+label+"|"+json.dumps(value,sort_keys=True,separators=(",",":")),flush=True)


def run(work_dir:Path, *, smoke:bool=False)->dict:
    import torch

    work_dir.mkdir(parents=True,exist_ok=True)
    public_dir=work_dir/"public"
    public_manifest=public.build(public_dir)
    emit_json("public_corpus",public_manifest)

    if smoke:
        generator.QUOTAS={"T08":2}
        curator.QUOTAS={"T08":1}
        oversample=2.0
    else:
        oversample=2.25

    candidate_path=work_dir/"targeted_candidates.jsonl"
    generated_manifest=generator.generate(public_dir/"target_seeds.jsonl",candidate_path,oversample=oversample)
    emit_json("targeted_generation",generated_manifest)
    gc.collect()
    if torch.cuda.is_available():torch.cuda.empty_cache()

    targeted_path=work_dir/"targeted_curated.jsonl"
    curated_manifest=curator.curate(candidate_path,targeted_path)
    emit_json("targeted_curation",curated_manifest)
    gc.collect()
    if torch.cuda.is_available():torch.cuda.empty_cache()

    train_dir=work_dir/"training"
    training_receipt=trainer.train(
        public_dir/"general_sft.jsonl",
        public_dir/"general_preferences.jsonl",
        targeted_path,
        train_dir,
        smoke=smoke,
    )
    emit_json("training",training_receipt)
    gc.collect()
    if torch.cuda.is_available():torch.cuda.empty_cache()

    qual_dir=work_dir/"qualification"
    qualification_receipt=qualifier.qualify(train_dir/"adapter",qual_dir,smoke=smoke)
    emit_json("qualification",qualification_receipt)
    gc.collect()
    if torch.cuda.is_available():torch.cuda.empty_cache()

    artifacts_dir=work_dir/"artifacts"
    artifacts_dir.mkdir(parents=True,exist_ok=True)
    targeted_gz=artifacts_dir/"targeted_curated.jsonl.gz"
    holdout_gz=artifacts_dir/"dynamic_holdout.jsonl.gz"
    gzip_copy(targeted_path,targeted_gz)
    gzip_copy(qual_dir/"dynamic_holdout.jsonl",holdout_gz)

    artifact_meta={}
    artifact_meta["adapter_model"]=emit_file(train_dir/"adapter"/"adapter_model.safetensors","adapter_model.safetensors")
    artifact_meta["adapter_config"]=emit_file(train_dir/"adapter"/"adapter_config.json","adapter_config.json")
    artifact_meta["targeted_corpus"]=emit_file(targeted_gz,"targeted_curated.jsonl.gz")
    artifact_meta["dynamic_holdout"]=emit_file(holdout_gz,"dynamic_holdout.jsonl.gz")
    artifact_meta["training_receipt"]=emit_file(train_dir/"training_receipt.json","training_receipt.json")
    artifact_meta["qualification_receipt"]=emit_file(qual_dir/"qualification_receipt.json","qualification_receipt.json")

    final={
        "schema":"VERA_V5_PIPELINE_RECEIPT_V1",
        "smoke":smoke,
        "public_manifest_sha256":public_manifest["manifest_sha256"],
        "targeted_curated_sha256":curated_manifest["sha256"],
        "adapter_sha256":training_receipt["adapter_sha256"],
        "qualification_status":qualification_receipt["status"],
        "artifacts":artifact_meta,
    }
    emit_json("pipeline_final",final)
    print("PIPELINE_COMPLETE|"+json.dumps(final,sort_keys=True),flush=True)
    return final


if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--work-dir",type=Path,default=Path("/tmp/vera-v5"))
    ap.add_argument("--smoke",action="store_true")
    args=ap.parse_args()
    run(args.work_dir,smoke=args.smoke)
