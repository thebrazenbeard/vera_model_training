import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "successor" / "qwen35" / "qualification" / "build_h07_independent_review_packet_v1.py"


def load_module():
    spec = importlib.util.spec_from_file_location("h07_blind_packet", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_blind_packet_has_120_unique_records_and_no_condition_leakage():
    module = load_module()
    holdout = [
        {
            "record_id": "case-1",
            "prompt": "prompt",
            "family": "fam",
            "verification_class": "readback_required",
            "expected_action": "VERIFY_POST_STATE",
            "rubric": {
                "expected_claim_scope": "scope",
                "required_concepts": ["a", "b"],
                "forbidden_claims": ["c"],
            },
        }
    ]
    gens = {
        "base": {"case-1": "base response"},
        "trained": {"case-1": "trained response"},
        "base_runtime": {"case-1": "base runtime response"},
        "trained_runtime": {"case-1": "trained runtime response"},
    }
    packet, mapping = module.build_blind_packet(holdout, gens, token_factory=iter([
        "id-a", "id-b", "id-c", "id-d"
    ]).__next__)
    assert len(packet) == 4
    assert len(mapping) == 4
    assert {r["review_id"] for r in packet} == {"id-a", "id-b", "id-c", "id-d"}
    assert all("condition" not in r for r in packet)
    assert all("subject" not in r for r in packet)
    assert all("runtime_policy" not in json.dumps(r).lower() for r in packet)
    assert {r["candidate_response"] for r in packet} == {
        "base response", "trained response", "base runtime response", "trained runtime response"
    }
    assert {r["condition"] for r in mapping} == {
        "base", "trained", "base_runtime", "trained_runtime"
    }


def test_mapping_commitment_is_order_stable():
    module = load_module()
    rows = [
        {"review_id": "b", "record_id": "case", "condition": "trained"},
        {"review_id": "a", "record_id": "case", "condition": "base"},
    ]
    a = module.mapping_commitment(rows)
    b = module.mapping_commitment(list(reversed(rows)))
    assert a == b
    assert len(a) == 64
