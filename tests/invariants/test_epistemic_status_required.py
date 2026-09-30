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


def test_every_status_in_sway_state_is_declared_vocabulary():
    # Replaces test_forbidden_inflation_tokens, which scanned a hard-coded sample string and so could
    # never fail on anything in the repository (a vacuous guard). This one reads the real state file.
    import json, pathlib
    root = pathlib.Path(__file__).resolve().parents[2]
    state = json.loads((root / "research/sway/state.json").read_text())
    method_states = {"ADOPTED", "DOOR", "WITHDRAWN", "PENDING", "CONFIRMED_NON_SUBSTANTIVE",
                     "CONFIRMED_SUBSTANTIVE", "OPEN", "RESOLVED", "OPEN_UNRUN"}
    found = {state["status"]} | {x["status"] for k in ("items", "errata", "observations", "predictions")
                                 for x in state[k]}
    assert found <= method_states | ALLOWED, found - (method_states | ALLOWED)
