#!/usr/bin/env python3
"""SUB-2 harness (registration docs/SUB2_PREREG.md). Prints HELD/REFUTED per P1-P5, VERDICT, DIGEST.

  python tools/sub2_run.py              the registered run
  python tools/sub2_run.py --sabotage   detector pointed at SUB-1's src/ in place of the current one (must exit 1)
SUB-1's own harness is not in this tree any more; CI runs it at fb5194a in a separate worktree (P6).
"""
import io
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tarfile
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "tests" / "substrate"), str(ROOT / "tools")]
sys.dont_write_bytecode = True

import sub1_cases as K  # noqa: E402
import sub2_no_rules  # noqa: E402
from eunoia import Gate, replay  # noqa: E402
from eunoia.substrate import digest  # noqa: E402
from oracle import OracleGate  # noqa: E402

SABOTAGE = "--sabotage" in sys.argv
SUB1 = "fb5194a"
RECORDED = (("P1", "P2", "P3", "P4", "P5"),
            "2c04d80e5dd249cce1c578a6d825fb38965c21f0570fa8c2cdec307e3f5a8e87")  # registered run, 7220163

# SUB-1's mutant edits, byte-identical (tools/sub1_run.py at fb5194a). Each is applied to whichever of
# FILES holds its anchor; the anchor must occur exactly once across both.
FILES = ("src/eunoia/substrate.py", "tests/substrate/oracle.py")
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


def sub1_src():
    tmp = pathlib.Path(tempfile.mkdtemp())
    data = subprocess.run(["git", "archive", SUB1, "src"], cwd=ROOT, capture_output=True, check=True).stdout
    with tarfile.open(fileobj=io.BytesIO(data)) as tf:
        tf.extractall(tmp, **({"filter": "data"} if hasattr(tarfile, "data_filter") else {}))
    return tmp / "src"


def run_mutant(name):
    tmp = pathlib.Path(tempfile.mkdtemp())
    try:
        for part in ("src", "tests"):
            shutil.copytree(ROOT / part, tmp / part, ignore=shutil.ignore_patterns("__pycache__"))
        shutil.copy(ROOT / "pyproject.toml", tmp / "pyproject.toml")
        where = None
        if MUTANTS[name] is not None:
            old, new = MUTANTS[name]
            counts = {f: (tmp / f).read_text(encoding="utf-8").count(old) for f in FILES}
            if sum(counts.values()) != 1:
                return "HARNESS_ERROR", None
            where = next(f for f, c in counts.items() if c)
            text = (tmp / where).read_text(encoding="utf-8")
            (tmp / where).write_text(text.replace(old, new), encoding="utf-8")
        env = {k: v for k, v in os.environ.items() if k != "EUNOIA_SRC"}
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        p = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "tests/substrate"],
                           cwd=tmp, env=env, capture_output=True, text=True)
        return ("KILLED" if p.returncode != 0 else "SURVIVED"), where
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def pytest_summary(path):
    p = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", path], cwd=ROOT,
                       capture_output=True, text=True)
    last = [ln for ln in p.stdout.splitlines() if ln.strip()][-1]
    return p.returncode, last.split(" in ")[0]


def main():
    print(f"SUB-2 | {'SABOTAGE: detector pointed at SUB-1 src' if SABOTAGE else 'registered run'} | python "
          f"{sys.version.split()[0]} | {sys.platform}")
    old_src = sub1_src()
    old_hits = sub2_no_rules.hits(old_src)
    now_hits = sub2_no_rules.hits(old_src if SABOTAGE else ROOT / "src")
    shutil.rmtree(old_src.parent, ignore_errors=True)
    print(f"  detector at {SUB1}: {len(old_hits)} hits in {sorted({h[0] for h in old_hits})}; now: {len(now_hits)}")

    try:
        Gate()
        abstract = False
    except TypeError:
        abstract = True
    decisions = {c: OracleGate().decide(*K.build(c)).outcome for c in sorted(K.EXPECTED, key=lambda c: int(c[1:]))}
    matched = sum(decisions[c] == K.EXPECTED[c] for c in decisions)
    print(f"  Gate() abstract: {abstract} | OracleGate matrix {matched} of {len(decisions)}")

    mutants = {m: run_mutant(m) for m in MUTANTS}
    for m, (o, where) in mutants.items():
        print(f"  {m:<6} {o:<8} {where or '-'}")

    class AlwaysDefer(Gate):
        rule_set = "always_defer"

        def rules(self, view):
            return "DEFER", "X", "always"
    rec = OracleGate().decide(*K.build("C1")).record
    rp_ok = replay(rec, OracleGate())
    rp_other = replay(rec, AlwaysDefer())
    caught = {}
    for key in ("observation", "evidence", "claim", "verifier", "verification", "authorization"):
        bad = json.loads(json.dumps(rec))
        dep = bad["dependencies"][key]
        bad["dependencies"][key] = ["0" * 64] if isinstance(dep, list) else "0" * 64
        caught[key] = key in replay(bad, OracleGate())["mismatches"]
    print(f"  replay oracle {rp_ok} | always_defer {rp_other['mismatches']} | tamper caught {sum(caught.values())} of 6")

    inv = pytest_summary("tests/invariants")
    sub = pytest_summary("tests/substrate")
    print(f"  tests/invariants: {inv[1]} (exit {inv[0]}) | tests/substrate: {sub[1]} (exit {sub[0]})")

    n_sub = int(sub[1].split()[0]) if sub[1].split()[0].isdigit() else 0
    v = {
        "P1": len(old_hits) == 14 and {h[0] for h in old_hits} == {"eunoia/substrate.py"} and len(now_hits) == 0,
        "P2": abstract and matched == 19,
        "P3": all(mutants[m][0] == "KILLED" for m in MUTANTS if m != "M0") and mutants["M0"][0] == "SURVIVED",
        "P4": (rp_ok == {"match": True, "mismatches": [], "outcome": "ALLOW"}
               and {"rule_set", "decision"} <= set(rp_other["mismatches"]) and all(caught.values())),
        "P5": inv == (0, "15 passed") and sub[0] == 0 and n_sub >= 32,
    }
    print()
    for k, held in v.items():
        print(f"  {k}  {'HELD' if held else 'REFUTED'}")
    held = tuple(k for k, x in v.items() if x)
    print(f"VERDICT {len(held)} of {len(v)} as registered (P6 is CI; P7 is the unrun door)")
    results = {"detector_sub1": [list(h) for h in old_hits], "detector_now": [list(h) for h in now_hits],
               "gate_abstract": abstract, "oracle_decisions": decisions,
               "mutants": {m: list(x) for m, x in mutants.items()}, "c1_record_sha256": digest(rec),
               "replay_oracle": rp_ok, "replay_always_defer": rp_other, "tamper_caught": caught,
               "verdicts": v}
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
