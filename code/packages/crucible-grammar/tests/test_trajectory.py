from __future__ import annotations

import pytest

from crucible_grammar import Phase, TrajectoryGrammar


def test_legal_episode_accepted() -> None:
    seq = [Phase.THINK, Phase.EMIT, Phase.THINK, Phase.REFLECT, Phase.THINK, Phase.HALT]
    assert TrajectoryGrammar.accepts(seq)


def test_must_start_think_end_halt() -> None:
    assert not TrajectoryGrammar.accepts([Phase.EMIT, Phase.HALT])
    assert not TrajectoryGrammar.accepts([Phase.THINK, Phase.EMIT])  # no halt
    assert not TrajectoryGrammar.accepts([])


def test_emit_cannot_follow_emit() -> None:
    g = TrajectoryGrammar()
    g.transition(Phase.EMIT)
    with pytest.raises(ValueError, match="illegal phase transition"):
        g.transition(Phase.EMIT)


def test_no_transition_after_halt() -> None:
    g = TrajectoryGrammar()
    g.transition(Phase.HALT)
    assert g.halted
    with pytest.raises(ValueError, match="halted"):
        g.transition(Phase.THINK)
