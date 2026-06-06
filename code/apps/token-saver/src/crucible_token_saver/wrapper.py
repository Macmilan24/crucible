"""The drop-in wrapper. It reuses crucible-core's Substrate (a true subset) to give
an existing agent grammar-scoped emission + an adaptive draft budget, with no fork.
"""

from __future__ import annotations

from crucible_core import Substrate
from crucible_engine import ROOT, ControlSurface
from crucible_grammar import EmissionSchema
from crucible_tokeneconomy import ReasoningMode, StepSignal


class TokenSaver:
    """Slots under an existing local agent's emission/reasoning step.

    Enable it once; it returns the same answers for fewer tokens, and malformed
    calls become impossible (grammar-scoped emission).
    """

    def __init__(self, engine: ControlSurface, *, vocab_size: int = 8) -> None:
        self._substrate = Substrate(engine, vocab_size=vocab_size)

    def emit(self, schema: EmissionSchema) -> int:
        """Emit a structurally-valid token under ``schema`` (zero malformed calls)."""
        return self._substrate.emit_token(ROOT, schema)

    def reasoning_mode(self, signal: StepSignal) -> ReasoningMode:
        """Pick the cheap draft on easy steps; full reasoning on hard ones."""
        return self._substrate.reasoning_mode(signal)
