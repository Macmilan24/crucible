from __future__ import annotations

import pytest
from hypothesis import given
from hypothesis import strategies as st

from crucible_atomix import (
    Effect,
    KeyValueStore,
    ReversibilityClass,
    Transaction,
    TransactionAborted,
)


def _failing_effect() -> Effect:
    def boom() -> None:
        raise RuntimeError("boom")

    return Effect(
        name="boom",
        reversibility=ReversibilityClass.COMPENSABLE,
        apply=boom,
        compensate=lambda: None,
    )


def test_successful_settlement_persists() -> None:
    store = KeyValueStore()
    txn = Transaction()
    txn.add(store.set_effect("a", 1))
    txn.add(store.set_effect("b", 2))
    txn.settle()
    assert store.snapshot() == {"a": 1, "b": 2}


def test_irreversible_rejected_on_speculative_branch() -> None:
    txn = Transaction(speculative=True)
    irreversible = Effect(
        name="send_email",
        reversibility=ReversibilityClass.IRREVERSIBLE,
        apply=lambda: None,
    )
    with pytest.raises(ValueError, match="irreversible"):
        txn.add(irreversible)


def test_compensable_requires_handler() -> None:
    with pytest.raises(ValueError, match="needs a compensate"):
        Effect(name="x", reversibility=ReversibilityClass.COMPENSABLE, apply=lambda: None)


@given(
    writes=st.lists(
        st.tuples(st.text(min_size=1, max_size=4), st.integers()),
        min_size=0,
        max_size=12,
    )
)
def test_aborted_transaction_leaves_no_observable_effect(writes: list[tuple[str, int]]) -> None:
    """The core invariant: after an abort, the resource is byte-for-byte its prior state."""
    store = KeyValueStore()
    # Seed some prior state so compensation has something to restore.
    store.set_effect("seed", 99).apply()
    before = store.snapshot()

    txn = Transaction()
    for key, value in writes:
        txn.add(store.set_effect(key, value))
    txn.add(_failing_effect())  # forces an abort partway through

    with pytest.raises(TransactionAborted, match="boom"):
        txn.settle()

    assert store.snapshot() == before
