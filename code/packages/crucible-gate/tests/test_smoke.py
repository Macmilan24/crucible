from __future__ import annotations

import crucible_gate


def test_importable_and_versioned() -> None:
    assert crucible_gate.__version__ == "0.0.1"
