import bootcamp
import fast_bootcamp


def test_transfer_learned_state_preserves_exact_source_anchor_metadata():
    cap = bootcamp.Capability("rls", "RLS", "Model-proposed scope", True, score=4, observations=2)
    cap.evidence_url = "https://supabase.com/docs/guides/database/postgres/row-level-security"
    cap.evidence_quote = "RLS must always be enabled on any tables stored in an exposed schema."

    state = fast_bootcamp.source_only_learned_state("Supabase Platform Specialist", [], [cap])

    assert cap.evidence_url in state
    assert cap.evidence_quote in state
    assert "MODEL-PROPOSED SCOPE" in state
