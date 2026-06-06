from __future__ import annotations

import crucible_govern


def test_importable_and_versioned() -> None:
    assert crucible_govern.__version__ == "0.0.1"
