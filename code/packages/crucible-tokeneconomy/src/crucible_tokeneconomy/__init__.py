"""crucible-tokeneconomy — adaptive Chain-of-Draft + typed KV-cache handoffs."""

from __future__ import annotations

from .budget import (
    DRAFT_MAX_WORDS,
    ReasoningMode,
    StepSignal,
    choose_mode,
    reasoning_token_budget,
)
from .handoff import Handoff

__version__ = "0.0.1"

__all__ = [
    "DRAFT_MAX_WORDS",
    "Handoff",
    "ReasoningMode",
    "StepSignal",
    "__version__",
    "choose_mode",
    "reasoning_token_budget",
]
