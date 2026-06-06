"""Adaptive reasoning budget (a stand-in for the VoI controller).

Principle 3.3: spend compute by its value. Brevity (Chain-of-Draft) is applied only
where it is safe — trivial, single-file, in-scope steps — and suspended (full
free-text reasoning) on anything pivotal. This heuristic is deliberately
conservative: when in doubt, reason fully.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

# Chain-of-Draft constrains each reasoning step to a terse sketch.
DRAFT_MAX_WORDS = 5


class ReasoningMode(Enum):
    DRAFT = "draft"  # terse, ~5-word sketch (cheap)
    FULL = "full"  # full free-text reasoning (or hand off to a VGSS expansion)


@dataclass(frozen=True, slots=True)
class StepSignal:
    """What the controller knows about a step before deciding how hard to think."""

    verifier_value: float  # in [0, 1]; low ⇒ the model is unsure ⇒ think more
    touches_multiple_files: bool = False
    cross_scope: bool = False


def choose_mode(signal: StepSignal, *, confidence_floor: float = 0.6) -> ReasoningMode:
    """Pick a reasoning mode. FULL whenever the step is risky; DRAFT only when safe."""
    if signal.touches_multiple_files or signal.cross_scope:
        return ReasoningMode.FULL
    if signal.verifier_value < confidence_floor:
        return ReasoningMode.FULL
    return ReasoningMode.DRAFT


def reasoning_token_budget(mode: ReasoningMode, *, full_budget: int = 512) -> int:
    """Map a mode to a token budget. DRAFT is a few words; FULL is the full budget."""
    if full_budget <= 0:
        raise ValueError("full_budget must be positive")
    if mode is ReasoningMode.DRAFT:
        return DRAFT_MAX_WORDS * 2  # ~2 tokens/word, a tight cap
    return full_budget
