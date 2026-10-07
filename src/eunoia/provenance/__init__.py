"""Provenance and integrity. A content id establishes identity and integrity, not truth (E7)."""
from __future__ import annotations

from typing import Any

from .._canon import Frozen, content_id, exact_time, nonempty_str


class Provenance(Frozen):
    """Who or what produced an object, and when (integer seconds). Declared, not authenticated."""

    def __init__(self, source: str, created_at: int) -> None:
        self._set("source", nonempty_str(source, "source"))
        self._set("created_at", exact_time(created_at, "created_at"))
        self._set("id", content_id(self.to_dict()))

    def to_dict(self) -> dict[str, Any]:
        return {"source": self.source, "created_at": self.created_at}
