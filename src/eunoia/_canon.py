"""Canonical JSON, content ids and exact times shared by the v0.01 objects."""
from __future__ import annotations

import hashlib
import json
from typing import Any


def canonical(value: Any) -> str:
    # allow_nan=False: NaN and Infinity are not JSON; a payload carrying them is refused, not encoded.
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def content_id(value: Any) -> str:
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def exact_time(value: Any, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{name} must be an int (seconds), not {type(value).__name__} {value!r}")
    return value


def nonempty_str(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value:
        raise TypeError(f"{name} must be a non-empty str, not {value!r}")
    return value


class Frozen:
    """Immutable after __init__; equal and hashed by content id."""

    id: str

    def __setattr__(self, name: str, value: Any) -> None:
        raise AttributeError(f"{type(self).__name__} is immutable")

    def _set(self, name: str, value: Any) -> None:
        # Sealed once the id exists: a field changed after that would leave the id naming other content.
        if "id" in self.__dict__:
            raise AttributeError(f"{type(self).__name__} is sealed")
        object.__setattr__(self, name, value)

    def __eq__(self, other: object) -> bool:
        return type(self) is type(other) and self.id == other.id  # type: ignore[attr-defined]

    def __hash__(self) -> int:
        return hash((type(self).__name__, self.id))

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.id[:12]})"
