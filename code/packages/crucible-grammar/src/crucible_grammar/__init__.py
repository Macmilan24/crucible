"""crucible-grammar — two-phase decoding (constrain emission, never cognition)."""

from __future__ import annotations

from .emission import EmissionSchema, mask_for_phase
from .gbnf import ToolSchema, action_gbnf, is_valid_tool_call, tool_call_gbnf
from .trajectory import Phase, TrajectoryGrammar

__version__ = "0.0.1"

__all__ = [
    "EmissionSchema",
    "Phase",
    "ToolSchema",
    "TrajectoryGrammar",
    "__version__",
    "action_gbnf",
    "is_valid_tool_call",
    "mask_for_phase",
    "tool_call_gbnf",
]
