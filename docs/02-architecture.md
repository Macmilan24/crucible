# 02 — Architecture

This is the engineering view of the six-layer architecture from the treatise. It is the **target** architecture; build scope for this phase is only the Substrate + token economy (Product 1). Everything else is documented so we never design ourselves into a corner.

## The one idea: orchestrate beneath the wall

```
   API-bounded (today)                         Inference-native (Crucible)
 ┌───────────────────┐                       ┌───────────────────────────────┐
 │   orchestrator    │   prompt ─────▶       │  orchestrator   │  inference   │
 │   (text only)     │   ◀───── text         │   (own fault    │   engine     │
 └───────────────────┘                       │    domain)      │ (own domain) │
 ┌───────────────────┐                       └────────┬────────┴──────┬───────┘
 │  inference engine │  cache, logits, draft,         │   zero-copy   │
 │     (sealed)      │  scores, weights: DISCARDED     shared memory: KV-cache
 └───────────────────┘                                tree · logits · draft ·
                                                       scores · reversible adapters
```

**Critical systems decision (refined after red-team, §7.5.1 of the treatise):** "inference-native" means **shared state access, not a shared fault domain.** The engine and orchestrator run as **separate processes**. Cache tree, logits, and adapter handles are exposed via **zero-copy shared memory + IPC handles** (not copies). A supervisor restarts the orchestrator on crash *without losing engine state*. This preserves every inference-native capability while removing the single-crash-domain hazard.

> This is an architectural invariant. No design may put arbitrary agentic logic in the engine process.

## The stack (top sits above the wall = prior systems)

```
┌──────────────────────────────────────────────────────────────────────────┐
│ 6  AMPLIFICATION & FEDERATION   learned router · EaTS teacher loop · FEaTS  │
├──────────────────────────────────────────────────────────────────────────┤
│ 5  GOVERNANCE & SECURITY        sandboxing · LTL monitors · constitution    │
│                                 probe · reversibility                       │
├──────────────────────────────────────────────────────────────────────────┤
│ 4  EVOLUTION (gated, teacher-grounded)  ACE · PANDO · CG-TTRL · ROSE · SGC  │
├──────────────────────────────────────────────────────────────────────────┤
│ 3  MEMORY & CONSOLIDATION       3-tier memory · STC sleep-time consolidation│
├──────────────────────────────────────────────────────────────────────────┤
│ 2  COGNITION                    parallel decode · steering · co-evolved     │
│                                 verifier (GenPRM/AgentPRM) · VoI market      │
├──────────────────────────────────────────────────────────────────────────┤
│ 1  SUBSTRATE                    grammar-scoped emission · unified spec +     │
│                                 Atomix sagas · VGSS · shared KV-cache        │
├──────────────────────────────────────────────────────────────────────────┤
│    ENGINE & HARDWARE   SGLang (RadixAttention · XGrammar-2 · EAGLE-3) ·      │
│                        veRL · GPU policy + BitNet CPU swarm                   │
└──────────────────────────────────────────────────────────────────────────┘
  ◀── inference-native control surfaces (the wall): prior systems sit ABOVE this box
```

**Strict dependency order:** each layer presupposes the control surfaces beneath it. This is why we build bottom-up and why partial deployments (Layers 1–2) do *not* test the full thesis — they test the wedge.

## Layer 1 — Substrate *(in build scope: Product 1)*

The capabilities that exist only beneath the wall. Job: make the small model structurally incapable of failing, and fast enough to think more, without touching *what* it reasons about.

- **Grammar-scoped decoding (two-phase).** Constrain *emission*, never *cognition*. Cognition phase = unconstrained generation (full logits, pretraining distribution preserved). On a trigger tag (XGrammar-2 TagDispatch), activate the tool-schema grammar for the emission only, then release. A tiny trajectory grammar governs only the legal *sequence* of phases:
  ```
  ⟨episode⟩ ::= ( ⟨think⟩ (⟨emit⟩ | ⟨reflect⟩) )* ⟨halt⟩
  ⟨think⟩ → Σ* (free)        ⟨emit⟩ → schema
  ```
  This pins the per-step structural-validity line at 1 by construction (eliminating the malformed-action failure mode) while leaving reasoning intact. **Why this matters:** at 95% per-step validity, a 20-step episode has ~64% chance of *some* malformed action; production agency needs ≥99.9%/step, unreachable by prompting alone. *Forcing reasoning into a grammar measurably hurts — so we never do it.*
- **Failure-recovery diagnostic mode (red-team §7.5.2):** on tool-execution failure or verifier rejection, drop *all* grammar constraints for the following reflection, let the model diagnose in free natural language, penalize superficial syntactic fixes, and re-engage the mask for the next emission only after the verifier confirms the *semantic* error was actually restructured.
- **Unified token-and-action speculation.** One EAGLE-3-style draft head drafts both next *tokens* (target verifies in one pass) and next *actions*; side-effect-free actions (reads, searches) are pre-executed during think-time and cached; side-effecting actions are staged. Token- and action-level speculation share **one cache tree**.
- **Atomix transactional settlement.** Speculative actions settle through epochs/scopes/effects/frontiers/transactions. An effect becomes permanent only when its resource frontier passes its epoch. **Reversibility classes** (idempotent / compensable / snapshot-reversible / irreversible) decide what may be speculated; irreversible actions need confirmation and never run on a speculative branch. Local state uses micro-VM (Firecracker-class) epoch snapshots for millisecond rollback.
- **VGSS (preview here, full in Layer-2 budget).** Bounded tree search over trajectories, branches proposed by the draft model, scored/pruned by the verifier, side-effect-free branches pre-executed — all on one KV-cache.
- **Shared KV-cache.** The cache tree is a first-class object the orchestrator reads and prunes; RadixAttention shares the common prefix across branches, which is what makes VGSS and best-of-N affordable on one consumer GPU.

### The token economy *(in build scope — this is the wedge's value)*

The most natural first product, because its benefits are immediate and measurable without any heavier machinery:

- **Grammar eliminates *structural* hallucination, not factual.** A constrained decoder guarantees a *well-formed* call, not a *true* one. Structure → grammar; truth → verifier + retrieval. We never claim the first solves the second.
- **Compressed reasoning, adaptively.** Chain-of-Draft (~5-word steps) matches CoT accuracy at ~8% of tokens on amenable steps — but applied *per step by the VoI controller*, never as a blanket constraint. Trivial steps get a one-line draft; pivotal steps get full free-text reasoning or a VGSS expansion; the verifier checks compression didn't cost correctness.
- **Inter-agent communication without natural language.** Three cheaper channels available only below the wall: (i) typed message schemas (same zero-malformed guarantee), (ii) KV-cache reuse between co-located agents (DroidSpeak/KVComm, up to ~2.8× lower prefill), (iii) embedding-space messages (CIPHER).

## Layer 2 — Cognition *(design-only this phase)*

- **Parallel/diffusion decoding** for compute *headroom* (more test-time compute at fixed latency).
- **Activation steering** — a small bank of control vectors (verification, backtracking, caution) added at inference time; a cheaper alternative to best-of-N for nudging a hard step. Off the critical path (ablatable; model-dependent).
- **The verifier `V_φ`** — the most load-bearing component. GenPRM (explicit derivation + code execution before scoring) + AgentPRM (turn-level value functions for long trajectories). **Co-evolved** with the policy (a frozen judge is eventually gamed) and grounded in execution where possible (isomorphic verification). Its accuracy is a first-class measured quantity — *the system's safety reduces to it.*
- **VoI compute market** — allocates compute by expected value-per-cost against a shadow price `λ_t`; cheap ternary verifiers/draft heads bid low and run often, the frontier bids high and runs rarely.

## Layer 3 — Memory & Consolidation *(design-only)*

- **Three-tier memory:** working (in context), episodic (bounded log of trajectories+outcomes), semantic (distilled, deduplicated knowledge + ACE playbook). Paging is agent-controlled via tool calls.
- **STC (sleep-time consolidation):** runs in idle/charging windows — sleep-time compute over the day's contexts, episodic→semantic consolidation, gated EaTS distillation, ROSE merges, optional federated round. *Plus a bipartite reconstruction gate* (a second process must reconstruct the original trace from the summary; lossy/hallucinated summaries are rejected) and *verified-only consolidation* (only execution-verified or teacher-confirmed episodes are eligible).

## Layer 4 — Evolution *(design-only; highest risk)*

Self-improvement at four granularities of increasing permanence/risk, all driven by **one teacher-grounded signal** and all subject to **the gate**:
- **Context (ACE)** — itemized playbook via delta updates merged by non-LLM logic.
- **Skills (PANDO)** — keyword retrieval, polarity-pair merging, confidence demotion.
- **Policy (CG-TTRL)** — on-device RL grounded in teacher-verified escalations, not majority votes (neutralizes spurious-reward failure).
- **Weights (ROSE)** — reversible orthogonal low-rank adapters; an edit is a separable tensor that can be dropped or merged instantly.

## Layer 5 — Governance & Security *(design-only)*

- **Capability sandboxing + information-flow control** — every tool runs least-privilege in an isolated env (microVM/gVisor-class), no ambient network/filesystem authority; each adapter declares a typed capability schema.
- **Temporal-logic runtime monitors** — safety requirements compiled to LTL specs ("authenticate before accessing data", "never write outside the workspace", "confirm before an irreversible effect"), enforced at the emission/settlement boundary → genuine *pre-execution* guarantees, not post-hoc detection.
- **Protecting the self-improvement loop** — the gate protects against statistical degradation; governance against behavioral regression. A frozen **constitution probe** sits in the canary, so safety-degrading edits are rejected by the same reversible mechanism as competence regressions. All self-edit and escalation logs are immutable and auditable.

## Layer 6 — Amplification & Federation *(design-only; the endgame moat)*

- **Learned routing to a frontier teacher** — escalate only when a learned router predicts the local system can't reach parity, against a calibrated cost–quality threshold. Escalated trajectories feed EaTS.
- **Federation (FEaTS)** — a community improves together while each keeps data strictly local, sharing only DP, gate-passed abstractions (ACE deltas, PANDO skills, ROSE adapter updates) — never raw data or activations. Recipients re-gate every incoming abstraction (Byzantine robustness by construction). Cross-tenant pooling of raw activations is *prohibited* (it admits prompt-inversion attacks).

## The control-surface contract (Appendix A.2 of the treatise)

The orchestrator↔engine interface is the load-bearing API of the whole system. It must expose, over zero-copy shared memory + IPC:

| Capability | Surface | Used by |
|---|---|---|
| (i) read logits `z_t`, apply mask `m_t` before sampling | logit buffer + mask channel | grammar-scoped emission, steering |
| (ii) read / fork / prune the cache tree `K` | KV-cache tree handles | unified speculation, VGSS, cache sharing, best-of-N |
| (iii) read draft proposals + process-reward scores | draft + verifier score channels | speculation, VGSS, VoI |
| (iv) apply persistent but **reversible** updates `θ ↦ θ'` | adapter (ROSE) handles | evolution, gate rollback |
| (v) schedule idle computation | STC scheduler hook | consolidation, gated learning |

None of (i)–(v) is expressible under an API-bounded orchestrator. This table *is* the precise definition of what "below the wall" buys us.

## The risk ledger

Every "high" risk has an explicit guard proved or specified in the treatise.

| Component | Necessity | Risk | Primary guard |
|---|---|---|---|
| Grammar-scoped emission | necessary | low | emission-only scope; free cognition |
| Unified speculation | high value | medium | Atomix transactional settlement |
| VGSS search | high value | medium | verifier pruning; side-effect-free only |
| Co-evolved verifier | necessary | medium | adversarial hardening; isomorphic checks |
| VoI compute market | high value | low | verifier-estimated value; budget cap |
| Memory + STC | high value | low | bounded stores; gated consolidation; reconstruction gate |
| ACE / PANDO | high value | low | gate + confidence demotion |
| CG-TTRL / ROSE | high value | **high** | DP gate + FDR + orthogonal LoRA + rollback |
| Governance monitors | necessary | low | formal LTL guarantees; sandbox |
| Learned routing | high value | low | calibrated thresholds; transfer |
| EaTS / FEaTS | high value | **high** | teacher-grounded; DP federation; recipient re-gate |
| Latent reasoning | **excluded** | — | negative result; cited and excised |

## What fails if a mechanism is removed (the ablation logic = RQ7)

- No grammar-scoped emission → reliability collapses over long episodes.
- No VoI → compute is wasted and VGSS unaffordable.
- No DP gate → EaTS overfits the probe and degrades.
- No ROSE → weight edits forget and can't be cleanly reversed.
- No STC → the expensive learning has nowhere off-path to run.
- No FEaTS → the system works but forgoes the network effect.

> **The verifier is the hub** — it routes compute (VoI), prunes search (VGSS), and gates learning (the gate). Its co-evolution is a structural necessity, not polish. Treat verifier quality as a first-class measured quantity everywhere.
