# Crucible — code

The Crucible monorepo. This folder is a single **uv workspace**; the research and
the planning docs live one level up in [`../paper/`](../paper/) and [`../docs/`](../docs/) and are
deliberately kept out of here.

> Build scope right now: **Phase 0 + Product 1 (Crucible Core)**. Packages marked
> _design-only_ are scaffolded so the dependency graph and boundaries are real
> from day one, but carry no implementation yet. See [`../docs/06-roadmap.md`](../docs/06-roadmap.md).

## Getting started

```bash
cd code
uv sync --all-packages   # creates .venv and installs every workspace package + dev tools
make check               # lint + type-check + import-boundaries + tests  (the local gate)
```

`uv` is the only entry point — every command runs inside the locked workspace
environment, so there is no "works on my machine" drift. If you don't have uv:
`curl -LsSf https://astral.sh/uv/install.sh | sh`.

## Layout

```
code/
├── pyproject.toml          # workspace root (virtual), dev tools, shared config
├── .python-version         # pinned interpreter (3.12)
├── .importlinter           # the package-graph contract
├── pyrightconfig.json      # type-checking (strict on engine/grammar/gate)
├── Makefile                # make help
├── packages/               # each dir = one responsibility = one future repo
│   ├── crucible-engine/         # 🟢 control-surface contract + SGLang integration
│   ├── crucible-grammar/        # 🟢 trajectory grammar + two-phase emission masking
│   ├── crucible-atomix/         # 🟢 transactional settlement (reversibility classes)
│   ├── crucible-tokeneconomy/   # 🟢 Chain-of-Draft + KV-cache inter-agent comms
│   ├── crucible-core/           # 🟢 the orchestrator / agent loop (P1)
│   ├── crucible-verify/         # 🟡 GenPRM/AgentPRM verifier (P2)
│   ├── crucible-search/         # 🟡 VGSS + VoI (P3)
│   ├── crucible-memory/         # 🟡 three-tier memory + STC (P4)
│   ├── crucible-evolve/         # 🟡 ACE/PANDO/CG-TTRL/ROSE/EaTS/SGC (P5–6)
│   ├── crucible-gate/           # 🟡 DP holdout + FDR + canary gate
│   ├── crucible-govern/         # ⚪ sandboxing + LTL monitors (P7)
│   └── crucible-federation/     # ⚪ FEaTS coordinator (P8)
├── apps/
│   ├── token-saver/        # 🟢 0b drop-in wrapper (true subset of Core)
│   └── calculator/         # 🟢 0c public token calculator (web; stack TBD)
├── bench/
│   └── crucible-bench/     # 🟢 0a reproducible benchmark harness
├── tools/                  # repo tooling / codegen / release scripts
└── tests/                  # cross-package integration + e2e
```
🟢 in scope · 🟡 design-only (interfaces, built later) · ⚪ future

## The rules that keep "extract to its own repo later" cheap

1. One package = one responsibility = one future repo ([ADR-0002](../docs/adr/0002-monorepo-now-polyrepo-later.md)).
2. Dependencies are one-directional and acyclic — enforced by `make imports`.
3. Never import another package's `_internal`; only its public API.
4. Per-package version + license metadata from day one.

Heavy ML runtime deps (SGLang, torch, XGrammar) are **deliberately not installed
yet** — they are platform/GPU-specific and not needed for the scaffold. They are
recorded as commented extras in `crucible-engine` and pulled in when we start the
real engine integration.
