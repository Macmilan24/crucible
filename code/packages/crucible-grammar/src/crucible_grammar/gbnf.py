"""Real grammar-scoped emission: build GBNF grammars for agent actions and validate
output against them.

GBNF is the grammar format llama.cpp consumes to constrain decoding. A tool call is
emitted as a JSON object with exactly the declared parameters, so the model is
*structurally incapable* of emitting a malformed call (wrong name, missing/extra
args, unparseable JSON). The action grammar additionally lets the model end the
episode with a final answer — and that choice, too, is structurally valid.

It does NOT guarantee the *values* are correct — that is the verifier's job. Grammar
solves structure; the verifier solves truth.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import cast

# Shared GBNF rules reused by every grammar we build.
_STRING_RULE = 'string ::= "\\"" ([^"\\\\] | "\\\\" .)* "\\""'
_WS_RULE = "ws ::= [ \\t\\n]*"


@dataclass(frozen=True, slots=True)
class ToolSchema:
    """A minimal tool signature: a name and ordered string parameters."""

    name: str
    params: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("tool name is required")
        if not self.params:
            raise ValueError("a tool needs at least one parameter")


def _tool_object(schema: ToolSchema) -> str:
    """The GBNF expression for one valid tool-call JSON object (no root/rules)."""
    arg_rules: list[str] = []
    for i, p in enumerate(schema.params):
        sep = "" if i == 0 else ' "," '
        arg_rules.append(f'{sep} "\\"{p}\\":" ws string')
    args = " ".join(arg_rules)
    return (
        f'"{{" ws "\\"tool\\":" ws "\\"{schema.name}\\"" ws "," ws '
        f'"\\"arguments\\":" ws "{{" ws {args} ws "}}" ws "}}"'
    )


def tool_call_gbnf(schema: ToolSchema) -> str:
    """A grammar that admits exactly one valid JSON call to ``schema``."""
    return f"root ::= ws {_tool_object(schema)} ws\n{_STRING_RULE}\n{_WS_RULE}\n"


def action_gbnf(tools: list[ToolSchema], *, allow_final: bool = True) -> str:
    """A grammar admitting EITHER a valid call to any of ``tools`` OR a final answer.

    Final answer shape: {"final": "<text>"}
    """
    if not tools and not allow_final:
        raise ValueError("an action grammar needs at least one tool or a final answer")
    branches = [f"({_tool_object(t)})" for t in tools]
    if allow_final:
        branches.append('("{" ws "\\"final\\":" ws string ws "}")')
    union = " | ".join(branches)
    return f"root ::= ws ({union}) ws\n{_STRING_RULE}\n{_WS_RULE}\n"


def is_valid_tool_call(text: str, schema: ToolSchema) -> bool:
    """Whether ``text`` is a structurally valid call to ``schema`` (parses + right
    name + exactly the declared arguments)."""
    try:
        parsed: object = json.loads(text)
    except (json.JSONDecodeError, ValueError):
        return False
    if not isinstance(parsed, dict):
        return False
    obj = cast(dict[str, object], parsed)
    if obj.get("tool") != schema.name:
        return False
    args = obj.get("arguments")
    if not isinstance(args, dict):
        return False
    arguments = cast(dict[str, object], args)
    return set(arguments.keys()) == set(schema.params)
