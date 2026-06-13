# Benchmarks & methodology

Every headline number is produced by the bundled harness (`crucible-bench`) on a real local
model. No estimates, no illustrative figures — if it's quoted, it was measured.

## Run manifest

The numbers on this site come from this configuration:

| Field | Value |
|-------|-------|
| Suite | `crucible-mini` (tool-use + GSM-style) |
| Model | Qwen2.5-3B-Instruct Q4_K_M |
| Hardware | Apple M-series, Metal |
| Seeds | 0, 1, 2 |
| Commit | `234859e` |

Each run records a manifest (model hash, env-lock hash, hardware, seeds, commit) alongside
the results, so a run is traceable and reproducible.

## What it measures

### 1. Malformed-rate (structure)
Unconstrained decoding vs grammar-scoped emission on the same tool-call prompts.

| | Unconstrained | Grammar |
|---|---|---|
| Malformed rate (12 trials) | **1.00** | **0.00** |

### 2. Compounding (reliability over a long episode)
Probability of a *clean* 20-step episode (every step well-formed).

| | Unconstrained | Grammar |
|---|---|---|
| Clean 20-step episode | **0.00** | **1.00** |

A 100%-per-step structure guarantee is the difference between an agent that finishes and one
that derails by step 3.

### 3. Token economy (Chain-of-Draft)
Mean completion tokens at **matched success** (a token win that costs accuracy is rejected
by the gate).

| Mode | Mean tokens | Success |
|---|---|---|
| Full chain-of-thought | 152.5 | 100% |
| Chain-of-Draft | 35.7 | 100% |
| **Reduction** | **4.28×** | 95% CI 3.4–5.5× |

### 4. KV-cache reuse (prefill)
Prefill tokens actually processed over 5 turns on a 4,050-token shared context.

| | Prefill tokens |
|---|---|
| No reuse | 20,263 |
| Reuse | 4,099 |
| **Reduction** | **4.94×** |

…with byte-identical output (a property test asserts the reuse path doesn't change results).

## The gate

The token-economy result isn't just printed — it's **gated**. The harness asserts the
reduction holds *at matched success*; a run that trades accuracy for tokens fails. This is
the same discipline as the kill-criteria in the evaluation plan: a number only counts if it
survives its gate.

## Reproduce it

From a source checkout, with a model in `models/`:

```sh
uv run python tools/run_benchmark.py
```

It prints all four measurements and writes a timestamped JSON (with the full manifest) into
`bench/crucible-bench/runs/`. The unit-level harness logic is covered by `make check`; the
model-backed runs are marked `slow` and excluded from the fast gate.

!!! warning "Your numbers will vary"
    Exact figures depend on model, quant, seeds, and hardware. The *direction and
    magnitude* are the claim: grammar removes malformed calls entirely, Chain-of-Draft cuts
    completion tokens several-fold at matched success, and prefix reuse cuts prefill
    several-fold. Re-run the harness on your machine to get your own manifest.
