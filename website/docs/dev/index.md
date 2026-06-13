# Developer Docs

How Crucible works under the hood, and how to build on or contribute to it.

Crucible is a **uv workspace** of small, single-responsibility packages with a strict,
enforced dependency graph. Product 1 — **Crucible Core** — is the three token-savers, the
agent loop, transactional settlement, and the OpenAI-compatible server.

<div class="grid cards" markdown>

-   :material-layers: **[Architecture](architecture.md)**

    The six layers, the API-boundary wall, the control-surface contract.

-   :material-fire: **[The three token-savers](token-savers.md)**

    Grammar-scoped emission, Chain-of-Draft, KV-cache reuse — with real numbers.

-   :material-code-braces: **[Grammar & two-phase decoding](grammar.md)**

    How a malformed tool call becomes structurally impossible.

-   :material-sync: **[The agent loop](agent-loop.md)**

    THINK → EMIT → SETTLE, with failure recovery.

-   :material-connection: **[Engine contract](engine-contract.md)**

    The orchestrator↔engine boundary — the five control surfaces.

-   :material-package-variant: **[Package map](packages.md)**

    What each package does and the rules that keep the graph clean.

-   :material-chart-line: **[Benchmarks](benchmarks.md)**

    Methodology, real results, and how to reproduce them.

-   :material-map: **[Roadmap](roadmap.md)** · :material-hand-heart: **[Contributing](contributing.md)**

</div>

## The one-paragraph version

Today's agents reach the model through a stateless text API, throwing away the KV-cache,
the logits, the draft proposals, and the verifier scores on every call. Crucible places the
agent loop **below that wall** and uses those control surfaces directly: it masks logits to
guarantee valid tool calls, dials reasoning length per step, and reuses the KV-cache across
turns. The thesis is that the gap for local agents is **architectural, not parameters** —
and Product 1 is the measured proof of the cheapest part of that claim.
