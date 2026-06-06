# 05 — Evaluation Plan

> In Crucible, **the evaluation questions of the treatise are exactly the product gates.** The science and the business are validated by the same experiments. This document is therefore both a research pre-registration and a product go/no-go protocol.

We **pre-register** research questions, baselines, suites, metrics, and analysis *before* building, and we separate **component claims** from the **longitudinal thesis claim**. Reproducibility is not a nicety — for the Phase-0 benchmark, **the reproducibility is the marketing.**

## The decisive fairness rule

The honest baseline is **the frontier model wrapped in the identical Crucible harness, `Φ(θ_fr)`** — not a bare frozen frontier. Scaffolding dominates raw capability; comparing a scaffolded local model to an unscaffolded frontier would be rigged and we would deserve to be called out for it. Every thesis-level comparison uses the same harness on both sides.

## Research questions (each maps to a build stage and a gate)

| RQ | Question | Stage |
|---|---|---|
| **RQ1 (Substrate)** | Does grammar-scoped emission drive malformed-action rate to **0** and cut latency **≥2×** at fixed size, *without* the reasoning loss of full constraint? | **P1 / Phase 0** |
| **RQ2 (Cognition)** | Do VGSS, VoI compute, and the co-evolved verifier raise success toward the frontier? How does success scale with budget `B`? What is verifier accuracy, and does co-evolution keep reward-hacking near zero? | P2–3 |
| **RQ3 (EaTS/STC dynamics)** | Does the escalation rate decay geometrically (Prop 6.2) with measurable `γ, δ_0`, while committed competence stays non-decreasing (Thm 6.5) and canary regressions stay within bound (Prop 6.7)? | P5–6 |
| **RQ4 (the thesis)** | After `t*` epochs, does `Φ(θ_t*)` exceed a frozen frontier on held-out `D_u` at lower cost (Eq. 3.1) — **and does it fail on broad/non-stationary `D_u`, as predicted?** | P6 |
| **RQ5 (Federation)** | Does FEaTS lower `δ_0^fed` and accelerate decay (Thm 6.9) without degrading any participant or breaching the privacy budget? | P8 |
| **RQ6 (Governance)** | Do monitors block specified violations *before settlement*, at what overhead? | P7 |
| **RQ7 (Ablations)** | Per-mechanism marginal contribution (the "what fails if removed" logic). | ongoing |
| **RQ8 (Injection survival)** | Under adversarial tool outputs whose payload is a plausible-but-wrong "convention", does the poisoning defense prevent a committed backdoor? | P5+ |

**This phase (Phase 0 + P1) is RQ1 and the substrate half of RQ2.** RQ3–8 are pre-registered but not yet exercised.

## Baselines

- API-bounded local agents: **OpenHands + Ollama**, **opencode**.
- **Vanilla SGLang** function-calling agent.
- Static cascade and a learned **RouteLLM** router.
- The bare frozen frontier, zero-shot.
- **The decisive fair baseline: `Φ(θ_fr)`** — the frontier model in the identical Crucible harness.
- Crucible with **each layer ablated** (for RQ7).

## Suites

| Suite | Role |
|---|---|
| **SWE-bench Verified** | Human-validated, Docker-reproducible code-agent tasks; primary RQ1/2 success. |
| **SWE-bench Pro / SWE-rebench** | **Contamination-resistant** public success measure (SWE-bench Verified is now contaminated); use for headline public numbers. |
| **AppWorld** | Long-horizon API workflows; validates VoI/PANDO token economics and routing savings. |
| **BFCL-v3, τ-bench** | Tool-calling correctness + tool-agent dialogue; RQ1 malformed-action rate. |
| **Reward Hacking Benchmark** | Exploit propensity; environmental-hardening ablation as a headline RQ3 metric. |
| **Terminal-Bench** | Deep CLI/state manipulation; validates Atomix settlement under fault injection (RQ6). |
| **Longitudinal per-domain** | A fixed, narrow `D_u` replayed over epochs with strict **temporal** train/probe/canary/test splits. **The instrument for the thesis claim — not any static leaderboard.** |

## Metrics

Success · malformed-action rate · tokens, wall-clock, cost · escalation rate `q_t` with fitted `(γ, δ_0, δ_0^fed)` · committed-competence trajectory on `H` and held-out test · accepted vs. rejected edits and rollbacks · verifier accuracy · exploit propensity + hardening effect · monitor block-rate and overhead · cumulative privacy loss.

## Statistical methodology (non-negotiable)

- **≥3 seeds** per condition.
- **Paired bootstrap confidence intervals** on per-task deltas.
- **Holm–Bonferroni** correction across RQs (we are running many tests; control family-wise error).
- **Pre-registered effect sizes** — we state the minimum effect that counts as a win *before* running.
- **Per-epoch holdout refresh** (Cor. 6.6) using *execution as a free oracle* (tests/compilers are deterministic verifiable rewards), not paid teacher calls.
- For RQ4: **per-domain win/loss with CIs, never a single aggregate.**
- **All raw per-epoch logs released** — reproducibility is the marketing.

## Kill-criteria (the gates that double as product decisions)

| Gate | Pass condition | **Kill / re-scope condition** |
|---|---|---|
| **Phase 0 master gate** | independent repros confirm headline | **independent repros show < 2× end-to-end token reduction at matched success** |
| RQ1 | malformed → 0; latency ≥2×; no reasoning loss vs unconstrained | reasoning degrades, or no latency win |
| RQ2 | success rises with `B` toward frontier; verifier accurate; reward-hacking ≈0 | verifier too weak to gate compute without losing success |
| RQ3 | geometric decay with fitted `γ>δ_0`; competence non-decreasing; canary within bound | no measurable decay (non-stationary domain) |
| RQ4 | `Φ(θ_t*)` beats frozen frontier on `D_u` at lower cost, **zero un-reverted regressions** | no win over frozen baseline, or regressions exceed bound |
| RQ5 | `δ_0^fed` drops with community size within privacy budget | too little cross-user overlap (`σ≈0`) or privacy cost too high |
| RQ6 | monitors block violations pre-settlement at acceptable overhead | governance overhead unacceptable to real ops |

## What the evaluation must be *designed to detect its own failure*

The methodology treats failure as informative. We **predict** the system should fail on broad, non-stationary, or adversarially-poisoned distributions unless specific safeguards hold (assumptions A1–A4, see [Risk Register](07-risk-register.md)). A review-quality test measures **both** success on a user's stable distribution **and** failure outside the assumptions. An evaluation that cannot fail is not evidence.
