"""The inference-native agent loop (scaffold).

Demonstrates a grammar-valid episode that uses every substrate primitive on the
MockEngine: free cognition, masked emission, an adaptive reasoning dial, and atomic
settlement. It is intentionally small — it proves the wiring, not the intelligence.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from crucible_atomix import Effect
from crucible_engine import ROOT, ControlSurface
from crucible_grammar import EmissionSchema, Phase, TrajectoryGrammar
from crucible_tokeneconomy import ReasoningMode, StepSignal

from .substrate import Substrate


@dataclass(slots=True)
class EpisodeResult:
    phases: list[Phase] = field(default_factory=list)
    emitted: list[int] = field(default_factory=list)
    reasoning_mode: ReasoningMode | None = None
    settled_effects: int = 0

    @property
    def grammar_valid(self) -> bool:
        return TrajectoryGrammar.accepts(self.phases)


class Agent:
    """A minimal agent over the substrate."""

    def __init__(self, engine: ControlSurface, *, vocab_size: int = 8) -> None:
        self._engine = engine
        self._substrate = Substrate(engine, vocab_size=vocab_size)

    def run_episode(
        self,
        schema: EmissionSchema,
        signal: StepSignal,
        effects: list[Effect] | None = None,
    ) -> EpisodeResult:
        """Run one think → emit → halt episode, settling any effects atomically."""
        grammar = TrajectoryGrammar()
        result = EpisodeResult(phases=[Phase.THINK])

        # Cognition (free): decide how hard to think, then sample a reasoning token.
        result.reasoning_mode = self._substrate.reasoning_mode(signal)
        _ = self._substrate.think_token(ROOT)

        # Emission (masked): structurally valid by construction.
        grammar.transition(Phase.EMIT)
        result.phases.append(Phase.EMIT)
        token = self._substrate.emit_token(ROOT, schema)
        assert schema.accepts(token)  # invariant; never fires under a correct mask
        result.emitted.append(token)

        # Settle any tool effects atomically.
        if effects:
            txn = self._substrate.new_transaction(speculative=True)
            for effect in effects:
                txn.add(effect)
            txn.settle()
            result.settled_effects = len(effects)

        grammar.transition(Phase.HALT)
        result.phases.append(Phase.HALT)
        return result
