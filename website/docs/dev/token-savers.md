# The three token-savers

Product 1 is three mechanisms that each cut tokens or guarantee structure — all real, all
measured on Apple M-series with Qwen2.5-3B-Instruct Q4_K_M. The numbers below are from the
bundled [benchmark harness](benchmarks.md) (`crucible-mini` suite, seeds 0/1/2).

---

## 1. Grammar-scoped emission → 0% malformed

**Problem.** Free-form models emit malformed tool calls — wrong name, missing arguments,
unparseable JSON. Across a multi-step episode these compound: one bad call breaks the run.

**Mechanism.** Crucible decodes in two phases. Cognition (THINK) is unconstrained. Emission
(EMIT) is masked to a GBNF grammar that admits *only* a valid call to a declared tool (right
name, exactly the required arguments, valid JSON) or a final answer.

```python
from crucible_grammar import ToolSchema, action_gbnf

grammar = action_gbnf([ToolSchema("create_event", ("title", "date", "time", "location"))])
# the engine samples under this grammar -> the output is structurally valid, always
```

**Measured.**

| | Unconstrained | Crucible (grammar) |
|---|---|---|
| Malformed tool-call rate | **100%** | **0%** |
| Clean 20-step episode | **0%** | **100%** |

A malformed call isn't rare — it's *impossible*. → [How the grammar works](grammar.md)

---

## 2. Chain-of-Draft reasoning → 4.28× fewer tokens

**Problem.** Full chain-of-thought is verbose. On easy steps, most of those tokens are
wasted — and you pay for every one.

**Mechanism.** A reasoning **dial** classifies each step and picks a mode: a terse *draft*
on easy steps, full reasoning on hard ones. Same answers, far fewer tokens.

```python
from crucible_tokeneconomy import StepSignal, choose_mode
mode = choose_mode(StepSignal(...))   # -> DRAFT (cheap) or FULL (when it matters)
```

**Measured** (matched 100% task success):

| Reasoning | Mean completion tokens |
|---|---|
| Full chain-of-thought | 152.5 |
| Chain-of-Draft | 35.7 |
| **Reduction** | **4.28×** (95% CI 3.4–5.5×) |

!!! info "Chain-of-Draft is prior work, used honestly"
    Chain-of-Draft is a published technique, not a Crucible invention. Crucible's
    contribution is wiring it to the control surface as a per-step *dial* and **measuring**
    the saving on a real local model — and gating the result so a token win that costs
    accuracy doesn't count.

---

## 3. KV-cache reuse → 4.94× less prefill

**Problem.** Multi-turn and multi-agent work re-sends a big shared context (a codebase, a
spec) every turn. Re-encoding it each time is the dominant prefill cost.

**Mechanism.** The shared prefix is encoded once into the KV-cache and **reused** across
turns instead of re-read. The metric is `prompt_eval_tokens` — prompt tokens the engine
*actually processed* — exposed on every [`Generation`](engine-contract.md).

**Measured** (5 turns over a 4,050-token shared context):

| | Prefill tokens processed |
|---|---|
| No reuse (re-encode each turn) | 20,263 |
| Crucible (reuse prefix) | 4,099 |
| **Reduction** | **4.94×** |

Output is **byte-identical** with and without reuse — a property test in the suite asserts
`cold.text == warm.text` while `warm.prompt_eval_tokens < cold.prompt_eval_tokens`.

!!! note "Scope today"
    On the Mac engine this is same-model, shared-prefix reuse across turns (`llama.cpp`
    auto-reuses prefix KV). Full cross-*agent* KV transfer between different models is
    deferred to the SGLang engine (ADR-0010).

---

## Why it compounds

Structure (saver 1) keeps episodes alive; the draft dial (saver 2) shrinks each step; cache
reuse (saver 3) shrinks the prompt side. Together they make a 3B model a viable agent where
an unconstrained one would stall on malformed calls or drown in tokens. → [Benchmarks](benchmarks.md)
