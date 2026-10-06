import importlib
import importlib.util


def test_stage2_baseline_manifest_is_deterministic_and_weight_frozen():
    spec = importlib.util.find_spec("training.stage2_baseline_manifest")
    assert spec is not None, "Stage-2 baseline manifest module is missing"
    s2 = importlib.import_module("training.stage2_baseline_manifest")
    cases = [
        {
            "case_id": "case-001",
            "bank": "truth_over_agreement",
            "prompt_hash": "a" * 64,
            "grading_hash": "b" * 64,
            "custody": "protected-final",
        },
        {
            "case_id": "case-002",
            "bank": "correction_proposition_fidelity",
            "prompt_hash": "c" * 64,
            "grading_hash": "d" * 64,
            "custody": "protected-final",
        },
    ]
    one = s2.build_stage2_baseline_manifest(
        cases,
        source_head="1" * 40,
        training_manifest_sha256="2" * 64,
        runtime_binding_sha256="3" * 64,
        decoding_mode="deterministic",
        seed=1729,
    )
    two = s2.build_stage2_baseline_manifest(
        list(reversed(cases)),
        source_head="1" * 40,
        training_manifest_sha256="2" * 64,
        runtime_binding_sha256="3" * 64,
        decoding_mode="deterministic",
        seed=1729,
    )
    assert one["status"] == "PASS"
    assert one["manifest_sha256"] == two["manifest_sha256"]
    assert one["weight_change_performed"] is False
    assert one["case_count"] == 2
