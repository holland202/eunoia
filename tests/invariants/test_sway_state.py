"""research/sway/state.json must satisfy schemas/sway.schema.json, and the schema must reject an
OPEN item marked settled without evidence (anti-vacuity: until 2026-09-30 it accepted that)."""
import copy, json, pathlib

import pytest

jsonschema = pytest.importorskip("jsonschema")
ROOT = pathlib.Path(__file__).resolve().parents[2]
SCHEMA = json.loads((ROOT / "schemas/sway.schema.json").read_text())
STATE = json.loads((ROOT / "research/sway/state.json").read_text())


def valid(doc):
    try:
        jsonschema.validate(doc, SCHEMA)
        return True
    except jsonschema.ValidationError:
        return False


def test_state_is_valid():
    assert valid(STATE)


@pytest.mark.parametrize("mutate", [
    lambda d: d["observations"][0].update(status="RESOLVED"),
    lambda d: d["predictions"][0].update(status="HELD"),
    lambda d: d["items"][0].update(status="VALIDATED"),
    lambda d: d.update(status="VALIDATED"),
])
def test_settling_without_evidence_is_rejected(mutate):
    d = copy.deepcopy(STATE)
    mutate(d)
    assert not valid(d)


def test_settling_with_evidence_is_accepted():
    d = copy.deepcopy(STATE)
    d["predictions"][0].update(status="HELD", evidence="commit abc1234, output pasted in P5_RESULTS.md")
    assert valid(d)
