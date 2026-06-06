"""crucible-atomix — transactional settlement for agent tool calls."""

from __future__ import annotations

from .effects import SPECULATABLE, Effect, ReversibilityClass
from .store import KeyValueStore
from .transaction import Transaction, TransactionAborted

__version__ = "0.0.1"

__all__ = [
    "SPECULATABLE",
    "Effect",
    "KeyValueStore",
    "ReversibilityClass",
    "Transaction",
    "TransactionAborted",
    "__version__",
]
