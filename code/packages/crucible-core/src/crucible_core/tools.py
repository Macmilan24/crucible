"""A minimal, sandboxed tool runtime.

A tool = a ToolSchema (which becomes a GBNF grammar, so calls to it are structurally
valid by construction) + a sandboxed Python function. Tools are deliberately
least-privilege (docs/08-security-threat-model.md): the calculator evaluates only
arithmetic (no names, no calls); the file reader cannot escape its workspace root.
"""

from __future__ import annotations

import ast
import operator
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from crucible_grammar import ToolSchema

# --- a safe arithmetic evaluator (the calculator sandbox) -------------------
_BIN_OPS: dict[type[ast.operator], Callable[[float, float], float]] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}
_UNARY_OPS: dict[type[ast.unaryop], Callable[[float], float]] = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


def safe_arithmetic(expr: str) -> float:
    """Evaluate a pure arithmetic expression. Rejects anything but numbers/operators."""

    def _eval(node: ast.AST) -> float:
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return float(node.value)
        if isinstance(node, ast.BinOp) and type(node.op) in _BIN_OPS:
            return _BIN_OPS[type(node.op)](_eval(node.left), _eval(node.right))
        if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARY_OPS:
            return _UNARY_OPS[type(node.op)](_eval(node.operand))
        raise ValueError(f"unsafe or unsupported expression near {type(node).__name__}")

    return _eval(ast.parse(expr, mode="eval").body)


# --- the tool + registry ----------------------------------------------------
@dataclass(frozen=True, slots=True)
class Tool:
    schema: ToolSchema
    description: str
    run: Callable[[dict[str, str]], str]


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        self._tools[tool.schema.name] = tool

    def get(self, name: str) -> Tool:
        return self._tools[name]

    def has(self, name: str) -> bool:
        return name in self._tools

    def schemas(self) -> list[ToolSchema]:
        return [t.schema for t in self._tools.values()]

    def describe(self) -> str:
        """A compact, prompt-ready listing of available tools."""
        lines = []
        for t in self._tools.values():
            params = ", ".join(t.schema.params)
            lines.append(f"- {t.schema.name}({params}): {t.description}")
        return "\n".join(lines)


# --- built-in tools ---------------------------------------------------------
def calculator_tool() -> Tool:
    def run(args: dict[str, str]) -> str:
        return str(safe_arithmetic(args["expression"]))

    return Tool(
        schema=ToolSchema("calculator", ("expression",)),
        description="Evaluate an arithmetic expression, e.g. '23*47+19'.",
        run=run,
    )


def read_file_tool(root: Path, *, max_chars: int = 2000) -> Tool:
    root = root.resolve()

    def run(args: dict[str, str]) -> str:
        target = (root / args["path"]).resolve()
        if root != target and root not in target.parents:
            raise ValueError("path escapes the workspace")
        return target.read_text()[:max_chars]

    return Tool(
        schema=ToolSchema("read_file", ("path",)),
        description="Read a text file from the workspace by relative path.",
        run=run,
    )
