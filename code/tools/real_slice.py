"""Real-model vertical slice: run an ACTUAL local LLM and produce HONEST numbers.

Unlike tools/demo.py (which uses the mock + illustrative inputs), this loads a real
Qwen model via llama.cpp/Metal and measures, for real:

  [A] malformed tool-call rate, unconstrained vs grammar-constrained emission
  [B] completion tokens, full chain-of-thought vs Chain-of-Draft, at matched success
  [C] the Phase-0 gate verdict on those REAL numbers

Run with:  cd code && uv run python tools/real_slice.py
Needs the model at code/models/Qwen2.5-3B-Instruct-Q4_K_M.gguf (see README).
"""

from __future__ import annotations

import re
from pathlib import Path

from crucible_bench import ArmResult, passes_phase0_gate
from crucible_engine import LlamaCppEngine
from crucible_grammar import ToolSchema, is_valid_tool_call, tool_call_gbnf

MODEL = Path(__file__).resolve().parents[1] / "models" / "Qwen2.5-3B-Instruct-Q4_K_M.gguf"

WEATHER = ToolSchema(name="get_weather", params=("city", "units"))

# Simple word problems with known integer answers (kept easy so a 3B is reliable).
TASKS: list[tuple[str, int]] = [
    (
        "Natalia sold clips to 48 friends in April, and half as many in May. "
        "How many clips did she sell altogether?",
        72,
    ),
    (
        "Weng earns $12 per hour for babysitting. Yesterday she babysat for 60 minutes. "
        "How many dollars did she earn?",
        12,
    ),
    (
        "A robe takes 2 bolts of blue fiber and half that much white fiber. "
        "How many bolts in total does it take?",
        3,
    ),
    (
        "There are 15 trees. Workers plant more so there are 21 trees. "
        "How many trees did they plant?",
        6,
    ),
    (
        "Shawn has 5 toys. For Christmas he got 2 toys each from mom and dad. "
        "How many toys does he have now?",
        9,
    ),
]


def last_int(text: str) -> int | None:
    nums = re.findall(r"-?\d+", text.replace(",", ""))
    return int(nums[-1]) if nums else None


def part_a_malformed(engine: LlamaCppEngine, trials: int = 8) -> tuple[float, float]:
    """Return (unconstrained_malformed_rate, constrained_malformed_rate)."""
    instruction = (
        "Call the get_weather tool. Reply with ONLY a JSON object with keys "
        '"tool" and "arguments"; arguments must have "city" and "units". '
        "Weather in Paris in celsius."
    )
    msgs = [{"role": "user", "content": instruction}]
    grammar = tool_call_gbnf(WEATHER)

    unconstrained_bad = 0
    constrained_bad = 0
    for i in range(trials):
        free = engine.chat(msgs, temperature=0.8, seed=i, max_tokens=128)
        if not is_valid_tool_call(free.text.strip(), WEATHER):
            unconstrained_bad += 1
        forced = engine.chat(msgs, grammar=grammar, temperature=0.8, seed=i, max_tokens=128)
        if not is_valid_tool_call(forced.text.strip(), WEATHER):
            constrained_bad += 1
    return unconstrained_bad / trials, constrained_bad / trials


def part_b_tokens(engine: LlamaCppEngine) -> tuple[ArmResult, ArmResult]:
    """Measure full-CoT vs Chain-of-Draft: mean completion tokens + success."""
    full_tokens, full_ok = [], 0
    cod_tokens, cod_ok = [], 0

    for question, gold in TASKS:
        full_prompt = f"{question}\nThink step by step, then end with 'Answer: <number>'."
        full = engine.chat(
            [{"role": "user", "content": full_prompt}], temperature=0.0, max_tokens=512
        )
        full_tokens.append(full.completion_tokens)
        full_ok += int(last_int(full.text) == gold)

        cod_prompt = (
            f"{question}\nThink step by step, but keep EACH step to at most 5 words "
            "(a terse draft). Then end with 'Answer: <number>'."
        )
        cod = engine.chat(
            [{"role": "user", "content": cod_prompt}], temperature=0.0, max_tokens=512
        )
        cod_tokens.append(cod.completion_tokens)
        cod_ok += int(last_int(cod.text) == gold)

    n = len(TASKS)
    stock = ArmResult(
        "full-CoT", sum(full_tokens) / n, malformed_rate=0.0, success_rate=full_ok / n
    )
    crucible = ArmResult(
        "chain-of-draft", sum(cod_tokens) / n, malformed_rate=0.0, success_rate=cod_ok / n
    )
    return stock, crucible


def main() -> None:
    if not MODEL.exists():
        print(f"Model not found at {MODEL}\nDownload it first (see code/README.md).")
        raise SystemExit(1)

    print("Loading real model (Qwen2.5-3B-Instruct, Metal)... ", flush=True)
    engine = LlamaCppEngine(str(MODEL), seed=0)
    print("loaded.\n" + "=" * 64)

    print("[A] Malformed tool-call rate (REAL generations):")
    free_bad, forced_bad = part_a_malformed(engine)
    print(f"    unconstrained : {free_bad:.0%} malformed")
    print(f"    grammar-scoped: {forced_bad:.0%} malformed   <- 0 by construction\n")

    print("[B] Token economy on", len(TASKS), "word problems (REAL token counts):")
    stock, crucible = part_b_tokens(engine)
    print(
        f"    full CoT       : {stock.mean_tokens:6.1f} tok/task, {stock.success_rate:.0%} correct"
    )
    print(
        f"    Chain-of-Draft : {crucible.mean_tokens:6.1f} tok/task, "
        f"{crucible.success_rate:.0%} correct"
    )
    factor = stock.mean_tokens / crucible.mean_tokens
    print(f"    -> {factor:.2f}x fewer reasoning tokens\n")

    # Fold the real malformed rate into the Crucible arm for the gate.
    crucible = ArmResult(
        crucible.name,
        crucible.mean_tokens,
        malformed_rate=forced_bad,
        success_rate=crucible.success_rate,
    )
    gate = passes_phase0_gate(stock, crucible)
    print("[C] Phase-0 gate on these REAL numbers:")
    print(f"    verdict: {'PASS' if gate.passed else 'FAIL'} - {gate.reason}")
    print("\nNote: a tiny 5-task probe on a 3B model — a real measurement, NOT the")
    print("0a benchmark. The real headline needs the full suite + CIs (docs/05).")


if __name__ == "__main__":
    main()
