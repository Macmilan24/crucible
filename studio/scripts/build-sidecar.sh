#!/usr/bin/env bash
# Build the bundled `crucible` runtime as a Tauri sidecar binary — one per OS.
#
# This is what makes Studio a true one-download app: the frozen binary contains
# Python + the Crucible runtime + llama.cpp, so a user needs nothing else.
#
# Requirements: Python 3.11+, a C toolchain (for llama.cpp), network access to
# PyPI (for llama-cpp-python), and Rust (for the target-triple name).
# Output: studio/src-tauri/binaries/crucible-server-<target-triple>[.exe]
#
# NOTE: freezing llama-cpp-python (with its native backend / Metal shaders) is the
# finicky part and may need per-OS tuning — validate the produced binary by running
#   ./crucible-server-<triple> serve --model <some.gguf>
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
STUDIO="$(cd "$HERE/.." && pwd)"
ROOT="$(cd "$STUDIO/.." && pwd)"
CODE="$ROOT/code"
OUT="$STUDIO/src-tauri/binaries"
BUILD="$STUDIO/.sidecar-build"
mkdir -p "$OUT"

TRIPLE="$(rustc -Vv | sed -n 's/^host: //p')"
EXE=""
case "$TRIPLE" in *windows*) EXE=".exe" ;; esac
echo "target triple: $TRIPLE"

# 1. Build all Crucible wheels into a local wheelhouse (no PyPI needed for these).
rm -rf "$BUILD"
mkdir -p "$BUILD/wheelhouse"
(cd "$CODE" && uv build --all-packages --out-dir "$BUILD/wheelhouse")

# 2. Isolated venv: the server + the llama.cpp engine from the wheelhouse, + PyInstaller.
python3 -m venv "$BUILD/venv"
# shellcheck disable=SC1091
source "$BUILD/venv/bin/activate"
python -m pip install --upgrade pip
python -m pip install --find-links "$BUILD/wheelhouse" \
  "crucible-server" "crucible-engine[llama]" pyinstaller

# 3. Freeze the CLI entry into one binary (bundles llama_cpp's native library).
pyinstaller --noconfirm --onefile --clean --name crucible-server \
  --collect-all llama_cpp \
  --collect-all crucible_server \
  --collect-submodules uvicorn \
  --hidden-import uvicorn.lifespan.on \
  --hidden-import uvicorn.protocols.http.auto \
  --hidden-import uvicorn.protocols.websockets.auto \
  --distpath "$OUT" --workpath "$BUILD/work" --specpath "$BUILD" \
  "$HERE/sidecar_entry.py"

# 4. Tauri resolves sidecars by the target-triple suffix.
mv "$OUT/crucible-server$EXE" "$OUT/crucible-server-$TRIPLE$EXE"
echo "sidecar -> $OUT/crucible-server-$TRIPLE$EXE"
