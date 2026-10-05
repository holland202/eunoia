"""SUB-3 (docs/SUB3_PREREG.md): an origin state on Evidence, from evidence-ledger SPEC.md section 2."""
import copy

import pytest
from eunoia import Claim, Evidence, Observation, Provenance, Validity, replay
from eunoia.substrate import ORIGIN_STATES
from oracle import OracleGate, OriginOracleGate
from sub1_cases import ACTION, STATEMENT, T, authorization, verifier

ORIGINS = ("MEASURED", "OPERATOR", "DERIVED", "INFERRED", "ABSENT", "DEFAULTED", "NEVER_WIRED", "UNVERIFIED")
BLOCKING = {"ABSENT", "DEFAULTED", "NEVER_WIRED", "UNVERIFIED"}


def c1(origin):
    """SUB-1's C1 (otherwise ALLOW) with the given origin on its one piece of evidence."""
    content = {"sensor": "PT-101", "kPa": 412}
    ev = Evidence(Observation(content, Provenance.of(content, "sensor:PT-101", 990)), "AUTHENTIC",
                  Validity(0, 2000), origin)
    claim = Claim(STATEMENT, [ev])
    return claim, verifier().run(claim), authorization(), ACTION, T


def test_S1_origin_vocabulary():
    assert ORIGIN_STATES == set(ORIGINS)
    for o in (None,) + ORIGINS:
        assert c1(o)[0].evidence[0].origin == o
    for bad in ("measured", "OBSERVED"):
        with pytest.raises(ValueError):
            c1(bad)


def test_S2_undeclared_origin_changes_nothing():
    a, b = OracleGate().decide(*c1(None)).record, OracleGate().decide(*c1(None)).record
    assert "origin" not in a["inputs"]["evidence"][0]
    assert a == b


@pytest.mark.parametrize("origin", ORIGINS)
def test_S3_origin_reaches_the_rules(origin):
    d = OriginOracleGate().decide(*c1(origin))
    want = ("DEFER", "R5o") if origin in BLOCKING else ("ALLOW", "R9")
    assert (d.outcome, d.rule) == want
    assert d.record["inputs"]["evidence"][0]["origin"] == origin
    control = OracleGate().decide(*c1(origin))  # the old oracle ignores origin
    assert (control.outcome, control.rule) == ("ALLOW", "R9")


def test_S4_origin_is_a_dependency():
    rec = OriginOracleGate().decide(*c1("MEASURED")).record
    assert replay(rec, OriginOracleGate())["match"]
    bad = copy.deepcopy(rec)
    bad["inputs"]["evidence"][0]["origin"] = "DEFAULTED"
    r = replay(bad, OriginOracleGate())
    assert {"evidence", "decision"} <= set(r["mismatches"])
    rec0 = OriginOracleGate().decide(*c1(None)).record
    added = copy.deepcopy(rec0)
    added["inputs"]["evidence"][0]["origin"] = "MEASURED"
    assert "evidence" in replay(added, OriginOracleGate())["mismatches"]
