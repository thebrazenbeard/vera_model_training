import json

from fastapi.testclient import TestClient

from successor.openwebui_server import (
    _extract_tool_calls,
    _openai_tools_to_xml_tools,
    create_app,
)


class FakeBackend:
    candidate_digest = "a" * 64

    def __init__(self, response="hello"):
        self.response = response
        self.calls = []

    def generate(self, messages, *, tools, temperature, top_p, max_tokens):
        self.calls.append(
            {
                "messages": messages,
                "tools": tools,
                "temperature": temperature,
                "top_p": top_p,
                "max_tokens": max_tokens,
            }
        )
        return self.response


def test_openai_tools_are_reduced_for_smollm_xml_template():
    tools = [
        {
            "type": "function",
            "function": {
                "name": "read_file",
                "description": "Read a file",
                "parameters": {
                    "type": "object",
                    "properties": {"path": {"type": "string"}},
                    "required": ["path"],
                },
            },
        }
    ]
    assert _openai_tools_to_xml_tools(tools) == [
        {
            "name": "read_file",
            "description": "Read a file",
            "parameters": {
                "type": "object",
                "properties": {"path": {"type": "string"}},
                "required": ["path"],
            },
        }
    ]


def test_extract_tool_call_maps_to_openai_shape():
    content, calls = _extract_tool_calls(
        'I will check. <tool_call>{"name":"read_file","arguments":{"path":"a.txt"}}</tool_call>'
    )
    assert content == "I will check."
    assert len(calls) == 1
    assert calls[0]["type"] == "function"
    assert calls[0]["function"]["name"] == "read_file"
    assert json.loads(calls[0]["function"]["arguments"]) == {"path": "a.txt"}


def test_models_endpoint_exposes_exact_dev_model():
    backend = FakeBackend()
    client = TestClient(create_app(backend, "vera-v3-full-dev"))
    response = client.get("/v1/models")
    assert response.status_code == 200
    assert response.json()["data"][0]["id"] == "vera-v3-full-dev"


def test_chat_completion_returns_content_and_candidate_fingerprint():
    backend = FakeBackend("hello from Vera")
    client = TestClient(create_app(backend, "vera-v3-full-dev"))
    response = client.post(
        "/v1/chat/completions",
        json={
            "model": "vera-v3-full-dev",
            "messages": [{"role": "user", "content": "hello"}],
            "temperature": 0,
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["choices"][0]["message"]["content"] == "hello from Vera"
    assert body["system_fingerprint"] == "a" * 16
    assert backend.calls[0]["temperature"] == 0


def test_chat_completion_maps_model_tool_call():
    backend = FakeBackend(
        '<tool_call>{"name":"read_file","arguments":{"path":"x.py"}}</tool_call>'
    )
    client = TestClient(create_app(backend, "vera-v3-full-dev"))
    response = client.post(
        "/v1/chat/completions",
        json={
            "model": "vera-v3-full-dev",
            "messages": [{"role": "user", "content": "read x.py"}],
            "tools": [
                {
                    "type": "function",
                    "function": {
                        "name": "read_file",
                        "parameters": {
                            "type": "object",
                            "properties": {"path": {"type": "string"}},
                        },
                    },
                }
            ],
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["choices"][0]["finish_reason"] == "tool_calls"
    tool_call = body["choices"][0]["message"]["tool_calls"][0]
    assert tool_call["function"]["name"] == "read_file"


def test_streaming_completion_emits_openai_sse_done_marker():
    backend = FakeBackend("streamed")
    client = TestClient(create_app(backend, "vera-v3-full-dev"))
    with client.stream(
        "POST",
        "/v1/chat/completions",
        json={
            "model": "vera-v3-full-dev",
            "messages": [{"role": "user", "content": "hello"}],
            "stream": True,
        },
    ) as response:
        text = "".join(response.iter_text())
    assert response.status_code == 200
    assert "chat.completion.chunk" in text
    assert "data: [DONE]" in text


def test_unknown_model_is_rejected():
    backend = FakeBackend()
    client = TestClient(create_app(backend, "vera-v3-full-dev"))
    response = client.post(
        "/v1/chat/completions",
        json={
            "model": "wrong",
            "messages": [{"role": "user", "content": "hello"}],
        },
    )
    assert response.status_code == 404
