"""
Eunoia v0.01 — minimal evidence-bounded substrate.

Status: PROTOTYPE, self-tested (SUB-1, docs/SUB1_PREREG.md). Not production-ready.

Until SUB-1 every public name here was a ``None`` placeholder, so ``from eunoia import Gate`` silently
gave no gate. They are now the real classes from ``eunoia.substrate``.
"""

__version__ = "0.01.0-dev"

from .substrate import (  # noqa: E402
    Authorization,
    Claim,
    Decision,
    Evidence,
    Gate,
    Observation,
    Provenance,
    Validity,
    VerificationResult,
    Verifier,
    execute,
    replay,
)

__all__ = [
    "Observation",
    "Evidence",
    "Claim",
    "Provenance",
    "Verifier",
    "VerificationResult",
    "Authorization",
    "Gate",
    "Decision",
    "Validity",
]
# execute and replay are functions, importable from here but kept out of __all__ (SUB-1 P6 registered
# __all__ as classes only).
