from __future__ import annotations

from crucible_atomix import KeyValueStore
from crucible_core import Agent, Substrate
from crucible_engine import ROOT, MockEngine
from crucible_grammar import EmissionSchema
from crucible_tokeneconomy import ReasoningMode, StepSignal


def test_episode_is_grammar_valid_and_emission_in_schema() -> None:
    engine = MockEngine(vocab_size=8)
    agent = Agent(engine, vocab_size=8)
    schema = EmissionSchema(frozenset({3, 5}))
    result = agent.run_episode(schema, StepSignal(verifier_value=0.9))

    assert result.grammar_valid
    assert all(schema.accepts(t) for t in result.emitted)
    assert result.reasoning_mode is ReasoningMode.DRAFT  # easy step ⇒ draft


def test_episode_settles_effects_atomically() -> None:
    engine = MockEngine(vocab_size=8)
    agent = Agent(engine, vocab_size=8)
    store = KeyValueStore()
    schema = EmissionSchema(frozenset({1}))

    result = agent.run_episode(
        schema,
        StepSignal(verifier_value=0.2, touches_multiple_files=True),  # ⇒ FULL reasoning
        effects=[store.set_effect("k", "v")],
    )

    assert result.settled_effects == 1
    assert store.get("k") == "v"
    assert result.reasoning_mode is ReasoningMode.FULL


def test_substrate_is_reusable_subset() -> None:
    # The 0b token-saver relies on this facade existing and being usable alone.
    engine = MockEngine(vocab_size=4)
    sub = Substrate(engine, vocab_size=4)
    schema = EmissionSchema(frozenset({2}))
    assert sub.emit_token(ROOT, schema) == 2
