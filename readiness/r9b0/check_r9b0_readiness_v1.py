#!/usr/bin/env python3
import hashlib,json,math,pathlib,sys
H=pathlib.Path(__file__).parent
F=['R9B0_READINESS_MANIFEST_V1.json','R9B0_READINESS_SCHEMA_V1.json','check_r9b0_readiness_v1.py']
PRIVATE={'PRIVATE_USER_SOURCE','PRIVATE_THIRD_PARTY_SOURCE'}
class E(Exception):pass
def bad(s): raise E(s)
def pairs(p):
 d={}
 for k,v in p:
  if k in d: bad('duplicate JSON key: '+k)
  d[k]=v
 return d
def load(n):
 def c(x):
  v=float(x)
  if not math.isfinite(v): bad('non-finite JSON')
  return v
 return json.loads((H/n).read_text(),object_pairs_hook=pairs,parse_constant=lambda x:bad('non-finite JSON'),parse_float=c)
def req(x,s):
 if not x: bad(s)
def sha(b): return hashlib.sha256(b).hexdigest()
def checks(c):
 req(c.get('schema')=='R9B0_READINESS_CHECKSUMS_V1','checksum schema mismatch')
 e=c.get('entries'); req(isinstance(e,list),'checksum entries missing'); req([x.get('path') for x in e]==sorted(F),'checksum target set/order mismatch')
 for x in e:
  b=(H/x['path']).read_bytes(); req(x.get('bytes')==len(b),'byte count mismatch: '+x['path']); req(x.get('sha256')==sha(b),'sha256 mismatch: '+x['path'])
def schema(s):
 req(s.get('$schema')=='https://json-schema.org/draft/2020-12/schema','JSON Schema draft mismatch'); req(s.get('additionalProperties') is False,'top-level schema must be strict')
 d=s.get('$defs',{}); req({'runtime_resolved_premise','component','source_binding','derivation_provenance','contamination_result'}<=set(d),'required schema defs missing')
 p=d['runtime_resolved_premise']['properties']; req(p['immutable_for_record'].get('const') is True and p['runtime_resolution_required'].get('const') is True and p['runtime_fact_is_input_not_target'].get('const') is True,'runtime premise invariant missing')
 ce=d['component']['properties']; req('RETRAIN_CANDIDATE' in ce['disposition']['enum'] and ce['runtime_fact_is_input_not_target'].get('const') is True,'component invariant missing')
 req(PRIVATE<=set(d['source_class']['enum']),'private source classes missing'); req('EXCLUDE_FROM_WEIGHT_TRAINING' in d['privacy_eligibility']['enum'],'private exclusion enum missing')
def manifest(m):
 req(m.get('schema')=='R9B0_READINESS_MANIFEST_V1','manifest schema mismatch'); req(m.get('contract_package_claim_ceiling')=='CONTRACT_PACKAGE_VALID_ONLY','claim ceiling mismatch'); req(m.get('readiness_status')=='NOT_READY','manifest must be NOT_READY')
 l=m['lease_binding']; req(l=={'lease_id':'BT2-VMT-PA-VERA-R9B0-READINESS-ARTIFACTS-V1','repository':'thebrazenbeard/vera_model_training','branch':'vera/r9b0-training-reconciliation','required_base_head':'b030dce399ea533510df275d781d5829334bf20b','required_base_tree':'2173f7294eb1ce5313d1cef6bc8954e5c31cfd19','reviewed_spec_path':'docs/reconciliation/R9B0_RETRAIN_CANDIDATE_FAMILY_SPEC.md','reviewed_spec_blob':'79b71a2c9bce28be176389d088cee3e5a1704cbc'},'lease/spec binding mismatch')
 a=m['current_owner_anchor']; req(a['repository']=='thebrazenbeard/vera-R9A0' and a['commit']=='1d2bb27d5ff89854c93c431998c5ba255704c1b2','current-owner anchor mismatch')
 req('RUNTIME_RESOLVED_FACTS_ARE_IMMUTABLE_INPUTS_NOT_TARGETS' in m['invariants'],'runtime-input invariant missing'); req('WEIGHT_OR_ADAPTER_PRESENCE != VERA_IDENTITY_OR_CURRENT_OWNER_AUTHORITY' in m['invariants'],'identity non-bootstrap invariant missing')
 s=m['corpus_surfaces']; req(set(s)=={'TRAINING','DEVELOPMENT_VALIDATION','FROZEN_HISTORICAL_EVALUATION','CURRENT_OWNER_FINAL_HOLDOUT'},'surface set mismatch'); req(s['FROZEN_HISTORICAL_EVALUATION']['role']=='KNOWN_REGRESSION_ONLY','historical eval not regression-only'); req(s['CURRENT_OWNER_FINAL_HOLDOUT']['embargoed'] is True and s['CURRENT_OWNER_FINAL_HOLDOUT']['one_shot'] is True,'final holdout semantics missing')
 p=m['source_privacy_policy'];
 for x in PRIVATE: req(p['mandatory_mapping'].get(x)=='EXCLUDE_FROM_WEIGHT_TRAINING','private source can become weight-training eligible')
 req(p['authorization_can_override_private_exclusion'] is False,'private exclusion override forbidden')
 c=m['contamination_policy']; req(c['near_duplicate_control_recall_gate']>=.99 and c['report_false_positive_rate'] is True and c['thresholds_cannot_weaken_after_results'] is True,'contamination gate incomplete')
 req(set(m['attribution_ablation']['cells'])=={'W0/S1','W1/S1','W0/S0','W1/S0'},'ablation cells missing'); req(m['attribution_ablation']['invalid_when_mandatory_gate_weakened']=='NOT_VALID_FOR_WEIGHT_ATTRIBUTION','unsafe ablation policy missing')
 f=m['family_preregistration']; req(set(f)==set('ABCDEF'),'A-F preregistration missing')
 for k,v in f.items(): req(all(x in v for x in ['hypothesis','metrics','thresholds','minimum_effect','negative_control','no_regression','critical_failure']),'family prereg incomplete: '+k)
 g=m['readiness_gates']; req(g['HISTORICAL_ROLE_REGRESSION_ONLY']['state']=='SATISFIED','historical role gate mismatch')
 t=m['training_authority']; req(t['training_execution_authorized'] is False and t['model_promotion_authorized'] is False and t['separate_explicit_protected_effect_authority_required'] is True,'training authority ceiling broken')
 blockers=[]
 for k,v in g.items():
  if v['state'] not in {'SATISFIED','FROZEN','COMPLETE'}: blockers.append(k+':'+v['state'])
 for k,v in m['exact_lineage_slots'].items():
  if v['state']!='SATISFIED': blockers.append('LINEAGE.'+k+':'+v['state'])
 for k,v in c.items():
  if isinstance(v,dict) and v.get('state')=='UNRESOLVED': blockers.append('CONTAMINATION_POLICY.'+k+':UNRESOLVED')
 return sorted(set(blockers))
def main():
 try:
  s=load('R9B0_READINESS_SCHEMA_V1.json'); m=load('R9B0_READINESS_MANIFEST_V1.json'); c=load('R9B0_READINESS_CHECKSUMS_V1.json'); checks(c); schema(s); b=manifest(m)
  print(json.dumps({'contract_package_status':'CONTRACT_PACKAGE_VALID','readiness_status':'NOT_READY' if b else 'RETRAIN_CANDIDATE_READY','blocker_count':len(b),'blockers':b,'training_execution_authorized':False,'model_promotion_authorized':False},sort_keys=True,separators=(',',':'))); return 0
 except Exception as e:
  print(json.dumps({'contract_package_status':'CONTRACT_PACKAGE_INVALID','readiness_status':'NOT_READY','error':str(e),'training_execution_authorized':False,'model_promotion_authorized':False},sort_keys=True,separators=(',',':'))); return 1
if __name__=='__main__': sys.exit(main())
