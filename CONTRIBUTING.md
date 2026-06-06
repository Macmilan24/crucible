# Contributing to Crucible

This is how we work — whether "we" is the author, a future teammate, or an AI engineer pairing on the code. It's short on purpose; the detail lives in [`docs/`](docs/).

## Before you write code

1. **Read the foundation.** Start at the [README](README.md) and the numbered docs. At minimum know the [Vision & Scope](docs/00-vision-and-scope.md), the [Architecture](docs/02-architecture.md), and the [Glossary](docs/01-glossary.md).
2. **Find the PRD and the rung.** Every change maps to a [PRD](docs/product/) and a [Roadmap](docs/06-roadmap.md) rung. If it doesn't, it's not ready (see Definition of Ready in [Engineering Standards](docs/09-engineering-standards.md)).
3. **Respect the invariants.** The seven design principles ([doc 00](docs/00-vision-and-scope.md)) and the architectural invariants (separate fault domains; constrain emission not cognition; the loop expands competence not authority) are non-negotiable. A change that appears to break one must say so explicitly and justify it via an ADR.

## The working rhythm

- **Decisions of consequence get an [ADR](docs/adr/)** before the code. Code that contradicts an accepted ADR updates the ADR first.
- **Trunk-based**, short-lived branches; `main` always releasable.
- **[Conventional Commits](https://www.conventionalcommits.org/)** (`feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `perf:`, `chore:`).
- **Docs ship with code.** A PR that changes behavior without updating the relevant PRD/ADR/glossary/[traceability matrix](docs/10-traceability-matrix.md) is incomplete.
- **Claims need measurements.** Any performance/quality claim lands with a reproducible number ([ADR-0009](docs/adr/0009-evaluation-as-product-gate.md)).

## Quality bar

Every change satisfies the **Definition of Done** in [Engineering Standards](docs/09-engineering-standards.md): typed public APIs, tests (property/contract where invariants exist), import boundaries green, no secrets, deps pinned, relevant doc updated. The control-surface contract and the grammar are property-tested — invariants, not examples.

## Package boundaries

The repo is a [monorepo designed for spin-out extraction](docs/03-repo-and-modularization.md). One package = one responsibility = one future repo. Never import another package's internals — only its public API. `import-linter` enforces this; if it fails, the design is wrong, not the linter.

## Security & privacy are not optional

Read the [Threat Model](docs/08-security-threat-model.md). Data stays on the device; tools run sandboxed under a declared capability schema; secrets never enter prompts/logs/memory/federation; self-edit and escalation logs are immutable. New tools trigger a capability-schema review.

## When in doubt

Prefer the boring, reversible choice. Surface the trade-off. Update the doc. Measure the claim.
