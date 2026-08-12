import bootcamp
import fast_bootcamp
import quality_gate


def _cap():
    return bootcamp.Capability("rls", "RLS", "Model-proposed implementation scope", True, score=4, observations=3)


def test_transfer_correction_prevents_package_readiness():
    spec = {"identity": "SB", "function": "Supabase Platform Specialist", "target": "practitioner", "rounds": 2}
    audit = [
        {"round": 1, "exam": {"score": 4, "passed": True, "critical_failure": False, "corrections": []}},
        {"round": 2, "exam": {"score": 4, "passed": True, "critical_failure": False, "corrections": []}},
    ]
    transfers = [
        {"transfer": 1, "task": {"adversarial": False}, "exam": {"score": 3, "passed": True, "critical_failure": False, "corrections": ["material correction"]}},
        {"transfer": 2, "task": {"adversarial": True}, "exam": {"score": 4, "passed": True, "critical_failure": False, "corrections": []}},
    ]
    qual = quality_gate.conservative_qualification(spec, [_cap()], audit, transfers, [])
    assert qual["training_package_ready"] is False
    assert qual["outcome"] == "FAIL"
    assert qual["transfer_clean"] is False


def test_transfer_profile_requires_one_clean_normal_and_one_adversarial_exam():
    spec = {"identity": "SB", "function": "Supabase Platform Specialist", "target": "practitioner", "rounds": 2}
    audit = [
        {"round": 1, "exam": {"score": 4, "passed": True, "critical_failure": False, "corrections": []}},
        {"round": 2, "exam": {"score": 4, "passed": True, "critical_failure": False, "corrections": []}},
    ]
    transfers = [
        {"transfer": 1, "task": {"adversarial": True}, "exam": {"score": 4, "passed": True, "critical_failure": False, "corrections": []}},
        {"transfer": 2, "task": {"adversarial": True}, "exam": {"score": 4, "passed": True, "critical_failure": False, "corrections": []}},
    ]
    qual = quality_gate.conservative_qualification(spec, [_cap()], audit, transfers, [])
    assert qual["training_package_ready"] is False
    assert qual["transfer_profile_ready"] is False


def test_capsule_labels_model_generated_capability_scope_unverified():
    spec = {"identity": "SB", "function": "Supabase Platform Specialist", "target": "practitioner"}
    qual = {
        "source_evidence": [{"url": "https://example.test/source", "status": "ok"}],
        "capability_proxy_evidence": [{
            "id": "rls",
            "name": "RLS",
            "description": "Can implement and manage every authorization scenario",
            "evidence_url": "https://example.test/source",
            "evidence_quote": "Row Level Security restricts which rows can be accessed.",
            "proxy_score": 4,
            "proxy_observations": 3,
            "proxy_status": "PROXY_EVIDENCED",
            "critical": True,
        }],
    }
    capsule = quality_gate.build_capsule(spec, "", [], [], qual)
    assert "MODEL-PROPOSED SCOPE (UNVERIFIED)" in capsule
    assert "Can implement and manage every authorization scenario" in capsule
    assert "Source anchor" in capsule


def test_transfer_one_is_forced_non_adversarial_even_if_model_marks_it_adversarial(monkeypatch):
    caps = [
        bootcamp.Capability("rls", "RLS", "Row security", True),
        bootcamp.Capability("auth", "Auth", "Authentication", True),
    ]
    answers = iter([
        {"rounds": [{"task": "normal transfer", "capability_ids": ["rls", "auth"], "hidden_rubric": ["check"], "adversarial": True, "critical": True}]},
        {"rounds": [{"task": "adversarial transfer", "capability_ids": ["rls", "auth"], "hidden_rubric": ["check"], "adversarial": False, "critical": True}]},
    ])
    monkeypatch.setattr(bootcamp, "json_llm", lambda *a, **k: next(answers))
    tasks = fast_bootcamp.robust_build_transfer_tasks({"function": "Supabase Platform Specialist"}, caps, [])
    assert tasks[0]["adversarial"] is False
    assert tasks[1]["adversarial"] is True


def test_grounded_runtime_prompts_explicitly_forbid_unsupported_implementation_syntax():
    assert "do not invent" in fast_bootcamp.GROUNDED_STUDENT_SYSTEM.lower()
    assert "implementation syntax" in fast_bootcamp.GROUNDED_STUDENT_SYSTEM.lower()
    assert "unsupported concrete" in fast_bootcamp.GROUNDED_EXAMINER_SYSTEM.lower()
    assert "score" in fast_bootcamp.GROUNDED_EXAMINER_SYSTEM.lower()
