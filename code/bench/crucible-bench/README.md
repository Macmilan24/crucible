# crucible-bench 🟢 — Phase 0 (0a)

The reproducible benchmark. Its headline: **"5–10× fewer tokens, 0 malformed calls,
locally"** — three curves (tokens, malformed-rate, success) for a stock local agent
vs. the same model under the Crucible substrate.

- PRD: [`../../../docs/product/0a-benchmark.md`](../../../docs/product/0a-benchmark.md)
- Eval plan: [`../../../docs/05-evaluation-plan.md`](../../../docs/05-evaluation-plan.md)
- Decision: [ADR-0009](../../../docs/adr/0009-evaluation-as-product-gate.md) (evaluation is the product gate)

**Reproducibility is the marketing.** Every run logs a `RunManifest` (commit, seeds,
model hash, hardware, suite) so anyone can reproduce the headline from the repo.

**The master gate** is encoded here: `passes_phase0_gate` returns False if the
end-to-end token reduction is **< 2× at matched success** — the falsifiable
kill-criterion that decides whether we build Product 1.

**Status:** scaffold — the manifest, metrics, and gate logic are real and tested.
The actual SWE-bench-style task runners + baselines (OpenHands+Ollama, opencode,
vanilla SGLang) plug in here.
