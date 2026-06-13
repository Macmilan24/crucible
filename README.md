<div align="center">

# 🔥 Crucible

**A token-frugal local agent runtime — frontier-grade agents on your own machine.**

[![License: Apache-2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Docs](https://img.shields.io/badge/docs-macmilan24.github.io%2Fcrucible-ff5a1f.svg)](https://macmilan24.github.io/crucible/)
[![Release](https://img.shields.io/badge/release-v0.1.0-success.svg)](https://github.com/Macmilan24/crucible/releases)

[Documentation](https://macmilan24.github.io/crucible/) ·
[Quickstart](https://macmilan24.github.io/crucible/user/quickstart/) ·
[Download](https://github.com/Macmilan24/crucible/releases) ·
[Architecture](https://macmilan24.github.io/crucible/dev/architecture/)

</div>

---

Crucible lifts a **small local language model** into a reliable, tool-using agent and serves
it behind the **OpenAI Chat Completions API** — so opencode, Continue, Cursor, or the
`openai` SDK work against it unchanged, and every tool call comes back **grammar-valid by
construction**.

> The gap that matters for local agents is **architectural, not parameters**. Today's agents
> reach the model only through a stateless text API — discarding the KV-cache, the logits,
> the draft proposals, the verifier scores. Crucible runs the agent loop *below that wall*
> and uses those control surfaces directly.

### What it is — and what it isn't

Crucible **runs the model itself, locally**. It is **not** a proxy that shrinks your
OpenAI/Claude bill — two of its three token-savers (logit-level grammar masking and KV-cache
reuse) physically require access to model internals that no cloud API exposes. The payoff of
running local isn't a smaller API invoice; it's **speed, compute, privacy, and reliability**:
fewer tokens to prefill and generate, nothing leaving your machine, and tool calls that
*can't* be malformed. (Self-host at scale and those token savings become real
throughput-per-GPU savings.) See [Why local?](https://macmilan24.github.io/crucible/user/faq/).

## Quickstart

```sh
curl -LsSf https://raw.githubusercontent.com/Macmilan24/crucible/main/scripts/install.sh | sh
crucible download-model        # Qwen2.5-3B-Instruct Q4_K_M, ~1.9 GB, resumable
crucible serve                 # OpenAI-compatible server on http://127.0.0.1:8000/v1
```

Then call it like OpenAI:

```sh
curl http://127.0.0.1:8000/v1/chat/completions -H 'Content-Type: application/json' -d '{
  "model": "crucible-local",
  "messages": [{"role": "user", "content": "Book a 2pm meeting in Room B"}],
  "tools": [{"type": "function", "function": {"name": "create_event",
    "parameters": {"type": "object",
      "properties": {"title": {"type":"string"}, "date": {"type":"string"},
                     "time": {"type":"string"}, "location": {"type":"string"}},
      "required": ["title","date","time","location"]}}}]
}'
# → finish_reason: "tool_calls", a structurally valid create_event call.
```

Full walkthrough and client configs (opencode, Continue, Cursor): **[Quickstart →](https://macmilan24.github.io/crucible/user/quickstart/)**

## What ships today — Product 1: Crucible Core

Three token-savers, an agent loop, transactional settlement, and the OpenAI-compatible
server. The headline numbers are **measured, not estimated** — reproduce them with the
bundled harness.

| Mechanism | Result | Measure |
|---|---|---|
| **Grammar-scoped emission** | **100% → 0%** malformed tool calls | unconstrained vs grammar, same suite |
| **Chain-of-Draft reasoning** | **4.28×** fewer tokens at matched 100% success | 152.5 → 35.7 mean completion tokens (95% CI 3.4–5.5×) |
| **KV-cache reuse** | **4.94×** less prefill, byte-identical output | 20,263 → 4,099 prefill tokens over 5 turns / 4,050-token context |

<sub>Measured on Apple M-series (Metal) · Qwen2.5-3B-Instruct Q4_K_M · `crucible-mini` suite · seeds 0/1/2 · commit `234859e`. Your numbers will vary with model, quant, seeds, and hardware — re-run the harness for your own manifest.</sub>

## Install options

| Method | Command |
|---|---|
| **One-liner** | `curl -LsSf https://raw.githubusercontent.com/Macmilan24/crucible/main/scripts/install.sh \| sh` |
| **From a release** | Download `crucible-wheelhouse-*.tar.gz` from [Releases](https://github.com/Macmilan24/crucible/releases), then `uv tool install --find-links <dir> --with llama-cpp-python crucible-server` |
| **From source** | `git clone … && cd crucible/code && uv sync --all-packages --extra llama` |

Details, prerequisites, and `crucible doctor`: **[Install →](https://macmilan24.github.io/crucible/user/install/)**

## Build from source

```sh
cd code
uv sync --all-packages --extra llama   # .venv + every package + dev tools + the llama.cpp engine
make check                             # lint + format + types + import-boundaries + tests
```

The fast gate runs on `MockEngine` — no model, no GPU. Model-backed runs are marked `slow`.
See [`code/README.md`](code/README.md) for workspace layout and conventions.

## Roadmap

**Product 1 (Crucible Core) is real and shipping today.** The later rungs are scaffolded
(interfaces + package boundaries in place) and built in sequence, each gated by evidence:
process **Verify** (P2), **Search** (P3), **Memory** (P4), self-**Evolve** (P5–6),
**Govern** (P7), **Federation** (P8). See the
[roadmap](https://macmilan24.github.io/crucible/dev/roadmap/).

## The research

- [`paper/`](paper/) — the research-book edition, the structured treatise, and the product
  portfolio / go-to-market strategy.
- [`docs/`](docs/) — the engineering record: vision & scope, architecture, evaluation plan,
  ADRs, and the traceability matrix.

## License & author

Apache-2.0 © 2026 **Samuel Dagne** — Independent Researcher.
