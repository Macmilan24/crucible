# ADR-0005 — The 0b token-saver is a true subset of Product 1

- **Status:** accepted
- **Date:** 2026-06-06
- **Deciders:** Samuel Dagne
- **Relates to:** strategy paper §3.2, §4 (three laws); [PRD 0b](../product/0b-token-saver.md), [PRD P1](../product/p1-core.md)

## Context

The drop-in token-saver (0b) must deliver value on day one with a one-line install and a one-flag enable, slotting under whatever agent the developer already runs (a local model via Ollama/vLLM, or a popular framework). The temptation is to build it as a quick standalone hack. But one of the portfolio's three laws is **true subset**: every product must be a real slice of the final architecture, never a throwaway. If 0b forks from Core, we maintain two codebases and the funnel breaks.

## Options considered

1. **Standalone throwaway wrapper** — fastest to ship. *Con: violates the true-subset law; becomes tech debt; diverges from Core.*
2. **0b = a thin façade over a subset of `crucible-core`** — the token-economy + grammar primitives are imported from the same packages Core uses; 0b just packages them for drop-in use under an existing agent.

## Decision

**Option 2.** `apps/token-saver` depends only on a *subset* of `crucible-core` (the grammar-scoped emission + Chain-of-Draft + KV-cache primitives) and adds host adapters (Ollama/vLLM/framework hooks). It shares code with Core; it does not fork it.

## Consequences

- Positive: a developer who adopts 0b has already integrated a Crucible primitive — the integrated runtime becomes the obvious upgrade (the funnel works); one codebase.
- Negative / costs: 0b's "one-line install, one-flag enable" simplicity constrains how the shared primitives are packaged (they must be usable without the full runtime).
- Commits us to: designing the token-economy + grammar packages so they are usable *both* standalone (0b) and inside the full loop (Core) — clean public APIs, no hidden dependence on later layers.

## Revisit when

The drop-in distribution requirements diverge so far from Core that sharing code costs more than a (carefully versioned) split.
