"""Evidence layer: Observation, Evidence, Claim (E1 Observation != Evidence, E3 Claim != Verification)."""
from __future__ import annotations

import json
from typing import Any, Iterable

from .._canon import Frozen, canonical, content_id, exact_time, nonempty_str
from ..provenance import Provenance


def _need(value: Any, kind: type, name: str) -> Any:
    if not isinstance(value, kind):
        raise TypeError(f"{name} must be {kind.__name__}, not {type(value).__name__}")
    return value


class Observation(Frozen):
    """Something received or measured. Not evidence, and not a fact."""

    def __init__(self, payload: Any, provenance: Provenance) -> None:
        self._set("_payload_json", canonical(payload))  # raises on NaN, Infinity, non-JSON
        self._set("provenance", _need(provenance, Provenance, "provenance"))
        self._set("id", content_id(self._content()))

    @property
    def payload(self) -> Any:
        return json.loads(self._payload_json)  # a fresh copy: the stored content cannot be mutated

    def _content(self) -> dict[str, Any]:
        return {"kind": "observation", "payload": self.payload, "provenance": self.provenance.to_dict()}

    def to_dict(self) -> dict[str, Any]:
        return self._content()


class Evidence(Frozen):
    """An observation (or other evidence) admitted with provenance and a validity interval [from, until).

    Exactly one of `observation` or `derived_from`. Amendment 1: valid at t only if every ancestor
    derived from is valid at t too, so a derivation cannot outlive what it was derived from."""

    def __init__(self, *, provenance: Provenance, valid_from: int, valid_until: int,
                 observation: Observation | None = None, derived_from: Iterable["Evidence"] = ()) -> None:
        derived = tuple(derived_from)
        if (observation is None) == (not derived):
            raise ValueError("evidence needs exactly one of observation or derived_from")
        if observation is not None:
            _need(observation, Observation, "observation")
        for parent in derived:
            _need(parent, Evidence, "derived_from item")
        if len({p.id for p in derived}) != len(derived):
            raise ValueError("derived_from repeats an item")
        vf, vu = exact_time(valid_from, "valid_from"), exact_time(valid_until, "valid_until")
        if not vf < vu:
            raise ValueError(f"empty validity interval [{vf}, {vu})")
        self._set("provenance", _need(provenance, Provenance, "provenance"))
        self._set("valid_from", vf)
        self._set("valid_until", vu)
        self._set("observation", observation)
        self._set("derived_from", tuple(sorted(derived, key=lambda e: e.id)))
        roots = ({observation.id} if observation is not None
                 else frozenset().union(*(p.roots for p in derived)))
        self._set("roots", frozenset(roots))
        self._set("id", content_id(self._content()))

    def _content(self) -> dict[str, Any]:
        return {"kind": "evidence", "provenance": self.provenance.to_dict(),
                "valid_from": self.valid_from, "valid_until": self.valid_until,
                "observation": None if self.observation is None else self.observation.id,
                "derived_from": [p.id for p in self.derived_from]}

    def to_dict(self) -> dict[str, Any]:
        return self._content()

    def is_valid_at(self, t: int) -> bool:
        exact_time(t, "t")
        return self.valid_from <= t < self.valid_until and all(p.is_valid_at(t) for p in self.derived_from)


class Claim(Frozen):
    """A proposition recorded as evaluable. It carries no status: status comes only from verification."""

    def __init__(self, statement: str, evidence: Iterable[Evidence]) -> None:
        items = tuple(evidence)
        if not items:
            raise ValueError("a claim needs at least one Evidence item")
        for e in items:
            _need(e, Evidence, "claim evidence item")  # an Observation is not evidence (E1)
        if len({e.id for e in items}) != len(items):
            raise ValueError("claim repeats an evidence item")
        self._set("statement", nonempty_str(statement, "statement"))
        self._set("evidence", tuple(sorted(items, key=lambda e: e.id)))
        self._set("id", content_id(self._content()))

    def _content(self) -> dict[str, Any]:
        return {"kind": "claim", "statement": self.statement, "evidence": [e.id for e in self.evidence]}

    def to_dict(self) -> dict[str, Any]:
        return self._content()
