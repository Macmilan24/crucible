"""An in-memory ``ControlSurface`` for development and contract tests (no GPU).

It is deterministic and dependency-free. It is NOT an inference engine — it exists
so packages above the wall (grammar, atomix, core) can be built and tested against
the real contract before the SGLang integration lands.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence

from .contract import AdapterId, CacheNodeId, ControlSurface, DraftProposal


class MockEngine(ControlSurface):
    """A trivial, deterministic stand-in for the inference engine."""

    def __init__(self, vocab_size: int = 8) -> None:
        self._vocab_size = vocab_size
        self._next_node = 1
        self._live: set[int] = {0}  # node 0 is the root
        self._active_adapters: set[str] = set()
        self._idle_queue: list[Callable[[], None]] = []

    # (i) logits + masking
    def read_logits(self, node: CacheNodeId) -> Sequence[float]:
        self._require_live(node)
        # A flat distribution is enough for contract tests.
        return [0.0] * self._vocab_size

    def sample(self, node: CacheNodeId, mask: Sequence[bool] | None = None) -> int:
        self._require_live(node)
        logits = list(self.read_logits(node))
        allowed = range(len(logits)) if mask is None else [i for i, ok in enumerate(mask) if ok]
        if not allowed:
            raise ValueError("mask forbids every token; emission cannot proceed")
        # Deterministic: pick the first allowed token.
        return next(iter(allowed))

    # (ii) cache tree
    def fork(self, node: CacheNodeId) -> CacheNodeId:
        self._require_live(node)
        new_id = self._next_node
        self._next_node += 1
        self._live.add(new_id)
        return CacheNodeId(new_id)

    def prune(self, node: CacheNodeId) -> None:
        self._require_live(node)
        if node == 0:
            raise ValueError("cannot prune the root node")
        self._live.discard(int(node))

    # (iii) draft + verifier scores
    def draft(self, node: CacheNodeId, width: int) -> Sequence[DraftProposal]:
        self._require_live(node)
        if width < 0:
            raise ValueError("width must be non-negative")
        return [DraftProposal(tokens=(i,), score=1.0 / (i + 1)) for i in range(width)]

    def verifier_score(self, node: CacheNodeId) -> float:
        self._require_live(node)
        return 0.5

    # (iv) reversible weight edits
    def apply_adapter(self, adapter: AdapterId) -> None:
        self._active_adapters.add(str(adapter))

    def revert_adapter(self, adapter: AdapterId) -> None:
        self._active_adapters.discard(str(adapter))

    # (v) idle scheduling
    def schedule_idle(self, task: Callable[[], None]) -> None:
        self._idle_queue.append(task)

    def run_idle(self) -> int:
        """Run and clear all queued idle tasks (test helper). Returns count run."""
        tasks, self._idle_queue = self._idle_queue, []
        for task in tasks:
            task()
        return len(tasks)

    def _require_live(self, node: CacheNodeId) -> None:
        if int(node) not in self._live:
            raise KeyError(f"cache node {int(node)} is not live")


ROOT = CacheNodeId(0)
