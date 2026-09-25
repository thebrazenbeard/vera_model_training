import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "successor" / "qwen35" / "qualification" / "score_h07_independent_review_v1.py"


def load_module():
    spec = importlib.util.spec_from_file_location("h07_independent_score", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_unblind_and_aggregate_by_condition():
    module = load_module()
    packets = {
        "r1": {
            "review_id": "r1",
            "record_id": "c1",
            "family": "fam",
            "expected_action": "VERIFY_POST_STATE",
            "required_concepts": ["a"],
            "forbidden_claims": ["bad"],
        },
        "r2": {
            "review_id": "r2",
            "record_id": "c1",
            "family": "fam",
            "expected_action": "VERIFY_POST_STATE",
            "required_concepts": ["a"],
            "forbidden_claims": ["bad"],
        },
    }
    mapping = {
        "r1": {"review_id": "r1", "record_id": "c1", "condition": "base"},
        "r2": {"review_id": "r2", "record_id": "c1", "condition": "trained"},
    }
    judgments = [
        {
            "review_id": "r1",
            "action": "VERIFY_POST_STATE",
            "claim_scope_ok": True,
            "required_concepts": {"a": True},
            "forbidden_claims": {"bad": False},
        },
        {
            "review_id": "r2",
            "action": "OTHER",
            "claim_scope_ok": False,
            "required_concepts": {"a": False},
            "forbidden_claims": {"bad": False},
        },
    ]
    result = module.score_review(packets, mapping, judgments)
    assert result["conditions"]["base"]["accuracy"] == 1.0
    assert result["conditions"]["trained"]["accuracy"] == 0.0
    assert result["cases"][0]["condition"] in {"base", "trained"}


def test_score_rejects_missing_or_duplicate_reviews():
    module = load_module()
    packets = {
        "r1": {
            "review_id": "r1",
            "record_id": "c1",
            "family": "fam",
            "expected_action": "VERIFY_POST_STATE",
            "required_concepts": ["a"],
            "forbidden_claims": ["bad"],
        }
    }
    mapping = {"r1": {"review_id": "r1", "record_id": "c1", "condition": "base"}}
    try:
        module.score_review(packets, mapping, [])
    except ValueError as exc:
        assert "review ids" in str(exc)
    else:
        raise AssertionError("missing review must fail")

    duplicate = [
        {
            "review_id": "r1",
            "action": "VERIFY_POST_STATE",
            "claim_scope_ok": True,
            "required_concepts": {"a": True},
            "forbidden_claims": {"bad": False},
        },
        {
            "review_id": "r1",
            "action": "VERIFY_POST_STATE",
            "claim_scope_ok": True,
            "required_concepts": {"a": True},
            "forbidden_claims": {"bad": False},
        },
    ]
    try:
        module.score_review(packets, mapping, duplicate)
    except ValueError as exc:
        assert "duplicate" in str(exc)
    else:
        raise AssertionError("duplicate review must fail")
