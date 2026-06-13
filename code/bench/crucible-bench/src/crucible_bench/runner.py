"""The benchmark experiments.

Three honest measurements, all on a real model:
  1. malformed-rate: unconstrained emission vs grammar-scoped emission.
  2. compounding: project per-step validity over an N-step episode (the paper's
     reliability argument), computed from the MEASURED single-step rate.
  3. token-economy: full chain-of-thought vs Chain-of-Draft, with a bootstrap CI,
     fed into the Phase-0 gate.

The engine is duck-typed (ChatEngine), so a fake engine drives the tests with no GPU.
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from typing import Any, Protocol

from crucible_engine import Generation
from crucible_grammar import is_valid_tool_call, tool_call_gbnf

from .kv import KvReuseResult
from .metrics import ArmResult, GateResult, passes_phase0_gate
from .stats import bootstrap_ci, mean
from .suite import REASONING_TASKS, TOOL_TASKS, ReasoningTask, ToolTask


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


def extract_int(text: str) -> int | None:
    nums = re.findall(r"-?\d+", text.replace(",", ""))
    return int(nums[-1]) if nums else None


# --- experiment 1: malformed-rate ------------------------------------------
@dataclass(frozen=True, slots=True)
class MalformedResult:
    unconstrained_rate: float
    grammar_rate: float
    trials: int


def run_malformed(
    engine: ChatEngine, tasks: list[ToolTask] | None = None, *, seeds: tuple[int, ...] = (0, 1, 2)
) -> MalformedResult:
    tasks = tasks if tasks is not None else TOOL_TASKS
    free_bad: list[float] = []
    forced_bad: list[float] = []
    for task in tasks:
        grammar = tool_call_gbnf(task.schema)
        prompt = (
            f"{task.instruction}\nReply with ONLY a JSON object: "
            '{"tool": "<name>", "arguments": {...}}.'
        )
        msgs = [{"role": "user", "content": prompt}]
        for s in seeds:
            free = engine.chat(msgs, temperature=0.7, seed=s, max_tokens=160)
            free_bad.append(0.0 if is_valid_tool_call(free.text.strip(), task.schema) else 1.0)
            forced = engine.chat(msgs, grammar=grammar, temperature=0.7, seed=s, max_tokens=160)
            forced_bad.append(0.0 if is_valid_tool_call(forced.text.strip(), task.schema) else 1.0)
    return MalformedResult(
        unconstrained_rate=mean(free_bad),
        grammar_rate=mean(forced_bad),
        trials=len(free_bad),
    )


def compounding_projection(per_step_malformed: float, steps: int = 20) -> dict[str, float]:
    """P(no malformed action over `steps`) for unconstrained vs grammar (=1.0)."""
    p_ok = (1.0 - per_step_malformed) ** steps
    return {
        "steps": float(steps),
        "unconstrained_clean_episode": p_ok,
        "grammar_clean_episode": 1.0,
    }


# --- experiment 2: token economy -------------------------------------------
@dataclass(frozen=True, slots=True)
class TokenEconomyResult:
    full: ArmResult
    cod: ArmResult
    reduction_factor: float
    reduction_ci: tuple[float, float]
    gate: GateResult


def _ask(engine: ChatEngine, prompt: str, seed: int) -> Generation:
    return engine.chat(
        [{"role": "user", "content": prompt}], temperature=0.0, max_tokens=512, seed=seed
    )


def run_token_economy(
    engine: ChatEngine,
    tasks: list[ReasoningTask] | None = None,
    *,
    seeds: tuple[int, ...] = (0,),
) -> TokenEconomyResult:
    tasks = tasks if tasks is not None else REASONING_TASKS
    full_tok: list[float] = []
    cod_tok: list[float] = []
    ratios: list[float] = []
    full_ok = 0
    cod_ok = 0
    n = 0
    for task in tasks:
        for s in seeds:
            n += 1
            full = _ask(
                engine,
                f"{task.question}\nThink step by step, then end with 'Answer: <number>'.",
                s,
            )
            cod = _ask(
                engine,
                f"{task.question}\nThink step by step, but keep EACH step to at most 5 "
                "words (a terse draft). Then end with 'Answer: <number>'.",
                s,
            )
            full_tok.append(float(full.completion_tokens))
            cod_tok.append(float(cod.completion_tokens))
            if cod.completion_tokens > 0:
                ratios.append(full.completion_tokens / cod.completion_tokens)
            full_ok += int(extract_int(full.text) == task.answer)
            cod_ok += int(extract_int(cod.text) == task.answer)

    full_arm = ArmResult("full-CoT", mean(full_tok), malformed_rate=0.0, success_rate=full_ok / n)
    cod_arm = ArmResult(
        "chain-of-draft", mean(cod_tok), malformed_rate=0.0, success_rate=cod_ok / n
    )
    return TokenEconomyResult(
        full=full_arm,
        cod=cod_arm,
        reduction_factor=mean(full_tok) / mean(cod_tok) if mean(cod_tok) else 0.0,
        reduction_ci=bootstrap_ci(ratios),
        gate=passes_phase0_gate(full_arm, cod_arm),
    )


# --- the whole run ----------------------------------------------------------
@dataclass(slots=True)
class BenchReport:
    malformed: MalformedResult
    compounding: dict[str, float]
    token_economy: TokenEconomyResult
    kv_reuse: KvReuseResult | None = None  # set by the runner when the engine supports it
    meta: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def run_all(engine: ChatEngine, *, seeds: tuple[int, ...] = (0, 1, 2)) -> BenchReport:
    malformed = run_malformed(engine, seeds=seeds)
    return BenchReport(
        malformed=malformed,
        compounding=compounding_projection(malformed.unconstrained_rate),
        token_economy=run_token_economy(engine, seeds=(seeds[0],)),
    )
