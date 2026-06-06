"""Effects and reversibility classes."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum


class ReversibilityClass(Enum):
    IDEMPOTENT = "idempotent"  # re-applying is safe; a read leaves no observable write
    COMPENSABLE = "compensable"  # has an explicit compensation handler
    SNAPSHOT_REVERSIBLE = "snapshot_reversible"  # undone by restoring a snapshot
    IRREVERSIBLE = "irreversible"  # cannot be undone; never speculated


# Only these classes may run on a speculative branch (docs/08).
SPECULATABLE: frozenset[ReversibilityClass] = frozenset(
    {
        ReversibilityClass.IDEMPOTENT,
        ReversibilityClass.COMPENSABLE,
        ReversibilityClass.SNAPSHOT_REVERSIBLE,
    }
)


@dataclass(frozen=True, slots=True)
class Effect:
    """A structured side-effect: how to apply it and how to undo it.

    ``idempotency_key`` lets a retried apply be deduplicated. ``compensate`` is
    required for COMPENSABLE/SNAPSHOT_REVERSIBLE effects (validated below).
    """

    name: str
    reversibility: ReversibilityClass
    apply: Callable[[], None]
    compensate: Callable[[], None] | None = None
    idempotency_key: str | None = None

    def __post_init__(self) -> None:
        needs_handler = self.reversibility in (
            ReversibilityClass.COMPENSABLE,
            ReversibilityClass.SNAPSHOT_REVERSIBLE,
        )
        if needs_handler and self.compensate is None:
            msg = f"{self.reversibility.value} effect {self.name!r} needs a compensate()"
            raise ValueError(msg)

    @property
    def speculatable(self) -> bool:
        return self.reversibility in SPECULATABLE
