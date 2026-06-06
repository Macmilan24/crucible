# ADR-0006 — Python 3.11+ and the toolchain baseline

- **Status:** accepted
- **Date:** 2026-06-06
- **Deciders:** Samuel Dagne
- **Relates to:** [Tech Stack](../04-tech-stack.md), [Engineering Standards](../09-engineering-standards.md)

## Context

The inference/RL ecosystem we depend on (SGLang, veRL/HybridFlow, PyTorch, XGrammar) is Python. We need fast iteration and access to that ecosystem, but also strict boundaries and types because the control-surface contract is load-bearing. Hot paths (grammar masking, IPC, snapshotting) may need native speed.

## Decision

- **Python 3.11+** as the primary language; type hints required on public APIs.
- **Rust/C++ via PyO3 / native extensions** only where profiling demands, confined to specific packages.
- Toolchain: **uv** (deps + lockfile), **ruff** (lint+format), **pyright** (strict on `crucible-engine`, `crucible-grammar`, `crucible-gate`), **pytest + hypothesis** (tests + property tests), **import-linter** (boundaries), **pre-commit** (pre-commit hooks).

## Consequences

- Positive: full access to the inference/RL ecosystem; fast iteration; strong typing where it matters; reproducible envs.
- Negative / costs: Python's runtime overhead on hot loops (mitigated by native extensions where measured); strict typing/boundary discipline is upfront effort.
- Commits us to: the CI gate composition in [doc 09](../09-engineering-standards.md); lockfile-first dependency management; no unpinned deps.

## Revisit when

A hot path proves un-fixable in Python and warrants a larger native component, or the ecosystem shifts.
