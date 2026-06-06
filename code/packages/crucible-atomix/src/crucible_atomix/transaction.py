"""Atomic settlement: a transaction settles all effects or aborts cleanly."""

from __future__ import annotations

from .effects import Effect, ReversibilityClass


class TransactionAborted(RuntimeError):
    """Raised when settlement fails; on raise, all applied effects are compensated."""


class Transaction:
    """A group of effects that settle atomically or leave no observable effect.

    ``speculative=True`` forbids irreversible effects (they may never run on a
    speculative branch).
    """

    def __init__(self, *, speculative: bool = True) -> None:
        self._speculative = speculative
        self._effects: list[Effect] = []
        self._applied: list[Effect] = []
        self._settled = False

    def add(self, effect: Effect) -> None:
        if self._settled:
            raise RuntimeError("cannot add effects to a settled transaction")
        if self._speculative and effect.reversibility is ReversibilityClass.IRREVERSIBLE:
            raise ValueError(
                f"irreversible effect {effect.name!r} cannot run in a speculative transaction"
            )
        self._effects.append(effect)

    def settle(self) -> None:
        """Apply every effect in order. If any raises, compensate in reverse and abort."""
        for effect in self._effects:
            try:
                effect.apply()
            except Exception as exc:  # intentional broad catch: re-raised as TransactionAborted
                self._abort()
                raise TransactionAborted(f"effect {effect.name!r} failed: {exc}") from exc
            self._applied.append(effect)
        self._settled = True

    def _abort(self) -> None:
        # Compensate already-applied effects in reverse order (LIFO).
        for effect in reversed(self._applied):
            if effect.compensate is not None:
                effect.compensate()
        self._applied.clear()
