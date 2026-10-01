"""
Eunoia v0.01 — minimal evidence-bounded substrate (skeleton).

Status: PROPOSAL / architectural prototype.
This package currently contains only the public-API surface and documentation
anchors. Full implementations of the contracts are the next executable target.

See docs/DESIGN_NOTES.md and ARCHITECTURE.md.
"""

__version__ = "0.01.0-dev"

# Public API surface (intentionally tiny). Implementations will land here
# incrementally and only after parity tests exist.
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
]

# Placeholder names so import-time checks do not fail while the substrate
# is still under construction. Real classes replace these in later commits.
Observation = None
Evidence = None
Claim = None
Provenance = None
Verifier = None
VerificationResult = None
Authorization = None
Gate = None
Decision = None
