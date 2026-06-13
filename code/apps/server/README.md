# crucible-server 🟢 — the packaging / drop-in runtime

An **OpenAI-compatible** local server backed by a Crucible engine. Point any
OpenAI-compatible client at it — **no client code changes** — and get:

- **Grammar-guaranteed tool calls:** when a request includes `tools`, the emission is
  constrained to the action grammar, so the returned `tool_calls` are structurally
  valid by construction (zero malformed calls).
- Plain chat passthrough otherwise.

## Run it

```bash
cd code
uv run crucible-server --model models/Qwen2.5-3B-Instruct-Q4_K_M.gguf --port 8000
```

## Point a client at it

Any OpenAI client — set the base URL to `http://127.0.0.1:8000/v1` and any API key:

```bash
curl http://127.0.0.1:8000/v1/chat/completions -H 'content-type: application/json' -d '{
  "model": "crucible-local",
  "messages": [{"role":"user","content":"Schedule Q3 Review on 2026-07-01 at 14:00 in Room B"}],
  "tools": [{"type":"function","function":{"name":"create_event",
    "parameters":{"type":"object","properties":{"title":{},"date":{},"time":{},"location":{}},
    "required":["title","date","time","location"]}}}]
}'
```

### opencode / Continue / Cursor

These speak the OpenAI API. Configure a custom/OpenAI-compatible provider with
base URL `http://127.0.0.1:8000/v1`, model `crucible-local`, any dummy key. Their
tool calls then route through Crucible and come back grammar-valid.

**Status:** real, tested (FastAPI TestClient + a live smoke test against the model).
Non-streaming for now; streaming + full tool-result round-trips are the next layer.
