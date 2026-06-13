# The agent loop

`crucible-core` is the orchestrator. Its `run_task` drives a model to solve a task with
tools — each step is **two-phase decoding**, and tool effects **settle transactionally**.

```python
from crucible_core import run_task, ToolRegistry

result = run_task(engine, registry, "What is 37 * 19 + 4?", max_steps=6)
print(result.final)        # the answer
print(result.tool_calls)   # how many tools were actually run
```

## One step = THINK → EMIT → (settle)

```
for each step (up to max_steps):
    THINK   engine.chat(..., temperature=0.3)         # free reasoning, kept brief
    EMIT    engine.chat(..., grammar=action_gbnf,     # a tool call OR a final answer,
                          temperature=0.0)            #   structurally valid, deterministic
    if action is {"final": ...}:  return the answer
    else:   observation = settle(tool call) ; feed it back into the next step
```

- **THINK** is unconstrained and short (a small `think_max_tokens` budget) — the model
  decides what to do next.
- **EMIT** is constrained to `action_gbnf(tools, allow_final=True)` and decoded at
  temperature 0, so it always produces either a valid tool call or a final answer.
- The result accumulates into a `TaskResult` (`steps`, `final`, `completion_tokens`,
  `tool_calls`, `malformed`). `result.solved` is `True` once a final answer is reached.

## Settlement is transactional (Atomix)

A tool call doesn't just run — it settles through a `crucible-atomix` `Transaction`:

```python
txn = Transaction(speculative=True)
txn.add(Effect(name=f"call {name}", reversibility=ReversibilityClass.IDEMPOTENT, apply=run_tool))
try:
    txn.settle()
except TransactionAborted as exc:
    observation = f"ERROR: {exc}"     # fed back to the model to recover from
```

Effects carry a **reversibility class**, so the settlement layer knows what can be rolled
back. A failing tool aborts cleanly and the error becomes the next observation — the
**failure-recovery path** — instead of crashing the run.

## The anti-repeat guard

Small models can loop, re-issuing the same tool call. The loop caches each action's result
by signature; a duplicate action is **not** re-run — the cached observation is returned and
the next emission is forced to finalise. This keeps episodes bounded and cheap.

## Duck-typed engine

`run_task` takes any `ChatEngine` (anything with the `chat(...)` signature), so it runs
against the real `LlamaCppEngine` **or** a scripted fake in tests — the control flow is
fully testable with no GPU. See `tools/agent_demo.py` for a real-model run, and
`crucible-core/tests/` for the scripted ones.
