# ADR-0007 — SQLite + vector index for all local stores

- **Status:** accepted
- **Date:** 2026-06-06
- **Deciders:** Samuel Dagne
- **Relates to:** treatise §7.1; [Tech Stack](../04-tech-stack.md); [Security](../08-security-threat-model.md)

## Context

Crucible is local-first and privacy-preserving: raw data must never leave the device. It needs to persist working/episodic/semantic memory, the ACE playbook, PANDO skills, ROSE adapters, the probe `H`, and the canary `C`. A server-based datastore would contradict the privacy posture and add ops burden on consumer hardware.

## Options considered

1. **A client–server DB (Postgres, etc.)** — powerful. *Con: a running server on a user's laptop; contradicts the local-first/zero-ops posture.*
2. **A managed/cloud vector DB** — easy scaling. *Con: data leaves the device; violates Principle 3.6 outright.*
3. **Embedded SQLite + a local vector index** — zero-server, single-file, transactional, ubiquitous; vector index (e.g. an embedded ANN / `sqlite-vec`-style) for semantic retrieval.

## Decision

**Option 3.** All local stores are SQLite + a local vector index. Nothing leaves the device except, optionally, DP-gated federated abstractions (and that path is its own subsystem, not the datastore).

## Consequences

- Positive: zero-ops on consumer hardware; transactional; trivially backed up (one file); aligns with the privacy threat model.
- Negative / costs: must manage store growth (STC prunes episodic memory; adapters merged/bounded); vector-index choice needs benchmarking for local scale.
- Commits us to: a storage interface in `crucible-memory` that abstracts the concrete vector index; bounded-store discipline enforced by STC.

## Revisit when

Local scale outgrows SQLite + embedded ANN for a real user `D_u`, or a better embedded option appears. The storage interface keeps this swap local.
