import fast_bootcamp
import bootcamp


class FakeResponse:
    def __init__(self, content, finish_reason="stop"):
        self._content = content
        self._finish_reason = finish_reason

    def raise_for_status(self):
        return None

    def json(self):
        return {
            "choices": [
                {
                    "finish_reason": self._finish_reason,
                    "message": {"content": self._content},
                }
            ]
        }


def test_json_prompts_use_llama_json_object_mode(monkeypatch):
    calls = []

    def fake_post(url, json, timeout):
        calls.append(json)
        return FakeResponse('{"capabilities": []}')

    monkeypatch.setattr(fast_bootcamp.requests, "post", fake_post)
    fast_bootcamp.bounded_llm(
        fast_bootcamp.GROUNDED_ARCHITECT_SYSTEM,
        "FUNCTION: test",
        max_tokens=800,
        temperature=0.0,
    )

    assert calls[0]["response_format"] == {"type": "json_object"}


def test_grounded_architect_keeps_requested_800_token_budget(monkeypatch):
    calls = []

    def fake_post(url, json, timeout):
        calls.append(json)
        return FakeResponse('{"capabilities": []}')

    monkeypatch.setattr(fast_bootcamp.requests, "post", fake_post)
    fast_bootcamp.bounded_llm(
        fast_bootcamp.GROUNDED_ARCHITECT_SYSTEM,
        "FUNCTION: test",
        max_tokens=800,
        temperature=0.0,
    )

    assert calls[0]["max_tokens"] == 800


def test_truncated_json_retries_with_larger_budget(monkeypatch):
    calls = []
    responses = iter(
        [
            FakeResponse('{"capabilities":[', finish_reason="length"),
            FakeResponse('{"capabilities": []}', finish_reason="stop"),
        ]
    )

    def fake_post(url, json, timeout):
        calls.append(json)
        return next(responses)

    monkeypatch.setattr(fast_bootcamp.requests, "post", fake_post)
    result = fast_bootcamp.bounded_llm(
        fast_bootcamp.GROUNDED_ARCHITECT_SYSTEM,
        "FUNCTION: test",
        max_tokens=800,
        temperature=0.0,
    )

    assert result == '{"capabilities": []}'
    assert len(calls) == 2
    assert calls[1]["max_tokens"] > calls[0]["max_tokens"]


def test_prose_prompts_do_not_force_json_mode(monkeypatch):
    calls = []

    def fake_post(url, json, timeout):
        calls.append(json)
        return FakeResponse("plain answer")

    monkeypatch.setattr(fast_bootcamp.requests, "post", fake_post)
    fast_bootcamp.bounded_llm(
        bootcamp.STUDENT_SYSTEM,
        "TASK: test",
        max_tokens=400,
        temperature=0.1,
    )

    assert "response_format" not in calls[0]
