"""Benchmark metrics and the Phase-0 master gate.

The gate is the falsifiable kill-criterion from the strategy paper and the eval
plan: if independent reproductions show < 2x end-to-end token reduction *at matched
success*, stop and re-scope before building Product 1.
"""

from __future__ import annotations

from dataclasses import dataclass

PHASE0_MIN_TOKEN_REDUCTION = 2.0  # the master kill-criterion threshold
DEFAULT_SUCCESS_TOLERANCE = 0.02  # "matched success" within 2 percentage points


@dataclass(frozen=True, slots=True)
class ArmResult:
    """One benchmark arm (e.g. the stock agent, or the Crucible arm)."""

    name: str
    mean_tokens: float
    malformed_rate: float
    success_rate: float

    def __post_init__(self) -> None:
        if self.mean_tokens <= 0:
            raise ValueError("mean_tokens must be positive")
        for field_name in ("malformed_rate", "success_rate"):
            v = getattr(self, field_name)
            if not 0.0 <= v <= 1.0:
                raise ValueError(f"{field_name} must be in [0, 1]")


def token_reduction_factor(stock: ArmResult, crucible: ArmResult) -> float:
    """How many times fewer tokens the Crucible arm uses (>1 means a saving)."""
    return stock.mean_tokens / crucible.mean_tokens


def success_is_matched(
    stock: ArmResult, crucible: ArmResult, tolerance: float = DEFAULT_SUCCESS_TOLERANCE
) -> bool:
    """Crucible must not buy token savings by giving up task success."""
    return crucible.success_rate >= stock.success_rate - tolerance


@dataclass(frozen=True, slots=True)
class GateResult:
    passed: bool
    reduction_factor: float
    matched_success: bool
    reason: str


def passes_phase0_gate(
    stock: ArmResult,
    crucible: ArmResult,
    *,
    min_reduction: float = PHASE0_MIN_TOKEN_REDUCTION,
    success_tolerance: float = DEFAULT_SUCCESS_TOLERANCE,
) -> GateResult:
    """Evaluate the Phase-0 master gate. Both conditions must hold."""
    factor = token_reduction_factor(stock, crucible)
    matched = success_is_matched(stock, crucible, success_tolerance)

    if not matched:
        return GateResult(
            False, factor, matched, "success regressed beyond tolerance — savings are not real"
        )
    if factor < min_reduction:
        return GateResult(
            False, factor, matched, f"token reduction {factor:.2f}x < required {min_reduction:.2f}x"
        )
    return GateResult(
        True, factor, matched, f"passed: {factor:.2f}x token reduction at matched success"
    )
