# Models

Crucible runs any **GGUF** model that `llama.cpp` supports. The default is a small,
fast, capable instruct model that the benchmarks were measured on.

## The default

| | |
|---|---|
| **Model** | Qwen2.5-3B-Instruct |
| **Quant** | Q4_K_M (~1.9 GB) |
| **File** | `Qwen2.5-3B-Instruct-Q4_K_M.gguf` |
| **Source** | [bartowski/Qwen2.5-3B-Instruct-GGUF](https://huggingface.co/bartowski/Qwen2.5-3B-Instruct-GGUF) |

```sh
crucible download-model        # -> ./models/Qwen2.5-3B-Instruct-Q4_K_M.gguf
```

Files land in `./models/` relative to where you run the command. `crucible serve` looks
there by default; override with `--model`.

## Using a different model

Any GGUF works — point `download-model` at a URL, or pass an existing file to `serve`:

```sh
# download a specific GGUF
crucible download-model \
  --url https://huggingface.co/bartowski/Qwen2.5-7B-Instruct-GGUF/resolve/main/Qwen2.5-7B-Instruct-Q4_K_M.gguf \
  --name Qwen2.5-7B-Instruct-Q4_K_M.gguf

# serve any local GGUF
crucible serve --model /path/to/your-model.gguf
```

## Choosing a size / quant

- **3B (default)** — fastest, lightest; great for tool-calling and structured tasks. This
  is the sweet spot for the grammar-scoped emission Crucible specialises in.
- **7–9B** — stronger reasoning; still comfortable on 16 GB+ Apple Silicon.
- **Quant** — `Q4_K_M` is the usual quality/size balance. Larger quants (`Q5_K_M`, `Q6_K`)
  are more faithful but bigger and slower.

!!! tip "Why small models are the point"
    Crucible's thesis is that the gap for local agents is **architectural, not
    parameters**. Grammar-scoped emission, Chain-of-Draft, and KV-cache reuse make a small
    model behave reliably — see [the three token-savers](../dev/token-savers.md).

## Where the model comes from

`download-model` is a plain, resumable HTTPS download (stdlib only — no extra
dependencies, no Hugging Face account needed for public files). The default URL is pinned
to the exact build the benchmarks cite, so your results match the published numbers.
