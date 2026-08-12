import bootcamp
import fast_bootcamp


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
