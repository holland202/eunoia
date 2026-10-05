"""SUB-1: one test per invariant E1-E10 plus the case matrix and replay (docs/SUB1_PREREG.md).
Every test here must be able to fail: tools/sub1_run.py applies one mutant per invariant and expects a failure."""
import json
import subprocess
import sys

import pytest

import eunoia
from eunoia import Claim, Gate, Validity, VerificationResult, execute, replay
from eunoia.substrate import digest
import sub1_cases as K


def decide(case):
    return Gate().decide(*K.build(case))


@pytest.mark.parametrize("case", sorted(K.EXPECTED, key=lambda c: int(c[1:])))
def test_case_matrix(case):
    assert decide(case).outcome == K.EXPECTED[case]


def test_E1_observation_is_not_evidence():
    obs = K.evidence().observation
    with pytest.raises(TypeError):
        Claim(K.STATEMENT, [obs])


def test_E2_authentic_evidence_without_verification_is_not_support():
    d = decide("C2")
    assert (d.outcome, d.rule) == ("DEFER", "R1")


def test_E3_a_claimed_verification_is_not_a_verification():
    d = decide("C3")
    assert (d.outcome, d.rule) == ("REFUSE", "R2")
    assert decide("C4").outcome == "REFUSE"


def test_E4_not_supported_is_not_refuted():
    assert decide("C5").outcome == "DEFER"
    assert decide("C6").outcome == "REFUSE"


def test_E5_verified_is_not_authorized():
    d = decide("C12")
    assert (d.outcome, d.rule) == ("DEFER", "R6")


def test_E6_deciding_does_not_execute_and_only_allow_executes():
    calls = []
    deferred = decide("C12")
    assert calls == []
    with pytest.raises(PermissionError):
        execute(deferred, lambda: calls.append(1))
    assert calls == []
    assert execute(decide("C1"), lambda: calls.append(1) or "done") == "done"
    assert calls == [1]


def test_E7_authentic_is_not_true_and_hash_is_rechecked():
    assert decide("C17").outcome == "REFUSE"  # authentic evidence, refuted claim
    d = decide("C11")
    assert (d.outcome, d.rule) == ("DEFER", "R5")


def test_E8_record_replays_and_detects_altered_dependencies():
    rec = decide("C1").record
    assert replay(rec) == {"match": True, "mismatches": [], "outcome": "ALLOW"}
    for key in ("observation", "evidence", "claim", "verifier", "verification", "authorization"):
        bad = json.loads(json.dumps(rec))
        dep = bad["dependencies"][key]
        bad["dependencies"][key] = [("0" * 64)] if isinstance(dep, list) else "0" * 64
        assert key in replay(bad)["mismatches"], key


def test_E8_record_is_deterministic_across_processes():
    h1 = digest(decide("C1").record)
    h2 = digest(decide("C1").record)
    code = ("import sys,os; sys.path[:0]=[os.environ.get('EUNOIA_SRC') or 'src','tests/substrate'];"
            "import sub1_cases as K; from eunoia import Gate; from eunoia.substrate import digest;"
            "print(digest(Gate().decide(*K.build('C1')).record))")
    import os, pathlib
    root = pathlib.Path(__file__).resolve().parents[2]
    h3 = subprocess.run([sys.executable, "-c", code], cwd=root, capture_output=True, text=True,
                        check=True, env=os.environ.copy()).stdout.strip()
    assert h1 == h2 == h3


def test_E9_time_matters():
    v = Validity(0, 1000)
    assert v.is_valid_at(999) and not v.is_valid_at(1000) and not v.is_valid_at(-1)
    for case in ("C10", "C15", "C18", "C19"):
        assert decide(case).outcome == "DEFER", case
    with pytest.raises(TypeError):
        Validity(0, 1.5)


def test_E10_unrecognised_status_fails_closed():
    d = decide("C16")
    assert (d.outcome, d.rule) == ("REFUSE", "R9")


def test_crashing_verifier_is_error_not_pass():
    from eunoia import Verifier
    claim = Claim(K.STATEMENT, [K.evidence()])
    r = Verifier("boom", lambda c: 1 / 0).run(claim)
    assert r.status == "ERROR"
    assert Gate().decide(claim, r, K.authorization(), K.ACTION, K.T).outcome == "DEFER"


def test_public_names_are_real_classes():
    for name in eunoia.__all__:
        obj = getattr(eunoia, name)
        assert obj is not None and isinstance(obj, type), name
