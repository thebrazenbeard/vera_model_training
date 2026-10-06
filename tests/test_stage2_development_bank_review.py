import importlib
import importlib.util


def _case(case_id, generator="Lane-A-generator"):
    return {
        "case_id": case_id,
        "generator_actor_id": generator,
        "prompt": f"prompt {case_id}",
        "grading": {"must_assert": ["x"]},
    }


def test_dev_bank_review_requires_independent_case_review_two_graders_and_adjudicator():
    spec = importlib.util.find_spec("training.stage2_development_bank_review")
    assert spec is not None, "development bank review module is missing"
    rev = importlib.import_module("training.stage2_development_bank_review")
    cases = [_case("c1"), _case("c2")]
    reviews = []
    for case in cases:
        reviews.append({
            "case_id": case["case_id"],
            "reviewer_id": "external-reviewer",
            "independent_from_generation": True,
            "semantic_ancestry_reviewed": True,
            "subject_digest": rev.review_subject_digest(case),
            "verdict": "ADMIT",
        })
    report = rev.build_development_bank_review_report(
        cases,
        case_reviews=reviews,
        grader_ids=["grader-a", "grader-b"],
        adjudicator_id="adjudicator-c",
    )
    assert report["status"] == "INDEPENDENTLY_REVIEWED"
    assert report["missing_case_reviews"] == []


def test_dev_bank_review_holds_on_missing_or_self_review():
    rev = importlib.import_module("training.stage2_development_bank_review")
    cases = [_case("c1"), _case("c2")]
    reviews = [{
        "case_id": "c1",
        "reviewer_id": "Lane-A-generator",
        "independent_from_generation": False,
        "semantic_ancestry_reviewed": True,
        "subject_digest": rev.review_subject_digest(cases[0]),
        "verdict": "ADMIT",
    }]
    report = rev.build_development_bank_review_report(
        cases,
        case_reviews=reviews,
        grader_ids=["grader-a"],
        adjudicator_id=None,
    )
    assert report["status"] == "HOLD"
    assert "independent_case_review_incomplete" in report["reasons"]
    assert "two_graders_required" in report["reasons"]
    assert "adjudicator_required" in report["reasons"]
