from __future__ import annotations

from crucible_bench import bootstrap_ci, mean


def test_mean() -> None:
    assert mean([1.0, 2.0, 3.0]) == 2.0
    assert mean([]) == 0.0


def test_bootstrap_ci_is_ordered_and_seeded() -> None:
    xs = [1.0, 2.0, 3.0, 4.0, 5.0]
    lo, hi = bootstrap_ci(xs, seed=0)
    assert lo <= hi
    # Reproducible with the same seed.
    assert bootstrap_ci(xs, seed=0) == (lo, hi)


def test_bootstrap_ci_constant_data() -> None:
    lo, hi = bootstrap_ci([7.0, 7.0, 7.0])
    assert lo == 7.0 and hi == 7.0
