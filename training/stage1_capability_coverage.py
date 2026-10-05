from __future__ import annotations
from collections import Counter

REQUIRED_CAPABILITY_FAMILIES = (
    "identity_stability",
    "instruction_following",
    "correction_uptake",
    "epistemic_provenance_currentness",
    "uncertainty_conflict_handling",
    "privacy_boundary_behavior",
    "relationship_authority_semantics",
    "reciprocal_identity_continuity",
    "tool_action_semantics",
    "reasoning_decomposition",
    "memory_retention",
    "novel_rule_adaptation",
    "negative_transfer_resistance",
)

def build_coverage_report(records: list[dict]) -> dict:
    counts=Counter()
    template_count=0
    twin_count=0
    unknown=[]
    for row in records:
        family=row.get("capability_family")
        if family in REQUIRED_CAPABILITY_FAMILIES:
            counts[family]+=1
        elif family is not None:
            unknown.append(family)
        if row.get("semantic_template_ancestry"):
            template_count+=1
        if row.get("counterfactual_twin_group"):
            twin_count+=1
    family_counts={family:counts.get(family,0) for family in REQUIRED_CAPABILITY_FAMILIES}
    missing=[family for family,count in family_counts.items() if count==0]
    return {
        "schema":"STAGE1_CAPABILITY_COVERAGE_REPORT_V1",
        "status":"PASS" if not missing and not unknown else "HOLD",
        "record_count":len(records),
        "family_counts":family_counts,
        "missing_families":missing,
        "unknown_families":sorted(set(unknown)),
        "records_with_template_ancestry":template_count,
        "records_with_counterfactual_twin_group":twin_count,
    }
