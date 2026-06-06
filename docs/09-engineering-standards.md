# 09 — Engineering Standards

How we build, so the codebase stays reviewable, reproducible, and ready for spin-out extraction. Modern, pragmatic, and matched to a research-heavy systems project. Tools here are *documented*; they get *configured* when we scaffold (see [ADR-0006](adr/0006-language-and-tooling.md)).

## Principles

1. **Reproducibility is a feature, not a chore.** For Phase 0, reproducibility *is* the marketing. Every benchmark run logs a manifest (commit, env lockfile, seeds, model hashes, hardware) and is re-runnable from it.
2. **The control-surface contract is typed and enforced.** The orchestrator↔engine interface is the load-bearing API; it gets strict typing and contract tests.
3. **Boundaries over cleverness.** The acyclic package graph (doc 03) is enforced by tooling, not goodwill.
4. **A change that can't be evaluated can't be claimed.** Performance/quality claims land with a reproducible measurement.

## Language & toolchain

| Concern | Tool | Standard |
|---|---|---|
| Language | Python 3.11+ | type hints required on public APIs |
| Env / deps | **uv** | lockfile committed; no unpinned deps |
| Lint + format | **ruff** | zero warnings in CI; format on save |
| Types | **pyright** (strict on `crucible-engine`, `crucible-grammar`, `crucible-gate`) | no `Any` in public signatures |
| Tests | **pytest** + **hypothesis** | property tests for invariants |
| Import boundaries | **import-linter** | the doc-03 dependency graph is the contract |
| Native hot paths | Rust/C++ via PyO3 | only where profiling justifies it |
| Pre-commit | **pre-commit** | lint, type-check, secret-scan before commit |

## Testing strategy (the test pyramid for an inference runtime)

- **Property tests (the foundation).** The grammar's core invariant — *every emitted byte parses against the active schema* — is a property test over generated schemas + inputs, not a handful of examples. Same for Atomix: *an aborted transaction leaves no observable effect.*
- **Unit tests** per package, colocated.
- **Contract tests** for the control-surface contract: a fake/mock engine implements the interface so `crucible-core` can be tested without a GPU.
- **Integration tests** for cross-package flows (top-level `tests/`).
- **Fault-injection tests** for Atomix (success-under-fault is a measured metric, not a hope).
- **Evaluation harness** ([doc 05](05-evaluation-plan.md)) is separate from the test suite but runs in CI on a schedule (it's slow + needs models).
- **Determinism gates.** Seeded runs must be bit-reproducible where the engine allows; non-determinism is documented and bounded.

## CI/CD plan (configured at scaffold time)

Pipeline stages, fail-fast:

```
 lint (ruff) ─▶ type-check (pyright) ─▶ import-boundaries (import-linter)
   ─▶ unit + property tests (pytest/hypothesis, coverage gate)
   ─▶ contract tests (mock engine)
   ─▶ secret + dependency scan
   ─▶ [nightly] integration + fault-injection
   ─▶ [scheduled, GPU runner] evaluation harness on pinned suites
```

- **Coverage gate:** meaningful threshold per package (not a vanity 100%); the gate is on the *contract-critical* packages.
- **Required green** before merge to `main`: lint, types, boundaries, unit+property, contract, scans.
- **Reproducibility artifact:** every eval CI run uploads its manifest + raw logs (we release these publicly for 0a).

## Branching, commits, versioning

- **Trunk-based** with short-lived feature branches; `main` always releasable.
- **Conventional Commits** (`feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`, `perf:`) — drives changelogs and semver.
- **Per-package SemVer** from day one (even inside the monorepo) so spin-out extraction inherits a clean history.
- **ADRs for decisions** that are costly to reverse (see `docs/adr/`). Code that contradicts an ADR must update the ADR first.
- **No direct commits to `main`**; PRs reviewed against the relevant PRD + ADRs + this standard.

## Definition of Done (per change)

- [ ] Code matches the surrounding style; public APIs typed and documented.
- [ ] Tests added/updated; property/contract tests where invariants exist.
- [ ] Import boundaries respected (import-linter green).
- [ ] No secrets; deps pinned; lockfile updated.
- [ ] Any performance/quality claim has a reproducible measurement.
- [ ] Relevant doc (PRD/ADR/glossary/traceability) updated in the same PR.
- [ ] If it touches the control-surface contract, the contract tests and `crucible-engine` types are updated.

## Definition of Ready (before a feature enters build)

- [ ] It maps to a PRD and a roadmap rung.
- [ ] Its evaluation/metric is defined (how we'll know it works).
- [ ] Its risks are in the [Risk Register](07-risk-register.md) with guards.
- [ ] Its package home and dependencies are clear and acyclic.

## Documentation as code

Docs live in-repo, version with the code, and are part of Definition of Done. The numbered `docs/` set is the canonical foundation; PRDs and ADRs are the living layer on top. **A PR that changes behavior without updating the relevant doc is incomplete.**

## Observability (for the runtime, when it exists)

- Structured logging of every step: tokens, latency, compute level (VoI), escalations, gate decisions, rollbacks.
- These logs *are* the eval metrics — instrument once, use for both ops and science.
- Immutable, tamper-evident audit log for self-edits and escalations (security requirement, doc 08).
