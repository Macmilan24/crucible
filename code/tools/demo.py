"""A tiny narrated walkthrough of the Crucible scaffold.

Run it with:  cd code && uv run python tools/demo.py
It uses the MockEngine, so it needs no GPU and no model download.
"""

from __future__ import annotations

from crucible_atomix import KeyValueStore
from crucible_bench import ArmResult, passes_phase0_gate
from crucible_core import Agent
from crucible_engine import MockEngine
from crucible_grammar import EmissionSchema
from crucible_tokeneconomy import StepSignal


def main() -> None:
    line = "=" * 64
    print(line)
    print("CRUCIBLE — scaffold walkthrough (no GPU, no model needed)")
    print(line)

    # [1] One agent episode on the mock engine: think -> emit -> halt.
    store = KeyValueStore()
    agent = Agent(MockEngine(vocab_size=8), vocab_size=8)
    schema = EmissionSchema(frozenset({2, 6}))  # only tokens 2 and 6 are valid
    easy = agent.run_episode(
        schema,
        StepSignal(verifier_value=0.95),  # an easy step
        effects=[store.set_effect("tests_pass", True)],
    )
    print("\n[1] One agent episode (think -> emit -> halt):")
    print(f"    phases        : {[p.value for p in easy.phases]}")
    print(f"    grammar valid : {easy.grammar_valid}")
    print(f"    emitted       : {easy.emitted}  (only schema tokens -> 0 malformed)")
    mode = easy.reasoning_mode.value if easy.reasoning_mode else "n/a"
    print(f"    reasoning     : {mode}  (easy step -> cheap draft)")
    print(f"    settled effect: store['tests_pass'] = {store.get('tests_pass')}")

    # [2] A hard, multi-file step forces full reasoning (no over-compression).
    hard = agent.run_episode(schema, StepSignal(verifier_value=0.2, touches_multiple_files=True))
    hmode = hard.reasoning_mode.value if hard.reasoning_mode else "n/a"
    print("\n[2] A hard, multi-file step:")
    print(f"    reasoning     : {hmode}  (risky -> full reasoning)")

    # [3] The Phase-0 master gate: >=2x fewer tokens at matched success.
    stock = ArmResult("stock", mean_tokens=40_000, malformed_rate=0.05, success_rate=0.50)
    crux = ArmResult("crucible", mean_tokens=5_000, malformed_rate=0.0, success_rate=0.50)
    gate = passes_phase0_gate(stock, crux)
    print("\n[3] Phase-0 master gate (>=2x tokens at matched success):")
    print(f"    stock         : {stock.mean_tokens:>6} tok, {stock.malformed_rate:.0%} malformed")
    print(f"    crucible      : {crux.mean_tokens:>6} tok, {crux.malformed_rate:.0%} malformed")
    print(f"    verdict       : {'PASS' if gate.passed else 'FAIL'} - {gate.reason}")
    print()


if __name__ == "__main__":
    main()
