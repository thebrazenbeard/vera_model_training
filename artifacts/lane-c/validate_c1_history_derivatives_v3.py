import argparse,collections,hashlib,json,pathlib,subprocess,sys

ROOT=pathlib.Path(__file__).resolve().parents[2]
ART=ROOT/"artifacts"/"lane-c"
OUT_DEFAULT=ART/"C1_HISTORY_DERIVATIVE_VALIDATION_V3.json"
DATA_HEAD="56ce762626e3956f4afe7b0a0a2fe57d74b40ff7"
VALIDATOR_PATH="artifacts/lane-c/validate_c1_history_derivatives_v3.py"
TRAIN_PATH="artifacts/lane-c/C1_HISTORY_BEHAVIOR_TRAIN_V1.jsonl"
REPLAY_PATH="artifacts/lane-c/C1_HISTORY_BEHAVIOR_REPLAY_V1.jsonl"
TRAIN_SHA="0fbd18f7e999fbc92ef10167fde6b1f8af35a544f5c955a3cbceebbdf9deed12"
REPLAY_SHA="f97ce0322804efed56ed50e4372d29aae0ae6de080f282ce2985fa2272c3f477"

def git_bytes(ref,path):
    return subprocess.check_output(["git","show",f"{ref}:{path}"],cwd=ROOT)

def git_text(*args):
    return subprocess.check_output(["git",*args],cwd=ROOT,text=True).strip()

def load(data):
    return [json.loads(x) for x in data.decode("utf-8").splitlines() if x.strip()]

def sha(data):
    return hashlib.sha256(data).hexdigest()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--validator-commit",required=True)
    ap.add_argument("--validator-blob",required=True)
    ap.add_argument("--out",default=str(OUT_DEFAULT))
    args=ap.parse_args()

    validator_blob_actual=git_text("rev-parse",f"{args.validator_commit}:{VALIDATOR_PATH}")
    tb=git_bytes(DATA_HEAD,TRAIN_PATH)
    pb=git_bytes(DATA_HEAD,REPLAY_PATH)
    t,p=load(tb),load(pb)

    tc=dict(sorted(collections.Counter(x["source_behavior"] for x in t).items()))
    pc=dict(sorted(collections.Counter(x["source_behavior"] for x in p).items()))
    expected_train={"C1-BA-001":2,"C1-BA-002":2,"C1-BA-003":2,"C1-BA-004":2,"C1-BA-006":2,"C1-BA-007":2,"C1-BA-008":2}
    expected_replay={f"C1-BA-{i:03d}":1 for i in range(1,9)}
    train_keys={"row_id","source_behavior","split","prompt","preferred","rejected","privacy"}
    replay_keys={"row_id","source_behavior","split","criterion"}
    ba005=[x for x in p if x["source_behavior"]=="C1-BA-005"]
    train_ids={x["row_id"] for x in t}
    replay_ids={x["row_id"] for x in p}

    checks={
      "validator_blob_matches_commit":validator_blob_actual==args.validator_blob,
      "train_sha_exact":sha(tb)==TRAIN_SHA,
      "replay_sha_exact":sha(pb)==REPLAY_SHA,
      "rows_exact":len(t)==14 and len(p)==8,
      "schemas_exact":all(set(x)==train_keys for x in t) and all(set(x)==replay_keys for x in p),
      "splits_exact":all(x["split"]=="train" for x in t) and all(x["split"] in {"replay","external_only"} for x in p),
      "privacy_exact":all(x["privacy"]=="SYNTHETIC_PUBLIC_SAFE" for x in t),
      "counts_exact":tc==expected_train and pc==expected_replay,
      "ba005_external_only":not any(x["source_behavior"]=="C1-BA-005" for x in t) and len(ba005)==1 and ba005[0]["split"]=="external_only",
      "row_ids_disjoint":not(train_ids & replay_ids)
    }
    status="PASS" if all(checks.values()) else "FAIL"
    receipt={
      "schema":"C1_HISTORY_DERIVATIVE_VALIDATION_V3",
      "supersedes":"C1_HISTORY_DERIVATIVE_VALIDATION_V2",
      "status":status,
      "provenance":{
        "validated_data_head":DATA_HEAD,
        "validator_commit":args.validator_commit,
        "validator_blob":args.validator_blob,
        "validator_path":VALIDATOR_PATH,
        "receipt_authority_model":"FIXED_DATA_HEAD_PLUS_IMMUTABLE_VALIDATOR_IDENTITY"
      },
      "inputs":{
        "train_path":TRAIN_PATH,"train_sha256":sha(tb),
        "replay_path":REPLAY_PATH,"replay_sha256":sha(pb)
      },
      "counts":{
        "train_rows":len(t),"replay_rows":len(p),
        "train_per_behavior":tc,"replay_per_behavior":pc
      },
      "checks":checks,
      "governance":{
        "protected_eval_consumed":False,
        "shared_gpu_used":False,
        "weight_change":False,
        "candidate_derivative_bytes_changed":False,
        "ba005_neural_training":False
      },
      "known_v2_defect":"V2 receipt embedded runtime HEAD as source_head, so a rerun at the receipt commit changed receipt bytes.",
      "repro_rule":"Run this validator with the same validator_commit and validator_blob; output must be byte-identical regardless of current checkout HEAD."
    }
    data=(json.dumps(receipt,indent=2,sort_keys=True)+"\n").encode("utf-8")
    pathlib.Path(args.out).write_bytes(data)
    print(json.dumps({"status":status,"receipt_sha256":sha(data),"validated_data_head":DATA_HEAD,"validator_commit":args.validator_commit,"validator_blob":args.validator_blob},sort_keys=True))
    return 0 if status=="PASS" else 41

if __name__=="__main__":
    sys.exit(main())
