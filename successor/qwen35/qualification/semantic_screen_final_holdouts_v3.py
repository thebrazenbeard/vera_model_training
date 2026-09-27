from __future__ import annotations
import json
import pathlib
import numpy as np
from sentence_transformers import SentenceTransformer

ROOT = pathlib.Path(__file__).resolve().parents[3]
Q = ROOT / "successor" / "qwen35"
TARGETS = [
    Q / "qualification" / "final_holdout_v3.jsonl",
    Q / "qualification" / "final_retention_v3.jsonl",
    Q / "qualification" / "final_adversarial_proxy_v3.jsonl",
]
MODEL_ID = "sentence-transformers/all-MiniLM-L6-v2"
COSINE_FAIL = 0.90

def rows(path):
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]

def main():
    excluded=set(TARGETS)
    source=[]
    for path in list((Q/"corpus").rglob("*.jsonl")) + list((Q/"qualification").rglob("*.jsonl")):
        if path in excluded:
            continue
        try:
            data=rows(path)
        except Exception:
            continue
        for i,row in enumerate(data):
            prompt=row.get("prompt")
            if isinstance(prompt,str) and prompt.strip():
                source.append((path.relative_to(ROOT).as_posix(),i,prompt))
    target=[]
    for path in TARGETS:
        for row in rows(path):
            target.append((path.name,row["record_id"],row["prompt"]))
    model=SentenceTransformer(MODEL_ID, device="cpu")
    src_emb=model.encode([x[2] for x in source],batch_size=64,normalize_embeddings=True,show_progress_bar=False)
    tgt_emb=model.encode([x[2] for x in target],batch_size=64,normalize_embeddings=True,show_progress_bar=False)
    sims=np.asarray(tgt_emb) @ np.asarray(src_emb).T
    failures=[]
    maxima=[]
    for i,t in enumerate(target):
        j=int(np.argmax(sims[i]))
        score=float(sims[i,j])
        maxima.append(score)
        src=source[j]
        if score >= COSINE_FAIL:
            failures.append((t[0],t[1],score,src[0],src[1],src[2]))
    print(f"MODEL={MODEL_ID} SOURCE_PROMPTS={len(source)} TARGET_PROMPTS={len(target)} THRESHOLD={COSINE_FAIL}")
    print(f"MAX_COSINE={max(maxima):.6f} P95={float(np.percentile(maxima,95)):.6f} MEAN_MAX={float(np.mean(maxima)):.6f}")
    for item in sorted(failures,key=lambda x:x[2],reverse=True):
        print("FAIL",json.dumps(item,ensure_ascii=False))
    print(f"FAIL_COUNT={len(failures)}")
    return 1 if failures else 0

if __name__=="__main__":
    raise SystemExit(main())