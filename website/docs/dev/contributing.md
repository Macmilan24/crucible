# Contributing

Crucible is open source under **Apache-2.0**. Contributions are welcome — bug reports,
docs, engines, and mechanism work alike.

## Dev setup

```sh
git clone https://github.com/Macmilan24/crucible
cd crucible/code
uv sync --all-packages --extra llama     # .venv + every package + dev tools + the engine
```

`uv` is the only entry point — every command runs inside the locked workspace, so there's
no environment drift.

## The gate

One command runs everything CI runs:

```sh
make check        # lint + format + type-check + import-boundaries + tests
```

Individually:

| Command | Tool | Checks |
|---------|------|--------|
| `make lint` | ruff | Lint (pyflakes, isort, bugbear, pyupgrade, …) |
| `make format` | ruff | Auto-format |
| `make type` | pyright | Strict typing on `engine`, `grammar`, `gate` |
| `make imports` | import-linter | The acyclic package-graph contract |
| `make test` | pytest + hypothesis | Unit + property tests (excludes `slow`) |

The fast gate runs in well under a second because the whole stack is testable on
`MockEngine` — no model, no GPU. Keep it green.

## Tests

- **Fast** tests run on mocks/fakes and gate every change.
- **Slow** tests (marked `@pytest.mark.slow`) need a real model and are excluded by default;
  run them with a model present:

```sh
uv run pytest -m slow
```

- Property tests (Hypothesis) guard invariants — e.g. the emission mask never admits a token
  the schema rejects.

## Conventions

- **One package = one responsibility = one future repo.** New behaviour goes in the package
  that owns that responsibility, behind its public API.
- **Acyclic dependencies.** If `import-linter` complains, the design is wrong, not the
  linter. Never import another package's `_internal`.
- **Type everything** (the C boundary in `llama_backend.py` is the one sanctioned
  exception).
- **No fake numbers.** Anything quoted as a measurement must come from the
  [benchmark harness](benchmarks.md). Illustrative figures are labelled as such.
- **Conventional commits** (`feat(scope): …`, `fix(scope): …`).

## Architecture decisions

Significant choices are recorded as ADRs in the repository's `docs/adr/` (monorepo-now,
engine isolation, the substrate-as-subset rule, KV-cache scope, …). Add one when you make a
decision that future-you would want explained.

## Good first contributions

- A new engine backend behind `ControlSurface`.
- Streaming support in the server.
- More tools in the agent's `ToolRegistry`.
- Docs fixes and additional client integration guides.
