"""crucible-engine — the inference-native control-surface contract.

Public API only. Internal modules (if any) live under ``_internal`` and must not
be imported by other packages (enforced by .importlinter).
"""

from __future__ import annotations

from .contract import (
    AdapterId,
    CacheNodeId,
    ControlSurface,
    DraftProposal,
    Generation,
)
from .llama_backend import LlamaCppEngine
from .mock import ROOT, MockEngine

__version__ = "0.0.1"

__all__ = [
    "ROOT",
    "AdapterId",
    "CacheNodeId",
    "ControlSurface",
    "DraftProposal",
    "Generation",
    "LlamaCppEngine",
    "MockEngine",
    "__version__",
]
