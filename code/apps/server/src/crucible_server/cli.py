"""`crucible-server` — start the OpenAI-compatible local runtime."""

from __future__ import annotations

import argparse


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Crucible OpenAI-compatible local server")
    parser.add_argument("--model", required=True, help="path to a GGUF model")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--model-name", default="crucible-local")
    args = parser.parse_args(argv)

    import uvicorn

    from crucible_engine import LlamaCppEngine

    from .app import create_app

    engine = LlamaCppEngine(args.model, seed=0)
    app = create_app(engine, model_name=args.model_name)
    print(f"Crucible server on http://{args.host}:{args.port}  (model: {args.model_name})")
    print("Point an OpenAI-compatible client at this base URL. Tool calls are grammar-guaranteed.")
    uvicorn.run(app, host=args.host, port=args.port)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
