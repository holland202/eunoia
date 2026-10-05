#!/usr/bin/env python3
"""SUB-1 harness (registration docs/SUB1_PREREG.md). Prints HELD/REFUTED per prediction, VERDICT, DIGEST.

  python tools/sub1_run.py              the registered run
  python tools/sub1_run.py --sabotage   gate replaced by the rival naive_gate: the verdict must differ (exit 1)
  python tools/sub1_run.py --json PATH  also write the results JSON
"""
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "tests" / "substrate")]
sys.dont_write_bytecode = True

import eunoia  # noqa: E402
import sub1_cases as K  # noqa: E402
from eunoia import Gate, replay  # noqa: E402
from eunoia.substrate import digest  # noqa: E402

SABOTAGE = "--sabotage" in sys.argv
CASES = sorted(K.EXPECTED, key=lambda c: int(c[1:]))
BASE = "bf437b0"
RECORDED = None  # pinned after the registered run: (held tuple, digest)

MUTANTS = {
    "M_E1": ("if not isinstance(e, Evidence):  # E1", "if False:  # E1"),
    "M_E2": ('    r = v["verification"]\n',
             '    r = v["verification"]\n'
             '    if r is None and v["evidence"] and all(e["state"] == "AUTHENTIC" for e in v["evidence"]):\n'
             '        r, v = {"claim_id": v["claim_id"], "status": "SUPPORTED", "verifier_id": None}, dict(v, issued=True)\n'),
    "M_E3": ('if not v["issued"] or r["claim_id"] != v["claim_id"]:', 'if r["claim_id"] != v["claim_id"]:'),
    "M_E4": ('return "DEFER", "R3", "claim not supported"', 'return "REFUSE", "R3", "claim not supported"'),
    "M_E5": ('return "DEFER", "R6", "no authorization"', 'return "ALLOW", "R6", "no authorization"'),
    "M_E6": ('if decision.outcome != "ALLOW":', "if False:"),
    "M_E7": ('if not e["intact"]:', "if False:"),
    "M_E8": ("if recomputed.get(key) != want:", "if False:"),
    "M_E9": ("return self.valid_from <= t < self.valid_until", "return self.valid_from <= t"),
    "M_E10": ('return "REFUSE", "R9", f"unrecognised', 'return "ALLOW", "R9", f"unrecognised'),
    "M0": None,
}


def naive_gate(claim, result, authorization, action, t):
    """The registered rival: ALLOW iff a SUPPORTED result and a granted authorization exist, else REFUSE."""
    ok = result is not None and result.status == "SUPPORTED" and authorization is not None and authorization.granted
    return "ALLOW" if ok else "REFUSE"


def gate_outcome(case, gate):
    args = K.build(case)
    return gate(*args) if gate is naive_gate else Gate().decide(*args).outcome


def run_mutant(name):
    tmp = pathlib.Path(tempfile.mkdtemp())
    try:
        shutil.copytree(ROOT / "src", tmp / "src")
        target = tmp / "src" / "eunoia" / "substrate.py"
        if MUTANTS[name] is not None:
            old, new = MUTANTS[name]
            text = target.read_text(encoding="utf-8")
            if text.count(old) != 1:
                return "HARNESS_ERROR"  # anchor missing or ambiguous: never reported as SURVIVED
            target.write_text(text.replace(old, new), encoding="utf-8")
        env = dict(os.environ, EUNOIA_SRC=str(tmp / "src"), PYTHONDONTWRITEBYTECODE="1")
        p = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "tests/substrate"],
                           cwd=ROOT, env=env, capture_output=True, text=True)
        return "KILLED" if p.returncode != 0 else "SURVIVED"
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def record_checks():
    rec = Gate().decide(*K.build("C1")).record
    h1, h2 = digest(rec), digest(Gate().decide(*K.build("C1")).record)
    code = ("import sys; sys.path[:0]=['src','tests/substrate']; import sub1_cases as K; from eunoia import Gate;"
            "from eunoia.substrate import digest; print(digest(Gate().decide(*K.build('C1')).record))")
    h3 = subprocess.run([sys.executable, "-c", code], cwd=ROOT, capture_output=True, text=True,
                        check=True).stdout.strip()
    rp = replay(rec)
    caught = {}
    for key in ("observation", "evidence", "claim", "verifier", "verification", "authorization"):
        bad = json.loads(json.dumps(rec))
        dep = bad["dependencies"][key]
        bad["dependencies"][key] = ["0" * 64] if isinstance(dep, list) else "0" * 64
        caught[key] = key in replay(bad)["mismatches"]
    return {"hash_in_process": [h1, h2], "hash_subprocess": h3, "replay": rp, "tamper_caught": caught}


def placeholder_checks():
    src = subprocess.run(["git", "show", f"{BASE}:src/eunoia/__init__.py"], cwd=ROOT, capture_output=True,
                         text=True)
    ns = {}
    if src.returncode == 0:
        exec(compile(src.stdout, f"{BASE}:__init__.py", "exec"), ns)
    before_none = src.returncode == 0 and ns.get("Gate", "missing") is None
    after = {n: isinstance(getattr(eunoia, n), type) for n in eunoia.__all__}
    return {"base_found": src.returncode == 0, "base_gate_is_none": before_none, "after_all_classes": after}


def old_tests():
    p = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "tests/invariants"],
                       cwd=ROOT, capture_output=True, text=True)
    last = [ln for ln in p.stdout.splitlines() if ln.strip()][-1]
    return {"returncode": p.returncode, "summary": last.split(" in ")[0]}


def main():
    gate = naive_gate if SABOTAGE else None
    print(f"SUB-1 | {'SABOTAGE: gate replaced by naive_gate' if SABOTAGE else 'registered run'} | python "
          f"{sys.version.split()[0]} | {sys.platform}")
    decisions = {c: gate_outcome(c, gate) for c in CASES}
    rival = {c: gate_outcome(c, naive_gate) for c in CASES}
    mutants = {m: run_mutant(m) for m in MUTANTS}
    rec, ph, old = record_checks(), placeholder_checks(), old_tests()

    for c in CASES:
        print(f"  {c:<4} expected {K.EXPECTED[c]:<6} gate {decisions[c]:<6} rival {rival[c]}")
    for m, o in mutants.items():
        print(f"  {m:<6} {o}")
    print(f"  C1 record sha256 {rec['hash_in_process'][0]} | subprocess {rec['hash_subprocess']}")
    print(f"  replay {rec['replay']} | tamper caught {rec['tamper_caught']}")
    print(f"  at {BASE}: found {ph['base_found']}, Gate is None {ph['base_gate_is_none']} | now classes "
          f"{sum(ph['after_all_classes'].values())} of {len(ph['after_all_classes'])}")
    print(f"  pre-existing tests: {old['summary']} (exit {old['returncode']})")

    match = [c for c in CASES if decisions[c] == K.EXPECTED[c]]
    rival_match = {c for c in CASES if rival[c] == K.EXPECTED[c]}
    rival_bad_allow = {c for c in CASES if rival[c] == "ALLOW" and K.EXPECTED[c] != "ALLOW"}
    v = {
        "P1": len(match) == 19,
        "P2": rival_match == {"C1", "C6", "C13", "C16", "C17"}
              and rival_bad_allow == {"C3", "C4", "C8", "C9", "C10", "C11", "C14", "C15", "C18", "C19"},
        "P3": all(mutants[m] == "KILLED" for m in MUTANTS if m != "M0"),
        "P4": mutants["M0"] == "SURVIVED",
        "P5": (len(set(rec["hash_in_process"] + [rec["hash_subprocess"]])) == 1
               and rec["replay"] == {"match": True, "mismatches": [], "outcome": "ALLOW"}
               and all(rec["tamper_caught"].values()) and len(rec["tamper_caught"]) == 6),
        "P6": ph["base_gate_is_none"] and all(ph["after_all_classes"].values()),
        "P7": old["returncode"] == 0 and old["summary"] == "15 passed",
    }
    print(f"  P1 gate matches expected on {len(match)} of 19")
    print(f"  P2 rival matches {sorted(rival_match, key=lambda c: int(c[1:]))}; wrong ALLOW on "
          f"{sorted(rival_bad_allow, key=lambda c: int(c[1:]))}")
    print()
    for k, held in v.items():
        print(f"  {k}  {'HELD' if held else 'REFUTED'}")
    held = tuple(k for k, x in v.items() if x)
    print(f"VERDICT {len(held)} of {len(v)} as registered (P8 is CI; P9 is the unrun door)")
    results = {"decisions": decisions, "rival": rival, "mutants": mutants,
               "c1_record_sha256": rec["hash_subprocess"], "replay": rec["replay"],
               "tamper_caught": rec["tamper_caught"], "verdicts": v}
    dg = digest(results)
    print(f"DIGEST {dg}")
    if "--json" in sys.argv:
        pathlib.Path(sys.argv[sys.argv.index("--json") + 1]).write_text(
            json.dumps(results, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    if RECORDED is None:
        return 0 if all(v.values()) else 1
    return 0 if (held, dg) == RECORDED else 1


if __name__ == "__main__":
    sys.exit(main())
