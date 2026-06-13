# Grammar & two-phase decoding

The core idea: **constrain emission, never cognition.** Crucible decodes every step in two
phases.

| Phase | Constraint | Why |
|-------|------------|-----|
| **THINK** | none (`mask = None`) | Reasoning must stay free — masking cognition makes models dumber. |
| **EMIT** | a grammar mask | The action must be structurally valid — masking emission makes it correct-by-construction. |

This is the `Substrate` facade in `crucible-core`:

```python
def think_token(self, node):                 # unconstrained — free cognition
    return self._engine.sample(node, mask=None)

def emit_token(self, node, schema):           # masked — valid by construction
    mask = mask_for_phase(Phase.EMIT, schema, self._vocab_size)
    return self._engine.sample(node, mask=mask)
```

## GBNF: the emission grammar

For the real `llama.cpp` engine, the EMIT phase uses a **GBNF** grammar — the format
`llama.cpp` consumes to constrain decoding. `crucible-grammar` builds it from a tool
signature.

```python
from crucible_grammar import ToolSchema, action_gbnf, tool_call_gbnf

schema = ToolSchema("create_event", ("title", "date", "time", "location"))

# a grammar admitting exactly one valid call to `schema`
print(tool_call_gbnf(schema))

# an "action" grammar: a valid call to ANY of these tools, OR a final answer
grammar = action_gbnf([schema], allow_final=True)
```

The generated grammar encodes a JSON object with the exact tool name and exactly the
declared keys. The model is **structurally incapable** of emitting:

- a tool that doesn't exist,
- a call missing a required argument, or one with an extra one,
- unparseable JSON.

The final-answer branch (`{"final": "..."}`) lets the model legitimately end the episode —
and that choice, too, is structurally valid.

## Validation

`is_valid_tool_call` checks a string against a schema (parses, right name, exactly the
declared arguments) — used in tests and as a belt-and-braces check:

```python
from crucible_grammar import is_valid_tool_call
is_valid_tool_call('{"tool":"create_event","arguments":{...}}', schema)  # -> True / False
```

## Determinism matters

A grammar with optional whitespace gives a high-temperature sampler room to *wander* —
emitting whitespace forever instead of committing to `{`. So Crucible decodes
grammar-constrained emission at **temperature 0**. The agent loop and the server both do
this; it's why tool calls are valid *and* reproducible. (This was a real bug found during
end-to-end testing and fixed in v0.1.0 — see the server's regression tests.)

## Structure ≠ truth

Grammar guarantees the **shape** of the call, not the **correctness** of its values. Whether
`date` is the *right* date is a different problem — the job of a **verifier** (Product 2, on
the [roadmap](roadmap.md)). Grammar solves structure; the verifier solves truth.

## Where it lives

`crucible-grammar` also carries the phase machinery used by the substrate:

- `EmissionSchema` / `mask_for_phase(phase, schema, vocab)` — the token-mask abstraction.
- `Phase` (`THINK` / `EMIT` / `HALT`) and `TrajectoryGrammar` — the legal phase transitions
  of an episode (`TrajectoryGrammar.accepts(phases)`).
