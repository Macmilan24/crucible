# Install

Crucible runs locally and uses [`llama.cpp`](https://github.com/ggerganov/llama.cpp)
(Metal-accelerated on Apple Silicon) as its engine.

## Prerequisites

- **macOS (Apple Silicon)** or **Linux**. Apple Silicon gets Metal GPU acceleration out of the box.
- **Python 3.11+**.
- A **C/C++ toolchain** (needed to build `llama-cpp-python`):
    - macOS: `xcode-select --install`
    - Debian/Ubuntu: `sudo apt install build-essential`
- **~2 GB** of free disk for the default model.

---

## Option A — one-liner (recommended)

Installs the `crucible` command into an isolated [uv](https://docs.astral.sh/uv/)-managed
environment and compiles the local engine:

```sh
curl -LsSf https://raw.githubusercontent.com/Macmilan24/crucible/main/scripts/install.sh | sh
```

Then:

```sh
crucible download-model     # ~1.9 GB, resumable
crucible serve              # http://127.0.0.1:8000/v1
```

!!! tip
    Skip the engine compile (no inference, just the CLI/server scaffolding) with
    `CRUCIBLE_WITH_ENGINE=0 sh`. Add it later with
    `uv tool install --with llama-cpp-python crucible-server`.

---

## Option B — from source (for development)

Best if you want to read, modify, or contribute to the code. Everything runs through
`uv`, so the environment is always the locked workspace — no "works on my machine" drift.

```sh
git clone https://github.com/Macmilan24/crucible
cd crucible/code
uv sync --all-packages --extra llama     # .venv + all packages + dev tools + engine
uv run crucible download-model
uv run crucible serve
```

Verify the toolchain with the local gate:

```sh
make check        # lint + type-check + import-boundaries + tests
```

---

## Option C — manual / offline (release wheelhouse)

Every [release](https://github.com/Macmilan24/crucible/releases) ships a
`crucible-wheelhouse-<version>.tar.gz` containing prebuilt wheels for the whole runtime.
Download and extract it, then install with **uv**:

```sh
tar -xzf crucible-wheelhouse-v0.1.0.tar.gz -C wheelhouse
uv tool install --find-links ./wheelhouse --with llama-cpp-python crucible-server
```

…or with plain **pip** into a virtualenv:

```sh
python -m venv .venv && source .venv/bin/activate
pip install --find-links ./wheelhouse 'crucible-server' 'crucible-engine[llama]'
crucible serve
```

---

## Verify your install

```sh
crucible doctor
```

```text
Crucible 0.1.0 — doctor
  python     : 3.12.7 (arm64)
  platform   : Darwin 25.5.0
  llama-cpp  : 0.3.26
  model      : found models/Qwen2.5-3B-Instruct-Q4_K_M.gguf (1840 MB)
```

If `llama-cpp` shows `NOT INSTALLED`, see [Troubleshooting](troubleshooting.md).
