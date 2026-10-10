import pytest

import fast_bootcamp


@pytest.mark.parametrize("budget", [0, -1, 1.5, "800", None, True])
def test_invalid_token_budget_rejected_before_model_call(monkeypatch, budget):
    def reject_network(*args, **kwargs):
        raise AssertionError("invalid budget attempted a model/network call")

    monkeypatch.setattr(fast_bootcamp.requests, "post", reject_network)
    with pytest.raises(ValueError, match="max_tokens"):
        fast_bootcamp.bounded_llm(
            fast_bootcamp.GROUNDED_ARCHITECT_SYSTEM,
            "FUNCTION: test",
            max_tokens=budget,
        )
