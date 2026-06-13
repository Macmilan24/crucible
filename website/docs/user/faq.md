# FAQ

**What is Crucible, in one sentence?**
A local runtime that makes small language models behave like reliable tool-using agents —
grammar-guaranteed tool calls, far fewer tokens — served behind the OpenAI API so your
existing tools work unchanged.

**Is it really 100% local?**
Yes. The model runs on your machine via `llama.cpp`. The server binds to `127.0.0.1` by
default. There are no API keys, no telemetry, and nothing is sent anywhere. The only
network call is the one-time model download (a plain HTTPS GET you can audit).

**Why does it need a local model? Can't it just shrink my OpenAI / Claude bill?**
No — and this is the most important thing to understand about Crucible. It does **not** sit
in front of a cloud model as a proxy. It **replaces** the cloud model with a local one.
Two of the three token-savers physically *require* access to the model's internals that no
cloud API exposes: grammar-scoped emission masks the **logits** at every decode step, and
KV-cache reuse reuses the model's **attention memory** across turns. OpenAI and Anthropic
give you text-in/text-out only — you never touch the logits or the KV-cache. That boundary
is the project's whole thesis (["the wall"](../dev/architecture.md)). The deep savings only
exist *below* it, which means owning the inference — i.e. a local (or self-hosted) model.
(Chain-of-Draft, the third saver, is just a prompting style and *would* work against a cloud
API — but on its own that's a thin trick, not the product.)

**So if it's local, what do the "token savings" actually save me?**
A local model isn't billed per token, so the win is **not** a smaller API invoice — it's
**speed, compute, context, and privacy**: fewer tokens to prefill and generate means faster
replies on your hardware, less GPU/battery per request, and more room in a fixed context
window. If you *self-host at scale* (your own GPUs serving many users), the same token
savings become real infrastructure-dollar savings — more requests per GPU. If your goal is
specifically "make my cloud bill smaller," Crucible isn't that tool; if it's "own a fast,
private, reliable local agent," it is.

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
