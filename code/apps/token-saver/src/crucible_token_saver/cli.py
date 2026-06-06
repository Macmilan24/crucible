"""Minimal CLI entry point (placeholder).

The real CLI will discover the user's agent (Ollama/vLLM/framework) and enable the
saver with one flag. For now it reports status so the console-script wiring is real.
"""

from __future__ import annotations

import sys

from . import __version__


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if args and args[0] in {"-v", "--version"}:
        print(f"crucible-token-saver {__version__}")
        return 0
    print(
        "crucible-token-saver (scaffold)\n"
        "  Drop-in token-saver for local agents — grammar-scoped emission +\n"
        "  adaptive Chain-of-Draft. Host adapters land with the real build.\n"
        "  Try: crucible-token-saver --version"
    )
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
