# PRD 0a — The Benchmark + Post

> Phase 0's job: prove the thesis publicly so a developer grasps it in one screenshot and a CFO grasps it in one number. **Not monetized** — currency is attention and credibility.

## Pain / why now

A single agentic task burns 15,000–80,000 tokens vs 500–2,000 for chat; enterprises exhaust AI budgets in months; the fastest-growing software of 2026 is private, self-hosted AI. Developers trust a repo they can run, not a claim.

## What it is

A rigorous, **reproducible** benchmark with a single headline:

> **"We cut agent token cost by 5–10× with zero malformed tool calls — running locally."**

On real agent workloads (SWE-bench-style tasks), three curves comparing a **stock local agent** vs. **the same model under the Crucible substrate**:

1. **Tokens** (the headline saving)
2. **Malformed-call rate** (→ 0 under Crucible, by construction)
3. **Task success** (must be *matched* — savings at equal success, not savings by giving up)

## Users

- **Developers** (the screenshot): "0 malformed calls, 8× fewer tokens, on my machine."
- **Decision-makers** (the number): the projected cost reduction.
- **Skeptics** (the moat): people who will *reproduce* it — the benchmark is built for them.

## Scope

- A benchmark harness (`bench/crucible-bench`) that runs both arms under identical conditions.
- Stock baselines: API-bounded local agents (OpenHands+Ollama, opencode), vanilla SGLang function-calling.
- The Crucible arm: grammar-scoped emission + Chain-of-Draft + KV-cache comms (the P1/0b primitives).
- **Contamination-resistant suites** for public numbers: SWE-bench Pro / SWE-rebench (SWE-bench Verified is now contaminated).
- Full reproducibility: pinned env lockfile, fixed seeds, model hashes, hardware manifest, raw per-run logs — **all released.**
- The launch post (the narrative around the curves).

## Out of scope

Self-improvement, verifier, memory, federation. Phase 0 proves the *substrate/token* win only.

## Aha demo

A side-by-side token counter dropping by ~8× while malformed calls sit at 0 and task success matches — one screenshot, reproducible by anyone who clones the repo.

## Acceptance criteria

- [ ] One command reproduces every headline number from the manifest.
- [ ] Three curves (tokens, malformed-rate, success) on ≥2 contamination-resistant suites, ≥3 seeds, paired bootstrap CIs.
- [ ] Malformed-call rate is **0** in the Crucible arm.
- [ ] Token reduction is reported **at matched success** (no success regression hidden by token savings).
- [ ] A third party can reproduce within the stated tolerance using only the repo.

## Success metric

Stars + weekly active installs; **third-party reproductions**; waitlist size (via 0c).

## ⛔ Kill-criterion (the master gate)

**If independent reproductions show < 2× end-to-end token reduction at matched success — stop and re-scope before building Product 1.** Everything downstream depends on this number being real.

## Dependencies

The P1/0b primitives (grammar-scoped emission, Chain-of-Draft, KV-cache comms) must exist in runnable form. In practice 0a, 0b, and the relevant slice of P1 are built together.
