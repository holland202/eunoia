"""TEST ORACLE, not a gate (SUB-2, docs/SUB2_PREREG.md).

SUB-1's rules R1-R9, moved out of the eunoia package unchanged in logic. They exist to exercise Eunoia's
contracts in tests. Eunoia ships no decision rule; production decisions are meant to come from Sovereign
Veritas's sv.gate/0 through an adapter.
"""
from eunoia import Gate, Validity


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


class OracleGate(Gate):
    rule_set = "eunoia-test-oracle/r1-r9"

    def rules(self, view):
        return decide_view(view)
