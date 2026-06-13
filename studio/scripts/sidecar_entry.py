"""PyInstaller entry point for the bundled `crucible` runtime sidecar.

Freezing this module produces a single self-contained executable that behaves
exactly like the `crucible` CLI (`serve`, `download-model`, `doctor`, …), so a
Studio user needs no Python and no separate Crucible Core install. Studio spawns
it as a Tauri sidecar. See scripts/build-sidecar.sh.
"""

import sys

from crucible_server.cli import main

if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
