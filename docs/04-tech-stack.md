# 04 — Tech Stack

We follow the treatise's choices (confirmed decision). Each choice is justified against the architecture, and the *isolation strategy* that lets us swap it later is noted. Formal records are in the [ADRs](adr/).

## Summary

| Concern | Choice | Why | Swap isolation |
|---|---|---|---|
| Language | **Python 3.11+** | the inference/RL ecosystem (SGLang, veRL, PyTorch) is Python; fast iteration | — |
| Performance-critical paths | **Rust / C++ via PyO3 / native ext** where profiling demands (grammar masking, IPC, snapshotting) | hot loops shouldn't pay the Python tax | confined to specific packages |
| Inference engine | **SGLang** | RadixAttention prefix sharing, co-located structured generation (XGrammar-2), EAGLE-3 self-speculation — exactly the control surfaces we need | all access via `crucible-engine` (ADR-0003) |
| Grammar / structured decoding | **XGrammar-2 (TagDispatch)** | trigger-tag activation of schema grammar for *emission only* → two-phase decoding | `crucible-grammar` package boundary (ADR-0004) |
| Speculation | **EAGLE-3** | self-speculation head; 2–6× throughput at no output change; same draft mechanism for token+action | inside `crucible-engine` |
| CPU "swarm" (draft/verifier/PRM) | **BitNet.cpp (1.58-bit ternary)** | lets draft head + verifier + PRM run on CPU so the stack fits one consumer machine | behind verifier/draft interfaces |
| RL training path | **veRL / HybridFlow** (PPO/GRPO) | hands off between SGLang inference and RL with minimal data movement; Search-R1-style tool-interleaved rollouts | `crucible-evolve` (design-only now) |
| Local storage | **SQLite + a vector index** | working/episodic/semantic memory, ACE playbook, PANDO skills, ROSE adapters, probe `H`, canary `C` — all local, no server | `crucible-memory` (design-only now) |
| Sandboxing | **microVM (Firecracker-class) / gVisor-class** | least-privilege tool execution; micro-VM epoch snapshots for millisecond rollback | `crucible-govern` + Atomix |
| Tool/agent baselines (for bench) | **OpenHands+Ollama, opencode, vanilla SGLang function-calling** | the honest baselines the eval plan requires | `bench/` only |

## Phase-by-phase: what's actually needed now

### Phase 0 + P1 (in scope)
- **SGLang** — engine of record. We will pin a specific version and document the exact RadixAttention / XGrammar-2 / EAGLE-3 feature set we rely on.
- **XGrammar-2** — the trajectory grammar compiler + two-phase decoding policy.
- **Chain-of-Draft + KV-cache reuse** — the token-economy wins (the wedge's value).
- **Atomix settlement runtime** — needed as soon as the agent takes side-effecting actions (even Core needs safe tool execution).
- **A local model** — a 7–9B policy (e.g. a Qwen/Llama-class instruct model) on GPU; a ternary draft/verifier on CPU.
- **Benchmark deps (0a)** — SWE-bench-style harness, contamination-resistant suites (SWE-bench Pro / SWE-rebench), token/latency/success instrumentation.

### Deferred (design-only this phase)
veRL/HybridFlow, GenPRM/AgentPRM training, ROSE adapter training, DP gate libraries, federation/DP accounting. We document interfaces now so the build order from the [Roadmap](06-roadmap.md) stays unblocked.

## Deployment profiles (the stack must scale down, not just up)

| Profile | Policy | Search | STC |
|---|---|---|---|
| 24–48 GB workstation GPU | 7–14 B | full VGSS depth | frequent |
| 8–16 GB laptop | 4-bit 7 B | shallow, VoI-gated VGSS | charging-time |
| CPU/NPU only | ternary policy | best-of-few | as available |

> **Invariant across all profiles:** what changes is search depth and self-edit throughput — **never the correctness and safety guarantees**, which rest on grammar scoping, the gate, and the monitors, not on FLOPs. Any design that makes a safety guarantee depend on having a big GPU is wrong.

## Tooling baseline (dev experience)

Documented here; configured when we scaffold (ADR-0006).

| Concern | Tool | Note |
|---|---|---|
| Env / deps | **uv** | fast, reproducible, lockfile-first |
| Lint + format | **ruff** (lint + format) | one tool, fast |
| Types | **pyright** (or mypy) in strict mode | the control-surface contract is type-heavy; we want it enforced |
| Tests | **pytest** + **hypothesis** | property tests for the grammar (invariants like "emitted bytes always parse") |
| Import boundaries | **import-linter** | enforces the acyclic package graph from doc 03 |
| Pre-commit | **pre-commit** | lint/type/secret-scan before commit |
| Benchmark reproducibility | pinned env + fixed seeds + logged manifests | reproducibility *is* the marketing for 0a |

See [Engineering Standards](09-engineering-standards.md) for how these compose into CI gates.
