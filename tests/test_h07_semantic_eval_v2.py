import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "successor" / "qwen35" / "qualification" / "evaluate_h07_rule_transfer_v2.py"


def load_module():
    spec = importlib.util.spec_from_file_location("h07_eval_v2", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_judge_packet_preserves_case_and_uses_semantic_rubric():
    module = load_module()
    row = {
        "record_id": "h07-v2-dev-001",
        "family": "scheduler",
        "verification_class": "readback_required",
        "expected_action": "VERIFY_POST_STATE",
        "prompt": "Case prompt",
        "reference_answer": "Reference",
        "rubric": {
            "expected_claim_scope": "request_or_execution_state_only",
            "required_concepts": ["concept one", "concept two"],
            "forbidden_claims": ["bad claim"],
        },
    }
    packet = module.build_judge_packet(row, "Generated answer")
    assert packet["record_id"] == row["record_id"]
    assert packet["candidate_response"] == "Generated answer"
    assert packet["expected_action"] == "VERIFY_POST_STATE"
    assert packet["expected_claim_scope"] == "request_or_execution_state_only"
    assert packet["required_concepts"] == ["concept one", "concept two"]
    assert packet["forbidden_claims"] == ["bad claim"]
    assert "semantically" in packet["judge_instruction"].lower()
    assert "keyword" in packet["judge_instruction"].lower()


def test_validate_judgment_requires_all_required_concepts_and_no_forbidden_claims():
    module = load_module()
    packet = {
        "record_id": "x",
        "expected_action": "VERIFY_POST_STATE",
        "required_concepts": ["a", "b"],
        "forbidden_claims": ["bad"],
    }
    good = {
        "record_id": "x",
        "action": "VERIFY_POST_STATE",
        "claim_scope_ok": True,
        "required_concepts": {"a": True, "b": True},
        "forbidden_claims": {"bad": False},
    }
    bad = dict(good)
    bad["required_concepts"] = {"a": True, "b": False}

    assert module.validate_judgment(packet, good)["pass"] is True
    assert module.validate_judgment(packet, bad)["pass"] is False


def test_aggregate_judgments_reports_accuracy_and_family_results():
    module = load_module()
    cases = [
        {"record_id": "a", "family": "scheduler", "pass": True},
        {"record_id": "b", "family": "scheduler", "pass": False},
        {"record_id": "c", "family": "secret_rotation", "pass": True},
    ]
    result = module.aggregate_judgments(cases)
    assert result["n"] == 3
    assert result["passed"] == 2
    assert result["accuracy"] == 2 / 3
    assert result["by_family"]["scheduler"]["accuracy"] == 0.5
    assert result["by_family"]["secret_rotation"]["accuracy"] == 1.0


def test_build_result_preserves_judge_status():
    module = load_module()
    result = module.build_result(
        [{"record_id": "x", "family": "scheduler", "pass": True}],
        judge_status="INTERNAL_HOST_MODEL_REVIEW",
    )
    assert result["judge_status"] == "INTERNAL_HOST_MODEL_REVIEW"
    assert result["result"]["accuracy"] == 1.0



def test_build_result_preserves_judge_status():
    module = load_module()
    result = module.build_result(
        [{"record_id": "x", "family": "scheduler", "pass": True}],
        judge_status="INTERNAL_HOST_MODEL_REVIEW",
    )
    assert result["judge_status"] == "INTERNAL_HOST_MODEL_REVIEW"
    assert result["result"]["accuracy"] == 1.0



def test_build_result_preserves_judge_status():
    module = load_module()
    result = module.build_result(
        [{"record_id": "x", "family": "scheduler", "pass": True}],
        judge_status="INTERNAL_HOST_MODEL_REVIEW",
    )
    assert result["judge_status"] == "INTERNAL_HOST_MODEL_REVIEW"
    assert result["result"]["accuracy"] == 1.0
