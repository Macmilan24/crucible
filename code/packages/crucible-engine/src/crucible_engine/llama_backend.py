"""A real, local inference backend for Apple Silicon / Metal via llama-cpp-python.

This is the Mac engine (ADR-0003 keeps engine access isolated, so SGLang can take
over on CUDA later behind the same package). It gives us the two things the wedge
needs below the wall: real token accounting and grammar-constrained emission.

`llama_cpp` is an *optional* dependency: it is imported lazily inside the
constructor, so `import crucible_engine` works with or without it installed.
Install it with:  uv pip install "llama-cpp-python>=0.3.2"

The underlying ``llama_cpp.Llama`` handle is held as ``Any`` on purpose: it is a
thin wrapper over a large, dynamic C++ binding, so we keep the *public* surface of
this class precisely typed (``Generation`` in, out) and treat the binding itself as
untyped at the boundary.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class Generation:
    """The result of one generation, with *real* token counts."""

    text: str
    prompt_tokens: int
    completion_tokens: int


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
            from llama_cpp import Llama
        except ImportError as exc:  # pragma: no cover - depends on optional install
            raise ImportError(
                'llama-cpp-python is not installed. Run: uv pip install "llama-cpp-python>=0.3.2"'
            ) from exc

        self._llm: Any = Llama(
            model_path=model_path,
            n_ctx=n_ctx,
            n_gpu_layers=n_gpu_layers,
            seed=seed,
            verbose=verbose,
        )

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
        is constrained to it — structural validity by construction."""
        compiled: Any = None
        if grammar is not None:
            from llama_cpp import LlamaGrammar

            compiled = LlamaGrammar.from_string(grammar, verbose=False)

        out: Any = self._llm.create_chat_completion(
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            grammar=compiled,
            seed=seed,
        )
        choice = out["choices"][0]["message"]["content"]
        usage = out["usage"]
        return Generation(
            text=str(choice or ""),
            prompt_tokens=int(usage["prompt_tokens"]),
            completion_tokens=int(usage["completion_tokens"]),
        )
