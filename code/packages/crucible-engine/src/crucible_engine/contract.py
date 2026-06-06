"""The control-surface contract: the typed orchestrator↔engine boundary.

This is the load-bearing API of the whole system (docs/02-architecture.md). It is
the precise, programmable form of Definition 3.2 ("inference-native orchestrator")
from the treatise. Prior, API-bounded systems can express *none* of these
capabilities — that is the entire point of being "below the wall".

Status: provisional contract for the scaffold. Types are intentionally minimal and
backend-agnostic (no torch/SGLang import here) so the contract can be type-checked
and mock-tested with no GPU. The SGLang-backed implementation will refine these.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import NewType, Protocol, runtime_checkable

# Opaque handles. The orchestrator holds these; it never copies engine state.
CacheNodeId = NewType("CacheNodeId", int)
AdapterId = NewType("AdapterId", str)


@dataclass(frozen=True, slots=True)
class DraftProposal:
    """A speculative continuation proposed by the draft head (control surface iii)."""

    tokens: tuple[int, ...]
    score: float


@runtime_checkable
class ControlSurface(Protocol):
    """The five inference-native control surfaces (Def. 3.2 / docs/02 contract table).

    (i)   read logits and apply a mask before sampling
    (ii)  read / fork / prune the KV-cache tree
    (iii) read draft proposals and process-reward scores
    (iv)  apply persistent but reversible weight updates (ROSE adapters)
    (v)   schedule idle computation (STC)
    """

    # (i) logits + masking -------------------------------------------------
    def read_logits(self, node: CacheNodeId) -> Sequence[float]:
        """Return the next-token logit vector at ``node`` (no sampling yet)."""
        ...

    def sample(self, node: CacheNodeId, mask: Sequence[bool] | None = None) -> int:
        """Sample the next token at ``node``, optionally masking disallowed tokens.

        Masking is how grammar-scoped *emission* is enforced (crucible-grammar);
        cognition is sampled with ``mask=None`` so reasoning is never constrained.
        """
        ...

    # (ii) cache tree ------------------------------------------------------
    def fork(self, node: CacheNodeId) -> CacheNodeId:
        """Fork the cache at ``node`` (cheap, prefix-shared) for a new branch."""
        ...

    def prune(self, node: CacheNodeId) -> None:
        """Discard a branch and free its cache subtree."""
        ...

    # (iii) draft + verifier scores ---------------------------------------
    def draft(self, node: CacheNodeId, width: int) -> Sequence[DraftProposal]:
        """Return up to ``width`` speculative continuations from the draft head."""
        ...

    def verifier_score(self, node: CacheNodeId) -> float:
        """Return the process-verifier value estimate for the state at ``node``."""
        ...

    # (iv) reversible weight edits ----------------------------------------
    def apply_adapter(self, adapter: AdapterId) -> None:
        """Activate a reversible ROSE adapter (a separable tensor)."""
        ...

    def revert_adapter(self, adapter: AdapterId) -> None:
        """Deactivate/drop an adapter — rollback is dropping a tensor, not a rebuild."""
        ...

    # (v) idle scheduling --------------------------------------------------
    def schedule_idle(self, task: Callable[[], None]) -> None:
        """Queue work for a sleep-time (STC) window, off the interactive path."""
        ...
