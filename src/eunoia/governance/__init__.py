"""Authorization and Gate. Verification is not authorization (E5); ALLOW is never the default (E10).

This Gate decides whether a claim may be relied on for one action at one time. It is not
sovereign-veritas's sv.gate/0 (runtime state, capability registries and policy are not here) and
claims no agreement with it. Rules and their order: docs/substrate/V001_PREREG.md."""
from __future__ import annotations

from typing import Any, Iterable

from .._canon import Frozen, content_id, exact_time, nonempty_str
from ..continuity import EvidenceBudgetExceeded, independent_roots
from ..decisions import Decision, build_record
from ..evidence import Claim
from ..verification import Outcome, Verifier


class Authorization(Frozen):
    """Permission for one action on one claim, valid on [valid_from, valid_until).

    It must name at least one verifier and require at least one independent line of evidence:
    an authorization that needs no evidence would be authority without evidence."""

    def __init__(self, *, action: str, claim_id: str, issued_by: str, valid_from: int, valid_until: int,
                 required_verifiers: Iterable[str], min_independent_roots: int) -> None:
        req = tuple(required_verifiers)
        if not req:
            raise ValueError("an authorization must name at least one required verifier")
        for v in req:
            nonempty_str(v, "required verifier id")
        if len(set(req)) != len(req):
            raise ValueError("required_verifiers repeats an id")
        if isinstance(min_independent_roots, bool) or not isinstance(min_independent_roots, int) \
                or min_independent_roots < 1:
            raise ValueError("min_independent_roots must be an int >= 1")
        vf, vu = exact_time(valid_from, "valid_from"), exact_time(valid_until, "valid_until")
        if not vf < vu:
            raise ValueError(f"empty validity interval [{vf}, {vu})")
        self._set("action", nonempty_str(action, "action"))
        self._set("claim_id", nonempty_str(claim_id, "claim_id"))
        self._set("issued_by", nonempty_str(issued_by, "issued_by"))
        self._set("valid_from", vf)
        self._set("valid_until", vu)
        self._set("required_verifiers", req)
        self._set("min_independent_roots", min_independent_roots)
        self._set("id", content_id(self.to_dict()))

    def to_dict(self) -> dict[str, Any]:
        return {"kind": "authorization", "action": self.action, "claim_id": self.claim_id,
                "issued_by": self.issued_by, "valid_from": self.valid_from, "valid_until": self.valid_until,
                "required_verifiers": list(self.required_verifiers),
                "min_independent_roots": self.min_independent_roots}

    def is_valid_at(self, t: int) -> bool:
        return self.valid_from <= exact_time(t, "t") < self.valid_until


class Gate:
    """Runs its own registered verifiers; it never accepts a verification result as input."""

    def __init__(self, verifiers: Iterable[Verifier]) -> None:
        registry: dict[str, Verifier] = {}
        for v in verifiers:
            if not isinstance(v, Verifier):
                raise TypeError(f"not a Verifier: {v!r}")
            if v.verifier_id in registry:
                raise ValueError(f"duplicate verifier id {v.verifier_id!r}")
            registry[v.verifier_id] = v
        self._verifiers = registry

    def decide(self, claim: Claim, authorization: Authorization | None, action: str, at: int) -> Decision:
        refuse: list[str] = []
        # Rule 1: malformed input. Nothing below can be evaluated on the wrong types.
        if isinstance(at, bool) or not isinstance(at, int):
            refuse.append("malformed:time")
        if not isinstance(claim, Claim):
            refuse.append("malformed:claim")
        if authorization is not None and not isinstance(authorization, Authorization):
            refuse.append("malformed:authorization")
        if refuse:
            return _decision("REFUSE", refuse, [], action, at, None, None, (), None)

        # Rules 2-5: authority. Cheap and side-effect free, so all are collected; verifiers do not
        # run under a refused authorization.
        if authorization is None:
            refuse.append("no_authorization")
        else:
            if authorization.claim_id != claim.id:
                refuse.append("authorization_claim_mismatch")
            if authorization.action != action:
                refuse.append("authorization_scope")
            if not authorization.is_valid_at(at):
                refuse.append("authorization_not_valid_at_time")
        if refuse:
            return _decision("REFUSE", refuse, [], action, at, claim, authorization, (), None)

        # Rule 6: verification, run here. Verifier.verify is called unbound, so an override of
        # verify() in a subclass is never what produces the result.
        defer: list[str] = []
        results = []
        for vid in authorization.required_verifiers:
            verifier = self._verifiers.get(vid)
            if verifier is None:
                defer.append(f"verifier_unavailable:{vid}")
                continue
            result = Verifier.verify(verifier, claim, at)
            results.append(result)
            if result.outcome is Outcome.REFUTED:
                refuse.append(f"verification_refuted:{vid}")
            elif result.outcome is Outcome.NOT_SUPPORTED:
                defer.append(f"not_supported:{vid}")
            elif result.outcome is Outcome.ERROR:
                defer.append(f"verification_error:{vid}")
            elif result.outcome is not Outcome.SUPPORTED:  # unreachable today; guards Outcome additions
                defer.append(f"verification_error:{vid}")

        # Rule 7: time-valid, root-independent evidence.
        valid = [e for e in claim.evidence if e.is_valid_at(at)]
        k = None
        try:
            k = independent_roots(valid)
        except EvidenceBudgetExceeded:
            defer.append("evidence_budget_exceeded")
        if k is not None and k < authorization.min_independent_roots:
            defer.append(f"insufficient_independent_evidence:{k}<{authorization.min_independent_roots}")

        verdict = "REFUSE" if refuse else "DEFER" if defer else "ALLOW"
        return _decision(verdict, refuse + defer, results, action, at, claim, authorization,
                         tuple(e.id for e in valid), k)


def _decision(verdict, reasons, results, action, at, claim, authorization, valid_ids, k) -> Decision:
    record = build_record(verdict=verdict, reasons=reasons, action=action, at=at, claim=claim,
                          authorization=authorization, results=results, valid_evidence=valid_ids,
                          independent_roots=k)
    return Decision(verdict, tuple(reasons), record)
