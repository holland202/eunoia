#!/usr/bin/env python3
"""substrate_mutants.py - V001 P10: switch off each guard of the v0.01 substrate in turn; the tests must fail.

Each mutant is applied to a temporary copy of the repository (never to the working tree), then
`python -m pytest -q tests/substrate` runs there. KILLED = at least one test failed. A guard whose
mutant SURVIVES is one no test can see.

    python tools/substrate_mutants.py            # exit 0 only if every reachable mutant is killed
    python tools/substrate_mutants.py --sabotage # adds a no-op "mutant": it must SURVIVE, or the runner is broken
"""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
G = "src/eunoia/governance/__init__.py"
E = "src/eunoia/evidence/__init__.py"
V = "src/eunoia/verification/__init__.py"
C = "src/eunoia/continuity/__init__.py"
K = "src/eunoia/_canon.py"

# (name, file, exact source text, replacement). Each source text must occur exactly once.
MUTANTS = [
    ("rule1 time type", G, 'refuse.append("malformed:time")', "pass"),
    ("rule1 claim type", G, 'refuse.append("malformed:claim")', "pass"),
    ("rule1 authorization type", G, 'refuse.append("malformed:authorization")', "pass"),
    ("rule2 no authorization", G, 'refuse.append("no_authorization")', "return _decision('ALLOW', [], [], action, at, claim, None, (), None)"),
    ("rule3 claim mismatch", G, 'refuse.append("authorization_claim_mismatch")', "pass"),
    ("rule4 action scope", G, 'refuse.append("authorization_scope")', "pass"),
    ("rule5 authorization time", G, 'refuse.append("authorization_not_valid_at_time")', "pass"),
    ("rule6 verifier unavailable", G, 'defer.append(f"verifier_unavailable:{vid}")', "pass"),
    ("rule6 refuted", G, 'refuse.append(f"verification_refuted:{vid}")', "pass"),
    ("rule6 not supported", G, 'defer.append(f"not_supported:{vid}")', "pass"),
    ("rule6 error", G, '''            elif result.outcome is Outcome.ERROR:
                defer.append(f"verification_error:{vid}")''', '''            elif result.outcome is Outcome.ERROR:
                pass'''),
    ("rule6 unknown outcome (unreachable)", G, '''            elif result.outcome is not Outcome.SUPPORTED:  # unreachable today; guards Outcome additions
                defer.append(f"verification_error:{vid}")''', '''            elif result.outcome is not Outcome.SUPPORTED:  # unreachable today; guards Outcome additions
                pass'''),
    ("rule6 unbound verify", G, "result = Verifier.verify(verifier, claim, at)", "result = verifier.verify(claim, at)"),
    ("rule7 budget", G, 'defer.append("evidence_budget_exceeded")', "pass"),
    ("rule7 independence", G, "if k is not None and k < authorization.min_independent_roots:", "if False:"),
    ("verdict DEFER", G, 'verdict = "REFUSE" if refuse else "DEFER" if defer else "ALLOW"', 'verdict = "REFUSE" if refuse else "ALLOW"'),
    ("auth needs a verifier", G, '''        if not req:
            raise ValueError''', '''        if False:
            raise ValueError'''),
    ("auth needs >= 1 root", G, "or min_independent_roots < 1:", "or min_independent_roots < 0:"),
    ("auth bool roots", G, "if isinstance(min_independent_roots, bool) or not", "if not"),
    ("evidence own interval", E, "return self.valid_from <= t < self.valid_until and all(", "return all("),
    ("evidence ancestors (Amendment 1)", E, "and all(p.is_valid_at(t) for p in self.derived_from)", ""),
    ("claim refuses observation", E, '_need(e, Evidence, "claim evidence item")', "pass"),
    ("claim needs evidence", E, '''        if not items:
            raise ValueError''', '''        if False:
            raise ValueError'''),
    ("verify: exception is ERROR", V, "outcome=Outcome.ERROR, detail=f\"raised", "outcome=Outcome.SUPPORTED, detail=f\"raised"),
    ("verify: non-Outcome is ERROR", V, "if not isinstance(out, Outcome):", "if False:"),
    ("independence: disjointness", C, "if roots[i] & used:", "if False:"),
    ("independence: budget", C, "if len(items) > max_items:", "if False:"),
    ("seal after id (A4)", K, 'if "id" in self.__dict__:', "if False:"),
]
UNREACHABLE = {"rule6 unknown outcome (unreachable)"}
SABOTAGE = ("no-op (sabotage control)", G, "from __future__ import annotations", "from __future__ import annotations")


def run(mutant):
    name, rel, old, new = mutant
    with tempfile.TemporaryDirectory() as tmp:
        dst = Path(tmp) / "repo"
        shutil.copytree(ROOT, dst, ignore=shutil.ignore_patterns(".git", "__pycache__", ".pytest_cache"))
        path = dst / rel
        src = path.read_text(encoding="utf-8")
        if src.count(old) != 1:
            return "COULD NOT APPLY"
        path.write_text(src.replace(old, new), encoding="utf-8")
        p = subprocess.run([sys.executable, "-m", "pytest", "-q", "-x", "-p", "no:cacheprovider", "tests/substrate"],
                           cwd=dst, capture_output=True, text=True)
        return "SURVIVED" if p.returncode == 0 else "KILLED"


def main():
    mutants = MUTANTS + ([SABOTAGE] if "--sabotage" in sys.argv else [])
    survived, broken = [], []
    for m in mutants:
        verdict = run(m)
        print(f"  {m[0]:<40} {verdict}")
        if verdict == "COULD NOT APPLY":
            broken.append(m[0])
        elif verdict == "SURVIVED" and m[0] not in UNREACHABLE:
            survived.append(m[0])
    reachable = len(MUTANTS) - len(UNREACHABLE)
    killed = reachable - len([s for s in survived if s != SABOTAGE[0]]) - len(broken)
    print(f"VERDICT  {killed} of {reachable} reachable guards killed, {len(UNREACHABLE)} listed as unreachable, "
          f"{len(survived)} survived, {len(broken)} could not apply")
    sys.exit(1 if survived or broken else 0)


if __name__ == "__main__":
    main()
