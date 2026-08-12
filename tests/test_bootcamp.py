import bootcamp
import fast_bootcamp
import quality_gate


def test_select_source_segments_is_bounded_and_samples_full_document():
    text = "A" * 5000 + "MIDDLE_MARKER" + "B" * 5000 + "END_MARKER"
    packed = bootcamp.select_source_segments(text, 3000)
    assert len(packed) <= 3100
    assert packed.startswith("A")
    assert "MIDDLE_MARKER" in packed
    assert "END_MARKER" in packed


def test_select_source_segments_returns_short_source_unchanged():
    text = "short source"
    assert bootcamp.select_source_segments(text, 3000) == text


def test_validate_curriculum_accepts_exact_round_count_and_known_capabilities():
    caps = [
        bootcamp.Capability("rls", "RLS", "Row level security", True),
        bootcamp.Capability("queues", "Queues", "Durable queues", False),
    ]
    raw = {
        "rounds": [
            {
                "task": f"task {i}",
                "capability_ids": ["rls" if i % 2 else "queues"],
                "hidden_rubric": ["one check"],
                "adversarial": i % 3 == 0,
                "critical": i % 2 == 1,
            }
            for i in range(1, 7)
        ]
    }
    out = bootcamp.validate_curriculum(raw, 6, caps)
    assert len(out) == 6
    assert out[0]["task"] == "task 1"


def test_validate_curriculum_rejects_unknown_capability():
    caps = [bootcamp.Capability("rls", "RLS", "Row level security", True)]
    raw = {
        "rounds": [
            {
                "task": f"task {i}",
                "capability_ids": ["not_real"],
                "hidden_rubric": ["check"],
                "adversarial": False,
                "critical": False,
            }
            for i in range(6)
        ]
    }
    try:
        bootcamp.validate_curriculum(raw, 6, caps)
    except ValueError as exc:
        assert "unknown capability" in str(exc)
    else:
        raise AssertionError("unknown capability should be rejected")


def test_safe_source_url_rejects_loopback_and_non_https():
    assert not bootcamp.safe_source_url("http://example.com")
    assert not bootcamp.safe_source_url("https://127.0.0.1/private")
    assert not bootcamp.safe_source_url("https://localhost/private")
    assert bootcamp.safe_source_url("https://supabase.com/docs")


def test_transfer_exams_are_generated_independently(monkeypatch):
    caps = [
        bootcamp.Capability("rls", "RLS", "Row level security", True),
        bootcamp.Capability("queues", "Queues", "Durable queues", False),
    ]
    calls = []

    def fake_json_llm(system, user, max_tokens, temperature=0.1):
        calls.append(user)
        n = len(calls)
        return {
            "rounds": [{
                "task": f"novel transfer {n}",
                "capability_ids": ["rls", "queues"],
                "hidden_rubric": ["check both capabilities"],
                "adversarial": n == 2,
                "critical": True,
            }]
        }

    monkeypatch.setattr(bootcamp, "json_llm", fake_json_llm)
    tasks = fast_bootcamp.robust_build_transfer_tasks(
        {"function": "Supabase Platform Specialist"}, caps, [{"task": "old task"}]
    )
    assert len(tasks) == 2
    assert len(calls) == 2
    assert tasks[0]["task"] != tasks[1]["task"]


def test_single_observation_capability_is_provisional():
    assert quality_gate.capability_status({"score": 4, "observations": 1}) == "PROVISIONAL_SINGLE_OBSERVATION"
    assert quality_gate.capability_status({"score": 4, "observations": 2}) == "PROXY_EVIDENCED"


def test_capsule_never_promotes_practitioner_to_expert_and_preserves_actual_sources():
    spec = {"identity": "SB", "function": "Supabase Platform Specialist", "target": "practitioner"}
    qual = {
        "source_evidence": [{"url": "https://supabase.com/docs/guides/queues", "status": "ok"}],
        "capability_proxy_evidence": [{
            "id": "queues", "name": "Queues", "proxy_score": 4,
            "proxy_observations": 1, "proxy_status": "PROVISIONAL_SINGLE_OBSERVATION", "critical": True,
        }],
    }
    capsule = quality_gate.build_capsule(spec, "Queues are Postgres-native.", [], [], qual)
    assert "Expert" not in capsule
    assert "expert status" in capsule
    assert "https://supabase.com/docs/guides/queues" in capsule
    assert "PROVISIONAL_SINGLE_OBSERVATION" in capsule
    assert "does not establish exhaustive coverage" in capsule
    assert "Native identity qualification has NOT been run" in capsule


def test_external_proxy_can_only_make_package_ready_not_native_identity_pass():
    spec = {"identity": "SB", "function": "Supabase Platform Specialist", "target": "practitioner", "rounds": 2}
    cap = bootcamp.Capability("rls", "RLS", "Row security", True, score=4, observations=2)
    audit = [
        {"round": 1, "exam": {"critical_failure": False}},
        {"round": 2, "exam": {"critical_failure": False}},
    ]
    transfers = [
        {"transfer": 1, "exam": {"score": 4, "critical_failure": False}},
        {"transfer": 2, "exam": {"score": 4, "critical_failure": False}},
    ]
    qual = quality_gate.conservative_qualification(spec, [cap], audit, transfers, [])
    assert qual["training_package_ready"] is True
    assert qual["native_identity_qualification"] == "NOT_RUN"
    assert "external_bootcamp_pass" not in qual
    assert qual["outcome"] == "CONDITIONAL PASS"


def test_capability_support_filter_rejects_topics_absent_from_source_pack():
    source_pack = "Postgres database. Row Level Security policies. Authentication with JWT. Durable queues."
    supported = bootcamp.Capability("rls", "Row Level Security", "Manage RLS policies for database tables", True)
    unsupported = bootcamp.Capability("deployment", "Deployment & Branching", "Preview environments and branching strategies", True)
    assert quality_gate.capability_supported_by_sources(supported, source_pack)
    assert not quality_gate.capability_supported_by_sources(unsupported, source_pack)


def test_generic_hidden_rubric_is_replaced_with_capability_specific_checks():
    caps = [bootcamp.Capability("rls", "Row Level Security", "Create and reason about table RLS policies", True)]
    task = {
        "task": "Diagnose an RLS failure",
        "capability_ids": ["rls"],
        "hidden_rubric": ["short check"],
        "adversarial": True,
        "critical": True,
    }
    repaired = quality_gate.strengthen_task_rubric(task, caps)
    assert repaired["hidden_rubric"] != ["short check"]
    assert any("RLS" in item or "Row Level Security" in item for item in repaired["hidden_rubric"])
    assert any("unsupported" in item.lower() or "false premise" in item.lower() for item in repaired["hidden_rubric"])


def test_capability_support_filter_rejects_description_smuggling():
    source_pack = "Configure database roles and permissions for users."
    smuggled = bootcamp.Capability(
        "roles_permissions",
        "Roles & Permissions",
        "Configure roles and permissions plus billing quotas and preview deployments",
        True,
    )
    assert not quality_gate.capability_supported_by_sources(smuggled, source_pack)


def test_training_package_not_ready_when_proxy_transfer_or_critical_capability_is_weak():
    spec = {"identity": "SB", "function": "Supabase Platform Specialist", "target": "practitioner", "rounds": 2}
    weak_cap = bootcamp.Capability("rls", "RLS", "Row security", True, score=1, observations=2)
    audit = [
        {"round": 1, "exam": {"score": 1, "passed": False, "critical_failure": False}},
        {"round": 2, "exam": {"score": 1, "passed": False, "critical_failure": False}},
    ]
    transfers = [
        {"transfer": 1, "exam": {"score": 1, "passed": False, "critical_failure": False}},
        {"transfer": 2, "exam": {"score": 1, "passed": False, "critical_failure": False}},
    ]
    qual = quality_gate.conservative_qualification(spec, [weak_cap], audit, transfers, [])
    assert qual["training_package_ready"] is False
    assert qual["outcome"] == "FAIL"
