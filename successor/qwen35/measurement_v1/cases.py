"""Case ingestion, group separation and 10k final preflight; no claimed external review."""
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

class CaseError(ValueError):
    pass

LANES = ("behavioral","adversarial","retention","runtime_effect")
DIMENSIONS = {f"H{i:02d}" for i in range(1,21)}
QUOTAS = {"behavioral":6500,"adversarial":2000,"retention":1500}
HEX = re.compile(r"[0-9a-f]{64}\Z")
GRADERS = {"exact","regex","numeric","contains","manual","runtime_effect"}

def normalized_prompt(value):
    if not isinstance(value,str):
        raise CaseError("prompt must be string")
    return " ".join(re.findall(r"[a-z0-9]+",value.casefold()))

def required(value,key):
    if not isinstance(value,str) or not value.strip():
        raise CaseError(f"{key} missing or empty")
    return value.strip()

def validate_row(r):
    if not isinstance(r,dict):
        raise CaseError("case must be object")
    for k in ("case_id","prompt","family_id"):
        required(r.get(k),k)
    if not normalized_prompt(r["prompt"]):
        raise CaseError("empty normalized prompt")
    lane=r.get("lane")
    if lane not in LANES:
        raise CaseError("invalid lane")
    if lane=="behavioral":
        if r.get("dimension") not in DIMENSIONS:
            raise CaseError("invalid H dimension")
    elif r.get("dimension") is not None:
        raise CaseError("dimension must be null outside behavioral lane")
    o=r.get("origin")
    if not isinstance(o,dict):
        raise CaseError("origin missing")
    for k in ("source_id","source_revision","license","generation_method"):
        required(o.get(k),"origin."+k)
    if o.get("privacy")!="public":
        raise CaseError("origin privacy not public")
    digest=o.get("source_sha256")
    if not isinstance(digest,str) or not HEX.fullmatch(digest):
        raise CaseError("invalid source SHA256")
    g=r.get("grader")
    if not isinstance(g,dict) or g.get("kind") not in GRADERS:
        raise CaseError("unsupported grader")
    kind=g["kind"]
    if kind=="exact" and not isinstance(g.get("expected"),str):
        raise CaseError("exact expected missing")
    if kind=="regex":
        required(g.get("pattern"),"pattern")
        try: re.compile(g["pattern"])
        except re.error as e: raise CaseError("invalid regex") from e
    if kind=="numeric":
        try: tolerance=float(g.get("tolerance",0)); float(g["expected"])
        except (TypeError,ValueError,KeyError) as e: raise CaseError("numeric expected/tolerance") from e
        if tolerance<0: raise CaseError("negative tolerance")
    if kind=="contains":
        if not isinstance(g.get("required"),list) or not g["required"]:
            raise CaseError("contains requires phrases")
    if kind in ("manual","runtime_effect"):
        required(g.get("rubric_id"),"rubric_id")

def validate_rows(rows):
    if not isinstance(rows,list) or not rows:
        raise CaseError("empty case collection")
    ids=set()
    prompts=set()
    for row in rows:
        validate_row(row)
        if row["case_id"] in ids:
            raise CaseError("duplicate case_id: "+row["case_id"])
        ids.add(row["case_id"])
        text=normalized_prompt(row["prompt"])
        if text in prompts:
            raise CaseError("duplicate normalized prompt: "+row["case_id"])
        prompts.add(text)

def read_cases(path):
    rows=[]
    for n,line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(),1):
        if line.strip():
            try: rows.append(json.loads(line))
            except json.JSONDecodeError as e: raise CaseError(f"invalid JSON line {n}") from e
    validate_rows(rows)
    return rows

def split_dev_cases(rows,*,seed):
    validate_rows(rows)
    grouped=defaultdict(list)
    for r in rows:
        grouped[r["family_id"]].append(r)
    if len(grouped)<2:
        raise CaseError("need at least two distinct families")
    train=[]
    val=[]
    for family in sorted(grouped):
        h=hashlib.sha256(f"{seed}|{family}".encode()).digest()
        fraction=int.from_bytes(h[:8],"big")/2**64
        (train if fraction < .8 else val).extend(grouped[family])
    if not val:
        pivot=sorted(grouped)[-1]
        val=grouped[pivot][:]
        train=[r for r in train if r["family_id"]!=pivot]
    if not train:
        pivot=sorted(grouped)[0]
        train=grouped[pivot][:]
        val=[r for r in val if r["family_id"]!=pivot]
    if not train or not val:
        raise CaseError("empty split")
    return sorted(train,key=lambda x:x["case_id"]),sorted(val,key=lambda x:x["case_id"])

def legacy_consumed_fingerprints():
    """Mandatory V3/V4 and earlier heldout exclusions; missing sources fail closed."""
    q=Path(__file__).resolve().parents[1]/"qualification"
    paths=(
        "final_holdout_v3.jsonl","final_retention_v3.jsonl","final_adversarial_proxy_v3.jsonl",
        "final_holdout_v4.jsonl","final_retention_v4.jsonl","final_adversarial_proxy_v4.jsonl",
        "history_behavior_holdout_v1.jsonl","h07_final_holdout_v1.jsonl",
    )
    blocked=set()
    for name in paths:
        path=q/name
        if not path.is_file():
            raise CaseError("mandatory consumed holdout missing: "+name)
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                row=json.loads(line)
                if isinstance(row.get("prompt"),str):
                    blocked.add(normalized_prompt(row["prompt"]))
    return blocked

def preflight_final_bank(rows,*,consumed_prompt_fingerprints,verify_independent_review=None,excluded_family_ids=None):
    """Mocked callbacks may prove structural contract, NEVER real independent review."""
    if len(rows)<10000:
        raise CaseError(f"final needs 10,000 cases minimum (observed {len(rows)})")
    validate_rows(rows)
    counts=Counter(r["lane"] for r in rows)
    for lane,minimum in QUOTAS.items():
        if counts[lane]<minimum:
            raise CaseError(f"{lane} must have >= {minimum} cases")
    dimensions=Counter(r["dimension"] for r in rows if r["lane"]=="behavioral")
    for d in sorted(DIMENSIONS):
        if dimensions[d]<300:
            raise CaseError(f"dimension {d} must have >=300 cases")
    all_blocked=legacy_consumed_fingerprints() | set(consumed_prompt_fingerprints)
    if any(normalized_prompt(r["prompt"]) in all_blocked for r in rows):
        raise CaseError("consumed final prompt encountered")
    excluded=excluded_family_ids or set()
    if any(r["family_id"] in excluded for r in rows):
        raise CaseError("development family overlaps final bank")
    if verify_independent_review is None:
        raise CaseError("independent reviewer verifier is required")
    for r in rows:
        required(r.get("review_receipt_id"),"review receipt")
        if verify_independent_review(r) is not True:
            raise CaseError("independent reviewer did not verify: "+r["case_id"])
    return {"status":"STRUCTURAL_PREFLIGHT_ONLY","case_count":len(rows),"lane_counts":dict(counts),
            "dimensions":dict(dimensions),"distinct_source_digests":len({r["origin"]["source_sha256"] for r in rows}),
            "sampling_warning":"REPRESENTATIVENESS_NOT_ESTABLISHED",
            "independent_review":"CALLBACK_ACCEPTED_NOT_A_RUNTIME_ATTESTATION",
            "runtime_effect_claim":"NOT_ESTABLISHED"}
