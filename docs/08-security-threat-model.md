# 08 — Security & Threat Model

Because Crucible edits its own weights, executes tools, and may federate, **its security analysis is part of its design, not a bolt-on.** This document is the canonical threat model; it is derived from §3.3.2 and the adversarial-hardening chapters of the treatise.

## Assets

1. The user's **private data and code**.
2. The **integrity of the local model's behavior** (it must not be silently degraded or backdoored).
3. The **integrity of external resources** the agent can affect (files, repos, APIs, money).

## Trust zones

| Zone | Trusted for | Examples |
|---|---|---|
| **Trusted core** | everything | the user's own / LAN machines: policy, verifier, memory, self-improvement |
| **Semi-trusted teacher** | capability, **not** privacy | a frontier API or larger local model used for escalation/EaTS |
| **Untrusted environment** | nothing | tools, web, servers — may overreach, poison observations, inject prompts |
| **Untrusted federation** | nothing | other instances + the aggregator: honest-but-curious at best, malicious at worst |

## Non-goals (explicit)

We do **not** defend against: a compromised core, sub-OS side channels, or a teacher adversarial *in capability* (we inherit its covered errors, Prop 6.11). Stating these prevents false assurance.

## Design consequences (enforced, not advisory)

1. **Capability sandboxing + information-flow control.** Every tool runs least-privilege in an isolated environment (microVM-/gVisor-class) with **no ambient network or filesystem authority**. Each tool adapter declares a **capability schema** — the typed scopes it may read/write — and the runtime enforces information-flow constraints, so a tool granted read-only file access cannot exfiltrate via a network effect.
2. **No cross-tenant pooling of raw activations.** Such activations admit prompt-inversion attacks; pooling is confined to the user's trusted domain only.
3. **Federation shares only DP, gate-passed abstractions** — ACE deltas, PANDO skills, ROSE adapter updates — never raw data, contexts, or activations. **Every recipient re-gates every incoming abstraction** through its own local DP-holdout gate and monitors → a poisoned or unhelpful contribution cannot degrade a recipient (Byzantine robustness by construction, not by trust).
4. **Temporal-logic runtime monitors** compile safety requirements ("authenticate before accessing data", "never write outside the workspace", "confirm before an irreversible effect") into LTL specs enforced **at the emission/settlement boundary** — pre-execution guarantees, not post-hoc detection. Because the monitor sits at Layer 1, it has the action and its declared effects in hand *before* they become permanent.
5. **The self-improvement loop is itself an attack surface** and is defended:
   - The **gate** (DP holdout + FDR + reversible canary) protects against *statistical* degradation.
   - **Governance** protects against *behavioral* regression: a **frozen constitution probe** sits in the canary, so any self-edit degrading a safety behavior is rejected by the same reversible mechanism that rejects competence regressions.
   - **All self-edit and escalation logs are immutable and auditable.**
   - **Federated updates are admitted only after passing local monitors.**
6. **Reversibility classes** gate speculation: only `idempotent` / `compensable` / `snapshot-reversible` actions may be speculated; `irreversible` actions require explicit confirmation and never run on a speculative branch.

## The poisoning channel (RQ8)

When learning ingests the environment, an adversary can plant a plausible-but-wrong "convention" in a tool output, hoping it gets distilled into a committed backdoor. Defenses: (a) teacher-grounding (the signal is the teacher's verified outcome, not the environment's claim); (b) SGC must show transfer on held-out variations, not just the planted case; (c) the gate + canary + constitution probe; (d) recipients re-gate federated abstractions. **RQ8 explicitly tests that an injected convention does not become a committed backdoor.**

## Bounded blast radius (the core safety guarantee)

> Realized competence never sits more than `κ + Var_C` below the last certified level, **regardless of any failure of the DP or FDR layers** (Prop 6.7), because the only committed changes between audits are reversible adapters and restoration is exact (drop the tensors). Safety degrades *gracefully and reversibly*, never catastrophically.

## The loop expands competence, not authority

A critical scoping invariant: the self-improvement loop expands competence **within a fixed, sandboxed action space — not the action space itself.** The agent gets better at using the tools it has; it never grants itself new capabilities. Any design that lets self-improvement widen the capability set violates this model and must be rejected.

## Engineering checklist (applies as we build)

- [ ] Every tool adapter ships with a capability schema; no tool runs with ambient authority.
- [ ] Secrets never enter prompts, logs, memory, or federated abstractions (secret-scanning in CI).
- [ ] Dependency + supply-chain scanning; pinned, locked deps; SBOM at release.
- [ ] The orchestrator↔engine IPC boundary validates all shared-memory handles; no untrusted code in the engine process.
- [ ] Self-edit / escalation audit log is append-only and tamper-evident.
- [ ] DP accounting is implemented and tested before any federation round ships (P8).
- [ ] Threat model reviewed at each rung transition; new tools trigger a capability-schema review.
