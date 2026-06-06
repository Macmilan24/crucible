# crucible-core 🟢 — Product 1, the wedge

> "Cut your agent's token bill 5–10× and never ship a malformed tool call — on your
> own machine."

The inference-native orchestrator: it runs the agent loop as a function of
`(context, engine state)`, in its **own fault domain** ([ADR-0001](../../../docs/adr/0001-inference-native-co-location.md)), composing the
substrate packages:

- `crucible-engine` — the control-surface contract (the wall)
- `crucible-grammar` — two-phase decoding (free cognition, masked emission)
- `crucible-tokeneconomy` — adaptive Chain-of-Draft + typed handoffs
- `crucible-atomix` — transactional settlement for tool calls

- PRD: [`../../../docs/product/p1-core.md`](../../../docs/product/p1-core.md)
- Architecture: [`../../../docs/02-architecture.md`](../../../docs/02-architecture.md)

`Substrate` is the public facade that the 0b token-saver reuses as a *true subset*
([ADR-0005](../../../docs/adr/0005-token-saver-as-true-subset.md)) — so the drop-in wrapper and the full runtime never fork.

**Status:** scaffold — `Agent.run_episode` demonstrates a grammar-valid
think→emit→halt episode end-to-end on the MockEngine, with masked emission and
atomic settlement. The SGLang-backed engine and the full loop replace the mock.
