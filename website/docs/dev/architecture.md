# Architecture

## The API-boundary wall

A conventional agent talks to its model through a **stateless text API**: prompt in, text
out. Everything the engine knows mid-generation — the next-token **logits**, the
**KV-cache** tree, the **draft** head's speculative proposals, a **verifier**'s score, the
ability to **edit weights** — is discarded at that boundary. Call this the *wall*.

Crucible's wager: for local agents, the gap that matters is **architectural, not
parameters**. So it runs the agent loop **below the wall** and programs those control
surfaces directly.

```
        ┌──────────────────────────── above the wall ───────────────────────────┐
        │   conventional agent:  prompt ──▶ [ TEXT API ] ──▶ text                │
        └────────────────────────────────────────────────────────────────────────┘
                                       ✂  (logits, KV-cache, draft, scores, weights discarded)
        ┌──────────────────────────── below the wall ───────────────────────────┐
        │   Crucible:  orchestrator ⇄ ControlSurface ⇄ engine (llama.cpp today)  │
        │              mask logits · fork/prune KV · read draft & scores · adapt │
        └────────────────────────────────────────────────────────────────────────┘
```

## The control-surface contract

The boundary is a typed Protocol, [`ControlSurface`](engine-contract.md) — the programmable
form of the treatise's "inference-native orchestrator." It names five surfaces:

| # | Surface | Method(s) | Used in Product 1 |
|---|---------|-----------|-------------------|
| i | Logits + masking | `read_logits`, `sample(mask=…)` | ✅ grammar-scoped emission |
| ii | KV-cache tree | `fork`, `prune` | ✅ prefix reuse across turns |
| iii | Draft + verifier scores | `draft`, `verifier_score` | ⏳ P2/P3 |
| iv | Reversible weight edits | `apply_adapter`, `revert_adapter` | ⏳ P5–6 (ROSE) |
| v | Idle scheduling | `schedule_idle` | ⏳ P4 (STC) |

Product 1 exercises surfaces **(i)** and **(ii)** for real. The rest are part of the same
contract so the architecture is honest from day one — they light up in later products.

!!! note "Engine of record vs engine today"
    The paper's engine of record is **SGLang** (RadixAttention / XGrammar / EAGLE) on a
    CUDA GPU. The shipping Mac engine is **`llama.cpp`** via `llama-cpp-python` (Metal).
    Because all engine access is isolated behind `ControlSurface`, swapping engines is an
    additive backend, not a rewrite (ADR-0003).

## The six layers

The full system is organised as six layers (see the research for the complete treatment):

1. **Engine / control surface** — the wall and its five surfaces. → `crucible-engine`
2. **Trajectory grammar** — two-phase decoding; constrain emission, never cognition. → `crucible-grammar`
3. **Token economy** — Chain-of-Draft reasoning dial + KV-cache inter-agent comms. → `crucible-tokeneconomy`
4. **Settlement** — transactional, reversibility-classed effects (Atomix). → `crucible-atomix`
5. **Orchestration** — the agent loop that composes the above. → `crucible-core`
6. **Self-improvement & governance** — verifier, search, memory, evolution, gates. → P2+ (design-only today)

Product 1 is layers 1–5, plus the OpenAI-compatible server (`crucible-server`) that exposes
the loop to the outside world.

## What "inference-native" buys you, concretely

- **Valid tool calls by construction** — masking at surface (i) makes a malformed call
  impossible, not merely unlikely. → [Grammar](grammar.md)
- **Fewer tokens for the same answer** — a reasoning dial picks terse drafts on easy steps.
  → [Token-savers](token-savers.md)
- **Less repeated prefill** — shared context is encoded once and reused via surface (ii).
  → [Token-savers](token-savers.md)

Each of these is **measured**, not asserted. → [Benchmarks](benchmarks.md)

## Further reading

The repository's `docs/` folder holds the full engineering record: vision & scope,
glossary, the architecture deep-dive, evaluation plan, risk register, security/threat
model, and the traceability matrix mapping every mechanism to a module and a test.
