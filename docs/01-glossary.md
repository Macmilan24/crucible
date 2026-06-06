# 01 — Glossary

The shared vocabulary of Crucible. When code, docs, or commits use these terms they mean exactly this. (Open primitives also make Crucible's vocabulary the ecosystem's vocabulary — that is itself part of the moat.)

## Core concepts

| Term | Definition |
|---|---|
| **API-boundary wall** | The stateless text interface through which conventional agents reach a model. A prompt string goes in, a completion comes out, and everything the engine knew between those events — KV-cache, logits, draft proposals, process-reward scores, weights — is discarded. Crucible's entire thesis is that the decisive techniques live *below* this wall. |
| **Inference-native orchestration** | An orchestrator that can (i) read logits and apply a mask before sampling; (ii) read/fork/prune the KV-cache tree; (iii) read draft proposals and process-reward scores; (iv) apply persistent but reversible weight updates between episodes; (v) schedule idle computation. Its policy is a function of `(context, engine state)`. |
| **API-bounded orchestrator** | The opposite: its sole interface is `prompt → completion`, retaining no engine state across calls. Today's agents (cloud and self-hosted) are all this. |
| **Control surface** | An internal piece of engine state the orchestrator can read or act on: logits, KV-cache, draft proposals, verifier scores, weights, idle scheduling. The five capabilities above. |
| **`D_u` (user distribution)** | The distribution of work a specific user/agent actually does. Crucible's claims are scoped to `D_u`, not to general benchmarks. |
| **`Φ` (the system)** | The full Crucible runtime wrapped around a model. Claims compare `Φ(θ_local)` to `Φ(θ_frontier)` — same harness, fair fight. |
| **The wager** | That a small local model inside Crucible can surpass a frozen frontier model on `D_u`, cheaper and privately, improving with use. |

## The six layers

| Layer | Name | Contents |
|---|---|---|
| **1** | **Substrate** | grammar-scoped emission · unified token+action speculation · Atomix transactional settlement · VGSS search · shared KV-cache |
| **2** | **Cognition** | parallel decoding · activation steering · co-evolved GenPRM/AgentPRM verifier · VoI compute market |
| **3** | **Memory & Consolidation** | three-tier memory (working/episodic/semantic) · STC sleep-time consolidation |
| **4** | **Evolution** | ACE context · PANDO skills · CG-TTRL policy · ROSE reversible weight edits (gated, teacher-grounded) |
| **5** | **Governance & Security** | capability sandboxing · temporal-logic runtime monitors · constitution probe · reversibility |
| **6** | **Amplification & Federation** | learned routing to a frontier teacher · EaTS teacher loop · FEaTS privacy-preserving collective improvement |

## The seven novel mechanisms

| Acronym | Name | One-line description |
|---|---|---|
| **EaTS** | Escalation-as-Training-Signal | Converts each escalation to the frontier teacher into a teacher-grounded labeled example, distilled into permanent local capability so the next instance is handled locally. Drives geometric cost decay. |
| **FEaTS** | Federated EaTS | A community of instances improves collectively while each keeps data strictly local, sharing only differentially-private, gate-passed abstractions. Recipients re-gate everything → Byzantine robustness by construction. The network-effect moat. |
| **VGSS** | Verifier-Guided Speculative Search | A bounded tree search over trajectories: draft model proposes children (sharing the parent's KV-cache), the process verifier scores and prunes, side-effect-free branches are pre-executed. Subsumes best-of-N and single speculation. |
| **VoI** | Value-of-Information compute market | Allocates compute (extra branches, steering, deeper VGSS, escalation) by expected value-per-cost, clearing each step against a shadow price so spend stays within budget. |
| **STC** | Sleep-Time Consolidation | During idle/charging windows: pre-compute day's contexts, consolidate episodic→semantic memory, run the gated EaTS distillation, merge/prune ROSE adapters, optional federated round. Moves all expensive permanent work off the interactive path. |
| **ROSE** | Reversible Orthogonal Self-Edits | Weight self-edits realized as low-rank adapters trained in subspaces orthogonal to prior edits. Reversible (drop a tensor), non-forgetting (orthogonality bounds interference), bounded (merged/pruned in STC). |
| **SGC** | Self-Generated Curriculum | Before gating, expands each escalated case into a small curriculum of paraphrases / perturbations / harder near-neighbors. Candidate edits must improve on the held-out variations, not just the single case — turns memorization into generalization. |

## Layer-4 evolution granularities (increasing permanence & risk)

| Term | Meaning |
|---|---|
| **ACE** | Agent Context Evolution — an itemized playbook of strategies and failure modes, evolved by delta updates merged with non-LLM logic (avoids context collapse). Lowest risk. |
| **PANDO** | The governed reusable agent-skill library lifecycle: deterministic keyword retrieval, polarity-pair merging of success/failure trajectories, confidence demotion that blacklists chronically-failing skills. |
| **CG-TTRL** | Code-Grounded Test-Time Reinforcement Learning — on-device RL grounding pseudo-labels in retrieved context and teacher-verified escalations rather than bare majority votes. |
| **ROSE** | (see above) — the weight tier. |

## The gate & theory

| Term | Meaning |
|---|---|
| **The gate** | The composite admission test for any self-edit: a **DP holdout** certificate (competence margin valid under adaptive reuse) + **online FDR** control (throttles acceptance over an unbounded update sequence) + a **reversible canary** (bounds realized harm). A candidate commits only if it passes all of it. |
| **DP holdout / Thresholdout** | A differentially-private mechanism for querying a held-out probe `H` so it stays valid under adaptive reuse. Gives a quadratic improvement in adaptivity budget (Θ(m²) vs Θ(m)). |
| **Online FDR** | False-discovery-rate control over the unbounded stream of candidate edits; throttles marginal acceptances as evidence accumulates. Necessary but *not sufficient* alone. |
| **Canary `C`** | A held-out set disjoint from `H`, never used for selection. If canary competence drops beyond a bound within `w` commits, roll back the offending ROSE adapters. Bounds realized degradation regardless of DP/FDR failure. |
| **Constitution probe** | A frozen battery of safety behaviors inside the canary set, so any self-edit that degrades safety is rejected by the same reversible mechanism that rejects competence regressions. |
| **Geometric cost decay** | `q_{t+1} = (1−γ)q_t + δ_0` ⇒ escalation rate decays geometrically toward floor `δ_0/γ`. `γ` = generalization rate of accepted edits; `δ_0` = arrival rate of genuinely novel hard cases. |
| **Weak-to-strong ceiling** | The honest limit: EaTS/FEaTS cannot exceed `η_w2s · V_fr_cov` — the teacher's covered competence times the weak-to-strong elicitation efficiency. The system can still beat a *frozen* frontier on `D_u` via specialization, coverage, and system effects. |

## Engine & infrastructure

| Term | Meaning |
|---|---|
| **SGLang** | The inference engine of record. Provides RadixAttention prefix sharing, co-located structured generation, EAGLE-3 self-speculation. |
| **RadixAttention** | Prefix-sharing KV-cache mechanism that makes branching (VGSS, best-of-N) cheap by sharing common cache across branches. |
| **XGrammar-2 / TagDispatch** | Grammar backend; the trigger-tag mechanism that switches the schema grammar on for emission only, then releases. |
| **EAGLE-3** | Self-speculation head: a lightweight autoregressive head conditioned on hidden states that drafts tokens the target verifies in one pass (2–6× throughput at 0.75–0.85 acceptance, no output change). |
| **Atomix** | The transactional settlement model: epochs (logical timestamps), scopes (typed resources), effects (side-effect descriptions with idempotency keys + compensation handlers), frontiers (per-resource commit cursors), transactions (atomic groups). An effect becomes permanent only when its resource frontier passes its epoch. |
| **veRL / HybridFlow** | The RL training path (PPO/GRPO) used for CG-TTRL, ROSE adapter training, and verifier co-evolution, handing off to/from SGLang inference. |
| **BitNet (1.58-bit)** | Ternary models used for the CPU "swarm" — draft head, verifier, and process-reward models — so the whole stack fits on one consumer machine. |
| **GenPRM / AgentPRM** | The verifier: a *generative* process-reward model (explicit derivation + code execution before scoring) augmented with turn-level value functions for long trajectories. Co-evolved with the policy. |
| **Two-phase decoding** | Cognition phase: model generates *unconstrained* (full logits, pretraining distribution preserved). Emission phase: on a trigger tag, the schema grammar masks logits for the structured emission only, then releases. |
| **Reversibility classes** | Every tool is typed `idempotent`, `compensable`, `snapshot-reversible`, or `irreversible`. Only the first three may be speculated; irreversible actions require confirmation and never run on a speculative branch. |
| **Day/night split** | Interactive ("day") path is fast — think/emit, speculation, VoI/VGSS, rare escalation. Expensive permanent work (gating, RL, weight edits, merges, consolidation, federation) is deferred to "night" (STC). |
