# ADR-0002 — Monorepo now, polyrepo-ready package boundaries

- **Status:** accepted
- **Date:** 2026-06-06
- **Deciders:** Samuel Dagne
- **Relates to:** [Repo & Modularization](../03-repo-and-modularization.md); strategy paper §5 (spin-outs)

## Context

The strategy paper ships Crucible as a portfolio: a vertical product ladder *and* six horizontal spin-out libraries that are independently useful and funnel developers back to the platform. Early on, a solo author benefits from a single repo (atomic changes, one CI, easy refactors). But each spin-out must eventually become its own public OSS repo with a clean history. We want the early-stage velocity of a monorepo without paying a painful split later. The user's explicit preference: "start as monorepo, move to polyrepo as we build."

## Options considered

1. **Polyrepo from day one** — maximal independence. *Con: heavy coordination overhead for a solo author; cross-cutting changes span many PRs; premature.*
2. **Monorepo forever** — simplest. *Con: contradicts the spin-out strategy; a single license/visibility blob; harder to position individual libraries as ecosystem defaults.*
3. **Monorepo now with strict, polyrepo-ready boundaries** — one repo, but packages are designed as if already separate: one-directional acyclic deps, explicit public APIs, per-package versioning + licensing, no shared "utils" god-package.

## Decision

**Option 3.** Build in a private monorepo; enforce the package graph in [doc 03](../03-repo-and-modularization.md) with `import-linter`; extract spin-outs to their own public repos (via `git subtree split`, preserving history) when each stabilizes.

## Consequences

- Positive: fast iteration now; extraction later is "move a directory + flip visibility", not a refactor; per-package SemVer/changelog from day one.
- Negative / costs: boundary discipline must be enforced by tooling and review from the start (it's tempting to reach across packages); per-package metadata is extra upkeep.
- Commits us to: import-boundary CI gate; the extraction playbook in doc 03; per-package version + license metadata even inside the monorepo.

## Revisit when

A spin-out's external contributor community or release cadence diverges enough from the platform that living in the monorepo costs more than the split — then extract it (expected, not a failure).
