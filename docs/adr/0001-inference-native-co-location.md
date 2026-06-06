# ADR-0001 — Inference-native co-location with separate fault domains

- **Status:** accepted
- **Date:** 2026-06-06
- **Deciders:** Samuel Dagne
- **Relates to:** treatise §3.3.4, §4.1, §7.5.1; [Architecture](../02-architecture.md)

## Context

Crucible's entire thesis is to orchestrate *beneath the API-boundary wall* — reading logits, forking the KV-cache, seeing draft/verifier scores, and applying reversible weight edits. That requires the orchestrator to share the engine's internal state. The naive reading ("shared address space", one process) is dangerous: an orchestrator bug during a deep VGSS expansion could crash the engine and destroy the shared KV-cache. The red-team (treatise §7.5.1) flagged this as a real defect in early drafts.

## Options considered

1. **Single process, shared address space** — maximal performance, simplest IPC. *Con: single crash domain; orchestrator OOM kills the engine and the cache. Unacceptable.*
2. **Fully separate services over a network/socket API** — clean isolation. *Con: re-introduces the wall (serialization, copies); defeats the purpose.*
3. **Separate processes, zero-copy shared memory + IPC handles** — engine and orchestrator each in their own fault domain; cache tree, logits, adapter handles exposed as handles (not copies); a supervisor restarts the orchestrator without losing engine state.

## Decision

**Option 3.** "Inference-native" means **shared state access, not a shared fault domain.** The engine does stateless tensor work in its own process; the stateful, transactional application logic lives in the orchestrator process with its own resource limits and a supervisor.

## Consequences

- Positive: every Def-3.2 capability preserved at memory speed; an orchestrator crash cannot take down the engine or the cache.
- Negative / costs: IPC + shared-memory plumbing is non-trivial; the control-surface contract ([doc 02](../02-architecture.md)) must be carefully designed and validated; handle lifetimes and security must be managed.
- Commits us to: a `crucible-engine` package that owns this boundary; contract tests with a mock engine; **no arbitrary agentic logic ever runs in the engine process** (hard invariant).

## Revisit when

A single-process embedding becomes provably safe (e.g. via language-level isolation) *and* profiling shows the IPC boundary is a real bottleneck we cannot otherwise close.
