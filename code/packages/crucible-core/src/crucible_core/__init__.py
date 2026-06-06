"""crucible-core — the inference-native orchestrator (Product 1)."""

from __future__ import annotations

from .agent import Agent, EpisodeResult
from .substrate import Substrate

__version__ = "0.0.1"

__all__ = [
    "Agent",
    "EpisodeResult",
    "Substrate",
    "__version__",
]
