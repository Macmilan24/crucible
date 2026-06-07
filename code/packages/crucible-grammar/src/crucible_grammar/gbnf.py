"""Real grammar-scoped emission: build a GBNF grammar for a tool call and validate
output against it.

GBNF is the grammar format llama.cpp consumes to constrain decoding. A tool call is
emitted as a JSON object with exactly the declared parameters — so the model is
*structurally incapable* of emitting a malformed call (wrong name, missing/extra
args, unparseable JSON). This is the real form of the two-phase decoding invariant
that the scaffold modelled with token sets.

It does NOT guarantee the *values* are correct — that is the verifier's job. Grammar
solves structure; the verifier solves truth.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import cast


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


def tool_call_gbnf(schema: ToolSchema) -> str:
    """Return a GBNF grammar that admits exactly one valid JSON call to ``schema``.

    Shape: {"tool": "<name>", "arguments": {"p1": "...", "p2": "...", ...}}
    """
    # Each argument is a JSON string value; keys and order are fixed.
    arg_rules: list[str] = []
    for i, p in enumerate(schema.params):
        sep = "" if i == 0 else ' "," '
        arg_rules.append(f'{sep} "\\"{p}\\":" ws string')
    args = " ".join(arg_rules)

    return (
        "root   ::= "
        f'"{{" ws "\\"tool\\":" ws "\\"{schema.name}\\"" ws "," ws '
        f'"\\"arguments\\":" ws "{{" ws {args} ws "}}" ws "}}"\n'
        'string ::= "\\"" ([^"\\\\] | "\\\\" .)* "\\""\n'
        "ws     ::= [ \\t\\n]*\n"
    )


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
