from __future__ import annotations

import json

from fastapi.testclient import TestClient

from crucible_engine import Generation
from crucible_server import create_app, tool_schemas_from_openai

_EVENT_CALL = (
    '{"tool": "create_event", "arguments": '
    '{"title": "Q3 Review", "date": "2026-07-01", "time": "14:00", "location": "Room B"}}'
)


class FakeEngine:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    def chat(
        self,
        messages: list[dict[str, str]],
        *,
        grammar: str | None = None,
        max_tokens: int = 512,
        temperature: float = 0.7,
        seed: int | None = None,
    ) -> Generation:
        self.calls.append({"grammar": grammar, "temperature": temperature})
        if grammar is not None:  # tools were supplied -> emit a valid tool call
            return Generation(_EVENT_CALL, prompt_tokens=12, completion_tokens=20)
        return Generation("hello there", prompt_tokens=5, completion_tokens=3)


_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "create_event",
            "parameters": {
                "type": "object",
                "properties": {"title": {}, "date": {}, "time": {}, "location": {}},
                "required": ["title", "date", "time", "location"],
            },
        },
    }
]


def _client() -> TestClient:
    return TestClient(create_app(FakeEngine()))


def test_openai_tools_convert() -> None:
    schemas = tool_schemas_from_openai(_TOOLS)
    assert schemas[0].name == "create_event"
    assert schemas[0].params == ("title", "date", "time", "location")


def test_models_endpoint() -> None:
    r = _client().get("/v1/models")
    assert r.status_code == 200
    assert r.json()["data"][0]["id"] == "crucible-local"


def test_plain_chat() -> None:
    r = _client().post(
        "/v1/chat/completions",
        json={"model": "crucible-local", "messages": [{"role": "user", "content": "hi"}]},
    )
    body = r.json()
    assert r.status_code == 200
    assert body["choices"][0]["message"]["content"] == "hello there"
    assert body["choices"][0]["finish_reason"] == "stop"
    assert body["usage"]["total_tokens"] == 8


def test_tool_call_is_grammar_valid() -> None:
    r = _client().post(
        "/v1/chat/completions",
        json={
            "model": "crucible-local",
            "messages": [{"role": "user", "content": "schedule it"}],
            "tools": _TOOLS,
        },
    )
    body = r.json()
    choice = body["choices"][0]
    assert choice["finish_reason"] == "tool_calls"
    call = choice["message"]["tool_calls"][0]
    assert call["function"]["name"] == "create_event"
    args = json.loads(call["function"]["arguments"])  # must be valid JSON
    assert set(args.keys()) == {"title", "date", "time", "location"}


def test_tool_emission_is_deterministic() -> None:
    """Regression: tool calls decode at temperature 0 even if the client asks for more,
    so the sampler commits to a valid call instead of wandering in grammar whitespace."""
    engine = FakeEngine()
    client = TestClient(create_app(engine))
    client.post(
        "/v1/chat/completions",
        json={
            "model": "crucible-local",
            "messages": [{"role": "user", "content": "schedule it"}],
            "tools": _TOOLS,
            "temperature": 0.9,
        },
    )
    assert engine.calls[-1]["grammar"] is not None
    assert engine.calls[-1]["temperature"] == 0.0


def test_plain_chat_respects_requested_temperature() -> None:
    engine = FakeEngine()
    client = TestClient(create_app(engine))
    client.post(
        "/v1/chat/completions",
        json={
            "model": "crucible-local",
            "messages": [{"role": "user", "content": "hi"}],
            "temperature": 0.2,
        },
    )
    assert engine.calls[-1]["grammar"] is None
    assert engine.calls[-1]["temperature"] == 0.2
