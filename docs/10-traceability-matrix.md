# 10 — Traceability Matrix

**The "don't miss anything" sheet.** Every mechanism and every theorem in the treatise is mapped to: the package that will implement it, the test that proves it, the evaluation RQ that validates it, and the risk/guard that protects it. If a row has a gap, that gap is work we haven't planned yet.

Legend for **Phase**: 🟢 = in scope now (Phase 0 + P1) · 🟡 = design-only (interfaces now, build later) · ⚪ = future.

## Mechanisms → implementation → test → RQ → risk

| Mechanism | Phase | Package (doc 03) | Key test / invariant | RQ (doc 05) | Risk/guard (doc 07) |
|---|---|---|---|---|---|
| Grammar-scoped emission (two-phase) | 🟢 | `crucible-grammar` + `crucible-engine` | property: every emitted byte parses against active schema; reasoning unconstrained | RQ1 | structure snowballing → emission-only + diagnostic mode |
| Trajectory grammar `G_traj` | 🟢 | `crucible-grammar` | property: only legal phase sequences accepted | RQ1 | — |
| Chain-of-Draft (adaptive) | 🟢 | `crucible-tokeneconomy` | per-step budget honored; accuracy preserved on amenable steps | RQ1 | over-compression → VoI-modulated, easy steps only |
| KV-cache inter-agent comms | 🟢 (Mac: prefix reuse) | `crucible-engine` (+ `crucible-bench`) | reuse cheaper + identical output (slow test); 4.94× fewer prefill tokens measured | RQ1 | full cross-agent transfer → SGLang ([ADR-0010](adr/0010-kv-cache-reuse-llamacpp.md)) |
| Unified token+action speculation | 🟢/🟡 | `crucible-engine` | accepted speculation ≡ non-speculative output | RQ2 | speculative state corruption → Atomix |
| Atomix transactional settlement | 🟢 | `crucible-atomix` | property: aborted txn leaves no observable effect; fault-injection success rate | RQ6 | compensation fails → reversibility classes + micro-VM snapshots |
| Reversibility classes | 🟢 | `crucible-atomix` | irreversible actions never speculated | RQ6 | — |
| Shared KV-cache / RadixAttention | 🟢/🟡 | `crucible-engine` | branch cache sharing reduces cost vs independent | RQ2 | — |
| VGSS | 🟡 | `crucible-search` | dominates best-of-N at equal verifier budget (Prop 6.13) | RQ2/RQ3 | variance/gaming → summary-level + execution anchor + firewall |
| Co-evolved verifier (GenPRM/AgentPRM) | 🟡 | `crucible-verify` | verifier accuracy; reward-hacking ≈ 0 under co-evolution | RQ2 | single point of failure (A3) → co-evolution + isomorphic checks |
| VoI compute market | 🟡 | `crucible-search` / cognition | sub-linear regret vs known-value greedy (Prop 6.14); budget respected | RQ2 | unreliable estimates → fall back to uniform spend |
| Activation steering | 🟡 | cognition | cheaper than best-of-N at matched lift (ablatable) | RQ7 | model-dependent → off critical path |
| Three-tier memory | 🟡 | `crucible-memory` | paging correctness; bounded stores | RQ4 | — |
| STC (sleep-time consolidation) | 🟡 | `crucible-memory` | runs off interactive path; consolidations gated | RQ3 | hallucinated drift → bipartite reconstruction gate + verified-only |
| ACE context evolution | 🟡 | `crucible-evolve` | delta merge by non-LLM logic; no context collapse | RQ3 | — |
| PANDO skills | 🟡 | `crucible-evolve` | keyword retrieval determinism; confidence demotion | RQ3 | skill bloat → PANDO lifecycle |
| CG-TTRL policy | 🟡 | `crucible-evolve` | teacher-grounded labels, not majority vote | RQ3 | spurious reward → teacher-grounding |
| ROSE reversible self-edits | 🟡 | `crucible-evolve` | edit = separable adapter; rollback = drop tensor; non-forgetting | RQ3/RQ4 | forget/opaque → orthogonal LoRA + SLAO merge |
| EaTS | ⚪ | `crucible-evolve` + `crucible-engine` | escalation → distilled local capability; geometric decay | RQ3 | poisoning → teacher-grounded + re-gate |
| SGC | ⚪ | `crucible-evolve` | candidate must improve on held-out variations, not just `x` | RQ3 | memorization → curriculum transfer test |
| The gate (DP holdout + FDR + canary) | 🟡 | `crucible-gate` | adaptive non-degradation (Thm 6.5); bounded realized harm (Prop 6.7) | RQ3 | gate failure → reversibility floor |
| Constitution probe | ⚪ | `crucible-govern` + `crucible-gate` | safety-degrading edit rejected like a competence regression | RQ6 | — |
| Temporal-logic monitors | ⚪ | `crucible-govern` | block specified violation *before* settlement | RQ6 | — |
| Capability sandboxing / IFC | 🟡 | `crucible-govern` + `crucible-atomix` | tool cannot exceed declared capability schema | RQ6/RQ8 | overreach → least privilege |
| Learned teacher routing | ⚪ | `crucible-evolve` | escalate only below calibrated threshold; transfers across model swaps | RQ4 | — |
| FEaTS federation | ⚪ | `crucible-federation` | recipient re-gate; DP budget composed; `δ_0^fed` drops | RQ5 | noise amplification → FedASK + symbolic-first |

## Theorems / propositions → falsifier → where validated

| Result | Statement | Falsifier (doc 07) | Validated by |
|---|---|---|---|
| Prop 6.2 | Geometric cost decay to floor `δ_0/γ` | non-stationary `D_u` (`δ_0→1`) | RQ3 longitudinal |
| Thm 6.5 | Adaptive non-degradation under DP holdout | canary regressions beyond bound (A2) | RQ3 |
| Cor 6.6 | Holdout capacity Θ(m²) under Thresholdout | budget exhaustion without refresh | RQ3; execution-as-oracle refresh |
| Prop 6.7 | Bounded realized degradation (reversibility floor) | realized drop > `κ + Var_C` | RQ3 |
| Prop 6.8 | FDR necessary but not sufficient | accepted harmful edit with FDR-only | (design rationale; gate composition) |
| Thm 6.9 | Federated cost acceleration; composed privacy | `σ≈0` or privacy cost too high | RQ5 |
| Prop 6.10 | Interior optimum of DP budget | — (locates the tension) | RQ5 |
| Prop 6.11 | Weak-to-strong ceiling `η_w2s · V_fr_cov` | teacher covered-competence < student (A4) | RQ4 |
| Prop 6.13 | VGSS dominates best-of-N at equal budget | search ≤ best-of-N at equal budget | RQ2/RQ3 |
| Prop 6.14 | Sub-linear VoI regret under noisy estimates | linear regret / budget overrun | RQ2 |
| Cor 6.16 | Break-even epoch exists when `γ>0, q_0>δ_0/γ` | savings never overtake STC overhead | RQ3 cost economics |

## Coverage check

- **Every 🟢 mechanism has a named package, a property/contract test, and an RQ.** ✅ (Phase 0 + P1 is fully traced.)
- **Every theorem has a falsifier and a validating RQ.** ✅
- **Open gaps to fill as we climb:** EaTS/SGC/federation packages currently have interfaces-only entries (⚪); flesh out their PRDs before P5/P8.

> Update this matrix in the same PR as any change to a mechanism, package boundary, or RQ. It is the contract that the architecture, the build, and the science stay in sync.
