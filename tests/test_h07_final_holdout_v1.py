import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TRAIN = ROOT / "successor" / "qwen35" / "corpus" / "h07_rule_transfer_v2_train_sft.jsonl"
DEV = ROOT / "successor" / "qwen35" / "qualification" / "h07_rule_transfer_v2_dev.jsonl"
FINAL = ROOT / "successor" / "qwen35" / "qualification" / "h07_final_holdout_v1.jsonl"

EXPECTED_FAMILIES = {
    "api_gateway_route",
    "cdn_edge_rule",
    "cache_cluster_setting",
    "message_broker_policy",
    "certificate_deployment",
    "observability_alert_route",
}
EXPECTED_CASE_TYPES = {
    "generic_success",
    "async_accept",
    "downstream_claim",
    "authoritative_receipt",
    "ambiguous_effect",
}


def rows(path):
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]


def test_final_holdout_is_family_disjoint_and_balanced():
    train = rows(TRAIN)
    dev = rows(DEV)
    final = rows(FINAL)

    seen = {r["family"] for r in train + dev}
    final_families = {r["family"] for r in final}

    assert len(final) == 30
    assert final_families == EXPECTED_FAMILIES
    assert not (seen & final_families)

    for family in EXPECTED_FAMILIES:
        fam = [r for r in final if r["family"] == family]
        assert len(fam) == 5
        assert {r["case_type"] for r in fam} == EXPECTED_CASE_TYPES


def test_final_holdout_has_semantic_rubrics_and_unique_prompts():
    final = rows(FINAL)
    prompts = [r["prompt"] for r in final]
    assert len(prompts) == len(set(prompts))
    for row in final:
        rubric = row["rubric"]
        assert row["expected_action"] in {
            "VERIFY_POST_STATE",
            "RECEIPT_SUFFICIENT",
            "RECONCILE_BEFORE_RETRY",
        }
        assert rubric["expected_claim_scope"]
        assert len(rubric["required_concepts"]) >= 2
        assert rubric["forbidden_claims"]
