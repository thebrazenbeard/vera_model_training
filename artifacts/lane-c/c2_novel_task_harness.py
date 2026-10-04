import json,hashlib,pathlib,random,collections,sys
ROOT=pathlib.Path(__file__).resolve().parents[2]; A=ROOT/"artifacts"/"lane-c"
SPLITS={"meta_train":["nonce_permute","mini_grammar","string_pipeline"],"meta_dev":["tool_contract"],"meta_test_open":["state_machine","contradictory_prior","goal_inference"]}
N=8
def norm(x): return " ".join(str(x).strip().split())
def dig(x): return hashlib.sha256(json.dumps(x,sort_keys=True).encode()).hexdigest()
def perm(seed):
 r=random.Random(seed); p=[0,1,2]; r.shuffle(p)
 f=lambda s:" ".join(s.split()[i] for i in p); xs=["dax wug zif","pel nor kiv","tob rem saz","vok lin mer"]
 return [(x,f(x)) for x in xs[:3]],xs[3],f(xs[3]),{"perm":p}
def gram(seed):
 r=random.Random(seed); order=list(r.choice([(0,1,2),(2,0,1),(1,2,0)])); suf=["-ka","-tu","-mi"]; xs=[("zan","miv","tor"),("pel","ruk","sev"),("zan","ruk","sev"),("pel","miv","tor")]
 f=lambda x:" ".join(x[i]+suf[i] for i in order)
 return [(" ".join(x),f(x)) for x in xs[:3]]," ".join(xs[3]),f(xs[3]),{"order":order,"suffixes":suf}
def tool(seed):
 r=random.Random(seed); fields=["nex","vul","qar"]; r.shuffle(fields); xs=[("red","7","cold"),("blue","2","hot"),("green","9","warm"),("amber","4","cool")]
 f=lambda x:"CALL<"+",".join(fields[i]+"="+x[i] for i in range(3))+">"
 return [("|".join(x),f(x)) for x in xs[:3]],"|".join(xs[3]),f(xs[3]),{"fields":fields}
def fsm(seed):
 r=random.Random(seed); st=["SA","SB","SC","SD"]; acts=["x","y"]; trans={(s,a):r.choice(st) for s in st for a in acts}
 sup=[(s+"+"+a,trans[(s,a)]) for s in st for a in acts]
 q="SA|x,y,x"; cur="SA"
 for a in ["x","y","x"]: cur=trans[(cur,a)]
 return sup,q,cur,{"trans":{s+"+"+a:v for (s,a),v in trans.items()}}
def anti(seed):
 r=random.Random(seed); src=["up","down","red","green"]; dst=["N4","Q2","M7","R1"]; r.shuffle(dst); m=dict(zip(src,dst))
 sup=[(x,m[x]) for x in src]; q="red|up"; e=m["red"]+"|"+m["up"]
 return sup,q,e,{"map":m}
def pipe(seed):
 r=random.Random(seed); k=r.choice([1,2,3]); mark=r.choice(["!","?","#"])
 def f(s):
  z=s[::-1].upper(); z=z[k:]+z[:k]; return z+mark
 xs=["mepa","zoril","tavin","kusen"]
 return [(x,f(x)) for x in xs[:3]],xs[3],f(xs[3]),{"rotate":k,"mark":mark}
def goal(seed):
 r=random.Random(seed); w=(r.choice([-2,-1,1,2]),r.choice([-2,-1,1,2]))
 pts=[("A",(0,0)),("B",(0,1)),("C",(1,0)),("D",(1,1))]
 sc=lambda v:w[0]*v[0]+w[1]*v[1]
 sup=[(k+":"+str(v),str(sc(v))) for k,v in pts]
 q="choose "+",".join(k+":"+str(v) for k,v in pts); e=max(pts,key=lambda kv:(sc(kv[1]),kv[0]))[0]
 return sup,q,e,{"weights":w}
G={"nonce_permute":perm,"mini_grammar":gram,"tool_contract":tool,"state_machine":fsm,"contradictory_prior":anti,"string_pipeline":pipe,"goal_inference":goal}
def episode(fam,split,i):
 seed=260000+list(G).index(fam)*100+i; sup,q,e,rule=G[fam](seed)
 return {"episode_id":f"C2-{fam}-{i:02d}","family_id":fam,"split":split,"seed":seed,"support":[{"input":a,"output":b} for a,b in sup],"query":q,"expected":e,"rule_fingerprint":dig(rule),"prompt_mode":"DEMONSTRATIONS_ONLY","control_variants":["shuffled_labels","irrelevant_memory","support_omitted","familiar_lookalike"]}
def generate():
 return [episode(f,s,i) for s,fs in SPLITS.items() for f in fs for i in range(N)]
def score(rows,preds):
 ok=sum(norm(preds.get(r["episode_id"],""))==norm(r["expected"]) for r in rows)
 return {"correct":ok,"total":len(rows),"accuracy":ok/len(rows) if rows else 0.0}
def main():
 rows=generate(); ids=[r["episode_id"] for r in rows]; fps=[r["rule_fingerprint"] for r in rows]
 famsets={s:set(fs) for s,fs in SPLITS.items()}
 checks={"rows_56":len(rows)==56,"ids_unique":len(ids)==len(set(ids)),"rule_reuse_family_bounded":all(len({r["family_id"] for r in rows if r["rule_fingerprint"]==f})==1 for f in set(fps)),"family_splits_disjoint":not(famsets["meta_train"]&famsets["meta_dev"] or famsets["meta_train"]&famsets["meta_test_open"] or famsets["meta_dev"]&famsets["meta_test_open"]),"query_not_support":all(r["query"] not in {x["input"] for x in r["support"]} for r in rows)}
 oracle={r["episode_id"]:r["expected"] for r in rows}; blank={}
 checks["oracle_score"]=score(rows,oracle)["accuracy"]==1.0; checks["blank_score"]=score(rows,blank)["accuracy"]==0.0
 bank="".join(json.dumps(r,sort_keys=True)+"\n" for r in rows).encode(); bh=hashlib.sha256(bank).hexdigest()
 (A/"C2_NOVEL_TASK_OPEN_BANK_V1.jsonl").write_bytes(bank)
 man={"schema":"C2_NOVEL_TASK_HARNESS_MANIFEST_V1","generator":"artifacts/lane-c/c2_novel_task_harness.py","rows":len(rows),"bank_sha256":bh,"family_splits":SPLITS,"episodes_per_family":N,"metrics":["zero_shot_competence","examples_to_success","improvement_per_example_or_failure","unseen_instance_generalization","structural_transfer","retention_after_context_removal","prior_capability_regression","false_task_recognition_rate","retrieval_dependence"],"negative_controls":["shuffled_labels","irrelevant_memory","support_omitted","familiar_lookalike","adapter_disabled","contradictory_prior"],"scoring":"normalized exact match for open V1; family-level aggregate required","protected_eval":False,"gpu":False,"weights_changed":False}
 (A/"C2_NOVEL_TASK_HARNESS_MANIFEST_V1.json").write_text(json.dumps(man,indent=2)+"\n",encoding="utf-8")
 rep={"schema":"C2_NOVEL_TASK_HARNESS_SELFTEST_V1","status":"PASS" if all(checks.values()) else "FAIL","checks":checks,"bank_sha256":bh,"oracle":score(rows,oracle),"blank":score(rows,blank)}
 (A/"C2_NOVEL_TASK_HARNESS_SELFTEST_V1.json").write_text(json.dumps(rep,indent=2)+"\n",encoding="utf-8")
 print(json.dumps(rep,sort_keys=True)); return 0 if rep["status"]=="PASS" else 41
if __name__=="__main__": sys.exit(main())
