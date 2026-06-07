"""crucible-core — the inference-native orchestrator (Product 1)."""

from __future__ import annotations

from .agent import Agent, EpisodeResult
from .loop import ChatEngine, Step, TaskResult, run_task
from .substrate import Substrate
from .tools import (
    Tool,
    ToolRegistry,
    calculator_tool,
    read_file_tool,
    safe_arithmetic,
)

__version__ = "0.0.1"

__all__ = [
    "Agent",
    "ChatEngine",
    "EpisodeResult",
    "Step",
    "Substrate",
    "TaskResult",
    "Tool",
    "ToolRegistry",
    "__version__",
    "calculator_tool",
    "read_file_tool",
    "run_task",
    "safe_arithmetic",
]
