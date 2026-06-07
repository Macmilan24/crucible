"""Small, dependency-free statistics for the benchmark.

A percentile bootstrap CI (seeded, so it is reproducible) is enough for the probe;
the full protocol (paired bootstrap, Holm-Bonferroni across RQs) is in
docs/05-evaluation-plan.md and lands with the big suites.
"""

from __future__ import annotations

import random


def mean(xs: list[float]) -> float:
    return sum(xs) / len(xs) if xs else 0.0


def bootstrap_ci(
    xs: list[float], *, resamples: int = 2000, alpha: float = 0.05, seed: int = 0
) -> tuple[float, float]:
    """A seeded percentile bootstrap confidence interval for the mean."""
    if not xs:
        return (0.0, 0.0)
    rng = random.Random(seed)
    n = len(xs)
    means: list[float] = []
    for _ in range(resamples):
        means.append(sum(xs[rng.randrange(n)] for _ in range(n)) / n)
    means.sort()
    lo = means[int((alpha / 2) * resamples)]
    hi = means[min(int((1 - alpha / 2) * resamples), resamples - 1)]
    return (lo, hi)
