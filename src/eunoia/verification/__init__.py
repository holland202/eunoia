"""Independent verification. NOT_SUPPORTED != REFUTED (E4); a verdict is not authority (E5)."""
from __future__ import annotations

from enum import Enum
from typing import Any

from .._canon import Frozen, content_id, exact_time, nonempty_str
from ..evidence import Claim


class Outcome(Enum):
    SUPPORTED = "SUPPORTED"
    NOT_SUPPORTED = "NOT_SUPPORTED"
    REFUTED = "REFUTED"
    ERROR = "ERROR"


class VerificationResult(Frozen):
    def __init__(self, *, verifier_id: str, claim_id: str, at: int, outcome: Outcome, detail: str = "") -> None:
        if not isinstance(outcome, Outcome):
            raise TypeError(f"outcome must be an Outcome, not {outcome!r}")
        self._set("verifier_id", nonempty_str(verifier_id, "verifier_id"))
        self._set("claim_id", nonempty_str(claim_id, "claim_id"))
        self._set("at", exact_time(at, "at"))
        self._set("outcome", outcome)
        self._set("detail", str(detail))
        self._set("id", content_id(self.to_dict()))

    def to_dict(self) -> dict[str, Any]:
        return {"kind": "verification", "verifier_id": self.verifier_id, "claim_id": self.claim_id,
                "at": self.at, "outcome": self.outcome.value, "detail": self.detail}


class Verifier:
    """Subclass and implement check(). The Gate calls Verifier.verify itself (the base method, so an
    override of verify() is never used): a result the caller writes is never an input."""

    def __init__(self, verifier_id: str) -> None:
        self.verifier_id = nonempty_str(verifier_id, "verifier_id")

    def check(self, claim: Claim, at: int) -> Outcome:
        raise NotImplementedError

    def verify(self, claim: Claim, at: int) -> VerificationResult:
        try:
            out = self.check(claim, at)
        except Exception as exc:  # a crashed verifier did not support anything
            return VerificationResult(verifier_id=self.verifier_id, claim_id=claim.id, at=at,
                                      outcome=Outcome.ERROR, detail=f"raised {type(exc).__name__}: {exc}")
        if not isinstance(out, Outcome):  # "SUPPORTED", True, None: not a verdict
            return VerificationResult(verifier_id=self.verifier_id, claim_id=claim.id, at=at,
                                      outcome=Outcome.ERROR, detail=f"returned {type(out).__name__} {out!r}")
        return VerificationResult(verifier_id=self.verifier_id, claim_id=claim.id, at=at, outcome=out)
