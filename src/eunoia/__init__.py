"""
Eunoia v0.01 — minimal evidence-bounded substrate.

Status: PROTOTYPE, self-tested (docs/substrate/V001_PREREG.md, V001_RESULTS.md). Represents
observation -> evidence -> claim -> verification -> authorization -> decision with explicit
provenance, temporal validity and a content-addressed dependency record. It checks structure,
integrity and time, not truth, and it executes nothing. Not a security boundary against code in
the same process. Not sovereign-veritas's sv.gate/0.
"""

from .decisions import Decision, check_record
from .evidence import Claim, Evidence, Observation
from .governance import Authorization, Gate
from .provenance import Provenance
from .verification import Outcome, VerificationResult, Verifier

__version__ = "0.01.0-dev"

__all__ = [
    "Observation",
    "Evidence",
    "Claim",
    "Provenance",
    "Verifier",
    "VerificationResult",
    "Outcome",
    "Authorization",
    "Gate",
    "Decision",
    "check_record",
]
