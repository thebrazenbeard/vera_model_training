#!/usr/bin/env python3
import hashlib,json,os,sys
HERE=os.path.dirname(os.path.abspath(__file__))
INV="R9B0_SOURCE_ELIGIBILITY_INVENTORY_V1.json"
LIN="R9B0_LINEAGE_BINDINGS_V1.json"
SUMS="R9B0_SOURCE_LINEAGE_CHECKSUMS_V1.json"
OWNER={"repository":"thebrazenbeard/vera-R9A0","commit":"1d2bb27d5ff89854c93c431998c5ba255704c1b2","tree":"939db8d84c8894df5d7ed136856f38ea19e4372e"}
SOURCES={
"validation/R9B0_NATIVE_OBLIGATION_MATRIX.json":"74bf2b66caf02db0a85f20edc42836e558d3c1f4",
"validation/R9B0_SEMANTIC_PROJECTION_MANIFEST.json":"1655e707a06759f27c7691e1d839ab1e350dd135",
"validation/R9B0_MEMORY_EPOCH_CONTRACT.json":"af1b5f9105af6ca2eb140c0580440f408069d096",
"validation/VERA_BEHAVIOR_PROFILE_V1.json":"0c79625b993a559bd22a6fbe68279450fc736eb2",
"schemas/native-project/r9b0_memory_epoch_envelope_v1.schema.json":"09d14e127d8d7d2f3275f70f64e4cac56be31071",
"project/VERA_R9A0_RUNTIME.md":"3591771f336dbe287c404d3ee8d473bb6abdd235"}
BASE=("a53d0300fe9508b8597ebf47bbcacbd2a3922675","600ca443447cf425c6231fcf437bcaaf8dcc3add","b030dce399ea533510df275d781d5829334bf20b")
SPEC=("b030dce399ea533510df275d781d5829334bf20b","2173f7294eb1ce5313d1cef6bc8954e5c31cfd19","79b71a2c9bce28be176389d088cee3e5a1704cbc")
REVIEWS={
5494571423:"PASS_H0_M0_AT_EXACT_B030DCE_THIRTEEN_M01_M05_REREVIEW_SCOPE",
5494646353:"PASS_H0_M0_AT_EXACT_B030DCE_SEVEN_METHOD_001_007_REREVIEW_SCOPE",
5495056386:"REVIEW_WAVE_CLOSED_H0_M0_AT_EXACT_B030DCE / SPECIFICATION_CURRENT / NOT_YET_RETRAIN_CANDIDATE_READY",
5499064383:"CUSTODY_GREEN_AT_A53D0300 / FOUR_NEW_PATHS_ONLY / CONTRACT_CEILING_PRESERVED / RELEASED_TO_ONE_MINIMUM_ACCEPTANCE / NOT_RETRAIN_READY",
5499276015:"ACCEPT_CONTRACT_PACKAGE_H0_M0 / CONTRACT_PACKAGE_VALID_ONLY / NOT_RETRAIN_CANDIDATE_READY"}
SAT=['SPECIFICATION_CURRENT', 'EXACT_OWNER_FREEZE', 'TARGET_COMPONENT_SCHEMA', 'RUNTIME_PREMISE_CONTRACT', 'SOURCE_PRIVACY_ELIGIBILITY', 'HISTORICAL_ROLE_REGRESSION_ONLY', 'PREREGISTERED_A_F_HYPOTHESES_THRESHOLDS_CONTROLS', 'IMMUTABLE_MANIFESTS_CHECKSUMS', 'INDEPENDENT_REREVIEW_HM_CLOSED']
UNRES=['IDENTITY_CURRENT_OWNER_NONBOOTSTRAP_TESTS', 'FROZEN_TRAINING', 'INDEPENDENTLY_FROZEN_DEVELOPMENT_VALIDATION', 'STRUCTURAL_CLUSTERING_CLEAN', 'SEMANTIC_NEIGHBOR_POLICY_CALIBRATION_CLEAN', 'EMBARGOED_CURRENT_OWNER_FINAL_HOLDOUT', 'ATTRIBUTION_ABLATION_MANIFEST', 'EXACT_MODEL_TOKENIZER_CONFIG_DECODE_EVALUATOR_LINEAGE']
UNRES_SLOTS=['base_model', 'tokenizer', 'training_config', 'decoding_policy', 'evaluator', 'premise_fixture', 'tool_fixture', 'harness']
PREREG_SHA="177e4b936c3394925b3f9bff16aa3b52b63d0b306dfb9c925fcb43256ee04313"
class E(Exception): pass
def bad(x): raise E(x)
def pairs(ps):
 d={}
 for k,v in ps:
  if k in d: bad("duplicate key:"+k)
  d[k]=v
 return d
def nonfinite(x): bad("non-finite:"+x)
def load(n):
 with open(os.path.join(HERE,n),"r",encoding="utf-8",newline="") as f:
  return json.load(f,object_pairs_hook=pairs,parse_constant=nonfinite)
def req(c,m):
 if not c: bad(m)
def canon(o): return json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=False,allow_nan=False).encode()
def main():
 inv,lin,sums=load(INV),load(LIN),load(SUMS)
 req(inv.get("schema")=="R9B0_SOURCE_ELIGIBILITY_INVENTORY_V1","inventory schema")
 req(lin.get("schema")=="R9B0_LINEAGE_BINDINGS_V1","lineage schema")
 req(sums.get("schema")=="R9B0_SOURCE_LINEAGE_CHECKSUMS_V1","checksum schema")
 expected=sorted([INV,LIN,os.path.basename(__file__)])
 es=sums.get("files")
 req(isinstance(es,list) and [e.get("path") for e in es]==expected,"checksum path set/order")
 for e in es:
  b=open(os.path.join(HERE,e["path"]),"rb").read()
  req(e.get("bytes")==len(b),"byte mismatch:"+e["path"])
  req(e.get("sha256")==hashlib.sha256(b).hexdigest(),"sha mismatch:"+e["path"])
 req(inv.get("owner_anchor")==OWNER,"owner anchor")
 got={}
 for s in inv.get("sources",[]):
  req({k:s.get(k) for k in OWNER}==OWNER,"source owner binding")
  req(s.get("privacy_eligibility")=="ELIGIBLE_FOR_DERIVATION","source privacy")
  req(s.get("rendered_neural_training_examples_allowed") is False,"auto-render prohibited")
  got[s.get("path")]=s.get("blob")
 req(got==SOURCES,"source path/blob set")
 pol=inv.get("source_class_policy",{})
 req(pol.get("PRIVATE_USER_SOURCE")=="EXCLUDE_FROM_WEIGHT_TRAINING","private user exclusion")
 req(pol.get("PRIVATE_THIRD_PARTY_SOURCE")=="EXCLUDE_FROM_WEIGHT_TRAINING","private third-party exclusion")
 req(pol.get("FROZEN_HISTORICAL_EVAL_PAYLOAD")=="EVAL_ONLY","historical eval role")
 req(pol.get("UNBOUND_ARCHIVE_OR_INVENTORY")=="NEEDS_EXACT_SOURCE","unbound archive role")
 l=lin.get("lease_binding",{})
 req(l.get("lease_id")=="BT2-VMT-PA-VERA-R9B0-SOURCE-BINDINGS-V1","lease")
 req((l.get("required_base_head"),l.get("required_base_tree"),l.get("required_base_sole_parent"))==BASE,"base binding")
 sp=lin.get("reviewed_spec_binding",{})
 req((sp.get("subject_commit"),sp.get("subject_tree"),sp.get("blob"))==SPEC,"spec binding")
 pkg=lin.get("accepted_readiness_package_binding",{})
 req((pkg.get("successor_commit"),pkg.get("tree"),pkg.get("sole_parent"))==BASE,"accepted package binding")
 req(pkg.get("claim_ceiling")=="CONTRACT_PACKAGE_VALID_ONLY" and pkg.get("readiness_status")=="NOT_READY","accepted package ceiling")
 req({r.get("comment_id"):r.get("verdict") for r in lin.get("review_bindings",[])}==REVIEWS,"review bindings")
 req(hashlib.sha256(canon(lin.get("family_preregistration_exact_transcription"))).hexdigest()==PREREG_SHA,"A-F exact transcription")
 slots=lin.get("exact_lineage_slots",{})
 req(set(slots)==set(UNRES_SLOTS+["runtime_owner"]),"slot set")
 for n in UNRES_SLOTS:
  req(slots[n].get("state")=="UNRESOLVED" and slots[n].get("evidence") is None and slots[n].get("missing_datum"),"unsupported satisfied slot:"+n)
 ro=slots["runtime_owner"]
 req(ro.get("state")=="SATISFIED","runtime_owner state")
 req(ro.get("evidence")=={**OWNER,"path":"project/VERA_R9A0_RUNTIME.md","blob":SOURCES["project/VERA_R9A0_RUNTIME.md"]},"runtime_owner evidence")
 g=lin.get("gate_accounting",{})
 req(g.get("source_evidence_satisfied")==SAT,"satisfied gates")
 req(g.get("unresolved")==UNRES,"unresolved gates")
 req(g.get("exact_model_tokenizer_config_decode_evaluator_lineage")=="UNRESOLVED","aggregate model lineage")
 req(lin.get("retrain_candidate_ready") is False,"retrain ready false")
 req(lin.get("training_execution_authorized") is False,"training false")
 req(lin.get("model_promotion_authorized") is False,"promotion false")
 out={"source_lineage_package_status":"SOURCE_LINEAGE_BINDINGS_VALID","retrain_candidate_ready":False,
 "satisfied_source_gates":SAT,"satisfied_lineage_slots":["runtime_owner"],
 "unresolved_lineage_slots":UNRES_SLOTS,"unresolved_gates":UNRES,
 "training_execution_authorized":False,"model_promotion_authorized":False}
 print(json.dumps(out,sort_keys=True,separators=(",",":"),allow_nan=False))
if __name__=="__main__":
 try: main()
 except E as e:
  print("SOURCE_LINEAGE_PACKAGE_INVALID:"+str(e),file=sys.stderr); sys.exit(1)
