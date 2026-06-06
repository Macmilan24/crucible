"""Run manifest — the reproducibility record (docs/09, docs/05).

Reproducibility is the marketing for 0a: a third party must be able to reproduce
the headline numbers from the repo using only what is captured here.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class RunManifest:
    commit: str
    suite: str
    model: str
    model_hash: str
    seeds: tuple[int, ...]
    hardware: str
    env_lock_hash: str
    notes: str = ""
    extra: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def is_reproducible(self) -> bool:
        """A manifest is reproducible only if every field needed to re-run is present."""
        required = (
            self.commit,
            self.suite,
            self.model,
            self.model_hash,
            self.hardware,
            self.env_lock_hash,
        )
        return all(bool(v) for v in required) and len(self.seeds) >= 1
