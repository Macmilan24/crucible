# 06 — Roadmap

**The rule:** ship in order; **let each rung's metric decide whether to climb.** Each rung is a standalone painkiller *and* a real layer of the architecture. Products overlap deliberately — each begins while the prior stabilizes — and the heavy, high-risk products (P6–8) come only after cheaper rungs validate demand and build the user base that makes them sellable.

## Where we are

```
  ▶ YOU ARE HERE: pre-implementation foundation (this docs set)
    next: scaffold the monorepo → build Phase 0 → build P1 Core
```

## The portfolio map

```
 buyer sophistication
 (enterprise) ▲                                              P8 Federation ◀ endgame
              │                                   P7 Team/Govern
              │                        P6 Evolve-Weights
              │                 P5 Evolve-Lite
              │           P4 Memory
              │       P3 Search
              │    P2 Verify
 (individual) │ P0 ──▶ P1 Core
              └────────────────────────────────────────────────────────▶ sophistication / ship order
   moat:        feature ───────▶ switching cost ──▶ specialization data ──▶ network effect
                (P1–P3)            (P4)              (P5–P6)                 (P8)
```

## This phase — committed build scope

### Phase 0 — proof of concept *(currency: attention + credibility, not revenue)*
- **0a Benchmark + post** — reproducible benchmark; headline "5–10× fewer tokens, 0 malformed calls, locally." → see [PRD](product/0a-benchmark.md)
- **0b Drop-in token-saver** — one-line install, one-flag enable; a true subset of P1. → see [PRD](product/0b-token-saver.md)
- **0c Token calculator** — paste spend, see savings, capture waitlist. → see [PRD](product/0c-calculator.md)
- **Gate:** independent repros confirm ≥2× end-to-end token reduction at matched success. **Fail ⇒ stop and re-scope before P1.**

### Product 1 — Crucible Core *(free, open-source; the wedge)*
- Substrate: two-phase decoding, trajectory grammar, grammar-scoped emission; first SGLang integration via `crucible-engine`.
- Token economy: Chain-of-Draft (VoI-stubbed: per-step budget heuristic until real VoI lands), KV-cache inter-agent comms.
- Atomix settlement for safe tool execution.
- **Metric:** weekly active installs; malformed-action rate → 0; median token reduction at matched success.
- **Proves:** a trusted local substrate under the user's agent. **Kill:** marginal real-world savings (< 2×). → see [PRD](product/p1-core.md)

## Future ladder — design-only now (documented so we don't corner ourselves)

| Product | One-liner | Depends on | Decisive metric | Kill-criterion |
|---|---|---|---|---|
| **P2 Verify** | frontier-grade reliability from a local model; compute spent only where it matters | P1 | success vs frozen frontier at fixed local size | verifier too weak to gate compute without losing success |
| **P3 Search** | spend a little more only on the hard steps, and get them right (VGSS) | P2 verifier | hard-subset success per unit compute (beats best-of-N) | search gains ≤ best-of-N at equal budget |
| **P4 Memory** | your agent gets faster and sharper the more you use it, privately | P2–3 | retention; week-over-week improvement | memory adds latency/clutter, not value |
| **P5 Evolve-Lite** | learns your project's patterns — context + skills, gated and reversible | P4 | fitted escalation-cost decay (`γ, δ_0`) | no measurable decay (non-stationary domain) |
| **P6 Evolve-Weights** | learns your codebase deeply enough to beat a frozen frontier on your work | P5 | Eq. 3.1: system > frozen frontier on `D_u`, zero un-reverted regressions | no win, or regressions exceed bound |
| **P7 Team & Governance** | a fleet of specialized agents an org can trust, audit, prove compliant | P6 | monitor coverage; audit completeness | governance overhead unacceptable to real ops |
| **P8 Federation** | your team's agents get smarter together without sharing a line of code | P6–7 | drop in novelty floor with community size, within budget | too little overlap, or privacy cost too high |

## Spin-out libraries (ship alongside the ladder; widen the funnel)

Each Crucible layer is *also* a standalone OSS library that funnels developers back to the platform. Extract from the monorepo when stable (see [doc 03](03-repo-and-modularization.md)): grammar engine → Core; Atomix → Core/Verify; process verifier → Verify; DP gate → Evolve; consolidation memory → Memory; federation coordinator → Federation.

## Indicative 24-month shape (from the strategy paper)

```
 month   0    3    6    9   12   15   18   21   24
 Phase0  ███
 P1 Core  ████████
 P2 Verify     ██████
 P3 Search          █████
 P4 Memory              ██████
 P5 Evolve-Lite             █████
 P6 Evolve-Weights              ██████
 P7 Team/Govern                      █████
 P8 Federation                            ██████
```

Treat dates as *indicative*; the gates, not the calendar, decide progression.

## The moat thesis (why this order)

The danger for any startup is shipping a feature a frontier lab absorbs in a quarter. The portfolio is built so the **moat moves up the ladder faster than the wedge commoditizes**: feature (P1–3) → switching cost (P4) → specialization data (P5–6) → network effect (P8). The top rung — *collective improvement over data that never leaves users' machines* — is the one thing a cloud incumbent structurally cannot copy in reverse, because their trust and scaling model forbids it. Ascend fast enough that by the time the wedge is copied, the defensibility already lives upstairs.
