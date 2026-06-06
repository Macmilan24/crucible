# 00 — Vision & Scope

## The wager

A locally-hosted 7–9B model loses to a frontier model on almost any single open-ended prompt. Crucible nonetheless defends a precise and achievable claim: **a system built around such a model, running privately on a user's own machine, can surpass a frozen frontier model on *that user's own distribution of work* — at a fraction of the cost, leaking none of the user's data, and improving every week it is used.**

The wager is *not* that small models are secretly as smart as large ones. It is that the gap that matters for agents is **architectural, not parametric**, and the architecture that closes it has not been built because everyone is building on the wrong side of a wall.

### The central claim, made falsifiable

Let `θ_fr` be a frozen frontier model and `θ_t` the local model after `t` epochs of self-improvement on the user distribution `D_u`. Let `Φ(·)` be the full Crucible system wrapped around a model. We claim there exists an epoch `t*` such that:

```
E_{x~D_u}[ R(Φ(θ_t*); x) ]  >  E_{x~D_u}[ R(θ_fr; x) ]      and      E[C(Φ(θ_t*))] ≪ E[C(θ_fr)]
```

i.e. **higher task reward on the user's distribution, at far lower cost.** Two honesty conditions are baked in:

- The claim is restricted to `D_u` and to the *system* `Φ`, not to the bare model.
- **The fair baseline is the frontier model *in the same harness*, `Φ(θ_fr)`** — not an unscaffolded frontier model. Scaffolding dominates raw capability; comparing a scaffolded local model to an unscaffolded frontier would be rigged.

The defensible claim is therefore: **parity-or-better against a scaffolded frontier on `D_u`, at far lower cost and full privacy.**

## What we are building first

The treatise describes the whole system; the strategy paper insists we **do not ship it all at once**. The decomposition is governed by three laws:

1. **Standalone value** — every product is a painkiller someone would adopt even if nothing after it ever shipped.
2. **True subset** — every product is a real slice of the final architecture, never a throwaway.
3. **Sets up the next** — every product makes the next easier to build and sell, moving the moat one notch toward uncopyable.

**Our committed first target (this phase): Phase 0 + Product 1.**

### Phase 0 — the proof of concept (not monetized; currency is attention + credibility)

- **0a — Benchmark + post.** A rigorous, *reproducible* benchmark with one headline: "We cut agent token cost by 5–10× with zero malformed tool calls — running locally." Three curves on real agent workloads (tokens, malformed-call rate, task success), stock local agent vs. the same model under Crucible.
- **0b — Drop-in token-saver.** A tiny, dependency-light wrapper that slots under whatever agent the developer already runs. One-line install, one-flag enable. Same answers, a fraction of the tokens, malformed calls eliminated. It is a genuine subset of Product 1.
- **0c — Public token calculator.** A web page where a developer pastes monthly agent token spend and sees projected savings. Top of the funnel; captures a waitlist.

### Product 1 — Crucible Core (the wedge; free, open-source)

> "Cut your agent's token bill 5–10× and never ship a malformed tool call — on your own machine."

- **Feature set:** grammar-scoped emission (zero structural hallucination) + Chain-of-Draft reasoning + KV-cache inter-agent communication.
- **The substrate begins here:** two-phase decoding, the trajectory grammar, and the first SGLang integration.
- **Proves:** a trusted local substrate under the user's agent.

Everything above Product 1 (Verify → Search → Memory → Evolve → Govern → Federation) stays **documented in the architecture but out of build scope** until the gates below say climb. See the [Roadmap](06-roadmap.md).

## Success criteria & kill-criteria

The defining engineering discipline of Crucible: **each rung's metric is simultaneously a product decision and a scientific result.** Ship in order; let the metric decide whether to climb. Each product carries a falsifiable kill-criterion.

| Target | Success metric | **Kill-criterion (stop / re-scope)** |
|---|---|---|
| **0a Benchmark** | Independent third-party reproductions confirm the headline | **< 2× end-to-end token reduction at matched success** in independent repros |
| **0b Token-saver** | One-line install works; weekly active installs grow | Real-world savings marginal (< 2×) or install friction too high |
| **0c Calculator** | Shareable; measurable waitlist | No waitlist conversion from traffic |
| **P1 Core** | Malformed-action rate → 0; median token reduction at matched success; weekly active installs | Marginal real-world savings (< 2×) |

> The Phase-0 kill-criterion is the master gate: **if independent reproductions show < 2× end-to-end token reduction at matched success, stop and re-scope before building Product 1.**

## Non-goals (for this phase, and some permanent)

- **Not** building Products 2–8 yet (verifier, search, memory, evolution, governance, federation are design-only for now).
- **Not** claiming a small model beats a frontier model in general — only `Φ(θ_t)` on `D_u` against a *scaffolded* frontier.
- **Not** claiming "zero hallucination." Grammar eliminates *structural* hallucination (malformed/invalid calls); *factual* hallucination is handled later by the verifier and retrieval. We never conflate the two.
- **Not** defending against a compromised core, sub-OS side channels, or a teacher that is adversarial in capability (see [Threat Model](08-security-threat-model.md)).
- **Not** monetizing the core. The free local runtime and spin-out libraries are the growth engine; revenue layers on top (open-core).

## Design principles (every later decision traces to one)

1. **Orchestrate beneath the wall** — the agent loop is a function of `(context, engine state)`, not text alone.
2. **Constrain emission, never cognition** — structure is enforced only on bytes a tool must parse; reasoning is never masked.
3. **Spend compute by its value** — allocate per step where expected marginal effect on outcome is largest (judged by the verifier).
4. **Improve only through a valid gate** — no change commits unless it provably helps on a clean certificate, and every change is reversible.
5. **Ground learning in a teacher, not in itself** — the improvement signal is a frontier teacher's verified outcome, not the model's own vote.
6. **Keep data on the device; share only gated abstractions** — raw data never leaves; only differentially-private, gated abstractions may be shared.
7. **Make safety a layer, not a prompt** — behavioral safety is enforced by sandboxing and formal runtime monitors, not natural-language instructions.

These principles are non-negotiable invariants. Any ADR or PRD that appears to violate one must call it out explicitly and justify it.
