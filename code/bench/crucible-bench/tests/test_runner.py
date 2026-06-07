"""Benchmark-runner logic, driven by a fake engine (no model)."""

from __future__ import annotations

from crucible_bench import (
    compounding_projection,
    extract_int,
    run_malformed,
    run_token_economy,
)
from crucible_engine import Generation

_VALID_EVENT = (
    '{"tool": "create_event", "arguments": '
    '{"title": "t", "date": "d", "time": "x", "location": "l"}}'
)


class FakeEngine:
    """Grammar calls return a valid event; free tool calls return junk; reasoning
    returns a fixed answer with full>cod token counts."""

    def chat(
        self,
        messages: list[dict[str, str]],
        *,
        grammar: str | None = None,
        max_tokens: int = 512,
        temperature: float = 0.7,
        seed: int | None = None,
    ) -> Generation:
        content = messages[-1]["content"]
        if grammar is not None:
            return Generation(_VALID_EVENT, 0, 20)
        if "terse draft" in content:  # Chain-of-Draft
            return Generation("Answer: 42", 0, 25)
        if "step by step" in content:  # full chain-of-thought
            return Generation("Answer: 42", 0, 100)
        return Generation("not json", 0, 10)  # unconstrained tool call -> malformed


def test_extract_int() -> None:
    assert extract_int("the answer is 1,100.") == 1100
    assert extract_int("no numbers here") is None


def test_malformed_contrast() -> None:
    res = run_malformed(FakeEngine(), seeds=(0, 1))
    assert res.unconstrained_rate == 1.0  # free calls were all junk
    assert res.grammar_rate == 0.0  # grammar made every call valid
    assert res.trials > 0


def test_compounding_projection() -> None:
    proj = compounding_projection(0.05, steps=20)
    assert proj["grammar_clean_episode"] == 1.0
    assert 0.0 < proj["unconstrained_clean_episode"] < 1.0  # 0.95**20 ~ 0.358


def test_token_economy_reduction_and_gate() -> None:
    res = run_token_economy(FakeEngine(), seeds=(0,))
    assert res.reduction_factor == 4.0  # 100 / 25
    assert res.gate.passed  # 4x at matched success
