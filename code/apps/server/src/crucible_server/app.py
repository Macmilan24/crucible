"""An OpenAI-compatible chat-completions server backed by a Crucible engine.

The value-add over a plain local server: when a request supplies ``tools``, Crucible
constrains the emission to the action grammar, so the returned tool call is
**structurally valid by construction** (zero malformed calls) — and the model may
still answer in plain text via the grammar's final-answer branch.

Point any OpenAI-compatible client (opencode, Continue, the openai SDK) at this
server's base URL; no client code changes.
"""

from __future__ import annotations

import json
import time
import uuid
from typing import Any, Protocol

from fastapi import FastAPI, Request

from crucible_engine import Generation
from crucible_grammar import ToolSchema, action_gbnf


class ChatEngine(Protocol):
    def chat(
        self,
        messages: list[dict[str, str]],
        *,
        grammar: str | None = None,
        max_tokens: int = 512,
        temperature: float = 0.7,
        seed: int | None = None,
    ) -> Generation: ...


def tool_schemas_from_openai(tools: list[dict[str, Any]] | None) -> list[ToolSchema]:
    """Convert OpenAI `tools` into Crucible ToolSchemas (name + required arg keys)."""
    schemas: list[ToolSchema] = []
    for entry in tools or []:
        fn = entry.get("function", {})
        name = fn.get("name")
        params = fn.get("parameters") or {}
        props = list((params.get("properties") or {}).keys())
        required = params.get("required") or props
        keys = tuple(required) if required else tuple(props)
        if name and keys:
            schemas.append(ToolSchema(name, keys))
    return schemas


def _format(gen: Generation, model: str, *, used_tools: bool) -> dict[str, Any]:
    message: dict[str, Any] = {"role": "assistant"}
    finish = "stop"
    if used_tools:
        try:
            action = json.loads(gen.text)
        except (json.JSONDecodeError, ValueError):
            action = {"final": gen.text}
        if isinstance(action, dict) and "tool" in action:
            message["content"] = None
            message["tool_calls"] = [
                {
                    "id": "call_" + uuid.uuid4().hex[:8],
                    "type": "function",
                    "function": {
                        "name": action["tool"],
                        "arguments": json.dumps(action.get("arguments", {})),
                    },
                }
            ]
            finish = "tool_calls"
        else:
            message["content"] = (
                action.get("final", gen.text) if isinstance(action, dict) else gen.text
            )
    else:
        message["content"] = gen.text
    return {
        "id": "chatcmpl-" + uuid.uuid4().hex[:12],
        "object": "chat.completion",
        "created": int(time.time()),
        "model": model,
        "choices": [{"index": 0, "message": message, "finish_reason": finish}],
        "usage": {
            "prompt_tokens": gen.prompt_tokens,
            "completion_tokens": gen.completion_tokens,
            "total_tokens": gen.prompt_tokens + gen.completion_tokens,
        },
    }


def create_app(engine: ChatEngine, *, model_name: str = "crucible-local") -> FastAPI:
    app = FastAPI(title="Crucible", version="0.0.1")

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/v1/models")
    def models() -> dict[str, Any]:
        return {
            "object": "list",
            "data": [{"id": model_name, "object": "model", "owned_by": "crucible"}],
        }

    @app.post("/v1/chat/completions")
    async def chat_completions(request: Request) -> dict[str, Any]:
        body = await request.json()
        messages = body.get("messages", [])
        temperature = float(body.get("temperature", 0.7))
        max_tokens = int(body.get("max_tokens") or 512)
        schemas = tool_schemas_from_openai(body.get("tools"))
        grammar = action_gbnf(schemas, allow_final=True) if schemas else None
        gen = engine.chat(messages, grammar=grammar, max_tokens=max_tokens, temperature=temperature)
        return _format(gen, model_name, used_tools=bool(schemas))

    return app
