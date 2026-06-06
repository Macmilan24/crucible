# PRD P1 — Crucible Core (the wedge)

> "Cut your agent's token bill 5–10× and never ship a malformed tool call — on your own machine."
> Free, open-source. Price: $0 (it buys distribution). The first real rung of the architecture.

## Pain

Token bills and flaky tool calls on local agents. Cheap local agents are unreliable; reliable ones are expensive metered cloud. Developers want a trusted local substrate *under* their agent.

## What it is

The free local runtime: the **Substrate** + the **token economy**, shipped as an integrated, installable agent runtime.

- **Grammar-scoped emission** — zero *structural* hallucination, by construction (two-phase decoding; see [ADR-0004](../adr/0004-grammar-two-phase-decoding.md)).
- **Chain-of-Draft reasoning** — adaptive per-step reasoning budget (VoI-stubbed with a heuristic until real VoI lands in P2-era).
- **KV-cache inter-agent communication** — typed message schemas, cache reuse, embedding-space messages.
- **Atomix transactional settlement** — safe tool execution with rollback and reversibility classes.
- First **SGLang integration** via `crucible-engine` (the control-surface contract).

## Users / ICP

Individual devs and small teams; privacy-constrained shops that can't send code to a cloud.

## Scope (build)

| Capability | Package | Notes |
|---|---|---|
| Control-surface contract + SGLang integration | `crucible-engine` | the wall boundary; mock engine for tests |
| Trajectory grammar + emission masking | `crucible-grammar` | two-phase decoding; property-tested |
| Chain-of-Draft + KV-cache comms | `crucible-tokeneconomy` | adaptive per-step budget (heuristic) |
| Transactional settlement | `crucible-atomix` | reversibility classes; fault-injection tested |
| The agent loop / orchestrator | `crucible-core` | ties it together; separate fault domain |

## Out of scope (design-only; later rungs)

Co-evolved verifier (P2), VGSS (P3), memory + STC (P4), evolution/ROSE/EaTS (P5–6), governance monitors (P7), federation (P8). Documented in [Architecture](../02-architecture.md) so Core's interfaces don't corner them.

## Aha demo

A side-by-side token counter dropping by ~8× while malformed calls sit at 0 — running locally, under the user's own agent, with task success matched.

## Acceptance criteria

- [ ] Malformed-action rate → **0** over multi-step episodes (RQ1).
- [ ] Median token reduction at **matched success** vs. a stock local agent (RQ1).
- [ ] Latency ≥2× better at fixed model size, **without** the reasoning loss of full constraint (RQ1).
- [ ] Runs on the deployment profiles in [Tech Stack](../04-tech-stack.md) (workstation / laptop / CPU), correctness/safety guarantees unchanged across profiles.
- [ ] Safe tool execution: an aborted Atomix transaction leaves no observable effect (property + fault-injection tests).
- [ ] Fully local; no data leaves the device.
- [ ] 0b is a verified true-subset (shared code, import-linter green).

## Success metric

**Weekly active installs.** Proves: a trusted local substrate under the user's agent.

## ⛔ Kill-criterion

Marginal real-world savings (< 2×). (Same master gate as Phase 0 — if the wedge's economic claim isn't real, the whole ladder rests on sand.)

## What this sets up (the next rung)

Core establishes the substrate and the trusted-local-runtime install base. **P2 Verify** then adds the co-evolved verifier on top — "frontier-grade reliability from a local model" — which produces the verified trajectories every later rung (search, evolution) needs.
