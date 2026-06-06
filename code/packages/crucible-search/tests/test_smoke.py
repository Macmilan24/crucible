from __future__ import annotations

import crucible_search


def test_importable_and_versioned() -> None:
    assert crucible_search.__version__ == "0.0.1"
