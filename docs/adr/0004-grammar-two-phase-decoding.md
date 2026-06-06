# ADR-0004 — XGrammar-2 + two-phase decoding (constrain emission, not cognition)

- **Status:** accepted
- **Date:** 2026-06-06
- **Deciders:** Samuel Dagne
- **Relates to:** treatise §4.2.1, §4.4.2, §7.5.2; Principle 3.2; [Architecture](../02-architecture.md)

## Context

Structural reliability must be near-perfect: at 95% per-step validity a 20-step episode has ~64% chance of *some* malformed action; production agency needs ≥99.9%/step, unreachable by prompting. Grammar-constrained decoding can pin structural validity at 100%. **But** forcing the *whole trajectory* into a grammar measurably degrades reasoning ("structure snowballing") — a real failure of Crucible's earlier drafts. The decoder masks logits, so if the model's natural reasoning continuation momentarily violates the schema, it's forced onto a lower-probability token and the chain derails.

## Options considered

1. **Constrain the whole trajectory** — guarantees structure everywhere. *Con: degrades reasoning; rejected by evidence.*
2. **No constraint, parse + retry** — preserves reasoning. *Con: malformed calls happen and compound; wasted retry tokens; what everyone does today.*
3. **Two-phase: free cognition, constrained emission** — cognition phase is fully unconstrained (full logits, pretraining distribution preserved); on a trigger tag (XGrammar-2 TagDispatch) the schema grammar activates for the emission only, then releases. A tiny trajectory grammar governs only the *sequence* of phases.

## Decision

**Option 3.** Adopt XGrammar-2 with TagDispatch for two-phase decoding. Constrain only the bytes a tool must parse; never mask reasoning. Add a **failure-recovery diagnostic mode**: on tool failure or verifier rejection, drop all grammar constraints for the next reflection, let the model diagnose in free NL, penalize superficial syntactic fixes, and re-engage the mask only after the verifier confirms the *semantic* error was restructured. Where even emission benefits, a fallback NL-to-format pass reasons free then translates to schema.

## Consequences

- Positive: malformed-action rate → 0 by construction *and* reasoning intact — the two are obtained simultaneously, not traded off. This is the wedge's core reliability claim.
- Negative / costs: the trigger-tag plumbing couples to the engine; the trajectory grammar `G_traj` and per-tool schemas must be authored and tested.
- Commits us to: a `crucible-grammar` package with the trajectory grammar + emission masking; the property-test invariant *every emitted byte parses*; honest messaging — grammar solves *structure*, not *facts* (factual hallucination is the verifier's job).

## Revisit when

A future engine offers an equivalent or better emission-only constraint mechanism, or evidence shows the two-phase boundary itself harms a class of tasks.
