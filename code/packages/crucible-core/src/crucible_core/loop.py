"""The real multi-step agent loop.

Each step is two-phase decoding (Principle 3.2): the model first THINKS in free text
(unconstrained cognition), then EMITS an action under the action grammar (structurally
valid by construction — a real tool call or a final answer). Tool calls are settled
through Atomix, so a failing tool aborts cleanly and the error is fed back for the
model to recover from (the failure-recovery path).

The engine is injected as a ``ChatEngine`` (duck-typed), so this loop runs against
the real LlamaCppEngine or a scripted fake in tests — no GPU required to test the
control flow.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Protocol, cast

from crucible_atomix import Effect, ReversibilityClass, Transaction, TransactionAborted
from crucible_engine import Generation
from crucible_grammar import action_gbnf

from .tools import ToolRegistry

_SYSTEM = (
    "You are Crucible, a careful local agent that solves tasks by calling tools.\n"
    "Rules:\n"
    "- You CANNOT do arithmetic in your head — always use the calculator tool.\n"
    "- You CANNOT know a file's contents — always use read_file.\n"
    "- Take ONE tool action at a time; after its result appears in the steps, decide "
    "the next action.\n"
    "- Only output a final answer once the steps above already contain every result "
    "you need.\n"
    'Example tool call: {"tool": "calculator", "arguments": {"expression": "2+2"}}'
)


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


@dataclass(slots=True)
class Step:
    thought: str
    action: dict[str, object]
    observation: str | None = None


@dataclass(slots=True)
class TaskResult:
    steps: list[Step] = field(default_factory=list)
    final: str | None = None
    completion_tokens: int = 0
    tool_calls: int = 0
    malformed: int = 0

    @property
    def solved(self) -> bool:
        return self.final is not None


def _history_text(steps: list[Step]) -> str:
    if not steps:
        return "(no steps yet)"
    lines: list[str] = []
    for i, s in enumerate(steps, 1):
        act = json.dumps(s.action)
        lines.append(f"{i}. thought: {s.thought}\n   action: {act}\n   result: {s.observation}")
    return "\n".join(lines)


def _execute(registry: ToolRegistry, action: dict[str, object]) -> str:
    """Run a tool call through an Atomix transaction; return its result or an error."""
    name = str(action.get("tool", ""))
    if not registry.has(name):
        return f"ERROR: unknown tool {name!r}"
    raw_args = action.get("arguments", {})
    args = cast(dict[str, str], raw_args if isinstance(raw_args, dict) else {})
    tool = registry.get(name)

    holder: list[str] = []

    def apply() -> None:
        holder.append(tool.run(args))

    txn = Transaction(speculative=True)
    txn.add(Effect(name=f"call {name}", reversibility=ReversibilityClass.IDEMPOTENT, apply=apply))
    try:
        txn.settle()
    except TransactionAborted as exc:
        return f"ERROR: {exc}"
    return holder[0]


def run_task(
    engine: ChatEngine,
    registry: ToolRegistry,
    task: str,
    *,
    max_steps: int = 6,
    think_max_tokens: int = 96,
    seed: int = 0,
) -> TaskResult:
    """Drive the agent to solve ``task`` with the registered tools."""
    full_grammar = action_gbnf(registry.schemas(), allow_final=True)
    final_only = action_gbnf([], allow_final=True)  # forces a {"final": ...} emission
    tools_desc = registry.describe()
    result = TaskResult()
    executed: dict[str, str] = {}  # action signature -> cached observation
    force_final = False

    for _ in range(max_steps):
        context = (
            f"Task: {task}\n\nAvailable tools:\n{tools_desc}\n\n"
            f"Steps so far:\n{_history_text(result.steps)}"
        )

        # Phase 1 — THINK (free cognition, kept brief).
        think = engine.chat(
            [
                {"role": "system", "content": _SYSTEM},
                {"role": "user", "content": context + "\n\nBriefly: what is the next step?"},
            ],
            temperature=0.3,
            max_tokens=think_max_tokens,
            seed=seed,
        )
        result.completion_tokens += think.completion_tokens
        thought = think.text.strip()

        # Phase 2 — EMIT (grammar-constrained action: valid by construction).
        emit = engine.chat(
            [
                {"role": "system", "content": _SYSTEM},
                {
                    "role": "user",
                    "content": context
                    + f"\n\nYour reasoning: {thought}\n\n"
                    + "Output ONLY one JSON action. To call a tool: "
                    + '{"tool": "<name>", "arguments": {...}}. To finish: '
                    + '{"final": "<answer>"}. If a calculation or file content you '
                    + "need is NOT already shown in the steps above, you MUST call a "
                    + "tool now instead of finishing.",
                },
            ],
            grammar=(final_only if force_final else full_grammar),
            temperature=0.0,
            max_tokens=256,
            seed=seed,
        )
        result.completion_tokens += emit.completion_tokens

        try:
            action = cast(dict[str, object], json.loads(emit.text))
        except (json.JSONDecodeError, ValueError):
            result.malformed += 1  # should be impossible under the grammar
            break

        if "final" in action:
            result.steps.append(Step(thought=thought, action=action))
            result.final = str(action["final"])
            return result

        # Anti-repeat guard: a duplicate action makes no progress. Don't re-run the
        # tool; serve the cached result and force the next emission to finalize.
        sig = json.dumps(action, sort_keys=True)
        if sig in executed:
            observation = executed[sig] + "  (already computed — finalize if this answers the task)"
            force_final = True
        else:
            observation = _execute(registry, action)
            executed[sig] = observation
            result.tool_calls += 1
        result.steps.append(Step(thought=thought, action=action, observation=observation))

    return result
