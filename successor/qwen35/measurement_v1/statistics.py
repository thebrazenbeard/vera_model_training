"""Paired test statistics with family-cluster bootstrap; exploratory, not an independence guarantee."""
from __future__ import annotations
import math
import random
from collections import defaultdict

VALID = {"PASS","FAIL","CRITICAL_FAIL"}

def exact_mcnemar_p(base_only, candidate_only):
    n=base_only+candidate_only
    if n==0:
        return 1.0
    k=min(base_only,candidate_only)
    ln2=math.log(2)
    logs=[math.lgamma(n+1)-math.lgamma(i+1)-math.lgamma(n-i+1)-n*ln2 for i in range(k+1)]
    peak=max(logs)
    tail=math.exp(peak)*sum(math.exp(x-peak) for x in logs)
    return min(1.0,2*tail)

def _percentile(sorted_values,frac):
    if not sorted_values:
        return None
    i=(len(sorted_values)-1)*frac
    l=int(math.floor(i))
    h=int(math.ceil(i))
    return sorted_values[l]*(h-i)+sorted_values[h]*(i-l) if l!=h else sorted_values[l]

def _stats(rows,seed,replicates):
    n=len(rows)
    counts={"both_pass":0,"base_only":0,"candidate_only":0,"neither":0}
    groups=defaultdict(lambda: [0,0])
    critical=0
    for r in rows:
        b=r["base"]["status"]=="PASS"
        a=r["candidate"]["status"]=="PASS"
        critical += r["candidate"]["status"]=="CRITICAL_FAIL"
        key=("both_pass" if b and a else "base_only" if b else "candidate_only" if a else "neither")
        counts[key]+=1
        family=r["family_id"]
        groups[family][0]+=1
        groups[family][1]+=int(a)-int(b)
    delta=(counts["candidate_only"]-counts["base_only"])/n
    ndisc=counts["base_only"]+counts["candidate_only"]
    # Matched-pair multinomial delta variance, not difference of independent binomials.
    variance=max(0,ndisc/n**2 - (counts["candidate_only"]-counts["base_only"])**2/n**3)
    half=1.959963984540054*math.sqrt(variance)
    ci=[max(-1,delta-half),min(1,delta+half)]
    families=sorted(groups)
    bootstrap=None
    if len(families)>=30 and replicates>=100:
        agg=[groups[f] for f in families]
        m=len(agg)
        rng=random.Random(seed)
        values=[]
        for _ in range(replicates):
            d=0; size=0
            for _ in range(m):
                n0,d0=agg[rng.randrange(m)]
                d+=d0;size+=n0
            values.append(d/size)
        values.sort()
        bootstrap=[_percentile(values,.025),_percentile(values,.975)]
    return {"n":n,"counts":counts,"accuracy_base":(counts["both_pass"]+counts["base_only"])/n,
            "accuracy_candidate":(counts["both_pass"]+counts["candidate_only"])/n,
            "delta":delta,"mcnemar_exact_p":exact_mcnemar_p(counts["base_only"],counts["candidate_only"]),
            "paired_normal_ci95":ci,"cluster_bootstrap_ci95":bootstrap,
            "independent_families_observed":len(families),"critical_candidate":critical,
            "interpretation":"INSUFFICIENT_INDEPENDENT_FAMILIES" if bootstrap is None else "PAIRED_ESTIMATE_WITH_UNVERIFIED_CLUSTER_ASSUMPTIONS"}

def paired_statistics(rows,*,seed=20260930,replicates=1000):
    if not isinstance(rows,list) or not rows:
        raise ValueError("nonempty list of paired observation results required")
    ids=set();by_lane=defaultdict(list);by_dim=defaultdict(list)
    for r in rows:
        caseid=r.get("case_id")
        if not isinstance(caseid,str) or not caseid:
            raise ValueError("case ID missing")
        if caseid in ids:
            raise ValueError("duplicate case_id in paired results")
        ids.add(caseid)
        if not r.get("family_id"):
            raise ValueError("family_id missing")
        for condition in ("base","candidate"):
            if not isinstance(r.get(condition),dict):
                raise ValueError("missing "+condition+" judgment")
            status=r[condition].get("status")
            if status=="UNREVIEWED":
                raise ValueError("UNREVIEWED result cannot be statistically scored")
            if status not in VALID:
                raise ValueError("invalid judgment: "+str(status))
        lane=r.get("lane")
        if lane not in ("behavioral","retention","adversarial","runtime_effect"):
            raise ValueError("invalid lane")
        by_lane[lane].append(r)
        if lane=="behavioral":
            if r.get("dimension") is None:
                raise ValueError("missing behavioral dimension")
            by_dim[r["dimension"]].append(r)
    return {"schema":"QWEN35_PAIRED_STATISTICS_V1","n":len(rows),"seed":seed,"replicates":replicates,
            "lanes":{lane:_stats(part,seed,replicates) for lane,part in sorted(by_lane.items())},
            "dimensions":{dim:_stats(part,seed,replicates) for dim,part in sorted(by_dim.items())},
            "claim_ceiling":"PAIRED_METRICS_ONLY_NOT_QUALIFICATION"}
