"""Run the 0a benchmark on the real local model and save a reproducible result.

  cd code && uv run python tools/run_benchmark.py

Produces real numbers for: malformed-rate (unconstrained vs grammar), the compounding
reliability projection, and the token economy (full CoT vs Chain-of-Draft) with a
bootstrap CI and the Phase-0 gate verdict. Writes a manifest + results JSON under
bench/crucible-bench/runs/ (git-ignored).
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path

from crucible_bench import RunManifest, run_all
from crucible_engine import LlamaCppEngine

ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / "models" / "Qwen2.5-3B-Instruct-Q4_K_M.gguf"


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return "sha256:" + h.hexdigest()[:16]


def _git_commit() -> str:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
        return out.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def main() -> None:
    if not MODEL.exists():
        print(f"Model not found at {MODEL} (see code/README.md).")
        raise SystemExit(1)

    print("Loading real model (Qwen2.5-3B, Metal)... ", flush=True)
    engine = LlamaCppEngine(str(MODEL), seed=0)
    print("loaded. Running benchmark (this takes a couple of minutes)...\n")

    report = run_all(engine, seeds=(0, 1, 2))

    manifest = RunManifest(
        commit=_git_commit(),
        suite="crucible-mini (tool-use + GSM-style)",
        model="Qwen2.5-3B-Instruct-Q4_K_M",
        model_hash=_sha256(MODEL),
        seeds=(0, 1, 2),
        hardware="Apple M5 / 24GB / Metal",
        env_lock_hash=_sha256(ROOT / "uv.lock")
        if (ROOT / "uv.lock").exists()
        else "sha256:nolock",
    )

    m = report.malformed
    c = report.compounding
    t = report.token_economy
    print("=" * 68)
    print("[1] Malformed tool-call rate (harder 4-field schema):")
    print(f"    unconstrained : {m.unconstrained_rate:.0%}  ({m.trials} trials)")
    print(f"    grammar-scoped: {m.grammar_rate:.0%}   <- 0 by construction")
    print("\n[2] Compounding over a 20-step episode (from the measured rate):")
    print(f"    unconstrained P(no malformed) : {c['unconstrained_clean_episode']:.1%}")
    print(f"    grammar      P(no malformed) : {c['grammar_clean_episode']:.0%}")
    print("\n[3] Token economy (full CoT vs Chain-of-Draft):")
    print(f"    full CoT       : {t.full.mean_tokens:6.1f} tok, {t.full.success_rate:.0%} correct")
    print(f"    Chain-of-Draft : {t.cod.mean_tokens:6.1f} tok, {t.cod.success_rate:.0%} correct")
    lo, hi = t.reduction_ci
    print(f"    reduction      : {t.reduction_factor:.2f}x  (95% CI {lo:.2f}-{hi:.2f})")
    print(f"\n[gate] {'PASS' if t.gate.passed else 'FAIL'} - {t.gate.reason}")

    runs = ROOT / "bench" / "crucible-bench" / "runs"
    runs.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    out = runs / f"run-{stamp}.json"
    out.write_text(
        json.dumps({"manifest": manifest.to_dict(), "report": report.to_dict()}, indent=2)
    )
    print(f"\nsaved: {out.relative_to(ROOT)}")
    print("(reproducible from the manifest; this is a probe, not the full suite — docs/05)")


if __name__ == "__main__":
    main()
