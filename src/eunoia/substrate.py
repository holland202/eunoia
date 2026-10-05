"""Eunoia v0.01 substrate (SUB-1; registration docs/SUB1_PREREG.md).

Observation -> Evidence -> Claim -> Verification -> Authorization -> Decision, with provenance, explicit
dependencies and integer-tick validity. Standard library only; no wall clock.

Status: PROTOTYPE, self-tested. The "verifier actually ran" check is in-process object identity: an
integrity check against careless callers, NOT a security boundary. This Gate is not a replacement for
Sovereign Veritas's sv.gate/0 and is not tested against its conformance vectors.
"""
from __future__ import annotations

import hashlib
import json
import weakref
from dataclasses import dataclass, field
from typing import Any, Callable, Optional

RECORD_SCHEMA = "eunoia.decision/0.01"
EVIDENCE_STATES = frozenset({"AUTHENTIC", "UNVERIFIED", "INVALID", "EXPIRED", "SUPERSEDED"})
VERIFICATION_STATUSES = frozenset({"SUPPORTED", "NOT_SUPPORTED", "REFUTED", "ERROR"})
OUTCOMES = ("ALLOW", "DEFER", "REFUSE")


def canonical(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def digest(obj: Any) -> str:
    return hashlib.sha256(canonical(obj)).hexdigest()


def _tick(x: Any, name: str) -> int:
    if isinstance(x, bool) or not isinstance(x, int):
        raise TypeError(f"{name} must be an int tick, got {type(x).__name__}")
    return x


@dataclass(frozen=True)
class Validity:
    """Half-open interval valid_from <= t < valid_until. Both bounds required (E9)."""
    valid_from: int
    valid_until: int

    def __post_init__(self):
        _tick(self.valid_from, "valid_from")
        _tick(self.valid_until, "valid_until")
        if self.valid_until <= self.valid_from:
            raise ValueError("valid_until must be after valid_from")

    def is_valid_at(self, t: int) -> bool:
        _tick(t, "t")
        return self.valid_from <= t < self.valid_until

    def data(self) -> dict:
        return {"valid_from": self.valid_from, "valid_until": self.valid_until}


@dataclass(frozen=True)
class Provenance:
    """Identity and integrity of content. A hash says what the bytes were, not that they are true (E7)."""
    source: str
    created_at: int
    content_hash: str
    parent_refs: tuple = ()

    @classmethod
    def of(cls, content: Any, source: str, created_at: int, parent_refs: tuple = ()) -> "Provenance":
        return cls(source, _tick(created_at, "created_at"), digest(content), tuple(parent_refs))

    def data(self) -> dict:
        return {"source": self.source, "created_at": self.created_at, "content_hash": self.content_hash,
                "parent_refs": list(self.parent_refs)}


@dataclass(frozen=True)
class Observation:
    """Something received or measured. Not automatically a fact, and not evidence (E1)."""
    content: Any
    provenance: Provenance

    def data(self) -> dict:
        return {"content": self.content, "provenance": self.provenance.data()}

    @property
    def id(self) -> str:
        return digest(self.data())

    def intact(self) -> bool:
        return digest(self.content) == self.provenance.content_hash


@dataclass(frozen=True)
class Evidence:
    """An observation with an evidence state and a validity window."""
    observation: Observation
    state: str
    validity: Validity

    def __post_init__(self):
        if not isinstance(self.observation, Observation):
            raise TypeError("Evidence wraps an Observation")
        if self.state not in EVIDENCE_STATES:
            raise ValueError(f"unknown evidence state {self.state!r}")

    def data(self) -> dict:
        return {"observation": self.observation.id, "state": self.state, "validity": self.validity.data()}

    @property
    def id(self) -> str:
        return digest(self.data())


@dataclass(frozen=True)
class Claim:
    """A proposition recorded as evaluable. Holds no truth value (E2, E3)."""
    statement: str
    evidence: tuple = ()

    def __post_init__(self):
        object.__setattr__(self, "evidence", tuple(self.evidence))
        for e in self.evidence:
            if not isinstance(e, Evidence):  # E1
                raise TypeError(f"Claim evidence must be Evidence, got {type(e).__name__}")

    def data(self) -> dict:
        return {"statement": self.statement, "evidence": [e.id for e in self.evidence]}

    @property
    def id(self) -> str:
        return digest(self.data())


@dataclass(frozen=True, eq=False)  # eq=False: hashed by identity, so a look-alike is not "issued"
class VerificationResult:
    claim_id: str
    status: str
    verifier_id: str
    detail: str = ""

    def __post_init__(self):
        if self.status not in VERIFICATION_STATUSES:
            raise ValueError(f"unknown verification status {self.status!r}")

    def data(self) -> dict:
        return {"claim_id": self.claim_id, "status": self.status, "verifier_id": self.verifier_id,
                "detail": self.detail}


_ISSUED: "weakref.WeakSet[VerificationResult]" = weakref.WeakSet()


class Verifier:
    """Applies a predicate to a claim. A toy: SUB-1 tests the plumbing, not verification quality."""

    def __init__(self, verifier_id: str, predicate: Callable[[Claim], str]):
        self.verifier_id = verifier_id
        self._predicate = predicate

    def run(self, claim: Claim) -> VerificationResult:
        try:
            status, detail = self._predicate(claim), ""
            if status not in VERIFICATION_STATUSES:
                status, detail = "ERROR", f"predicate returned {status!r}"
        except Exception as exc:  # a crashing verifier is an ERROR, never a pass
            status, detail = "ERROR", f"{type(exc).__name__}: {exc}"
        result = VerificationResult(claim.id, status, self.verifier_id, detail)
        _ISSUED.add(result)
        return result


def issued(result: VerificationResult) -> bool:
    return result in _ISSUED


@dataclass(frozen=True)
class Authorization:
    """May this action occur? Separate from verification (E5) and from execution (E6)."""
    action: str
    granted: bool
    authority: str
    validity: Validity

    def data(self) -> dict:
        return {"action": self.action, "granted": self.granted, "authority": self.authority,
                "validity": self.validity.data()}


@dataclass(frozen=True)
class Decision:
    outcome: str
    rule: str
    reason: str
    record: dict = field(repr=False)


def decide_view(v: dict) -> tuple:
    """The gate rules R1-R9 (docs/SUB1_PREREG.md) over plain data. First match wins. Fail closed (E10)."""
    r = v["verification"]
    if r is None:
        return "DEFER", "R1", "no verification result"
    if not v["issued"] or r["claim_id"] != v["claim_id"]:
        return "REFUSE", "R2", "verification not issued by a verifier for this claim"
    if r["status"] == "ERROR":
        return "DEFER", "R3", "verification errored"
    if r["status"] == "NOT_SUPPORTED":
        return "DEFER", "R3", "claim not supported"
    if r["status"] == "REFUTED":
        return "REFUSE", "R3", "claim refuted"
    if not v["evidence"]:
        return "DEFER", "R4", "claim has no evidence"
    for e in v["evidence"]:
        if e["state"] != "AUTHENTIC":
            return "DEFER", "R5", f"evidence {e['state']}"
        if not e["intact"]:
            return "DEFER", "R5", "evidence content does not match its provenance hash"
        if not Validity(**e["validity"]).is_valid_at(v["t"]):
            return "DEFER", "R5", "evidence not valid at t"
    a = v["authorization"]
    if a is None:
        return "DEFER", "R6", "no authorization"
    if not a["granted"] or a["action"] != v["action"]:
        return "REFUSE", "R7", "action not authorized"
    if not Validity(**a["validity"]).is_valid_at(v["t"]):
        return "DEFER", "R8", "authorization not valid at t"
    if r["status"] == "SUPPORTED":
        return "ALLOW", "R9", "supported, evidenced, authorized"
    return "REFUSE", "R9", f"unrecognised status {r['status']!r}"


def _dependencies(view: dict) -> dict:
    return {
        "observation": [digest(e["observation"]) for e in view["evidence"]],
        "evidence": [digest({k: e[k] for k in ("state", "validity")} | {"observation": digest(e["observation"])})
                     for e in view["evidence"]],
        "claim": view["claim_id"],
        "verifier": None if view["verification"] is None else view["verification"]["verifier_id"],
        "verification": None if view["verification"] is None else digest(view["verification"]),
        "authorization": None if view["authorization"] is None else digest(view["authorization"]),
    }


class Gate:
    """ALLOW / DEFER / REFUSE. Never ALLOW by default (E10)."""

    def decide(self, claim: Claim, result: Optional[VerificationResult], authorization: Optional[Authorization],
               action: str, t: int) -> Decision:
        _tick(t, "t")
        view = {
            "t": t, "action": action, "claim_id": claim.id, "statement": claim.statement,
            "issued": result is not None and issued(result),
            "verification": None if result is None else result.data(),
            "evidence": [{"observation": e.observation.data(), "state": e.state, "validity": e.validity.data(),
                          "intact": e.observation.intact()} for e in claim.evidence],
            "authorization": None if authorization is None else authorization.data(),
        }
        outcome, rule, reason = decide_view(view)
        record = {"schema": RECORD_SCHEMA, "inputs": view, "dependencies": _dependencies(view),
                  "outcome": outcome, "rule": rule, "reason": reason}
        return Decision(outcome, rule, reason, record)


def replay(record: dict) -> dict:
    """Recompute dependencies and the decision from a record's inputs (E8). 'issued' is replayed as recorded:
    whether the verifier ran is attested at decision time and cannot be re-observed later."""
    mismatches = []
    recomputed = _dependencies(record["inputs"])
    for key, want in record["dependencies"].items():
        if recomputed.get(key) != want:
            mismatches.append(key)
    outcome, rule, _ = decide_view(record["inputs"])
    if (outcome, rule) != (record["outcome"], record["rule"]):
        mismatches.append("decision")
    return {"match": not mismatches, "mismatches": mismatches, "outcome": outcome}


def execute(decision: Decision, handler: Callable[[], Any]) -> Any:
    """Run an action only under an ALLOW decision. Deciding never executes (E6)."""
    if decision.outcome != "ALLOW":
        raise PermissionError(f"decision is {decision.outcome}, not ALLOW")
    return handler()
