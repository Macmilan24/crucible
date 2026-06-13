"""KV-cache reuse experiment (ADR-0010).

Measures the prefill saving from reusing a shared prefix's KV-cache across turns —
the Mac/llama.cpp realization of the paper's inter-agent communication win. The
metric is prompt tokens *actually processed* (Generation.prompt_eval_tokens): with
reuse, a shared long prefix is processed once, not every turn.

Honest scope: this is same-model prefix reuse (real, measurable). Full cross-agent
KV transfer / tree sharing is the SGLang/GPU phase (docs/02, docs/06).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from crucible_engine import Generation


class KvEngine(Protocol):
    def chat(
        self,
        messages: list[dict[str, str]],
        *,
        grammar: str | None = None,
        max_tokens: int = 512,
        temperature: float = 0.7,
        seed: int | None = None,
    ) -> Generation: ...

    def reset_context(self) -> None: ...


@dataclass(frozen=True, slots=True)
class KvReuseResult:
    prefill_no_reuse: int  # total prompt tokens processed WITHOUT reuse
    prefill_with_reuse: int  # ...WITH reuse of the shared prefix
    reduction_factor: float
    turns: int
    shared_context_tokens: int


def _turn(engine: KvEngine, shared_context: str, user: str) -> Generation:
    return engine.chat(
        [{"role": "system", "content": shared_context}, {"role": "user", "content": user}],
        max_tokens=1,
        temperature=0.0,
    )


def run_kv_reuse(engine: KvEngine, *, shared_context: str, turns: list[str]) -> KvReuseResult:
    """Run `turns` short queries over a long shared context, with and without reuse."""
    # No-reuse arm: clear the cache before every turn -> full prefill each time.
    no_reuse = 0
    ctx_tokens = 0
    for user in turns:
        engine.reset_context()
        g = _turn(engine, shared_context, user)
        no_reuse += g.prompt_eval_tokens
        ctx_tokens = g.prompt_tokens

    # Reuse arm: clear once, then let the shared prefix be reused across turns.
    engine.reset_context()
    with_reuse = 0
    for user in turns:
        g = _turn(engine, shared_context, user)
        with_reuse += g.prompt_eval_tokens

    factor = no_reuse / with_reuse if with_reuse else 0.0
    return KvReuseResult(
        prefill_no_reuse=no_reuse,
        prefill_with_reuse=with_reuse,
        reduction_factor=factor,
        turns=len(turns),
        shared_context_tokens=ctx_tokens,
    )


# A long shared "codebase context" + short per-turn questions (where reuse pays off).
SHARED_CONTEXT = "You are a code assistant working in one repository. Project facts:\n" + "\n".join(
    f"- module m{i}.py exports function f{i}(x) which returns x*{i} and logs to channel {i % 5}."
    for i in range(150)
)

KV_TURNS = [
    "What does f3 return?",
    "Which channel does f10 log to?",
    "Summarize module m7.",
    "Does f0 multiply by zero?",
    "List two modules.",
]
