from __future__ import annotations

from crucible_engine import MockEngine
from crucible_grammar import EmissionSchema
from crucible_token_saver import TokenSaver
from crucible_token_saver.cli import main
from crucible_tokeneconomy import ReasoningMode, StepSignal


def test_emit_is_structurally_valid() -> None:
    saver = TokenSaver(MockEngine(vocab_size=6), vocab_size=6)
    schema = EmissionSchema(frozenset({4}))
    assert saver.emit(schema) == 4  # zero malformed calls, by construction


def test_picks_draft_on_easy_step() -> None:
    saver = TokenSaver(MockEngine(), vocab_size=8)
    assert saver.reasoning_mode(StepSignal(verifier_value=0.95)) is ReasoningMode.DRAFT


def test_cli_runs() -> None:
    assert main([]) == 0
    assert main(["--version"]) == 0
