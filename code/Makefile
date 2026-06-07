# Crucible dev tasks. Run from the code/ directory. All commands go through uv,
# so the environment is always the locked workspace venv (never a stray global).
.DEFAULT_GOAL := help
.PHONY: help install lock sync lint format type imports test check clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
	  awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-10s\033[0m %s\n", $$1, $$2}'

install: sync ## Alias for sync (create/refresh the environment)

lock: ## Resolve and write uv.lock
	uv lock

sync: ## Create .venv and install all workspace packages + dev tools + the local (llama.cpp) engine
	uv sync --all-packages --extra llama

lint: ## Lint with ruff
	uv run ruff check .

format: ## Auto-format with ruff
	uv run ruff format .

type: ## Type-check with pyright
	uv run pyright

imports: ## Enforce package boundaries (import-linter)
	uv run lint-imports --config .importlinter

test: ## Run the test suite (excluding slow/model tests)
	uv run pytest -m "not slow"

check: lint type imports test ## Run the full local gate (what CI runs)
	@echo "All checks passed."

clean: ## Remove caches and the virtualenv
	rm -rf .venv .pytest_cache .ruff_cache **/__pycache__
