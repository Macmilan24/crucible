from __future__ import annotations

import crucible_verify


def test_importable_and_versioned() -> None:
    assert crucible_verify.__version__ == "0.0.1"
