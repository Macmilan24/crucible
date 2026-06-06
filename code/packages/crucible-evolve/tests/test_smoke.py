from __future__ import annotations

import crucible_evolve


def test_importable_and_versioned() -> None:
    assert crucible_evolve.__version__ == "0.0.1"
