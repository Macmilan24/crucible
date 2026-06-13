# Roadmap

Crucible ships as a **portfolio ladder** — each product is independently useful, and each
rung is gated by evidence before the next begins. Product 1 is real today; the rest are
scaffolded (interfaces + boundaries in place) and built in sequence.

## ✅ Product 1 — Crucible Core (shipping)

The three [token-savers](token-savers.md), the [agent loop](agent-loop.md), transactional
settlement, and the OpenAI-compatible [server](../user/cli.md). Real, tested, benchmarked.

- Grammar-scoped emission · Chain-of-Draft · KV-cache reuse
- `crucible serve` / `download-model` / `doctor`
- Packages: `engine`, `grammar`, `tokeneconomy`, `atomix`, `core`, `server`, `token-saver`, `bench`

## ⏳ Next rungs (design-only today)

| Product | Package | What it adds |
|---|---|---|
| **P2 — Verify** | `crucible-verify` | A process verifier (execution-grounded + generative, GenPRM/AgentPRM-style) and Value-of-Information compute budgeting. Turns "structurally valid" into "actually correct." |
| **P3 — Search** | `crucible-search` | Verifier-Guided Stochastic Search (VGSS) + VoI — spend compute where it pays off. |
| **P4 — Memory** | `crucible-memory` | Three-tier memory + Sleep-Time Compute (STC): consolidate off the interactive path. |
| **P5–6 — Evolve** | `crucible-evolve` | Self-improvement: ACE / PANDO / CG-TTRL / ROSE reversible adapters / EaTS / SGC. |
| **Gate** | `crucible-gate` | Differential-privacy holdout + FDR control + canary gating for safe self-improvement. |
| **P7 — Govern** | `crucible-govern` | Sandboxing + LTL runtime monitors — the safety envelope. |
| **P8 — Federation** | `crucible-federation` | FEaTS: privacy-preserving cross-device coordination. |

## Near-term hardening of Product 1

Concrete, smaller items on the way:

- **Streaming** responses (`stream: true`).
- **Tool-result round-trips** — multi-turn conversations that feed tool outputs back.
- **SGLang engine** behind the same `ControlSurface`, unlocking full cross-agent KV
  transfer and the draft/verifier surfaces (iii).

## The discipline

Every mechanism is mapped to a module, a test, and an evaluation question in the
repository's **traceability matrix**, and every climb up the ladder is gated by a
kill-criterion that doubles as a product gate. A rung that can't show its evidence doesn't
ship.
