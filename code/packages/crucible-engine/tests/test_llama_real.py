"""Real-model engine tests (slow; skipped in the fast gate and when the model/llama
are absent). Run with:  uv run pytest -m slow
"""

from __future__ import annotations

from pathlib import Path

import pytest

MODEL = Path(__file__).resolve().parents[3] / "models" / "Qwen2.5-3B-Instruct-Q4_K_M.gguf"

pytestmark = [
    pytest.mark.slow,
    pytest.mark.skipif(not MODEL.exists(), reason="model GGUF not present"),
]


def test_kv_reuse_is_cheaper_and_does_not_change_output() -> None:
    pytest.importorskip("llama_cpp")
    from crucible_engine import LlamaCppEngine

    engine = LlamaCppEngine(str(MODEL), seed=0)
    shared = "You are terse. Facts: " + " ".join(f"item{i}={i * 2}" for i in range(300))
    msgs = [
        {"role": "system", "content": shared},
        {"role": "user", "content": "Reply with the single word OK."},
    ]

    engine.reset_context()
    cold = engine.chat(msgs, max_tokens=4, temperature=0.0)  # full prefill
    warm = engine.chat(msgs, max_tokens=4, temperature=0.0)  # shared prefix reused

    # The invariant: reusing the cache must not change the output.
    assert cold.text == warm.text
    # ...and it must actually be cheaper to prefill.
    assert warm.prompt_eval_tokens < cold.prompt_eval_tokens
