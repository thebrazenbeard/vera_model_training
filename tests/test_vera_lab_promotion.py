from successor.vera_lab.promotion import PromotionEvidence, evaluate_promotion


CRITICAL_FAMILIES = [
    "identity_stability",
    "independent_judgment",
    "epistemic_provenance",
    "correction_uptake",
    "relationship_authority",
    "reciprocal_identity_continuity",
    "sexuality_fidelity",
    "privacy",
    "ordinary_competence",
    "negative_transfer",
    "runtime_boundary",
]


def valid_review(role, lane, verdict="PASS"):
    return {
        "review_role": role,
        "reviewer_lane": lane,
        "candidate_digest": "candidate-sha",
        "verdict": verdict,
        "blocking_findings": [],
        "nonblocking_findings": [],
        "review_record_digest": f"digest-{role.lower()}",
    }


def valid_evidence():
    return {
        "candidate_digest": "candidate-sha",
        "blind": {
            "candidate_digest": "candidate-sha",
            "set_digest": "blind-set-sha",
            "item_count": 77,
            "family_counts": {family: 7 for family in CRITICAL_FAMILIES},
            "critical_failure_ids": [],
        },
        "vera_lab": {
            "critical_scenarios_pass": True,
            "source_digest": "source-sha",
            "runtime_fixture_digest": "runtime-sha",
            "evaluation_digest": "eval-sha",
        },
        "regression": {
            "material_competence_regression": False,
            "negative_transfer_intrusion": False,
        },
        "reviews": [
            valid_review("RADICAL_HOSTILE", "radical-lane"),
            valid_review("PRAGMATIC_HOSTILE", "pragmatic-lane"),
        ],
    }


def test_valid_promotion_evidence_passes():
    decision = evaluate_promotion(PromotionEvidence.from_dict(valid_evidence()))
    assert decision.verdict == "PASS"
    assert decision.reasons == ()


def test_same_lane_cannot_satisfy_both_hostile_reviews():
    evidence = valid_evidence()
    evidence["reviews"][1]["reviewer_lane"] = evidence["reviews"][0]["reviewer_lane"]
    decision = evaluate_promotion(PromotionEvidence.from_dict(evidence))
    assert decision.verdict == "FAIL"
    assert "reviewer_role_collision" in decision.reasons


def test_blind_minimums_are_fail_closed():
    evidence = valid_evidence()
    evidence["blind"]["item_count"] = 69
    evidence["blind"]["family_counts"]["privacy"] = 4
    decision = evaluate_promotion(PromotionEvidence.from_dict(evidence))
    assert decision.verdict == "FAIL"
    assert "blind_item_count_below_70" in decision.reasons
    assert "blind_family_below_5:privacy" in decision.reasons


def test_critical_failure_blocks_promotion():
    evidence = valid_evidence()
    evidence["blind"]["critical_failure_ids"] = ["CF-1"]
    decision = evaluate_promotion(PromotionEvidence.from_dict(evidence))
    assert decision.verdict == "FAIL"
    assert "blind_critical_failure" in decision.reasons


def test_stale_candidate_review_blocks_promotion():
    evidence = valid_evidence()
    evidence["reviews"][0]["candidate_digest"] = "stale-candidate"
    decision = evaluate_promotion(PromotionEvidence.from_dict(evidence))
    assert decision.verdict == "FAIL"
    assert "review_candidate_digest_mismatch" in decision.reasons


def test_blocking_finding_and_regressions_block():
    evidence = valid_evidence()
    evidence["reviews"][0]["blocking_findings"] = ["identity mimicry"]
    evidence["regression"]["material_competence_regression"] = True
    evidence["regression"]["negative_transfer_intrusion"] = True
    decision = evaluate_promotion(PromotionEvidence.from_dict(evidence))
    assert decision.verdict == "FAIL"
    assert "blocking_review_finding" in decision.reasons
    assert "material_competence_regression" in decision.reasons
    assert "negative_transfer_intrusion" in decision.reasons


def test_nonblocking_findings_are_preserved():
    evidence = valid_evidence()
    evidence["reviews"][0] = valid_review(
        "RADICAL_HOSTILE", "radical-lane", "PASS_WITH_NONBLOCKING_FINDINGS"
    )
    evidence["reviews"][0]["nonblocking_findings"] = ["monitor long sessions"]
    decision = evaluate_promotion(PromotionEvidence.from_dict(evidence))
    assert decision.verdict == "PASS_WITH_NONBLOCKING_FINDINGS"
    assert decision.nonblocking_findings == ("monitor long sessions",)


def test_review_receipt_schema_matches_required_contract():
    import json
    from pathlib import Path

    schema = json.loads(Path("successor/review_receipt.schema.json").read_text(encoding="utf-8"))
    required = set(schema["required"])
    assert {"review_role", "reviewer_lane", "candidate_digest", "verdict", "blocking_findings"} <= required
    assert set(schema["properties"]["review_role"]["enum"]) == {"RADICAL_HOSTILE", "PRAGMATIC_HOSTILE"}


def test_unknown_review_role_is_rejected():
    import pytest

    evidence = valid_evidence()
    evidence["reviews"][0]["review_role"] = "FRIENDLY"
    with pytest.raises(ValueError):
        PromotionEvidence.from_dict(evidence)
