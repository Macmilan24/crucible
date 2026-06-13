# FAQ

**What is Crucible, in one sentence?**
A local runtime that makes small language models behave like reliable tool-using agents —
grammar-guaranteed tool calls, far fewer tokens — served behind the OpenAI API so your
existing tools work unchanged.

**Is it really 100% local?**
Yes. The model runs on your machine via `llama.cpp`. The server binds to `127.0.0.1` by
default. There are no API keys, no telemetry, and nothing is sent anywhere. The only
network call is the one-time model download (a plain HTTPS GET you can audit).

**Do I need a GPU?**
No, but it helps. On Apple Silicon, `llama.cpp` uses the Metal GPU automatically. On Linux
it runs on CPU (or CUDA if you build `llama-cpp-python` for it).

**What does "grammar-guaranteed tool call" actually mean?**
When you pass `tools`, Crucible constrains the model's output to a grammar that only admits
a valid call to one of those tools (correct name, exactly the required arguments, valid
JSON) or a final answer. A malformed tool call is *structurally impossible* — not "rare,"
impossible. See [Grammar & two-phase decoding](../dev/grammar.md).

**Does the grammar make the model smarter / always correct?**
No. Grammar guarantees **structure**, not **truth**. The arguments are well-formed; whether
they're the *right* arguments is a separate problem (a verifier — Product 2 — is on the
[roadmap](../dev/roadmap.md)).

**Which models work?**
Any GGUF `llama.cpp` supports. Default is Qwen2.5-3B-Instruct Q4_K_M. See [Models](models.md).

**Is this OpenAI-compatible enough for my tool?**
If your tool speaks the OpenAI Chat Completions API, yes. Streaming and full tool-result
round-trips are not implemented yet — see the [support table](clients.md#whats-supported).

**Is it free?**
Yes — open source under Apache-2.0. You only pay for your own electricity.

**Where do the benchmark numbers come from?**
Real runs on Apple M-series with Qwen2.5-3B Q4_K_M, reproducible with the bundled harness.
Methodology and full results: [Benchmarks](../dev/benchmarks.md).

**How is this different from Ollama / LM Studio / a plain llama.cpp server?**
Those serve a model. Crucible adds the **agent control surfaces above the model**:
grammar-scoped emission (valid tool calls), Chain-of-Draft (fewer tokens), and KV-cache
reuse (less prefill) — measured, not promised. It's a runtime for *agents*, not just a
chat endpoint.
