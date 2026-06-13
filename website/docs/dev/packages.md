# Package map

Crucible is a **uv workspace**: one directory per responsibility, each designed to become
its own repository later. Dependencies are one-directional and acyclic, enforced in CI.

## Product 1 packages (shipping)

| Package | Layer | Responsibility |
|---------|-------|----------------|
| `crucible-engine` | 1 | The control-surface contract (the wall) + the `llama.cpp` backend + `MockEngine`. |
| `crucible-grammar` | 2 | GBNF builders, two-phase emission masking, the trajectory grammar. |
| `crucible-tokeneconomy` | 3 | Chain-of-Draft reasoning dial + KV-cache handoff. |
| `crucible-atomix` | 4 | Transactional settlement with reversibility classes. |
| `crucible-core` | 5 | The `Substrate` facade + the multi-step agent loop. |
| `crucible-server` (app) | — | The OpenAI-compatible server + the `crucible` CLI. |
| `crucible-token-saver` (app) | — | The 0b drop-in wrapper (a true subset of Core). |
| `crucible-bench` | — | The reproducible benchmark harness. |

## Design-only packages (later products)

Scaffolded so the dependency graph and boundaries are real from day one — interfaces today,
implementation in their product:

`crucible-verify` (P2) · `crucible-search` (P3) · `crucible-memory` (P4) ·
`crucible-evolve` (P5–6) · `crucible-gate` · `crucible-govern` (P7) ·
`crucible-federation` (P8). See the [roadmap](roadmap.md).

## The dependency rules

```
engine ◀── grammar ◀── core ──▶ atomix
   ▲          ▲          │
   └──────────┴──────────┴──▶ tokeneconomy
                          core ──▶ server (app), token-saver (app)
```

1. **One package = one responsibility = one future repo.** (ADR-0002)
2. **Dependencies are acyclic and one-directional** — enforced by `import-linter`
   (`make imports`). A layering contract plus a "no reaching into another package's
   internals" contract.
3. **Never import another package's `_internal`** — only its public API (`__init__`).
4. **Per-package version + license metadata** from day one (all Apache-2.0).

These are what make "extract this package into its own repo later" a cheap, mechanical move
rather than a refactor.

## Repo layout

```
crucible/
├── code/                     # the uv workspace
│   ├── packages/             # crucible-engine, -grammar, -atomix, -tokeneconomy, -core, …
│   ├── apps/                 # server (+ CLI), token-saver
│   ├── bench/crucible-bench/ # the benchmark harness
│   ├── tools/                # agent_demo.py, run_benchmark.py, real_slice.py
│   └── Makefile              # make check = the local gate
├── website/                  # this documentation site (MkDocs Material)
├── docs/                     # the engineering record (ADRs, vision, eval plan, …)
├── paper/                    # the research
└── scripts/install.sh
```
