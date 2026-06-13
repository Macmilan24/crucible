#!/usr/bin/env sh
# Crucible Core installer.
#
#   curl -LsSf https://raw.githubusercontent.com/Macmilan24/crucible/main/scripts/install.sh | sh
#
# Installs the `crucible` command from the latest GitHub Release's wheelhouse into
# an isolated uv-managed tool environment, and compiles llama-cpp-python (the local
# engine, Metal-accelerated on Apple Silicon). Override the source repo with
# CRUCIBLE_REPO=owner/name.
set -eu

REPO="${CRUCIBLE_REPO:-Macmilan24/crucible}"
WITH_ENGINE="${CRUCIBLE_WITH_ENGINE:-1}"   # set to 0 to skip llama-cpp-python (no inference)

say() { printf '\033[36m==>\033[0m %s\n' "$1"; }
die() { printf '\033[31merror:\033[0m %s\n' "$1" >&2; exit 1; }

# 1. Ensure uv is available (it manages the isolated environment + Python).
if ! command -v uv >/dev/null 2>&1; then
  say "Installing uv (https://astral.sh/uv) ..."
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="$HOME/.local/bin:$PATH"
fi
command -v uv >/dev/null 2>&1 || die "uv is not on PATH; open a new shell and re-run."

# 2. Find the wheelhouse asset on the latest release.
say "Looking up the latest Crucible release in $REPO ..."
api="https://api.github.com/repos/$REPO/releases/latest"
asset_url="$(curl -fsSL "$api" \
  | grep -oE '"browser_download_url"[[:space:]]*:[[:space:]]*"[^"]*crucible-wheelhouse[^"]*"' \
  | head -1 | sed -E 's/.*"(https[^"]*)".*/\1/')"
[ -n "${asset_url:-}" ] || die "no crucible-wheelhouse asset in the latest release of $REPO."

# 3. Download + unpack it.
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
say "Downloading $(basename "$asset_url") ..."
curl -fL# "$asset_url" -o "$tmp/wheelhouse.tar.gz"
tar -xzf "$tmp/wheelhouse.tar.gz" -C "$tmp"
wheels="$(dirname "$(find "$tmp" -name 'crucible_server-*.whl' | head -1)")"
[ -n "${wheels:-}" ] || die "wheelhouse did not contain crucible_server wheel."

# 4. Install the `crucible` command in an isolated tool environment.
if [ "$WITH_ENGINE" = "1" ]; then
  say "Installing crucible + local engine (compiling llama-cpp-python; needs a C/C++ toolchain) ..."
  uv tool install --find-links "$wheels" --with llama-cpp-python crucible-server
else
  say "Installing crucible (without the local engine; pass CRUCIBLE_WITH_ENGINE=1 to add it) ..."
  uv tool install --find-links "$wheels" crucible-server
fi

cat <<'NEXT'

✅ Crucible installed.

Next steps:
  crucible download-model      # fetch the default model (~1.9 GB, resumable)
  crucible serve               # OpenAI-compatible server on http://127.0.0.1:8000/v1
  crucible doctor              # verify your environment

Point opencode / Continue / any OpenAI client at  http://127.0.0.1:8000/v1
Docs: https://macmilan24.github.io/crucible/
NEXT
