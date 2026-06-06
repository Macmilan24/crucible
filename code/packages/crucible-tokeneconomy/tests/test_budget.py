from __future__ import annotations

from crucible_engine import CacheNodeId
from crucible_tokeneconomy import (
    Handoff,
    ReasoningMode,
    StepSignal,
    choose_mode,
    reasoning_token_budget,
)


def test_easy_step_drafts() -> None:
    assert choose_mode(StepSignal(verifier_value=0.9)) is ReasoningMode.DRAFT


def test_low_confidence_forces_full() -> None:
    assert choose_mode(StepSignal(verifier_value=0.2)) is ReasoningMode.FULL


def test_multifile_always_full_even_if_confident() -> None:
    sig = StepSignal(verifier_value=0.99, touches_multiple_files=True)
    assert choose_mode(sig) is ReasoningMode.FULL


def test_cross_scope_always_full() -> None:
    sig = StepSignal(verifier_value=0.99, cross_scope=True)
    assert choose_mode(sig) is ReasoningMode.FULL


def test_draft_budget_is_smaller_than_full() -> None:
    draft = reasoning_token_budget(ReasoningMode.DRAFT)
    full = reasoning_token_budget(ReasoningMode.FULL)
    assert draft < full


def test_handoff_reuses_cache() -> None:
    h = Handoff(
        sender="planner", recipient="coder", intent="apply_patch", cache_node=CacheNodeId(7)
    )
    assert h.reuses_cache()
    assert not Handoff(sender="a", recipient="b", intent="noop").reuses_cache()
