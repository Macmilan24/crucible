"""crucible-bench — the 0a reproducible benchmark harness."""

from __future__ import annotations

from .manifest import RunManifest
from .metrics import (
    PHASE0_MIN_TOKEN_REDUCTION,
    ArmResult,
    GateResult,
    passes_phase0_gate,
    success_is_matched,
    token_reduction_factor,
)

__version__ = "0.0.1"

__all__ = [
    "PHASE0_MIN_TOKEN_REDUCTION",
    "ArmResult",
    "GateResult",
    "RunManifest",
    "__version__",
    "passes_phase0_gate",
    "success_is_matched",
    "token_reduction_factor",
]
