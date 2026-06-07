# Crucible

**An inference-native, self-improving, privacy-preserving runtime that lifts small local language models (7–9B) to frontier-grade agency on a user's own distribution of work.**

> The gap that matters for local agents is mostly **architectural, not parameters**. Today's agents reach the model only through a stateless text API — discarding the KV-cache, logits, draft proposals, verifier scores, and the ability to change the model. Crucible co-locates the agent loop *below that wall* and uses those control surfaces.

This repository is the home of the Crucible system. It is currently at the **pre-implementation stage**: the research is complete (see [`paper/`](paper/)) and we are building the engineering foundation before writing runtime code.

---

## Status

| | |
|---|---|
| **Phase** | Foundation complete; **monorepo scaffolded** — building Phase 0 + P1 |
| **First build target** | Phase 0 wedge (benchmark + token-saver + calculator) → **Product 1: Crucible Core** |
| **Code** | [`code/`](code/) — a single `uv` workspace (kept out of `paper/` and `docs/`). Gate is green: lint + types + import-boundaries + 43 tests. |
| **Repo model** | Private monorepo now → extract spin-out libraries to their own repos later |
| **Primary stack** | Python 3.11+, SGLang (RadixAttention / XGrammar-2 / EAGLE-3), veRL, BitNet.cpp, SQLite + vector index |

## Build it

```bash
cd code
uv sync --all-packages   # creates .venv, installs every workspace package + dev tools
make check               # lint + type-check + import-boundaries + tests
```

See [`code/README.md`](code/README.md) for the workspace layout and conventions.

## The documents

Read in this order:

1. **[Vision & Scope](docs/00-vision-and-scope.md)** — the wager, what we ship first, success and kill criteria, non-goals.
2. **[Glossary](docs/01-glossary.md)** — every acronym and mechanism (EaTS, FEaTS, VGSS, VoI, STC, ROSE, SGC, ACE, PANDO, the wall …).
3. **[Architecture](docs/02-architecture.md)** — the six layers, the API-boundary wall, the control-surface contract, the risk ledger.
4. **[Repo & Modularization](docs/03-repo-and-modularization.md)** — monorepo layout designed for clean extraction into spin-out repos.
5. **[Tech Stack](docs/04-tech-stack.md)** — what we use and why, mapped to the architecture.
6. **[Evaluation Plan](docs/05-evaluation-plan.md)** — research questions, baselines, suites, metrics, statistics, and the kill-criteria that double as product gates.
7. **[Roadmap](docs/06-roadmap.md)** — the portfolio ladder and the sequencing, each climb gated by evidence.
8. **[Risk Register](docs/07-risk-register.md)** — technical risks, the treatise's standing assumptions, and threats to validity.
9. **[Security & Threat Model](docs/08-security-threat-model.md)** — trust zones, sandboxing, and the self-improvement attack surface.
10. **[Engineering Standards](docs/09-engineering-standards.md)** — language, testing, reproducibility, CI/CD plan, branching, versioning.
11. **[Traceability Matrix](docs/10-traceability-matrix.md)** — every mechanism and theorem mapped to a module, a test, and an evaluation question. *This is the "don't miss anything" sheet.*

Architecture Decision Records live in **[`docs/adr/`](docs/adr/)**.
Product requirement docs live in **[`docs/product/`](docs/product/)**.

## The research

- [`paper/Cruciable_book.pdf`](paper/) — the research-book edition (architecture, theory, engineering).
- [`paper/Cruciable_v2.pdf`](paper/) — the structured treatise edition (same content).
- [`paper/An_Inference_Native...pdf`](paper/) — the product portfolio & go-to-market strategy.

## Author

Samuel Dagne — Independent Researcher.
