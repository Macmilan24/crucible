"""The trajectory grammar: a finite-state machine over *phases*, not content.

It governs only the legal sequence of phases (think / emit / reflect / halt). It
NEVER constrains what the model reasons about — only the structure of the episode.
"""

from __future__ import annotations

from enum import Enum


class Phase(Enum):
    THINK = "think"
    EMIT = "emit"
    REFLECT = "reflect"
    HALT = "halt"


# ⟨episode⟩ ::= ( ⟨think⟩ (⟨emit⟩ | ⟨reflect⟩) )* ⟨halt⟩
_ALLOWED_NEXT: dict[Phase, frozenset[Phase]] = {
    Phase.THINK: frozenset({Phase.EMIT, Phase.REFLECT, Phase.HALT}),
    Phase.EMIT: frozenset({Phase.THINK, Phase.HALT}),
    Phase.REFLECT: frozenset({Phase.THINK, Phase.HALT}),
    Phase.HALT: frozenset(),
}


class TrajectoryGrammar:
    """Tracks the current phase and admits only legal transitions.

    An episode must start with THINK and end with HALT.
    """

    def __init__(self) -> None:
        self._phase: Phase = Phase.THINK
        self._halted = False

    @property
    def phase(self) -> Phase:
        return self._phase

    @property
    def halted(self) -> bool:
        return self._halted

    def allows(self, nxt: Phase) -> bool:
        return nxt in _ALLOWED_NEXT[self._phase]

    def transition(self, nxt: Phase) -> None:
        if self._halted:
            raise ValueError("episode has halted; no further phases are legal")
        if not self.allows(nxt):
            raise ValueError(f"illegal phase transition {self._phase.value} -> {nxt.value}")
        self._phase = nxt
        if nxt is Phase.HALT:
            self._halted = True

    @staticmethod
    def accepts(sequence: list[Phase]) -> bool:
        """Whether a complete phase sequence is a legal episode."""
        if not sequence or sequence[0] is not Phase.THINK or sequence[-1] is not Phase.HALT:
            return False
        g = TrajectoryGrammar()
        for nxt in sequence[1:]:
            if not g.allows(nxt):
                return False
            g.transition(nxt)
        return g.halted
