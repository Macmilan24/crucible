"""Contract tests for the control surface, exercised through MockEngine.

These run with no GPU and define the behaviour any real engine implementation
must also satisfy.
"""

from __future__ import annotations

import pytest

from crucible_engine import ROOT, ControlSurface, MockEngine


def test_mock_satisfies_protocol() -> None:
    assert isinstance(MockEngine(), ControlSurface)


def test_fork_creates_distinct_live_nodes() -> None:
    eng = MockEngine()
    a = eng.fork(ROOT)
    b = eng.fork(ROOT)
    assert a != b
    eng.prune(a)  # pruning a live node must not raise
    with pytest.raises(KeyError):
        eng.read_logits(a)  # pruned node is no longer live


def test_cannot_prune_root() -> None:
    eng = MockEngine()
    with pytest.raises(ValueError, match="root"):
        eng.prune(ROOT)


def test_sample_respects_mask() -> None:
    eng = MockEngine(vocab_size=4)
    # Only token 2 allowed → must sample exactly 2 (grammar-scoped emission).
    mask = [False, False, True, False]
    assert eng.sample(ROOT, mask=mask) == 2


def test_empty_mask_is_an_error() -> None:
    eng = MockEngine(vocab_size=4)
    with pytest.raises(ValueError, match="forbids every token"):
        eng.sample(ROOT, mask=[False, False, False, False])


def test_draft_width_and_scores() -> None:
    eng = MockEngine()
    proposals = eng.draft(ROOT, width=3)
    assert len(proposals) == 3
    # Scores are descending → a search layer can rank without ground truth.
    assert [p.score for p in proposals] == sorted((p.score for p in proposals), reverse=True)


def test_adapter_apply_and_revert_is_reversible() -> None:
    from crucible_engine import AdapterId

    eng = MockEngine()
    rose = AdapterId("rose-001")
    eng.apply_adapter(rose)
    eng.revert_adapter(rose)  # rollback = drop a tensor; must be idempotent-safe
    eng.revert_adapter(rose)


def test_idle_tasks_run_off_path() -> None:
    eng = MockEngine()
    ran: list[str] = []
    eng.schedule_idle(lambda: ran.append("stc"))
    assert ran == []  # nothing runs on the interactive path
    assert eng.run_idle() == 1
    assert ran == ["stc"]
