# User Guide

Welcome to **Crucible Core** — a local agent runtime that turns a small model on your
own machine into a reliable, tool-using agent, and serves it behind the **OpenAI API**
so your existing tools just work.

What you get:

- **`crucible serve`** — an OpenAI-compatible server. Point opencode, Continue, Cursor,
  or the `openai` SDK at it.
- **Grammar-guaranteed tool calls** — when a request includes `tools`, the reply is a
  structurally valid tool call *by construction* (zero malformed calls).
- **100% local** — no API keys, no telemetry, nothing leaves your machine.

<div class="grid cards" markdown>

-   :material-download: **[Install](install.md)**

    One-liner, from source, or from a release wheelhouse.

-   :material-rocket-launch: **[Quickstart](quickstart.md)**

    Download a model, start the server, make your first tool call.

-   :material-console: **[The `crucible` CLI](cli.md)**

    `serve`, `download-model`, `doctor`, `version`.

-   :material-robot: **[Connect opencode](opencode.md)**

    Wire Crucible in as a local provider.

</div>

!!! note "Status"
    This is **Product 1: Crucible Core** — the token-saving, tool-calling runtime. It is
    real, tested, and benchmarked. Later products (process verifier, search, memory,
    self-improvement) are on the [roadmap](../dev/roadmap.md).
