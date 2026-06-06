"""The Substrate facade — the public, reusable subset of Core.

This is exactly the surface the 0b token-saver wraps (ADR-0005): masked emission,
the adaptive reasoning dial, and transactional settlement. Keeping it a single
facade is what lets the drop-in wrapper be a true subset of the runtime rather than
a fork.
"""

from __future__ import annotations

from crucible_atomix import Transaction
from crucible_engine import CacheNodeId, ControlSurface
from crucible_grammar import EmissionSchema, Phase, mask_for_phase
from crucible_tokeneconomy import ReasoningMode, StepSignal, choose_mode


class Substrate:
    """A thin, dependency-injected facade over the substrate packages."""

    def __init__(self, engine: ControlSurface, *, vocab_size: int = 8) -> None:
        self._engine = engine
        self._vocab_size = vocab_size

    def think_token(self, node: CacheNodeId) -> int:
        """Sample a cognition token — unconstrained (no mask). Reasoning is free."""
        mask = mask_for_phase(Phase.THINK, None, self._vocab_size)
        return self._engine.sample(node, mask=mask)

    def emit_token(self, node: CacheNodeId, schema: EmissionSchema) -> int:
        """Sample an emission token under the schema mask — structurally valid by
        construction."""
        mask = mask_for_phase(Phase.EMIT, schema, self._vocab_size)
        return self._engine.sample(node, mask=mask)

    def reasoning_mode(self, signal: StepSignal) -> ReasoningMode:
        return choose_mode(signal)

    def new_transaction(self, *, speculative: bool = True) -> Transaction:
        return Transaction(speculative=speculative)
