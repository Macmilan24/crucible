# Connect opencode

[opencode](https://opencode.ai) is a terminal AI coding agent. Because Crucible serves the
**OpenAI Chat Completions API**, opencode can use your local model as a provider — and
every tool call opencode makes comes back grammar-valid.

## 1. Start Crucible

```sh
crucible serve          # http://127.0.0.1:8000/v1
```

Leave it running.

## 2. Add Crucible as a local provider

opencode reads a config file (`opencode.json` in your project, or
`~/.config/opencode/opencode.json` globally). Add Crucible as an OpenAI-compatible
provider pointing at the local base URL:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "crucible": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "Crucible (local)",
      "options": {
        "baseURL": "http://127.0.0.1:8000/v1",
        "apiKey": "local"
      },
      "models": {
        "crucible-local": { "name": "Crucible Local" }
      }
    }
  }
}
```

Then select the `crucible-local` model inside opencode.

!!! note
    Crucible implements the OpenAI request/response contract opencode needs (including the
    `tool_calls` shape — [verified here](quickstart.md#3-make-your-first-request)). The
    exact config keys can change between opencode versions; if anything looks different,
    check opencode's **Providers / Custom provider** docs and keep the
    `baseURL = http://127.0.0.1:8000/v1`.

## 3. Use it

Ask opencode to do something that calls a tool. The request goes to your local model;
Crucible constrains the tool emission so opencode receives a valid call — no "the model
returned malformed JSON" failures.

## Notes & limits

- **Any API key works.** Crucible doesn't authenticate; pass any non-empty string.
- **Non-streaming today.** Responses are returned whole, not token-streamed. Most clients
  handle this fine; streaming is on the [roadmap](../dev/roadmap.md).
- **Expose to other machines** with `crucible serve --host 0.0.0.0` (then use your
  machine's IP as the base URL). Only do this on trusted networks — there's no auth.
