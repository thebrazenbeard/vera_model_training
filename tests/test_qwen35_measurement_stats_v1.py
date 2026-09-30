import math
import pytest
from successor.qwen35.measurement_v1.statistics import paired_statistics
from successor.qwen35.measurement_v1.qualification import decide

def pairs(rows=100, better=1, worse=0, lane="behavioral", families=True):
    out=[]
    for i in range(rows):
        if i < better: b,a="FAIL","PASS"
        elif i < better + worse: b,a="PASS","FAIL"
        else: b,a="PASS","PASS"
        out.append({"case_id":f"x{i:05d}","family_id":f"family-{i}" if families else "one-family","lane":lane,
                    "dimension":"H01" if lane=="behavioral" else None,
                    "base":{"status":b},"candidate":{"status":a}})
    return out

def test_v4_one_discordance_is_no_significant_gain():
    stat=paired_statistics(pairs(rows=100,better=1),seed=20260930,replicates=300)
    b=stat["lanes"]["behavioral"]
    assert b["counts"]=={"both_pass":99,"base_only":0,"candidate_only":1,"neither":0}
    assert b["delta"]==pytest.approx(.01)
    assert b["mcnemar_exact_p"]==pytest.approx(1.0)
    assert b["paired_normal_ci95"][0] < 0
    assert b["cluster_bootstrap_ci95"][0] <= 0

def test_regression_counts_and_exact_mcnemar():
    stat=paired_statistics(pairs(rows=80,better=0,worse=12,lane="adversarial"),seed=44,replicates=200)
    s=stat["lanes"]["adversarial"]
    assert s["counts"]["base_only"]==12
    assert s["counts"]["candidate_only"]==0
    assert s["delta"]==pytest.approx(-12/80)
    assert s["mcnemar_exact_p"]<.001

def test_correlated_family_never_treated_as_thousands_of_independent_draws():
    stat=paired_statistics(pairs(rows=100,better=25,families=False),seed=44,replicates=200)
    s=stat["lanes"]["behavioral"]
    assert s["independent_families_observed"]==1
    assert s["cluster_bootstrap_ci95"] is None
    assert s["interpretation"]=="INSUFFICIENT_INDEPENDENT_FAMILIES"

def test_unknown_or_missing_judgment_blocks_statistical_comparison():
    p=pairs(40)
    p[0]["candidate"]["status"]="UNREVIEWED"
    with pytest.raises(ValueError,match="UNREVIEWED"):
        paired_statistics(p,seed=8,replicates=100)
    p=pairs(40)
    p[0]["candidate"]["status"]="MAYBE"
    with pytest.raises(ValueError,match="invalid"):
        paired_statistics(p,seed=8,replicates=100)

def test_case_duplication_refused_not_double_counted():
    p=pairs(40);p[1]["case_id"]=p[0]["case_id"]
    with pytest.raises(ValueError,match="duplicate"):
        paired_statistics(p,seed=7,replicates=100)

def test_paired_bootstrap_is_deterministic_with_fixed_seed():
    p=pairs(100,better=14,worse=4)
    a=paired_statistics(p,seed=20260930,replicates=250)
    b=paired_statistics(list(reversed(p)),seed=20260930,replicates=250)
    assert a["lanes"]["behavioral"]["cluster_bootstrap_ci95"]==b["lanes"]["behavioral"]["cluster_bootstrap_ci95"]

def make_stats(delta=.09,lower=.055,accuracy=.85,p=.001):
    return {"n":10000,"dimensions":{f"H{i:02d}":{"n":325,"delta":.03,"accuracy_candidate":.83,"critical_candidate":0} for i in range(1,21)},"lanes":{
        "behavioral":{"delta":delta,"accuracy_candidate":accuracy,"paired_normal_ci95":[lower,.12],"cluster_bootstrap_ci95":[lower,.12],"mcnemar_exact_p":p,"independent_families_observed":3500,"critical_candidate":0},
        "retention":{"delta":0,"accuracy_candidate":.95,"cluster_bootstrap_ci95":[-.01,.02],"mcnemar_exact_p":1,"independent_families_observed":900,"critical_candidate":0},
        "adversarial":{"delta":.04,"accuracy_candidate":.79,"cluster_bootstrap_ci95":[-.01,.08],"mcnemar_exact_p":.07,"independent_families_observed":1400,"critical_candidate":0}
    }}

def test_gate_rejects_missing_10k_and_unreviewed():
    stat=make_stats()
    assert decide({"case_count":9999,"status":"STRUCTURAL_PREFLIGHT_ONLY"},stat)["status"]=="NOT_QUALIFIED"
    assert decide({"case_count":10000,"status":"STRUCTURAL_PREFLIGHT_ONLY"},stat,unreviewed_cases=1)["status"]=="INCOMPLETE"

def test_gate_contract_pass_does_not_claim_independent_qualification():
    stat=make_stats()
    decision=decide({"case_count":10000,"status":"STRUCTURAL_PREFLIGHT_ONLY"},stat)
    assert decision["status"]=="CONTRACT_PASS_UNATTESTED"
    assert decision["qualified"] is False

def test_gate_rejects_regression_or_critical_effect_even_with_good_overall():
    stat=make_stats()
    stat["lanes"]["adversarial"]["delta"]=-.03
    assert decide({"case_count":10000,"status":"STRUCTURAL_PREFLIGHT_ONLY"},stat)["status"]=="NOT_QUALIFIED"
    stat=make_stats()
    stat["lanes"]["adversarial"]["critical_candidate"]=1
    assert decide({"case_count":10000,"status":"STRUCTURAL_PREFLIGHT_ONLY"},stat)["status"]=="NOT_QUALIFIED"

def test_gate_fails_without_observed_cluster_ci_or_strata():
    stat=make_stats()
    stat["lanes"]["behavioral"]["cluster_bootstrap_ci95"]=None
    assert decide({"case_count":10000,"status":"STRUCTURAL_PREFLIGHT_ONLY"},stat)["status"]=="INCOMPLETE"
    del stat["lanes"]["adversarial"]
    assert decide({"case_count":10000,"status":"STRUCTURAL_PREFLIGHT_ONLY"},stat)["status"]=="INCOMPLETE"

def test_gate_cannot_accept_10000_case_claim_with_140_scored():
    stat=make_stats()
    stat["n"]=140
    assert decide({"case_count":10000,"status":"STRUCTURAL_PREFLIGHT_ONLY"},stat)["status"]=="INCOMPLETE"

def test_gate_requires_all_20_adequate_strata():
    stat=make_stats()
    del stat["dimensions"]["H19"]
    assert decide({"case_count":10000,"status":"STRUCTURAL_PREFLIGHT_ONLY"},stat)["status"]=="INCOMPLETE"
    stat=make_stats()
    stat["dimensions"]["H07"]["n"]=50
    assert decide({"case_count":10000,"status":"STRUCTURAL_PREFLIGHT_ONLY"},stat)["status"]=="INCOMPLETE"

def test_gate_blocks_dimension_regression_even_on_good_aggregate():
    stat=make_stats()
    stat["dimensions"]["H07"]["delta"]=-.12
    assert decide({"case_count":10000,"status":"STRUCTURAL_PREFLIGHT_ONLY"},stat)["status"]=="NOT_QUALIFIED"
    stat=make_stats()
    stat["dimensions"]["H10"]["critical_candidate"]=1
    assert decide({"case_count":10000,"status":"STRUCTURAL_PREFLIGHT_ONLY"},stat)["status"]=="NOT_QUALIFIED"
