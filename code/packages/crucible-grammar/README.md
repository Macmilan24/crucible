# crucible-grammar 🟢

Two-phase decoding: cognition is **unconstrained**; only the structured **emission**
is grammar-masked, switched on by a trigger tag and released after. This pins the
per-step structural-validity line at 1 by construction — zero *structural*
hallucination — while leaving reasoning intact.

- Spec: [`../../../docs/02-architecture.md`](../../../docs/02-architecture.md) (Layer 1, two-phase decoding)
- Decision: [ADR-0004](../../../docs/adr/0004-grammar-two-phase-decoding.md)
- Glossary: two-phase decoding, structure snowballing

Trajectory grammar (governs only the *sequence* of phases, never reasoning content):
```
⟨episode⟩ ::= ( ⟨think⟩ (⟨emit⟩ | ⟨reflect⟩) )* ⟨halt⟩
⟨think⟩ → Σ* (free)        ⟨emit⟩ → schema
```

**Core invariant (property-tested):** every token the masked decoder can emit is
accepted by the active schema. Grammar solves *structure*; it never claims to solve
*facts* (that is the verifier's job).

**Status:** scaffold — a finite-state phase machine and a schema-mask primitive
that hold the invariant. The XGrammar-2 TagDispatch integration replaces the toy
schema later, behind this same API.
