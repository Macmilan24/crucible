# ADR-0003 — SGLang as the inference engine of record

- **Status:** accepted
- **Date:** 2026-06-06
- **Deciders:** Samuel Dagne
- **Relates to:** treatise §4.1, §7.1; [Tech Stack](../04-tech-stack.md)

## Context

Crucible needs an inference engine that exposes the control surfaces of Def 3.2: prefix-sharing KV-cache (for cheap branching in VGSS/best-of-N), co-located structured generation (for grammar-scoped emission), and self-speculation (for throughput and unified token/action speculation). Most engines expose none of these below the API wall.

## Options considered

1. **vLLM** — excellent throughput, PagedAttention, wide adoption. *Con: structured generation + cache-tree forking + self-speculation are less integrated for our below-the-wall needs.*
2. **llama.cpp / Ollama** — great for local/CPU, simple deployment. *Con: not built for the cache-tree control, co-located grammar, and RL-path integration we need; better as a 0b token-saver *host* than the core engine.*
3. **SGLang** — RadixAttention prefix sharing, co-located structured generation via XGrammar-2, EAGLE-3 self-speculation; veRL/HybridFlow RL path integration. Matches the treatise's requirements directly.

## Decision

**SGLang is the engine of record.** Crucible adds, on top of it: a trajectory-grammar compiler + two-phase decoding policy, a unified-speculation scheduler with Atomix settlement, a VGSS controller over the cache tree, the VoI budget controller, and an offline STC worker.

## Consequences

- Positive: the control-surface contract has a concrete, capable backend; RadixAttention makes branching affordable on one consumer GPU; RL path is integrated.
- Negative / costs: we depend on SGLang's feature set and release cadence; we pin a version and document the exact features we rely on.
- Commits us to: isolating *all* engine access behind `crucible-engine` so the rest of the system is engine-agnostic. An engine swap then touches one package.

## Revisit when

SGLang stops exposing a control surface we need, or another engine offers the full Def-3.2 surface with materially better local performance. Because access is isolated in `crucible-engine`, re-evaluation is cheap.
