# crucible-tokeneconomy 🟢

The wedge's economic value: spend a fraction of the tokens at matched accuracy.

- Spec: [`../../../docs/02-architecture.md`](../../../docs/02-architecture.md) (Layer 1, the token economy)
- Decision: [ADR-0004](../../../docs/adr/0004-grammar-two-phase-decoding.md) (works with two-phase decoding)

Two mechanisms:
1. **Chain-of-Draft, adaptively** — terse ~5-word reasoning on trivial steps, full
   free-text (or a VGSS expansion) on pivotal ones. Compression is a *dial the VoI
   controller turns down on hard steps*, never a blanket constraint. Until real VoI
   lands (P2-era), a heuristic chooses the mode; it always restores full reasoning
   on multi-file / cross-scope steps.
2. **Inter-agent communication without natural language** — typed handoffs that
   reference a shared KV-cache node instead of re-verbalizing the whole context.

**Status:** scaffold — the budget heuristic, draft-compliance check, and typed
handoff are real; they get wired to the verifier-driven VoI controller later.
