# The `crucible` CLI

One command, a few subcommands. (From a source checkout, prefix with `uv run`.)

```text
crucible serve            start the OpenAI-compatible server
crucible download-model   fetch the default local model (~1.9 GB, resumable)
crucible doctor           check your environment (python / llama-cpp / model)
crucible version          print the version
```

`crucible-server` remains as a back-compat alias for `crucible serve`.

---

## `crucible serve`

Starts the OpenAI-compatible HTTP server.

```sh
crucible serve [--model PATH] [--host HOST] [--port PORT] [--model-name NAME]
```

| Flag | Default | Description |
|------|---------|-------------|
| `--model` | `models/Qwen2.5-3B-Instruct-Q4_K_M.gguf` | Path to a GGUF model. |
| `--host` | `127.0.0.1` | Bind address. Use `0.0.0.0` to expose on your LAN. |
| `--port` | `8000` | Port. |
| `--model-name` | `crucible-local` | The id reported at `/v1/models` and echoed back in responses. |

Endpoints: `GET /health`, `GET /v1/models`, `POST /v1/chat/completions`.

!!! info "Determinism for tool calls"
    When a request includes `tools`, Crucible decodes the action at **temperature 0** under
    the tool grammar, regardless of the request's `temperature`. This is what makes tool
    calls valid *and* reproducible. Plain chat honours the requested temperature.

---

## `crucible download-model`

```sh
crucible download-model [--out DIR] [--url URL] [--name FILE] [--force]
```

| Flag | Default | Description |
|------|---------|-------------|
| `--out` | `models` | Directory to save into. |
| `--url` | Qwen2.5-3B Q4_K_M on Hugging Face | Any GGUF URL. |
| `--name` | `Qwen2.5-3B-Instruct-Q4_K_M.gguf` | Filename to save as. |
| `--force` | off | Re-download even if the file already exists. |

Downloads stream to a `.part` file and resume on re-run; the final file is only renamed
into place once complete.

---

## `crucible doctor`

Prints a quick environment report — Python version + architecture, OS, whether the
`llama-cpp` engine is installed, and whether the default model is present. Start here when
something isn't working.

---

## `crucible version`

Prints the installed version (e.g. `crucible 0.1.0`).
