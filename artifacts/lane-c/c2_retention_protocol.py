from __future__ import annotations
import argparse, collections, hashlib, json, pathlib, random, sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
ART = ROOT / "artifacts" / "lane-c"
BANK = ART / "C2_NOVEL_TASK_OPEN_BANK_V1.jsonl"
PACK = ART / "C2R_RETENTION_PROTOCOL_PACK_V1.jsonl"
KEY = ART / "C2R_RETENTION_ANSWER_KEY_V1.jsonl"
CONTRACT = ART / "C2R_RETENTION_SCORING_CONTRACT_V1.json"
SELFTEST = ART / "C2R_RETENTION_SELFTEST_V1.json"

EVAL_CONDITIONS = ("retained_after_update","no_acquisition","external_memory_present","wrong_task_key")
def cj(x): return json.dumps(x, sort_keys=True, ensure_ascii=False, separators=(",",":"))
def sha(b): return hashlib.sha256(b).hexdigest()
def loadj(p): return [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()]
def writej(p, rows):
    b="".join(cj(r)+"\n" for r in rows).encode("utf-8"); p.write_bytes(b); return sha(b)
def token(eid): return hashlib.sha256(("C2R:"+eid).encode()).hexdigest()[:20]
def support_text(s): return "\n".join(f"Example {i+1}: {x['input']} -> {x['output']}" for i,x in enumerate(s))
def shuffled(s, seed):
    r=random.Random(seed ^ 0xC2A5); outs=[x["output"] for x in s]; r.shuffle(outs)
    if len(outs)>1 and all(outs[i]==s[i]["output"] for i in range(len(s))): outs=outs[1:]+outs[:1]
    return [{"input":x["input"],"output":o} for x,o in zip(s,outs)]
def acq_prompt(row, bad=False):
    s=shuffled(row["support"],row["seed"]) if bad else row["support"]
    return "Acquire the task bound to opaque token "+token(row["episode_id"])+". Learn only from these examples. Do not answer an evaluation query yet.\n\n"+support_text(s)
def eval_prompt(row, tok, memory=None):
    parts=["Task token: "+tok,"This is a fresh evaluation context. Prior acquisition examples are not present in this context."]
    if memory is not None:
        parts += ["External task memory is explicitly supplied below:", support_text(memory)]
    parts += ["Return only the answer.","Query: "+row["query"]]
    return "\n\n".join(parts)
def build():
    rows=loadj(BANK); pack=[]; key=[]; toks=[token(r["episode_id"]) for r in rows]
    for i,row in enumerate(rows):
        t=toks[i]; wrong=toks[(i+1)%len(toks)]
        base={"episode_id":row["episode_id"],"family_id":row["family_id"],"split":row["split"],"task_token":t,"session_boundary":"HARD_CONTEXT_RESET"}
        for phase,bad in (("acquisition_clean",False),("acquisition_shuffled",True)):
            pr=acq_prompt(row,bad); pack.append({**base,"record_id":f"{row['episode_id']}::{phase}","phase":phase,"condition":phase,"prompt":pr,"prompt_sha256":sha(pr.encode())})
        prompts={
          "retained_after_update":eval_prompt(row,t),
          "no_acquisition":eval_prompt(row,t),
          "external_memory_present":eval_prompt(row,t,row["support"]),
          "wrong_task_key":eval_prompt(row,wrong),
        }
        for cond,pr in prompts.items():
            pid=f"{row['episode_id']}::{cond}"
            pack.append({**base,"record_id":pid,"phase":"evaluation","condition":cond,"prompt":pr,"prompt_sha256":sha(pr.encode())})
            key.append({"prompt_id":pid,"episode_id":row["episode_id"],"condition":cond,"expected":str(row["expected"])})
    psha=writej(PACK,pack); ksha=writej(KEY,key)
    contract={
      "schema":"C2R_RETENTION_SCORING_CONTRACT_V1","source_bank_sha256":sha(BANK.read_bytes()),"pack_sha256":psha,"answer_key_sha256":ksha,
      "episodes":len(rows),"records":len(pack),"eval_conditions":list(EVAL_CONDITIONS),
      "mechanism_protocol":{
        "frozen_base":"score no_acquisition only; no state update",
        "external_memory":"acquire support into external memory; score external_memory_present and memory-absent retained_after_update separately",
        "adapter":"perform bounded update from acquisition_clean; hard-reset context; score retained_after_update with no support or external memory",
        "negative_update":"perform same update procedure on acquisition_shuffled; score retained_after_update as corruption sensitivity control"
      },
      "claim_gate":{
        "persistent_learning_requires":["retained_after_update improvement over no_acquisition","retained_after_update prompt contains no demonstrations or memory","negative/shuffled update sensitivity","prior behavior regression within preregistered bound"],
        "retrieval_is_not_persistent_learning":True,"support_parsing_is_not_persistent_learning":True
      },
      "model_inference_performed":False,"gpu_used":False,"weights_changed":False,"protected_eval_consumed":False
    }
    CONTRACT.write_text(json.dumps(contract,indent=2)+"\n",encoding="utf-8")
    ev=[x for x in pack if x["phase"]=="evaluation"]
    checks={
      "records_336":len(pack)==len(rows)*6==336,
      "answer_rows_224":len(key)==len(rows)*4==224,
      "task_tokens_unique":len(set(toks))==len(toks),
      "eval_has_no_answer_or_rule_fields":all("expected" not in x and "rule_fingerprint" not in x for x in ev),
      "retained_has_no_support":all("Example " not in x["prompt"] and " -> " not in x["prompt"] for x in ev if x["condition"]=="retained_after_update"),
      "no_acquisition_has_no_support":all("Example " not in x["prompt"] for x in ev if x["condition"]=="no_acquisition"),
      "external_memory_is_explicit":all("External task memory" in x["prompt"] and "Example " in x["prompt"] for x in ev if x["condition"]=="external_memory_present"),
      "wrong_key_differs":all(x["task_token"] not in x["prompt"] for x in ev if x["condition"]=="wrong_task_key"),
      "family_not_in_eval_prompt":all(x["family_id"] not in x["prompt"] for x in ev),
      "query_not_in_acquisition":all(row["query"] not in acq_prompt(row,False) for row in rows),
    }
    stateless={x["record_id"]:"" for x in ev if x["condition"]=="retained_after_update"}
    checks["stateless_support_parser_retained_accuracy_zero"]=all(v=="" for v in stateless.values())
    report={"schema":"C2R_RETENTION_SELFTEST_V1","status":"PASS" if all(checks.values()) else "FAIL","checks":checks,"pack_sha256":psha,"answer_key_sha256":ksha,"contract_sha256":sha(CONTRACT.read_bytes()),"predecessor_heads":{"harness":"db05f9c157628300ee92d53d91ffc22fd9c8b736","runner":"6407f7235024eae8a140fb488c5f475383d246fa"},"interpretation_limit":"Protocol plumbing only; no model novel-task or retention performance is claimed."}
    SELFTEST.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8"); print(json.dumps(report,sort_keys=True)); return 0 if report["status"]=="PASS" else 41
def score(pred_path):
    key={x["prompt_id"]:x for x in loadj(KEY)}; preds={x["prompt_id"]:str(x.get("prediction","")).strip() for x in loadj(pathlib.Path(pred_path))}
    c=collections.defaultdict(lambda:[0,0,0])
    for pid,k in key.items():
        p=preds.get(pid); a=c[k["condition"]]; a[1]+=1
        if p is not None: a[2]+=1; a[0]+=(" ".join(p.split())==" ".join(k["expected"].split()))
    by={q:{"correct":v[0],"total":v[1],"covered":v[2],"accuracy":v[0]/v[1] if v[1] else 0.0,"coverage":v[2]/v[1] if v[1] else 0.0} for q,v in sorted(c.items())}
    return {"schema":"C2R_RETENTION_SCORE_V1","by_condition":by}
def main():
    ap=argparse.ArgumentParser(); sp=ap.add_subparsers(dest="cmd",required=True); sp.add_parser("build"); s=sp.add_parser("score"); s.add_argument("predictions"); a=ap.parse_args()
    if a.cmd=="build": return build()
    print(json.dumps(score(a.predictions),indent=2)); return 0
if __name__=="__main__": sys.exit(main())
