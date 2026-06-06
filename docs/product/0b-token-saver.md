# PRD 0b — The Drop-in Token-Saver

> The "come for the tool" artifact. Delivers value on day one, asks for no trust (local + open-source), and is a **genuine subset of Product 1** (see [ADR-0005](../adr/0005-token-saver-as-true-subset.md)).

## Pain

Developers running local agents bleed tokens (latency/throughput locally; budget on metered cloud) and ship malformed tool calls that trigger retry loops. They want the win *without* adopting a whole new runtime.

## What it is

A tiny, dependency-light wrapper that slots **under whatever agent the developer already runs** — a local model via Ollama/vLLM, or a popular agent framework — and returns the same answers for a fraction of the tokens, with malformed calls eliminated.

- **One-line install.**
- **One-flag enable.**
- Same answers; fewer tokens; zero malformed calls.

## Users

Individual developers and small teams running local agents who feel the token/reliability pain but won't (yet) switch their whole stack.

## Scope

- A wrapper/shim packaged from a **subset of `crucible-core`**: grammar-scoped emission + Chain-of-Draft + KV-cache reuse.
- **Host adapters**: Ollama, vLLM, and at least one popular framework hook.
- Trivial install + a single enable flag; sensible defaults; no config required to get the win.
- Telemetry-free by default (privacy posture); optional local stats the user can see.

## Out of scope

The full agent loop, self-improvement, memory, verifier. 0b is the thin edge — it must stay thin.

## Aha demo

`pip install` (or equivalent) + one flag → the user's existing agent now reports markedly fewer tokens and zero malformed calls, on the same tasks, locally.

## Acceptance criteria

- [ ] Install is genuinely one line; enable is genuinely one flag.
- [ ] Works as a drop-in under at least Ollama and vLLM, plus one framework.
- [ ] Same task outcomes as the user's unwrapped agent (no quality regression).
- [ ] Measurable token reduction and malformed-rate → 0 on the user's own workload.
- [ ] Shares code with `crucible-core` (no fork) — verified by the dependency graph (import-linter).
- [ ] Runs fully locally; no data leaves the device.

## Success metric

Weekly active installs; conversion from 0c calculator traffic; qualitative "it just worked" signal.

## ⛔ Kill-criterion

Real-world savings marginal (< 2×) on actual user workloads, or install/enable friction high enough that adoption stalls.

## Dependency / funnel

Depends on the token-economy + grammar primitives from `crucible-core`. Funnels to **Product 1** (the integrated runtime is the obvious upgrade once the developer has felt the primitive's value) and is fed by **0c** (the calculator) and **0a** (the benchmark).
