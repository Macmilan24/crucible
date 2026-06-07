# 03 — Repository & Modularization

**Decision:** start as a **private monorepo**, with package boundaries clean enough that each spin-out library can later be **extracted into its own public repo** with minimal churn. See [ADR-0002](adr/0002-monorepo-now-polyrepo-later.md).

The strategy paper's horizontal spin-outs are not an afterthought — they are how Crucible's primitives become the ecosystem's defaults. So we design the package graph today as if each spin-out were already a separate library: **strict, one-directional dependencies; no reaching across package internals; a public API per package.** Extraction later then becomes "move a directory + flip a visibility bit," not a refactor.

## Mapping: spin-out libraries → packages → products

| Spin-out (future OSS lib) | Monorepo package | Standalone value | Funnels to |
|---|---|---|---|
| **Grammar engine** | `crucible-grammar` | zero-malformed tool/structured emission for any local model | Core (P1) |
| **Atomix tool runtime** | `crucible-atomix` | safe, transactional tool execution with rollback for any agent | Core / Verify |
| **Process verifier** | `crucible-verify` | a drop-in local reward/verifier model + API | Verify (P2) |
| **DP self-improvement gate** | `crucible-gate` | a library for safe online learning (any self-improving system) | Evolve (P5–6) |
| **Consolidation memory** | `crucible-memory` | three-tier memory + sleep-time consolidation for any agent | Memory (P4) |
| **Federation coordinator** | `crucible-federation` | privacy-preserving federated distillation as a service | Federation (P8) |

## Monorepo layout

> **Scaffolded and live.** All source lives in [`../code/`](../code/) — a single `uv`
> workspace, kept out of `paper/` and `docs/`. Git, CI, and licensing live at the
> repo root. The full gate (lint + types + import boundaries + tests) is green.
> See [`../code/README.md`](../code/README.md) to run it.

```
crucible/                          # repo root (git, CI, license)
├── README.md · CONTRIBUTING.md
├── .github/workflows/ci.yml       # CI runs the gate inside code/
├── .pre-commit-config.yaml · .gitignore
├── paper/                         # the research (PDFs)
├── docs/                          # ← this foundation
└── code/                          # the uv workspace — ALL source lives here
    ├── pyproject.toml             # workspace root (virtual): dev tools + shared config
    ├── uv.lock                    # committed for reproducibility
    ├── .python-version · pyrightconfig.json · .importlinter · Makefile
    ├── packages/                  # each dir is a future standalone repo
    │   ├── crucible-engine/       # 🟢 control-surface contract + SGLang integration
    │   ├── crucible-grammar/      # 🟢 trajectory grammar + two-phase emission masking
    │   ├── crucible-atomix/       # 🟢 transactional settlement runtime
    │   ├── crucible-tokeneconomy/ # 🟢 Chain-of-Draft + KV-cache inter-agent comms
    │   ├── crucible-core/         # 🟢 P1: orchestrator / agent loop
    │   ├── crucible-verify/       # 🟡 GenPRM/AgentPRM verifier (P2)
    │   ├── crucible-search/       # 🟡 VGSS + VoI (P3)
    │   ├── crucible-memory/       # 🟡 three-tier memory + STC (P4)
    │   ├── crucible-evolve/       # 🟡 ACE/PANDO/CG-TTRL/ROSE (P5–6)
    │   ├── crucible-gate/         # 🟡 DP holdout + FDR + canary gate
    │   ├── crucible-govern/       # ⚪ sandboxing + LTL monitors (P7)
    │   └── crucible-federation/   # ⚪ FEaTS coordinator (P8)
    ├── apps/
    │   ├── token-saver/           # 🟢 0b: drop-in wrapper (true subset of Core)
    │   └── calculator/            # 🟢 0c: token calculator (web; not a Python member)
    ├── bench/
    │   └── crucible-bench/        # 🟢 0a: reproducible benchmark harness + Phase-0 gate
    ├── tools/                     # repo tooling, codegen, release scripts
    └── tests/                     # cross-package integration + e2e
```
🟢 implemented (scaffold) · 🟡 design-only · ⚪ future

### Dependency direction (must stay acyclic)

```
crucible-engine  ◀── crucible-grammar ◀── crucible-core
       ▲                  ▲                    │
       └── crucible-atomix ┘                    ▼
                                         crucible-tokeneconomy
apps/token-saver ──▶ crucible-core (subset)     bench/crucible-bench ──▶ crucible-core + baselines
```

- **`crucible-engine`** owns the control-surface contract (logits/cache/draft/scores/adapters/idle). Everything that needs the wall goes through it. *This is the single integration point with SGLang* — isolating it means an engine swap (e.g. to vLLM) touches one package.
- **No package imports another package's internals** — only its published API. Enforced by lint rules + import-linter (see [Engineering Standards](09-engineering-standards.md)).
- **`apps/token-saver` (0b)** depends only on a *subset* of `crucible-core` — it must remain a genuine true-subset of Product 1, not a fork.

## Rules that keep "extract later" cheap

1. **One package = one responsibility = one future repo.** If two things would ship as separate OSS libs, they are separate packages now.
2. **Public API is explicit.** Each package exposes its API through its top-level `__init__`/published surface; everything else is private. Cross-package imports of private modules fail CI.
3. **No shared "utils" dumping ground.** Shared code goes in a small, versioned `crucible-common` only if genuinely cross-cutting; prefer duplication over a god-package.
4. **Per-package versioning from day one** (even inside the monorepo), so extraction inherits a clean changelog.
5. **Per-package licensing metadata.** Free/OSS packages (Core, grammar, atomix, verify, gate, memory, federation-coordinator-client) vs. commercial/enterprise (govern dashboards, federation coordinator service). See [ADR-0008](adr/0008-licensing-open-core.md).
6. **Tests live with their package**; only true cross-package flows live in top-level `tests/`.

## Extraction playbook (when we move a spin-out to its own repo)

1. Confirm zero inbound deps on its private modules (import-linter report is green).
2. `git subtree split` the package directory into a new repo, preserving history.
3. Publish to the registry under its already-existing version.
4. Replace the monorepo path-dependency with the published package.
5. Flip visibility to public; attach the OSS license and a README pointing back to the platform.

This is deliberately boring — which is the point.
