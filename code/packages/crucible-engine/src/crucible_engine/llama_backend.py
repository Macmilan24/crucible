"""A real, local inference backend for Apple Silicon / Metal via llama-cpp-python.

This is the Mac engine (ADR-0003 keeps engine access isolated, so SGLang can take
over on CUDA later behind the same package). It gives us the things the wedge needs
below the wall: real token accounting, grammar-constrained emission, and KV-cache
prefix reuse (ADR-0010).

`llama_cpp` is an *optional* dependency, imported lazily, so `import crucible_engine`
works with or without it installed. Install:  uv pip install "llama-cpp-python>=0.3.2"

The ``llama_cpp.Llama`` handle is held as ``Any`` on purpose: it wraps a large,
dynamic C++ binding, so we keep this class's PUBLIC surface precisely typed
(``Generation`` in/out) and treat the binding as untyped at the boundary.
"""

from __future__ import annotations

from typing import Any

from .contract import Generation


class LlamaCppEngine:
    """A thin wrapper over llama_cpp.Llama for local, Metal-accelerated inference."""

    def __init__(
        self,
        model_path: str,
        *,
        n_ctx: int = 4096,
        n_gpu_layers: int = -1,  # -1 = offload all layers to Metal
        seed: int = 0,
        verbose: bool = False,
    ) -> None:
        try:
            import llama_cpp
            from llama_cpp import Llama
        except ImportError as exc:  # pragma: no cover - depends on optional install
            raise ImportError(
                'llama-cpp-python is not installed. Run: uv pip install "llama-cpp-python>=0.3.2"'
            ) from exc

        self._llama_cpp = llama_cpp
        self._llm: Any = Llama(
            model_path=model_path,
            n_ctx=n_ctx,
            n_gpu_layers=n_gpu_layers,
            seed=seed,
            verbose=verbose,
        )

    def enable_prefix_cache(self, capacity_mb: int = 512) -> None:
        """Enable a RAM cache so shared prefixes are reused even across switches."""
        from llama_cpp import LlamaRAMCache

        self._llm.set_cache(LlamaRAMCache(capacity_bytes=capacity_mb * 1024 * 1024))

    def reset_context(self) -> None:
        """Clear the KV-cache so the next call re-prefills fully (the no-reuse baseline)."""
        self._llm.reset()

    def chat(
        self,
        messages: list[dict[str, str]],
        *,
        grammar: str | None = None,
        max_tokens: int = 512,
        temperature: float = 0.7,
        seed: int | None = None,
    ) -> Generation:
        """Run a chat completion. If ``grammar`` (a GBNF string) is given, the output
        is constrained to it — structural validity by construction. ``prompt_eval_tokens``
        reports how many prompt tokens were actually processed (less than the logical
        prompt when a prefix is reused from cache)."""
        compiled: Any = None
        if grammar is not None:
            from llama_cpp import LlamaGrammar

            compiled = LlamaGrammar.from_string(grammar, verbose=False)

        ctx = self._llm._ctx.ctx
        self._llama_cpp.llama_perf_context_reset(ctx)
        out: Any = self._llm.create_chat_completion(
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            grammar=compiled,
            seed=seed,
        )
        perf: Any = self._llama_cpp.llama_perf_context(ctx)
        choice = out["choices"][0]["message"]["content"]
        usage = out["usage"]
        return Generation(
            text=str(choice or ""),
            prompt_tokens=int(usage["prompt_tokens"]),
            completion_tokens=int(usage["completion_tokens"]),
            prompt_eval_tokens=int(perf.n_p_eval),
        )
