# 07 — Risk Register

Risks are tracked as first-class engineering artifacts. Each has an owner-area, a guard, and where possible a **measured falsifier** — the quantity that would tell us the risk has materialized. The treatise's intellectual honesty (it states what would falsify its own claims) is inherited here verbatim.

## A. Standing assumptions (from the theory) — each maps to a measured falsifier

| # | Assumption | If it fails | **Falsifier (what we measure)** |
|---|---|---|---|
| **A1** | **Stationarity** — `D_u` drifts slowly enough that `δ_0 < γ` | the cost floor approaches the frontier's; self-improvement stalls | measure fitted `γ, δ_0`; `δ_0 → 1` means non-stationary |
| **A2** | **Clean probe + sound DP mechanism** | Thm 6.5 voids; gate can certify a bad edit | canary regressions exceeding the bound |
| **A3** | **Accurate, hard-to-game verifier** | VoI mis-allocates, the gate mis-certifies | verifier-accuracy + reward-hacking metrics |
| **A4** | **Teacher covered-competence exceeds the student's** | amplification has nothing to teach (Prop 6.11 ceiling) | win/loss vs teacher on covered cases |

> None of these is assumed without a test that could show it false. **An assumption with no falsifier is a bug in this document.**

## B. Technical risks

| Risk | Likelihood | Impact | Guard | Status |
|---|---|---|---|---|
| **Marginal real-world token savings (< 2×)** — the master kill-criterion | med | **fatal to wedge** | rigorous, reproducible Phase-0 benchmark on real workloads before building P1 | open — Phase-0 gate |
| **Constrained decoding degrades reasoning** ("structure snowballing") | med | high | constrain *emission only*, never cognition; two-phase decoding; failure-recovery diagnostic mode | designed-in (§02) |
| **Verifier is a single point of failure** | med | high | co-evolution, isomorphic/execution-grounded checks, reversibility; verifier accuracy measured (RQ2) | acknowledged (A3) |
| **Self-improvement collapse via multiple testing** | med | high | DP holdout (Thm 6.5) + online FDR + reversibility (Prop 6.7); collapse probability bounded and tunable | designed-in |
| **Weight self-edits forget / are opaque** | med | high | ROSE: orthogonal, separable, reversible, merged in STC | designed-in |
| **Holdout exhaustion voids cost-decay** | med | high | execution is a free oracle (RLVR); refresh `H`/`C` from execution-verified outcomes, not paid teacher calls | refuted-with-proof; honest boundary: domains with no cheap oracle |
| **ROSE rank saturation** | low–med | med | SLAO continual merging; rank pressure scales with *novelty*, not task count; STC prunes low-value adapters | designed-in |
| **Speculative execution corrupts state** | med | high | Atomix verify-then-settle + compensation; reversibility classes; only side-effect-free actions pre-execute; micro-VM snapshots | designed-in |
| **Memory co-location crash destroys engine/cache** | med | high | separate fault domains; zero-copy IPC; supervisor restarts orchestrator, engine survives | designed-in (§7.5.1) |
| **Sleep-time hallucinated drift** poisons semantic memory | med | med | bipartite reconstruction gate + verified-only consolidation; consolidations gated like any edit | designed-in |
| **Federation DP-noise amplification kills utility** | med | high | FedASK two-stage sketching + subspace-aware DP + symbolic-first channel | designed-in (P8) |
| **VGSS variance / verifier gaming** ("synergistic collapse") | med | high | summary-level search (RTV/PDR) + execution anchor overrides neural PRM + search/gate firewall | designed-in |
| **Poisoning channel** — learning ingests an adversarial "convention" | med | high | recipients re-gate every abstraction; RQ8 injection-survival test | designed-in (P5+) |
| **Chain-of-Draft over-compression on hard steps** | med | med | VoI sets reasoning budget per step; brevity only on easy single-file steps; suspended on multi-file/cross-scope | designed-in |
| **Engineering surface is large; partial deploys don't test the thesis** | high | med | strict layer dependency; phased build; each maps to an open artifact | managed by roadmap |

## C. Security & privacy risks
See the full [Security & Threat Model](08-security-threat-model.md). Headlines: tools run under capability sandboxes with information-flow control; cross-tenant pooling of raw activations is **prohibited** (prompt-inversion); federation shares only DP, gated abstractions; self-edit/escalation logs are immutable.

## D. Product / strategy risks

| Risk | Guard |
|---|---|
| **A frontier lab absorbs the wedge in a quarter** | the moat moves up the ladder faster than the wedge commoditizes (feature→switching→data→network); endgame is structurally uncopyable in reverse |
| **Open-source cedes the moat** | the moat is *downstream* (specialization data, network effect), not the license; tiered open-core |
| **Too complex / irreproducible** | strict layer dependency, each mapped to an open artifact, phased build; reproducibility is a launch requirement |
| **Benchmarks are gameable / leak** | contamination-resistant suites (SWE-bench Pro / SWE-rebench) + longitudinal temporal splits + explicit reward-hacking measurement |
| **Privacy dismissed as marketing** | privacy is architectural: Def 3.2(iv), on-device STC, DP-only sharing — not a policy promise |

## E. Threats to validity (honest residuals)

- **Stationarity is the binding empirical risk.** Most claims weaken on non-stationary `D_u`.
- **Verifier quality upper-bounds** gating, routing, and VoI — everything leans on it.
- **Teacher dependence** means amplification inherits the teacher's covered errors.
- **DP–utility tension** — strong privacy slows transfer (Prop 6.10 locates the optimum, doesn't hide it).
- **Federation assumes cross-user overlap** (`σ > 0`); with no overlap, no network effect.
- **No cheap verification oracle ⇒ weaker self-improvement.** For purely subjective tasks with no tests/execution, the holdout budget binds and refresh gets expensive. Crucible targets agentic-coding/tool-use distributions precisely because the oracle is free there.

## Review cadence

Re-score this register at each rung transition and whenever a falsifier fires. A fired falsifier is not a failure of the project — it is the evaluation working as designed; act on it (re-scope per the kill-criteria in the [Roadmap](06-roadmap.md)).
