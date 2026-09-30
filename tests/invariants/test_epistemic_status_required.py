"""
Invariant: claims must carry an epistemic status from the allowed vocabulary.
Status: IMPLEMENTED as a structural test of the schema/policy, not a scientific result.
"""

ALLOWED = {
    "FACT", "MEASURED", "DERIVED", "IMPLEMENTED", "HYPOTHESIS",
    "PROPOSAL", "SPECULATIVE", "UNKNOWN", "REFUTED",
    "INSUFFICIENT_EVIDENCE", "NOT_SUPPORTED", "EXPLORATORY", "PROPOSED",
}


def claim_is_well_formed(claim: dict) -> bool:
    if "status" not in claim:
        return False
    return claim["status"] in ALLOWED


def test_status_required():
    assert not claim_is_well_formed({"statement": "x"})
    assert claim_is_well_formed({"statement": "x", "status": "HYPOTHESIS"})
    assert not claim_is_well_formed({"statement": "x", "status": "PROVEN"})


def test_forbidden_inflation_tokens():
    forbidden = ["proves", "guarantees", "solves"]
    sample = "This measurement is consistent with H under conditions C."
    for w in forbidden:
        assert w not in sample.lower()
