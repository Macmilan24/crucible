# Troubleshooting

Start with:

```sh
crucible doctor
```

It reports your Python, platform, whether the engine is installed, and whether a model is
present. Most issues show up here.

---

### `llama-cpp : NOT INSTALLED`

The local engine wheel isn't in your environment.

- **One-liner / wheelhouse install:**
  `uv tool install --with llama-cpp-python crucible-server`
- **From source:** `uv sync --all-packages --extra llama`
- **pip:** `pip install 'crucible-engine[llama]'`

If the build itself fails, you're missing a C/C++ toolchain:

- macOS: `xcode-select --install`
- Debian/Ubuntu: `sudo apt install build-essential cmake`

---

### `model not found: models/...`

You haven't downloaded a model, or you're running from a different directory than where
`models/` lives.

```sh
crucible download-model            # fetches into ./models
crucible serve --model /abs/path/to/model.gguf   # or point at an explicit file
```

---

### Model download stalls or fails midway

The download is resumable — just run it again:

```sh
crucible download-model
```

It continues from the partial `.part` file. To start over, add `--force`.

---

### Server starts but the first request is slow

The model loads into memory on first use (a few seconds to tens of seconds depending on
size and disk). Subsequent requests are fast. The `/health` endpoint only returns once the
server is up.

---

### Tool calls come back as plain text / weird whitespace

Make sure you're sending real `tools` in the request (the grammar only activates when
`tools` are present) and that you're on **v0.1.0 or later** — earlier builds could let a
high `temperature` wander in the grammar. Crucible now decodes tool calls at temperature 0
by design. Confirm with `crucible version`.

---

### Port already in use

```sh
crucible serve --port 8001
```

---

### A client can't reach `localhost`

Some hosted clients proxy through their own backend and can't see your machine. Use
opencode or Continue (which connect directly), or expose Crucible on your LAN with
`crucible serve --host 0.0.0.0` and use your machine's IP (trusted networks only — there's
no authentication).

---

### Still stuck?

Open an issue with your `crucible doctor` output:
<https://github.com/Macmilan24/crucible/issues>
