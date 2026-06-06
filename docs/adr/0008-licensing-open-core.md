# ADR-0008 — Open-core licensing, private-until-launch

- **Status:** accepted
- **Date:** 2026-06-06
- **Deciders:** Samuel Dagne
- **Relates to:** strategy paper §5, §7, §7.5.10; [Roadmap](../06-roadmap.md)

## Context

The strategy is open-core: the free local runtime and the spin-out libraries are the growth engine; revenue layers on top (Pro/Team/Enterprise) without taxing the core. A common objection — "open-source cedes the moat" — is answered in the treatise: **the moat is downstream (specialization data, network effect), not the license.** The user's preference is to start private and go public at the right moment for maximum launch impact (Hacker-News dynamics reward a polished, reproducible drop).

## Decision

- **Repo starts private**; flip to public when the 0a benchmark is reproducible and the launch is ready (maximize launch-day impact).
- **Open-core tiers:**
  - **Free / OSS** (permissive, e.g. Apache-2.0/MIT): local runtime (Core) + spin-out libraries (grammar engine, Atomix, process verifier, DP gate, consolidation memory, federation-coordinator client).
  - **Commercial / source-available**: enterprise surfaces — governance/audit dashboards (P7), the federation coordinator *service* + privacy accounting (P8), managed/hosted escalation routing.
- **Per-package license metadata** from day one so the boundary is unambiguous at extraction time.

## Consequences

- Positive: OSS primitives build mindshare and make Crucible's vocabulary the ecosystem's (its own moat); revenue sits on governance/federation/managed surfaces where it doesn't tax adoption.
- Negative / costs: must keep the free/paid line clean as features land; contributor licensing (CLA/DCO) needs deciding before public launch.
- Commits us to: choosing exact OSS licenses per spin-out and a contribution agreement before going public; not monetizing the core.

## Revisit when

The free/paid boundary needs adjustment as the ladder climbs (e.g. which Pro features are usage- vs seat-priced), or licensing strategy shifts. Each change is a new ADR.
