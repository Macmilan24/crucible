from __future__ import annotations

import crucible_memory


def test_importable_and_versioned() -> None:
    assert crucible_memory.__version__ == "0.0.1"
