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
from .runner import (
    BenchReport,
    MalformedResult,
    TokenEconomyResult,
    compounding_projection,
    extract_int,
    run_all,
    run_malformed,
    run_token_economy,
)
from .stats import bootstrap_ci, mean
from .suite import REASONING_TASKS, TOOL_TASKS, ReasoningTask, ToolTask

__version__ = "0.0.1"

__all__ = [
    "PHASE0_MIN_TOKEN_REDUCTION",
    "REASONING_TASKS",
    "TOOL_TASKS",
    "ArmResult",
    "BenchReport",
    "GateResult",
    "MalformedResult",
    "ReasoningTask",
    "RunManifest",
    "TokenEconomyResult",
    "ToolTask",
    "__version__",
    "bootstrap_ci",
    "compounding_projection",
    "extract_int",
    "mean",
    "passes_phase0_gate",
    "run_all",
    "run_malformed",
    "run_token_economy",
    "success_is_matched",
    "token_reduction_factor",
]
