"""V001: one test group per registered prediction (docs/substrate/V001_PREREG.md, Amendment 1).
Self-tested: written by the model that wrote the substrate."""
import inspect
import itertools

import pytest

from eunoia import (Authorization, Claim, Evidence, Gate, Observation, Outcome, Provenance,
                    Verifier, check_record)
from eunoia.continuity import MAX_EVIDENCE, EvidenceBudgetExceeded, independent_roots


class Fixed(Verifier):
    def __init__(self, vid, out):
        super().__init__(vid)
        self.out, self.calls = out, 0

    def check(self, claim, at):
        self.calls += 1
        return self.out


def obs(n, src="sensor"):
    return Observation({"reading": n}, Provenance(src, 0))


def ev(o, vf=0, vu=100, src="lab"):
    return Evidence(provenance=Provenance(src, 0), valid_from=vf, valid_until=vu, observation=o)


def derived(parents, vf=0, vu=100, src="derive"):
    return Evidence(provenance=Provenance(src, 0), valid_from=vf, valid_until=vu, derived_from=parents)


def auth_for(claim, *, action="act", vf=0, vu=100, verifiers=("v1",), min_roots=2):
    return Authorization(action=action, claim_id=claim.id, issued_by="operator", valid_from=vf,
                         valid_until=vu, required_verifiers=verifiers, min_independent_roots=min_roots)


def healthy(out=Outcome.SUPPORTED, vf=0, vu=100):
    claim = Claim("the reading is 7", [ev(obs(1, "a"), vf, vu), ev(obs(2, "b"), vf, vu)])
    v = Fixed("v1", out)
    return claim, auth_for(claim), Gate([v]), v


def test_healthy_chain_allows():
    claim, auth, gate, v = healthy()
    d = gate.decide(claim, auth, "act", 50)
    assert (d.decision, d.reasons) == ("ALLOW", ())
    assert v.calls == 1


# ---- P1 (E1, E3): observation is not evidence; a claim needs evidence; malformed input refuses ----
def test_p1_observation_is_not_evidence():
    with pytest.raises(TypeError):
        Claim("x", [obs(1)])
    with pytest.raises(TypeError):
        Evidence(provenance=Provenance("p", 0), valid_from=0, valid_until=1, observation=ev(obs(1)))
    with pytest.raises(TypeError):
        derived([obs(1)])


def test_p1_claim_needs_evidence():
    with pytest.raises(ValueError):
        Claim("x", [])


@pytest.mark.parametrize("bad_claim", [obs(1), "a claim", None, {"statement": "x"}])
def test_p1_non_claim_refuses(bad_claim):
    claim, auth, gate, v = healthy()
    d = gate.decide(bad_claim, auth, "act", 50)
    assert (d.decision, d.reasons) == ("REFUSE", ("malformed:claim",))
    assert v.calls == 0


@pytest.mark.parametrize("bad_auth", ["authorized", True, {"action": "act"}])
def test_p1_non_authorization_refuses(bad_auth):
    claim, auth, gate, v = healthy()
    d = gate.decide(claim, bad_auth, "act", 50)
    assert (d.decision, d.reasons) == ("REFUSE", ("malformed:authorization",))


@pytest.mark.parametrize("bad_t", [50.0, True, "50", None])
def test_p1_non_int_time_refuses(bad_t):
    claim, auth, gate, v = healthy()
    assert gate.decide(claim, auth, "act", bad_t).reasons == ("malformed:time",)


# ---- P2 (E4): NOT_SUPPORTED != REFUTED ----
@pytest.mark.parametrize("out,decision,reason", [
    (Outcome.NOT_SUPPORTED, "DEFER", "not_supported:v1"),
    (Outcome.REFUTED, "REFUSE", "verification_refuted:v1"),
    (Outcome.ERROR, "DEFER", "verification_error:v1"),
])
def test_p2_outcomes_are_distinct(out, decision, reason):
    claim, auth, gate, v = healthy(out)
    d = gate.decide(claim, auth, "act", 50)
    assert (d.decision, d.reasons) == (decision, (reason,))


# ---- P3 (E5): verification is not authorization ----
def test_p3_no_authorization():
    claim, auth, gate, v = healthy()
    assert gate.decide(claim, None, "act", 50).reasons == ("no_authorization",)
    assert v.calls == 0


def test_p3_authorization_for_another_claim():
    claim, auth, gate, v = healthy()
    other = Claim("another", [ev(obs(9, "z"))])
    d = gate.decide(claim, auth_for(other), "act", 50)
    assert (d.decision, d.reasons) == ("REFUSE", ("authorization_claim_mismatch",))


def test_p3_authorization_for_another_action():
    claim, auth, gate, v = healthy()
    d = gate.decide(claim, auth, "delete_everything", 50)
    assert (d.decision, d.reasons) == ("REFUSE", ("authorization_scope",))


@pytest.mark.parametrize("t", [-1, 100, 1000])
def test_p3_authorization_outside_its_interval(t):
    claim = Claim("c", [ev(obs(1, "a"), -10, 2000), ev(obs(2, "b"), -10, 2000)])
    gate = Gate([Fixed("v1", Outcome.SUPPORTED)])
    d = gate.decide(claim, auth_for(claim, vf=0, vu=100), "act", t)
    assert (d.decision, d.reasons) == ("REFUSE", ("authorization_not_valid_at_time",))


# ---- P4 (E9): time matters, boundaries exact ----
@pytest.mark.parametrize("t,decision", [(9, "DEFER"), (10, "ALLOW"), (19, "ALLOW"), (20, "DEFER")])
def test_p4_evidence_validity_boundaries(t, decision):
    claim, auth, gate, v = healthy(vf=10, vu=20)
    d = gate.decide(claim, auth, "act", t)
    assert d.decision == decision
    if decision == "DEFER":
        assert d.reasons == ("insufficient_independent_evidence:0<2",)


# ---- P5 (E8): independence comes from the provenance graph, not from the count ----
def test_p5_common_root_counts_once():
    o = obs(1, "gnss")
    e1, e2 = ev(o, src="fusion-a"), ev(o, src="fusion-b")  # two evidence items, one observation
    claim = Claim("position", [e1, e2])
    gate = Gate([Fixed("v1", Outcome.SUPPORTED)])
    d = gate.decide(claim, auth_for(claim), "act", 50)
    assert (d.decision, d.reasons) == ("DEFER", ("insufficient_independent_evidence:1<2",))
    claim2 = Claim("position", [e1, e2, ev(obs(2, "camera"))])
    assert gate.decide(claim2, auth_for(claim2), "act", 50).decision == "ALLOW"


def test_p5_derivations_from_one_source_count_once():
    base = ev(obs(1, "gnss"))
    claim = Claim("position", [derived([base], src="a"), derived([base], src="b")])
    gate = Gate([Fixed("v1", Outcome.SUPPORTED)])
    assert gate.decide(claim, auth_for(claim), "act", 50).reasons == ("insufficient_independent_evidence:1<2",)


def test_p5_independent_roots_is_exact_not_greedy():
    a, b = ev(obs(1, "a")), ev(obs(2, "b"))
    ab = derived([a, b])
    assert independent_roots([ab]) == 1
    assert independent_roots([ab, a]) == 1           # {a,b} and {a} overlap
    assert independent_roots([ab, a, b]) == 2         # {a} and {b}; {a,b} must be dropped
    assert independent_roots([a, ev(obs(1, "a"), src="copy")]) == 1


def test_p5_budget_is_refused_not_approximated():
    items = [ev(obs(i, f"s{i}")) for i in range(MAX_EVIDENCE + 1)]
    with pytest.raises(EvidenceBudgetExceeded):
        independent_roots(items)
    claim = Claim("many", items)
    d = Gate([Fixed("v1", Outcome.SUPPORTED)]).decide(claim, auth_for(claim), "act", 50)
    assert (d.decision, d.reasons) == ("DEFER", ("evidence_budget_exceeded",))


# ---- P6: the Gate runs verifiers; caller-written verdicts are never inputs ----
class Raises(Verifier):
    def check(self, claim, at):
        raise RuntimeError("boom")


class Returns(Verifier):
    def __init__(self, vid, value):
        super().__init__(vid)
        self.value = value

    def check(self, claim, at):
        return self.value


@pytest.mark.parametrize("verifier", [Raises("v1"), Returns("v1", "SUPPORTED"), Returns("v1", True),
                                      Returns("v1", None), Returns("v1", "Outcome.SUPPORTED")])
def test_p6_misbehaving_verifier_never_allows(verifier):
    claim, auth, _, _ = healthy()
    d = Gate([verifier]).decide(claim, auth, "act", 50)
    assert (d.decision, d.reasons) == ("DEFER", ("verification_error:v1",))


def test_p6_overriding_verify_does_not_forge_a_result():
    from eunoia import VerificationResult

    class Forger(Verifier):
        def check(self, claim, at):
            return Outcome.REFUTED

        def verify(self, claim, at):
            return VerificationResult(verifier_id=self.verifier_id, claim_id=claim.id, at=at,
                                      outcome=Outcome.SUPPORTED)

    claim, auth, _, _ = healthy()
    d = Gate([Forger("v1")]).decide(claim, auth, "act", 50)
    assert (d.decision, d.reasons) == ("REFUSE", ("verification_refuted:v1",))


def test_p6_missing_verifier_defers():
    claim, auth, _, _ = healthy()
    d = Gate([Fixed("v2", Outcome.SUPPORTED)]).decide(claim, auth, "act", 50)
    assert (d.decision, d.reasons) == ("DEFER", ("verifier_unavailable:v1",))


def test_p6_decide_has_no_parameter_for_a_verification_result():
    assert list(inspect.signature(Gate.decide).parameters) == ["self", "claim", "authorization", "action", "at"]


# ---- P7 (E8): the record is closed, acyclic, deterministic, and tamper-visible ----
def _all_decisions():
    claim, auth, gate, _ = healthy()
    yield gate.decide(claim, auth, "act", 50)
    yield gate.decide(claim, None, "act", 50)
    yield gate.decide(claim, auth, "other", 50)
    yield gate.decide(obs(1), auth, "act", 50)
    yield healthy(Outcome.REFUTED)[2].decide(claim, auth, "act", 50)
    base = ev(obs(1, "g"))
    c2 = Claim("p", [derived([base]), derived([derived([base])])])
    yield Gate([Fixed("v1", Outcome.SUPPORTED)]).decide(c2, auth_for(c2), "act", 50)


def test_p7_every_record_is_closed_and_acyclic():
    for d in _all_decisions():
        assert check_record(d.record) == [], d


def test_p7_record_id_is_deterministic():
    assert [d.id for d in _all_decisions()] == [d.id for d in _all_decisions()]


def test_p7_check_record_can_fail():
    import copy
    rec = next(iter(_all_decisions())).record
    tampered = copy.deepcopy(rec)
    nid = next(k for k, v in tampered["nodes"].items() if v["kind"] == "observation")
    tampered["nodes"][nid]["payload"] = {"reading": 999}
    assert any("does not hash" in p for p in check_record(tampered))
    dangling = copy.deepcopy(rec)
    del dangling["nodes"][nid]
    assert any("undefined" in p for p in check_record(dangling))
    cyc = copy.deepcopy(rec)
    claim_id = next(k for k, v in cyc["nodes"].items() if v["kind"] == "claim")
    ev_id = next(k for k, v in cyc["nodes"].items() if v["kind"] == "evidence")
    cyc["edges"].append([ev_id, "DEPENDS_ON", claim_id])
    assert "dependency graph has a cycle" in check_record(cyc)
    relabeled = copy.deepcopy(rec)
    relabeled["decision"] = "REFUSE"
    assert "record id does not match its content" in check_record(relabeled)


# ---- P8 (E7): integrity and consistency are not truth (a limit, expected to hold) ----
def test_p8_fabricated_but_consistent_input_allows():
    lie = Observation({"reading": "the moon is made of cheese"}, Provenance("trusted-sensor", 0))
    claim = Claim("the moon is made of cheese", [ev(lie), ev(obs(2, "another-liar"))])
    d = Gate([Fixed("v1", Outcome.SUPPORTED)]).decide(claim, auth_for(claim), "act", 50)
    assert d.decision == "ALLOW"


# ---- P9 (E10): ALLOW exactly when every prerequisite holds, over all 128 fault combinations ----
FAULTS = ("auth_absent", "wrong_claim", "wrong_action", "auth_expired",
          "not_supported", "verifier_missing", "evidence_stale")


def _case(f):
    vu = 40 if f["evidence_stale"] else 100
    claim = Claim("c", [ev(obs(1, "a"), 0, vu), ev(obs(2, "b"), 0, vu)])
    other = Claim("other", [ev(obs(3, "x"))])
    auth = None if f["auth_absent"] else auth_for(other if f["wrong_claim"] else claim,
                                                  vu=40 if f["auth_expired"] else 100)
    verifiers = [] if f["verifier_missing"] else \
        [Fixed("v1", Outcome.NOT_SUPPORTED if f["not_supported"] else Outcome.SUPPORTED)]
    return Gate(verifiers).decide(claim, auth, "other" if f["wrong_action"] else "act", 50)


def test_p9_allow_iff_all_prerequisites_hold():
    allows = []
    for bits in itertools.product((False, True), repeat=len(FAULTS)):
        f = dict(zip(FAULTS, bits))
        d = _case(f)
        if d.decision == "ALLOW":
            allows.append(bits)
        assert check_record(d.record) == []
    assert allows == [(False,) * len(FAULTS)]


# ---- P13 (Amendment 1): a derivation cannot outlive what it was derived from ----
@pytest.mark.parametrize("t,decision", [(5, "ALLOW"), (50, "DEFER")])
def test_p13_staleness_is_not_laundered_by_derivation(t, decision):
    stale_source = ev(obs(1, "s"), 0, 10)
    laundered = derived([stale_source], 0, 100)
    claim = Claim("c", [laundered])
    d = Gate([Fixed("v1", Outcome.SUPPORTED)]).decide(claim, auth_for(claim, min_roots=1), "act", t)
    assert d.decision == decision


# ---- construction guards ----
def test_authorization_cannot_require_nothing():
    claim, *_ = healthy()
    with pytest.raises(ValueError):
        auth_for(claim, verifiers=())
    with pytest.raises(ValueError):
        auth_for(claim, min_roots=0)
    with pytest.raises(ValueError):
        auth_for(claim, min_roots=True)


def test_non_json_and_non_finite_payloads_are_refused():
    with pytest.raises(ValueError):
        Observation({"x": float("nan")}, Provenance("s", 0))
    with pytest.raises(ValueError):
        Observation({"x": float("inf")}, Provenance("s", 0))
    with pytest.raises(TypeError):
        Observation({"x": object()}, Provenance("s", 0))


def test_objects_are_immutable_and_payload_copies_cannot_change_identity():
    o = obs(1)
    before = o.id
    o.payload["reading"] = 999
    assert o.id == before and o.payload == {"reading": 1}
    with pytest.raises(AttributeError):
        o.provenance = Provenance("x", 1)


def test_float_times_are_refused():
    with pytest.raises(TypeError):
        Evidence(provenance=Provenance("p", 0), valid_from=0.0, valid_until=1, observation=obs(1))
    with pytest.raises(TypeError):
        Provenance("p", 0.5)


# ---- found after the registered run (self-attack A4, V001_RESULTS.md): identity must stay bound to content ----
def test_constructed_objects_cannot_be_reset_through_the_internal_setter():
    o = obs(1)
    with pytest.raises(AttributeError):
        o._set("provenance", Provenance("x", 9))
    assert o.provenance == Provenance("sensor", 0)


# ---- unregistered structural property, added after V001_RESULTS (the method sovereign-veritas's gate_constraint.py
# already uses on its 4608-case lattice): adding a fault never moves a decision toward ALLOW ----
ORDER = {"ALLOW": 0, "DEFER": 1, "REFUSE": 2}


def test_decisions_are_monotone_in_faults():
    dec = {bits: _case(dict(zip(FAULTS, bits))).decision
           for bits in itertools.product((False, True), repeat=len(FAULTS))}
    violations = [(p, i) for p in dec for i in range(len(FAULTS))
                  if not p[i] and ORDER[dec[p[:i] + (True,) + p[i + 1:]]] < ORDER[dec[p]]]
    assert violations == []
    assert set(dec.values()) == {"ALLOW", "DEFER", "REFUSE"}  # the order is exercised, not trivially constant
