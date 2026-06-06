# crucible-engine 🟢

Owns the **control-surface contract** — the single, typed boundary between the
orchestrator and the inference engine (the "wall"). Everything that needs to read
logits, fork the KV-cache, see draft/verifier scores, apply reversible adapters, or
schedule idle compute goes through here.

- Spec: [`../../../docs/02-architecture.md`](../../../docs/02-architecture.md) (control-surface contract table)
- Decisions: [ADR-0001](../../../docs/adr/0001-inference-native-co-location.md) (separate fault domains), [ADR-0003](../../../docs/adr/0003-inference-engine-sglang.md) (SGLang)

**Invariant:** no arbitrary agentic logic ever runs in the engine process. The
engine does stateless tensor work in its own fault domain; this package exposes its
state to the orchestrator via zero-copy shared memory + IPC handles.

**Status:** scaffold. The `ControlSurface` Protocol defines the contract; a
`MockEngine` lets the rest of the system be developed and tested without a GPU.
The SGLang-backed implementation is the first real build task.
