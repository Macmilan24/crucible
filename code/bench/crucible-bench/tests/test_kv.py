"""KV-reuse runner logic, driven by a fake engine that simulates prefill reuse."""

from __future__ import annotations

from crucible_bench import run_kv_reuse
from crucible_engine import Generation

_FULL = 1000  # logical prompt size of the shared context


class FakeKvEngine:
    """A cold context prefills fully; a warm one (prefix reused) prefills almost nothing."""

    def __init__(self) -> None:
        self._warm = False

    def reset_context(self) -> None:
        self._warm = False

    def chat(
        self,
        messages: list[dict[str, str]],
        *,
        grammar: str | None = None,
        max_tokens: int = 512,
        temperature: float = 0.7,
        seed: int | None = None,
    ) -> Generation:
        if self._warm:
            pe = 5
        else:
            pe = _FULL
            self._warm = True
        return Generation("x", prompt_tokens=_FULL, completion_tokens=1, prompt_eval_tokens=pe)


def test_kv_reuse_saves_prefill() -> None:
    turns = ["a", "b", "c", "d"]
    res = run_kv_reuse(FakeKvEngine(), shared_context="ctx", turns=turns)

    # No-reuse arm resets each turn -> full prefill every time.
    assert res.prefill_no_reuse == _FULL * len(turns)
    # Reuse arm: first turn cold, the rest reuse the shared prefix.
    assert res.prefill_with_reuse == _FULL + 5 * (len(turns) - 1)
    assert res.reduction_factor > 1.0
    assert res.turns == 4
    assert res.shared_context_tokens == _FULL
