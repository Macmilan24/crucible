"""Schema-scoped emission masking.

During the EMIT phase the runtime activates a schema grammar that produces a
boolean mask over the vocabulary, so the decoder can only emit tokens the schema
permits. During THINK/REFLECT there is *no* mask (``None``) — cognition is free.

This scaffold models a schema as the set of tokens it admits; the real backend
(XGrammar-2) computes the same mask from a tool's JSON schema / FSM, behind this
identical API.
"""

from __future__ import annotations

from collections.abc import Sequence

from .trajectory import Phase


class EmissionSchema:
    """A toy schema = the set of vocabulary tokens it accepts."""

    def __init__(self, allowed_tokens: frozenset[int]) -> None:
        if not allowed_tokens:
            raise ValueError("a schema must accept at least one token")
        self._allowed = allowed_tokens

    def accepts(self, token: int) -> bool:
        return token in self._allowed

    def mask(self, vocab_size: int) -> list[bool]:
        """A boolean mask over [0, vocab_size): True where the token is allowed."""
        if vocab_size <= 0:
            raise ValueError("vocab_size must be positive")
        return [tok in self._allowed for tok in range(vocab_size)]


def mask_for_phase(
    phase: Phase, schema: EmissionSchema | None, vocab_size: int
) -> Sequence[bool] | None:
    """Two-phase rule: a mask only during EMIT; ``None`` (free) otherwise.

    Returning ``None`` means "do not constrain" — the engine samples from the full
    distribution, preserving the pretraining distribution during cognition.
    """
    if phase is Phase.EMIT:
        if schema is None:
            raise ValueError("EMIT phase requires an active schema")
        return schema.mask(vocab_size)
    return None
