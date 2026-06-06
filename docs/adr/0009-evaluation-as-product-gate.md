# ADR-0009 — Evaluation is the product gate (science = business)

- **Status:** accepted
- **Date:** 2026-06-06
- **Deciders:** Samuel Dagne
- **Relates to:** treatise §7.2, §2.4–2.5; strategy paper §10; [Evaluation Plan](../05-evaluation-plan.md)

## Context

Crucible has an unusual property: the treatise's evaluation questions *are* the product go/no-go gates, and each carries a falsifiable kill-criterion. We could treat evaluation as a downstream QA activity. That would be a mistake — it would let us build rungs whose value isn't proven and ship claims we can't reproduce.

## Decision

**Evaluation is a first-class, pre-registered gate, not downstream QA.**

- Pre-register RQs, baselines, suites, metrics, and effect sizes *before* building each rung.
- The **fair baseline is always `Φ(θ_fr)`** (frontier in the identical harness), never an unscaffolded frontier.
- Each rung has a **kill-criterion**; failing it means stop/re-scope, not push on.
- **Reproducibility is a launch requirement** for 0a — all raw per-epoch logs + run manifests released.
- Holdout refresh uses **execution as a free oracle** (tests/compilers), not paid teacher calls.
- Statistics: ≥3 seeds, paired bootstrap CIs, Holm–Bonferroni across RQs, per-domain win/loss for the thesis.

## Consequences

- Positive: every claim is defensible and reproducible; the kill-criteria prevent sunk-cost climbing; "the plan is testable, not aspirational."
- Negative / costs: more upfront rigor; eval harness is real engineering (it's in scope as `bench/crucible-bench`); GPU CI runners needed for full suites.
- Commits us to: building the benchmark harness as a real package; the [traceability matrix](../10-traceability-matrix.md) staying in sync; treating a fired falsifier as a signal to act, not to rationalize.

## Revisit when

Never for the principle. Specific suites/metrics evolve (e.g. as contamination shifts which benchmarks are trustworthy) — those updates amend the Evaluation Plan, not this ADR.
