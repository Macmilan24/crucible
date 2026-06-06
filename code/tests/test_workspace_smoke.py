"""Cross-package integration smoke test: the whole in-scope substrate wires up and
an episode runs end-to-end on the mock engine.
"""

from __future__ import annotations

import importlib


def test_all_workspace_packages_import_and_version() -> None:
    modules = [
        "crucible_engine",
        "crucible_grammar",
        "crucible_atomix",
        "crucible_tokeneconomy",
        "crucible_core",
        "crucible_token_saver",
        "crucible_bench",
        "crucible_verify",
        "crucible_search",
        "crucible_memory",
        "crucible_evolve",
        "crucible_gate",
        "crucible_govern",
        "crucible_federation",
    ]
    for name in modules:
        mod = importlib.import_module(name)
        assert mod.__version__ == "0.0.1", name


def test_end_to_end_episode() -> None:
    from crucible_atomix import KeyValueStore
    from crucible_core import Agent
    from crucible_engine import MockEngine
    from crucible_grammar import EmissionSchema
    from crucible_tokeneconomy import StepSignal

    store = KeyValueStore()
    agent = Agent(MockEngine(vocab_size=8), vocab_size=8)
    result = agent.run_episode(
        EmissionSchema(frozenset({2, 6})),
        StepSignal(verifier_value=0.95),
        effects=[store.set_effect("done", True)],
    )
    assert result.grammar_valid
    assert result.settled_effects == 1
    assert store.get("done") is True
