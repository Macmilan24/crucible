"""Real agent loop on a real model with real tools.

Watch Qwen2.5-3B actually solve tasks on your machine by calling sandboxed tools,
with every action structurally valid by construction (0 malformed) and settled
through Atomix.

Run with:  cd code && uv run python tools/agent_demo.py
"""

from __future__ import annotations

import tempfile
from pathlib import Path

from crucible_core import ToolRegistry, calculator_tool, read_file_tool, run_task
from crucible_engine import LlamaCppEngine

MODEL = Path(__file__).resolve().parents[1] / "models" / "Qwen2.5-3B-Instruct-Q4_K_M.gguf"


def show(title: str, task: str, engine: LlamaCppEngine, registry: ToolRegistry) -> None:
    print("=" * 68)
    print(f"TASK: {title}\n  {task}")
    print("-" * 68)
    result = run_task(engine, registry, task, max_steps=6)
    for i, step in enumerate(result.steps, 1):
        print(f"  step {i}: action = {step.action}")
        if step.observation is not None:
            print(f"          observation = {step.observation}")
    print(f"  FINAL: {result.final}")
    print(
        f"  (tool calls: {result.tool_calls}, malformed actions: {result.malformed}, "
        f"completion tokens: {result.completion_tokens})\n"
    )


def main() -> None:
    if not MODEL.exists():
        print(f"Model not found at {MODEL} (see code/README.md).")
        raise SystemExit(1)

    workspace = Path(tempfile.mkdtemp(prefix="crucible-ws-"))
    (workspace / "numbers.txt").write_text("10\n20\n30\n40\n")

    print("Loading real model (Qwen2.5-3B, Metal)... ", flush=True)
    engine = LlamaCppEngine(str(MODEL), seed=0)
    print("loaded.\n")

    registry = ToolRegistry()
    registry.register(calculator_tool())
    registry.register(read_file_tool(workspace))

    show("single tool", "What is 23 * 47 + 19? Use the calculator tool.", engine, registry)
    show(
        "multi-step",
        "The file numbers.txt contains one number per line. Read it, then use the "
        "calculator to compute the sum of all the numbers.",
        engine,
        registry,
    )

    print("Every action above was grammar-constrained, so 'malformed actions' is 0 by")
    print("construction; tool calls were settled (and rolled back on error) via Atomix.")


if __name__ == "__main__":
    main()
