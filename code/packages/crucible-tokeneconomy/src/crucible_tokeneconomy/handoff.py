"""Inter-agent communication without natural language.

Instead of re-verbalizing the whole accumulated conversation each turn, a co-located
agent hands off a compact, typed message that references a shared KV-cache node
(the receiver reuses the sender's cached context instead of re-prefilling it).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from crucible_engine import CacheNodeId


@dataclass(frozen=True, slots=True)
class Handoff:
    """A typed agent-to-agent message.

    ``cache_node`` references shared context to reuse (KV-cache reuse); ``payload``
    is a compact structured summary, never a re-verbalized paragraph.
    """

    sender: str
    recipient: str
    intent: str
    payload: dict[str, Any] = field(default_factory=dict)
    cache_node: CacheNodeId | None = None

    def reuses_cache(self) -> bool:
        return self.cache_node is not None
