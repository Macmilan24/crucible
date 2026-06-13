# Engine contract

`crucible-engine` defines the **orchestrator↔engine boundary** — the wall, as a typed
Python `Protocol`. Everything above depends on this contract; nothing above imports a
specific engine. That's what lets the Mac (`llama.cpp`) and the GPU (SGLang) engines be
interchangeable backends.

## `ControlSurface` — the five surfaces

```python
@runtime_checkable
class ControlSurface(Protocol):
    # (i) logits + masking
    def read_logits(self, node: CacheNodeId) -> Sequence[float]: ...
    def sample(self, node: CacheNodeId, mask: Sequence[bool] | None = None) -> int: ...
    # (ii) KV-cache tree
    def fork(self, node: CacheNodeId) -> CacheNodeId: ...
    def prune(self, node: CacheNodeId) -> None: ...
    # (iii) draft + verifier scores
    def draft(self, node: CacheNodeId, width: int) -> Sequence[DraftProposal]: ...
    def verifier_score(self, node: CacheNodeId) -> float: ...
    # (iv) reversible weight edits
    def apply_adapter(self, adapter: AdapterId) -> None: ...
    def revert_adapter(self, adapter: AdapterId) -> None: ...
    # (v) idle scheduling
    def schedule_idle(self, task: Callable[[], None]) -> None: ...
```

`sample(mask=…)` is the surface that makes [grammar-scoped emission](grammar.md) possible:
cognition samples with `mask=None`; emission samples under a grammar mask. `fork`/`prune`
are the KV-cache tree surface.

## `Generation` — honest token accounting

Every generation returns real counts:

```python
@dataclass(frozen=True, slots=True)
class Generation:
    text: str
    prompt_tokens: int
    completion_tokens: int
    prompt_eval_tokens: int = 0   # prompt tokens ACTUALLY processed
```

`prompt_eval_tokens` is the KV-cache story made measurable: it drops below `prompt_tokens`
when a shared prefix is reused from cache. The benchmark reads it straight from
`llama_perf_context` — no estimates.

## `LlamaCppEngine` — the engine that ships today

The Mac backend wraps `llama-cpp-python` (Metal). Beyond the low-level surfaces it exposes a
high-level chat method that the [agent loop](agent-loop.md) and the
[server](../user/cli.md) use:

```python
def chat(
    self,
    messages: list[dict[str, str]],
    *,
    grammar: str | None = None,     # GBNF; None = free generation
    max_tokens: int = 512,
    temperature: float = 0.7,
    seed: int | None = None,
) -> Generation: ...
```

Pass a GBNF string to constrain emission; omit it for free chat. KV-cache prefix reuse is
automatic across calls that share a prefix.

```python
from crucible_engine import LlamaCppEngine

engine = LlamaCppEngine("models/Qwen2.5-3B-Instruct-Q4_K_M.gguf", seed=0)
gen = engine.chat([{"role": "user", "content": "Say hi."}])
print(gen.text, gen.completion_tokens)
```

!!! note "Implementation isolation"
    `llama_backend.py` is the one module allowed to touch `llama_cpp` types directly; it's
    excluded from strict type-checking precisely because it lives at the untyped C boundary.
    Everything else stays clean behind `ControlSurface`.

## `MockEngine` — test without a GPU

`crucible-engine` also ships a `MockEngine` (and a `ROOT` cache node) so the whole stack —
substrate, agent loop, grammar masking — can be unit-tested deterministically with no model
and no GPU. This is why `make check` runs in well under a second.
