"""`crucible` — the Crucible Core command line.

Subcommands:
  crucible serve            start the OpenAI-compatible server (the headline artifact)
  crucible download-model   fetch the default local model (~1.9 GB, resumable)
  crucible doctor           check the environment (python / llama-cpp / model)
  crucible version          print the version

`crucible-server` stays as a back-compat alias for `crucible serve`.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import cast

from .download import DEFAULT_NAME, DEFAULT_URL, download_model

_DEFAULT_MODEL = "models/Qwen2.5-3B-Instruct-Q4_K_M.gguf"


def _run_server(model: str, host: str, port: int, model_name: str) -> int:
    import uvicorn

    from crucible_engine import LlamaCppEngine

    from .app import create_app

    engine = LlamaCppEngine(model, seed=0)
    app = create_app(engine, model_name=model_name)
    print(f"Crucible server on http://{host}:{port}  (model: {model_name})")
    print("Point an OpenAI-compatible client at this base URL. Tool calls are grammar-guaranteed.")
    uvicorn.run(app, host=host, port=port)
    return 0


def _cmd_serve(args: argparse.Namespace) -> int:
    model = cast(str, args.model)
    if not Path(model).exists():
        print(
            f"model not found: {model}\n"
            "Run `crucible download-model` first, or pass --model <path-to.gguf>.",
            file=sys.stderr,
        )
        return 2
    return _run_server(
        model, cast(str, args.host), cast(int, args.port), cast(str, args.model_name)
    )


def _cmd_download(args: argparse.Namespace) -> int:
    download_model(
        cast(str, args.out),
        url=cast(str, args.url),
        name=cast(str, args.name),
        force=cast(bool, args.force),
    )
    return 0


def _cmd_doctor(_args: argparse.Namespace) -> int:
    import platform

    from . import __version__

    print(f"Crucible {__version__} — doctor")
    print(f"  python     : {platform.python_version()} ({platform.machine()})")
    print(f"  platform   : {platform.system()} {platform.release()}")
    try:
        import llama_cpp

        print(f"  llama-cpp  : {getattr(llama_cpp, '__version__', 'installed')}")
    except ImportError:
        print("  llama-cpp  : NOT INSTALLED")
        print("    -> uv sync --extra llama   (or: pip install 'crucible-engine[llama]')")
    model = Path(_DEFAULT_MODEL)
    if model.exists():
        size = model.stat().st_size / (1 << 20)
        print(f"  model      : found {model} ({size:.0f} MB)")
    else:
        print("  model      : missing -> run `crucible download-model`")
    return 0


def _cmd_version(_args: argparse.Namespace) -> int:
    from . import __version__

    print(f"crucible {__version__}")
    return 0


def _add_serve_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--model", default=_DEFAULT_MODEL, help="path to a GGUF model")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--model-name", default="crucible-local", help="id reported at /v1/models")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="crucible",
        description="Crucible Core — a token-frugal local agent runtime with "
        "grammar-guaranteed tool calls.",
    )
    sub = parser.add_subparsers(dest="command")

    p_serve = sub.add_parser("serve", help="start the OpenAI-compatible server")
    _add_serve_args(p_serve)
    p_serve.set_defaults(func=_cmd_serve)

    p_dl = sub.add_parser("download-model", help="download the default local model (~1.9 GB)")
    p_dl.add_argument("--out", default="models", help="directory to save into (default: models/)")
    p_dl.add_argument("--url", default=DEFAULT_URL, help="GGUF URL (default: Qwen2.5-3B Q4_K_M)")
    p_dl.add_argument("--name", default=DEFAULT_NAME, help="filename to save as")
    p_dl.add_argument("--force", action="store_true", help="re-download even if present")
    p_dl.set_defaults(func=_cmd_download)

    p_doc = sub.add_parser("doctor", help="check your environment")
    p_doc.set_defaults(func=_cmd_doctor)

    p_ver = sub.add_parser("version", help="print the version")
    p_ver.set_defaults(func=_cmd_version)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    func = getattr(args, "func", None)
    if func is None:
        parser.print_help()
        return 1
    return cast(int, func(args))


def server_main(argv: list[str] | None = None) -> int:
    """Back-compat entry point: `crucible-server ...` == `crucible serve ...`."""
    parser = argparse.ArgumentParser(
        prog="crucible-server", description="Crucible OpenAI-compatible local server"
    )
    _add_serve_args(parser)
    args = parser.parse_args(argv)
    return _cmd_serve(args)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
