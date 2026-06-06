"""crucible-grammar — two-phase decoding (constrain emission, never cognition)."""

from __future__ import annotations

from .emission import EmissionSchema, mask_for_phase
from .trajectory import Phase, TrajectoryGrammar

__version__ = "0.0.1"

__all__ = [
    "EmissionSchema",
    "Phase",
    "TrajectoryGrammar",
    "__version__",
    "mask_for_phase",
]
