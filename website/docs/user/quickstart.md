# Quickstart

This walks you from a fresh install to a real, grammar-valid tool call in a couple of
minutes. It assumes you've [installed](install.md) Crucible.

!!! note "`crucible` vs `uv run crucible`"
    If you installed from source (Option B), prefix commands with `uv run` (e.g.
    `uv run crucible serve`). If you installed via the one-liner or a wheelhouse,
    `crucible` is on your PATH directly.

## 1. Get a model

```sh
crucible download-model
```

Downloads `Qwen2.5-3B-Instruct-Q4_K_M.gguf` (~1.9 GB) into `./models/`. The download is
resumable — re-run it if your connection drops. See [Models](models.md) to use a
different one.

## 2. Start the server

```sh
crucible serve
```

```text
Crucible server on http://127.0.0.1:8000  (model: crucible-local)
Point an OpenAI-compatible client at this base URL. Tool calls are grammar-guaranteed.
```

## 3. Make your first request

In another terminal — plain chat first:

```sh
curl -s http://127.0.0.1:8000/v1/chat/completions \
  -H 'content-type: application/json' \
  -d '{"model":"crucible-local","messages":[{"role":"user","content":"Say hello in five words."}]}'
```

Now a **tool call**. Crucible constrains the emission to your tool's schema, so the reply
is a structurally valid call — every required argument present, valid JSON, no prose:

```sh
curl -s http://127.0.0.1:8000/v1/chat/completions \
  -H 'content-type: application/json' \
  -d '{
    "model": "crucible-local",
    "messages": [{"role":"user","content":"Schedule Q3 Review on 2026-07-01 at 14:00 in Room B"}],
    "tools": [{"type":"function","function":{
      "name":"create_event",
      "parameters":{"type":"object",
        "properties":{"title":{},"date":{},"time":{},"location":{}},
        "required":["title","date","time","location"]}}}]
  }'
```

```json
{
  "choices": [{
    "finish_reason": "tool_calls",
    "message": {
      "role": "assistant",
      "content": null,
      "tool_calls": [{
        "id": "call_ceff5460",
        "type": "function",
        "function": {
          "name": "create_event",
          "arguments": "{\"title\": \"Q3 Review\", \"date\": \"2026-07-01\", \"time\": \"14:00\", \"location\": \"Room B\"}"
        }
      }]
    }
  }]
}
```

That `arguments` payload is **valid by construction** — the grammar makes a malformed
call impossible. (This exact request is part of the test suite.)

## 4. Point a real client at it

You now have an OpenAI endpoint at `http://127.0.0.1:8000/v1`. Wire it into your tools:

- **[opencode →](opencode.md)**
- **[Continue / Cursor / openai SDK →](clients.md)**

## 5. (From source) Watch a real agent

If you cloned the repo, run the multi-step agent demo — the model solves tasks by calling
a calculator and a file reader, one grammar-valid action at a time:

```sh
uv run python tools/agent_demo.py
```

See how it works under the hood in [The agent loop](../dev/agent-loop.md).
