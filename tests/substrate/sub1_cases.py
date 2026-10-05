"""SUB-1 case matrix (docs/SUB1_PREREG.md). Constructed inputs; shared by tests and tools/sub1_run.py."""
from eunoia import Authorization, Claim, Evidence, Observation, Provenance, Validity, VerificationResult, Verifier

T = 1000
ACTION = "open_valve"
STATEMENT = "valve V1 pressure below limit"

EXPECTED = {
    "C1": "ALLOW", "C2": "DEFER", "C3": "REFUSE", "C4": "REFUSE", "C5": "DEFER", "C6": "REFUSE",
    "C7": "DEFER", "C8": "DEFER", "C9": "DEFER", "C10": "DEFER", "C11": "DEFER", "C12": "DEFER",
    "C13": "REFUSE", "C14": "REFUSE", "C15": "DEFER", "C16": "REFUSE", "C17": "REFUSE", "C18": "DEFER",
    "C19": "DEFER",
}


def evidence(state="AUTHENTIC", vf=0, vu=2000, content=None):
    content = {"sensor": "PT-101", "kPa": 412} if content is None else content
    obs = Observation(content, Provenance.of(content, "sensor:PT-101", 990))
    return Evidence(obs, state, Validity(vf, vu))


def authorization(action=ACTION, granted=True, vf=0, vu=2000):
    return Authorization(action, granted, "operator:shift-lead", Validity(vf, vu))


def verifier(status="SUPPORTED"):
    return Verifier("toy-threshold-v0", lambda claim: status)


def build(case):
    """-> (claim, result, authorization, action, t)"""
    ev, auth, status, result = [evidence()], authorization(), "SUPPORTED", "run"
    if case == "C2":
        result = None
    elif case == "C3":
        result = "forged"
    elif case == "C4":
        result = "other_claim"
    elif case in ("C5", "C6", "C7"):
        status = {"C5": "NOT_SUPPORTED", "C6": "REFUTED", "C7": "ERROR"}[case]
    elif case == "C8":
        ev = []
    elif case == "C9":
        ev = [evidence(state="UNVERIFIED")]
    elif case == "C10":
        ev = [evidence(vu=900)]
    elif case == "C12":
        auth = None
    elif case == "C13":
        auth = authorization(granted=False)
    elif case == "C14":
        auth = authorization(action="close_valve")
    elif case == "C15":
        auth = authorization(vu=900)
    elif case == "C17":
        status = "REFUTED"
    elif case == "C18":
        ev = [evidence(vf=1100, vu=2000)]
    elif case == "C19":
        ev = [evidence(vu=1000)]
    claim = Claim(STATEMENT, ev)
    if case == "C11":
        claim.evidence[0].observation.content["kPa"] = 380  # altered after its provenance hash was taken
    if result == "run":
        result = verifier(status).run(claim)
    elif result == "forged":
        result = VerificationResult(claim.id, "SUPPORTED", "toy-threshold-v0")
    elif result == "other_claim":
        result = verifier().run(Claim("some other proposition", [evidence()]))
    if case == "C16":
        object.__setattr__(result, "status", "MAYBE")
    return claim, result, auth, ACTION, T
