"""crucible-server — an OpenAI-compatible local runtime with grammar-guaranteed tool calls."""

from __future__ import annotations

from .app import create_app, tool_schemas_from_openai

__version__ = "0.1.0"

__all__ = ["__version__", "create_app", "tool_schemas_from_openai"]
