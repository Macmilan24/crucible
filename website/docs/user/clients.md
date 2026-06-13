# Other clients

Crucible is a standard OpenAI Chat Completions endpoint at `http://127.0.0.1:8000/v1`.
Anything that speaks the OpenAI API can use it — set the **base URL** and any dummy **API
key**.

## The `openai` Python SDK

```python
from openai import OpenAI

client = OpenAI(base_url="http://127.0.0.1:8000/v1", api_key="local")

# plain chat
r = client.chat.completions.create(
    model="crucible-local",
    messages=[{"role": "user", "content": "Say hello in five words."}],
)
print(r.choices[0].message.content)

# tool call — comes back structurally valid
r = client.chat.completions.create(
    model="crucible-local",
    messages=[{"role": "user", "content": "Schedule Q3 Review on 2026-07-01 at 14:00 in Room B"}],
    tools=[{"type": "function", "function": {
        "name": "create_event",
        "parameters": {"type": "object",
            "properties": {"title": {}, "date": {}, "time": {}, "location": {}},
            "required": ["title", "date", "time", "location"]}}}],
)
print(r.choices[0].message.tool_calls[0].function.arguments)
```

## Continue (VS Code / JetBrains)

Add a model with an OpenAI-compatible provider in `~/.continue/config.json`:

```json
{
  "models": [{
    "title": "Crucible Local",
    "provider": "openai",
    "model": "crucible-local",
    "apiBase": "http://127.0.0.1:8000/v1",
    "apiKey": "local"
  }]
}
```

## Cursor

In **Settings → Models**, enable a custom OpenAI base URL of
`http://127.0.0.1:8000/v1`, add a model named `crucible-local`, and use any API key.

!!! warning "Cursor needs a reachable URL"
    Some Cursor features proxy through Cursor's backend, which can't reach your
    `localhost`. A local tunnel or LAN address may be required. opencode and Continue talk
    to the endpoint directly and are the smoothest local fit.

## Raw HTTP

```sh
curl -s http://127.0.0.1:8000/v1/chat/completions \
  -H 'content-type: application/json' \
  -d '{"model":"crucible-local","messages":[{"role":"user","content":"hi"}]}'
```

## What's supported

| Feature | Status |
|---|---|
| `POST /v1/chat/completions` | ✅ |
| `tools` → `tool_calls` (grammar-valid) | ✅ |
| `GET /v1/models`, `GET /health` | ✅ |
| `temperature`, `max_tokens` | ✅ (tool calls always decode at temp 0) |
| Streaming (`stream: true`) | ⏳ roadmap |
| Multi-turn tool **results** round-trip | ⏳ roadmap |
