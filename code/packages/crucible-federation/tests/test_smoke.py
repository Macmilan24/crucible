from __future__ import annotations

import crucible_federation


def test_importable_and_versioned() -> None:
    assert crucible_federation.__version__ == "0.0.1"
