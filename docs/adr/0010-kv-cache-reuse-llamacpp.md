# ADR-0010 — KV-cache reuse on llama.cpp (Mac): same-model prefix reuse

- **Status:** accepted
- **Date:** 2026-06-13
- **Deciders:** Samuel Dagne
- **Relates to:** treatise §4.4.4; [Architecture](../02-architecture.md); P1 spec; [ADR-0003](0003-inference-engine-sglang.md)

## Context

P1's token economy has three savers: grammar-scoped emission, Chain-of-Draft, and
**KV-cache inter-agent communication** — a receiver reusing already-processed context
instead of re-reading it as text (~2.8× prefill saving in the paper). The full
cross-*different*-LLM transfer (DroidSpeak) and tree sharing want SGLang/RadixAttention
(CUDA), which the Mac doesn't have. The question: what real slice can we ship now?

## Spike result

A throwaway spike on llama.cpp/Metal showed that **a shared prefix's KV-cache is
reused automatically within a persistent context**: on a 2771-token shared prefix, a
repeat turn evaluated only **7** prompt tokens. `llama_perf_context(ctx).n_p_eval`
exposes "prompt tokens actually processed", giving a clean, honest metric.

## Options considered

1. **Low-level `eval`/`n_past` rewrite** — most control, but re-implements sampling +
   grammar at the token level; brittle. Rejected for now.
2. **`save_state`/`load_state` snapshots** — concrete "restore agent A's cache", but
   coarse (whole-context, single sequence). Kept in reserve.
3. **Persistent-context prefix reuse + `LlamaRAMCache`** — keep one engine; a shared
   `system` prefix is reused across turns/agents; `LlamaRAMCache` restores it across
   prefix switches. Simplest, real, measurable.

## Decision

**Option 3.** `LlamaCppEngine` exposes `Generation.prompt_eval_tokens` (tokens actually
prefilled), `reset_context()` (force a full prefill — the no-reuse baseline), and
`enable_prefix_cache()`. The benchmark's `run_kv_reuse` measures prefill tokens with vs
without reuse on a long-shared-context, multi-turn scenario.

## Consequences

- Positive: the third P1 token-saver is **real and measured on the Mac** — 4.94× fewer
  prefill tokens on a 5-turn / 4050-token-context probe; a correctness invariant test
  proves reuse does **not** change output.
- Negative / honest scope: this is **same-model prefix reuse**, not full cross-agent KV
  transfer (DroidSpeak) or embedding-space messages (CIPHER) — those remain the
  SGLang/GPU phase. The win is on **prefill**, not generation, and is ~0 for short
  un-shared contexts.
- Commits us to: keeping `prompt_eval_tokens` in the typed `Generation`; documenting the
  Mac-vs-GPU boundary wherever KV-cache is claimed.

## Revisit when

We move to the SGLang/GPU path, where RadixAttention enables true cross-agent tree
sharing — at which point this becomes the CPU/Mac profile of the same capability.
