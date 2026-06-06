"""A tiny in-memory resource used to build compensable effects (and to test the
abort invariant). Real resources (files, terminals, APIs) implement the same idea
via snapshots / compensation handlers.
"""

from __future__ import annotations

from typing import Any

from .effects import Effect, ReversibilityClass

_MISSING = object()


class KeyValueStore:
    """An observable resource: a dict whose mutations are compensable."""

    def __init__(self) -> None:
        self._data: dict[str, Any] = {}

    def snapshot(self) -> dict[str, Any]:
        return dict(self._data)

    def get(self, key: str) -> Any:
        return self._data.get(key)

    def set_effect(self, key: str, value: Any) -> Effect:
        """Build a COMPENSABLE effect that sets ``key`` and can restore it."""
        prev: Any = _MISSING

        def apply() -> None:
            nonlocal prev
            prev = self._data.get(key, _MISSING)
            self._data[key] = value

        def compensate() -> None:
            if prev is _MISSING:
                self._data.pop(key, None)
            else:
                self._data[key] = prev

        return Effect(
            name=f"set {key!r}",
            reversibility=ReversibilityClass.COMPENSABLE,
            apply=apply,
            compensate=compensate,
            idempotency_key=f"set:{key}",
        )
