# token-saver 🟢 — Phase 0 (0b)

The "come for the tool" artifact: a tiny wrapper that slots under whatever local
agent a developer already runs and returns the same answers for a fraction of the
tokens, with malformed calls eliminated. **One-line install, one-flag enable.**

- PRD: [`../../../docs/product/0b-token-saver.md`](../../../docs/product/0b-token-saver.md)
- Decision: [ADR-0005](../../../docs/adr/0005-token-saver-as-true-subset.md) — this is a **true subset** of
  `crucible-core` (it reuses `core.Substrate`), never a fork.

**Status:** scaffold — `TokenSaver` wraps the Core substrate (masked emission +
adaptive draft budget). Host adapters (Ollama / vLLM / a framework hook) come with
the real build.
