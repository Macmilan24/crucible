"""Fetch a local GGUF model with resume + a progress bar.

Stdlib only (urllib) so installing the runtime never drags in extra deps. The
default is the same Qwen2.5-3B-Instruct Q4_K_M build the benchmarks were measured
on; ``--url`` / ``--name`` let you point at any other GGUF.
"""

from __future__ import annotations

import sys
import urllib.request
from pathlib import Path

# Same single-file build the README/benchmarks cite (~1.93 GB), pinned by repo+path.
DEFAULT_URL = (
    "https://huggingface.co/bartowski/Qwen2.5-3B-Instruct-GGUF/"
    "resolve/main/Qwen2.5-3B-Instruct-Q4_K_M.gguf"
)
DEFAULT_NAME = "Qwen2.5-3B-Instruct-Q4_K_M.gguf"
_CHUNK = 1 << 20  # 1 MiB


def _human(num: float) -> str:
    size = float(num)
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024.0 or unit == "GB":
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} GB"


def _progress(done: int, total: int) -> None:
    if total <= 0:
        sys.stderr.write(f"\r  {_human(done)} downloaded")
        sys.stderr.flush()
        return
    frac = done / total
    bar = "█" * int(frac * 30)
    sys.stderr.write(f"\r  [{bar:<30}] {frac * 100:5.1f}%  {_human(done)} / {_human(total)}")
    sys.stderr.flush()


def download_model(
    dest_dir: str | Path,
    *,
    url: str = DEFAULT_URL,
    name: str = DEFAULT_NAME,
    force: bool = False,
) -> Path:
    """Download ``url`` into ``dest_dir/name``, resuming a partial download if present.

    Returns the path to the finished file. If the file already exists and ``force``
    is false, it is left untouched.
    """
    dest_dir = Path(dest_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / name

    if dest.exists() and not force:
        print(f"already present: {dest} ({_human(dest.stat().st_size)})")
        print("(pass --force to re-download)")
        return dest

    part = dest.with_name(dest.name + ".part")
    have = part.stat().st_size if part.exists() else 0

    req = urllib.request.Request(url)
    if have:
        req.add_header("Range", f"bytes={have}-")

    print(f"downloading {name}\n  from {url}")
    with urllib.request.urlopen(req) as resp:
        resumed = have > 0 and resp.status == 206
        start = have if resumed else 0
        length = resp.headers.get("Content-Length")
        total = (int(length) + start) if length is not None else 0
        done = start
        mode = "ab" if resumed else "wb"
        with part.open(mode) as fh:
            while True:
                buf = resp.read(_CHUNK)
                if not buf:
                    break
                fh.write(buf)
                done += len(buf)
                _progress(done, total)

    sys.stderr.write("\n")
    part.replace(dest)
    print(f"saved: {dest} ({_human(dest.stat().st_size)})")
    return dest
