"""Loop control-flow tests using a scripted fake engine (no model needed)."""

from __future__ import annotations

from crucible_core import ToolRegistry, calculator_tool, run_task
from crucible_engine import Generation


class FakeEngine:
    """Returns pre-scripted completions in order, ignoring the prompt/grammar."""

    def __init__(self, responses: list[str]) -> None:
        self._responses = list(responses)
        self._i = 0

    def chat(
        self,
        messages: list[dict[str, str]],
        *,
        grammar: str | None = None,
        max_tokens: int = 512,
        temperature: float = 0.7,
        seed: int | None = None,
    ) -> Generation:
        text = self._responses[self._i]
        self._i += 1
        return Generation(text=text, prompt_tokens=0, completion_tokens=len(text.split()))


def _registry() -> ToolRegistry:
    reg = ToolRegistry()
    reg.register(calculator_tool())
    return reg


def test_loop_calls_tool_then_finishes() -> None:
    engine = FakeEngine(
        [
            "compute it",  # think 1
            '{"tool": "calculator", "arguments": {"expression": "23*47+19"}}',  # emit 1
            "now answer",  # think 2
            '{"final": "1100"}',  # emit 2
        ]
    )
    result = run_task(engine, _registry(), "What is 23*47+19?", max_steps=4)
    assert result.solved
    assert result.final == "1100"
    assert result.tool_calls == 1
    assert result.malformed == 0
    assert result.steps[0].observation == "1100.0"  # the real tool ran (via Atomix)


def test_loop_recovers_from_tool_error() -> None:
    engine = FakeEngine(
        [
            "try a bad expr",
            '{"tool": "calculator", "arguments": {"expression": "nope()"}}',  # will error
            "give up gracefully",
            '{"final": "could not compute"}',
        ]
    )
    result = run_task(engine, _registry(), "break it", max_steps=4)
    assert result.steps[0].observation is not None
    assert result.steps[0].observation.startswith("ERROR:")  # aborted cleanly, fed back
    assert result.final == "could not compute"


def test_loop_stops_at_max_steps_without_final() -> None:
    engine = FakeEngine(
        [
            "t",
            '{"tool": "calculator", "arguments": {"expression": "1+1"}}',
            "t",
            '{"tool": "calculator", "arguments": {"expression": "2+2"}}',
        ]
    )
    result = run_task(engine, _registry(), "loop forever", max_steps=2)
    assert not result.solved
    assert result.tool_calls == 2


def test_loop_dedupes_repeated_action() -> None:
    # Identical actions: the tool runs once; the repeat is cached, not re-executed.
    engine = FakeEngine(
        [
            "t",
            '{"tool": "calculator", "arguments": {"expression": "5*5"}}',
            "t",
            '{"tool": "calculator", "arguments": {"expression": "5*5"}}',  # duplicate
            "t",
            '{"final": "25"}',
        ]
    )
    result = run_task(engine, _registry(), "compute 5*5", max_steps=5)
    assert result.tool_calls == 1  # duplicate served from cache
    assert result.final == "25"
