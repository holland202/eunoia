#!/usr/bin/env python3
"""SIM-1: fault-injection simulations as registered in research/simulations/SIM1_PREREG.md.

Ground truth lives only in this file's trial functions; the Gate sees observations, never the truth. Effects are
counted on an executor-side log that neither the Gate nor any ledger reads. Simulation only: nothing here is a
claim about a real system.

    python research/simulations/sim1.py              # registered run; exit 0 iff every prediction held
    python research/simulations/sim1.py --sabotage   # A0 runs with no Gate: A0 must come out REFUTED (exit 1)
    python research/simulations/sim1.py --json OUT   # also write per-cell results and their sha256
"""
from __future__ import annotations

import hashlib
import json
import math
import random
import sys
import tempfile
import threading
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from eunoia import Authorization, Claim, Evidence, Gate, Observation, Outcome, Provenance, Verifier  # noqa: E402

# ---- statistics: exact Clopper-Pearson, so a count of 0 is reported as a bound, not as "impossible" ----


def _binom_cdf(k: int, n: int, p: float) -> float:
    return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k + 1))


def clopper_pearson(k: int, n: int, alpha: float = 0.05) -> tuple[float, float]:
    def solve(f, lo=0.0, hi=1.0):
        for _ in range(100):
            mid = (lo + hi) / 2
            lo, hi = (mid, hi) if f(mid) else (lo, mid)
        return (lo + hi) / 2
    lower = 0.0 if k == 0 else solve(lambda p: 1 - _binom_cdf(k - 1, n, p) < alpha / 2)
    upper = 1.0 if k == n else solve(lambda p: _binom_cdf(k, n, p) > alpha / 2)
    return lower, upper


# ---- Scenario A: position against a fence -----------------------------------------------------------------------
R, W, TAU, M, T_DEC, N_A = 100, 5, 6, 8, 100, 400


def _root_observations(e: Evidence) -> list[Observation]:
    if e.observation is not None:
        return [e.observation]
    return [o for p in e.derived_from for o in _root_observations(p)]


def _readings(claim: Claim, at: int) -> list[int]:
    # one reading per evidence item valid at `at` (its first root observation)
    return [_root_observations(e)[0].payload["reading"] for e in claim.evidence if e.is_valid_at(at)]


class Agree(Verifier):
    def check(self, claim, at):
        r = _readings(claim, at)
        return Outcome.SUPPORTED if len(r) >= 2 and max(r) - min(r) <= TAU else Outcome.NOT_SUPPORTED


class Inside(Verifier):
    def check(self, claim, at):
        r = _readings(claim, at)
        if not r:
            return Outcome.NOT_SUPPORTED
        if max(r) <= R - M:
            return Outcome.SUPPORTED
        if min(r) > R + M:
            return Outcome.REFUTED
        return Outcome.NOT_SUPPORTED


class ReadsTheProposer(Verifier):
    """A8c: an evaluator the proposing model can influence. It reads the claim's text, not the evidence."""

    def check(self, claim, at):
        return Outcome.SUPPORTED if "inside" in claim.statement else Outcome.NOT_SUPPORTED


A_CELLS = ("A0", "A1", "A2", "A3a", "A3b", "A4", "A5", "A6", "A6c", "A7", "A7r", "A8", "A8c", "A9")


def _a_decide(cell, seed, t_read, d_at, z, statement, verifiers, at):
    sigma = 8 if cell == "A1" else 2
    noise = [round(sigma * z[0]), round(sigma * z[1])]
    offset = {"A4": (-20, 0), "A5": (-20, -20), "A6": (-20, 0)}.get(cell, (0, 0))
    reading = [d_at(t_read) + noise[i] + offset[i] for i in range(2)]

    def evidence(src, value, tag):
        o = Observation({"source": src, "reading": value, "t": t_read, "trial": f"{seed}{tag}"}, Provenance(src, t_read))
        return Evidence(provenance=Provenance("lab", t_read), valid_from=t_read, valid_until=t_read + W, observation=o)

    gnss = evidence("gnss", reading[0], "g")
    items = [gnss]
    if cell == "A6":
        items.append(evidence("vision", reading[0], "copy"))  # attacker's copy of the spoofed reading, relabelled
    elif cell == "A6c":
        items.append(Evidence(provenance=Provenance("fusion", t_read), valid_from=t_read,
                              valid_until=t_read + W, derived_from=[gnss]))  # the same copy, provenance honest
    elif cell != "A2":
        items.append(evidence("vision", reading[1], "v"))
    claim = Claim(statement, items)
    auth = Authorization(action="advance", claim_id=claim.id, issued_by="operator", valid_from=0, valid_until=1000,
                         required_verifiers=("agree", "inside"), min_independent_roots=2)
    return Gate(verifiers).decide(claim, auth, "advance", at).decision


def a_trial(cell: str, seed: int, sabotage: bool = False) -> dict:
    rng = random.Random(seed)
    d0 = rng.randint(0, 200)
    z = [rng.gauss(0, 1) for _ in range(4)]  # always 4 draws, so every cell sees the same world for a seed
    v = 3 if cell in ("A3a", "A3b", "A7", "A7r") else 0
    d_at = lambda t: d0 + v * (t - T_DEC)  # noqa: E731
    lag = {"A3a": 4, "A3b": 6}.get(cell, 0)
    hallucinating = cell in ("A8", "A8c")
    statement = "the vehicle is inside the fence" if hallucinating else "vehicle within fence"
    verifiers = [Agree("agree"), ReadsTheProposer("inside") if cell == "A8c" else Inside("inside")]
    if cell == "A9" or sabotage:
        decision = "ALLOW"
    else:
        decision = _a_decide(cell, seed, T_DEC - lag, d_at, z[:2], statement, verifiers, T_DEC)
    t_effect = 110 if cell in ("A7", "A7r") else T_DEC
    effect = decision == "ALLOW"
    if effect and cell == "A7r":  # re-check from fresh readings at the moment of the effect
        effect = _a_decide(cell, seed, t_effect, d_at, z[2:], statement, verifiers, t_effect) == "ALLOW"
    return {"decision": decision, "effect": effect, "unsafe": effect and d_at(t_effect) > R}


def run_a(cell: str, sabotage: bool = False) -> dict:
    trials = [a_trial(cell, s, sabotage) for s in range(N_A)]
    u = sum(t["unsafe"] for t in trials)
    return {"n": N_A, "allow": sum(t["decision"] == "ALLOW" for t in trials), "effects": sum(t["effect"] for t in trials),
            "unsafe": u, "unsafe_ci95": clopper_pearson(u, N_A), "decisions": [t["decision"] for t in trials]}


def judge_a(cell: str, r: dict, a0: dict | None) -> bool:
    u, allow, eff = r["unsafe"], r["allow"], r["effects"]
    return {
        "A0": u == 0 and allow > 0,
        "A1": u >= 1,
        "A2": allow == 0,
        "A3a": u >= 1,
        "A3b": allow == 0,
        "A4": u == 0,
        "A5": u >= 1,
        "A6": u >= 1,
        "A6c": allow == 0,
        "A7": u >= 1,
        "A7r": u == 0,
        "A8": a0 is not None and r["decisions"] == a0["decisions"] and u == 0,
        "A8c": u >= 1,
        "A9": u >= 100,
    }[cell] and eff <= allow


# ---- Scenario B: non-idempotent effects --------------------------------------------------------------------------
N_B, THREADS = 50, 8


class Always(Verifier):
    def check(self, claim, at):
        return Outcome.SUPPORTED


def run_b1() -> dict:
    effects = []
    for i in range(N_B):
        o1 = Observation({"intent": i, "balance": 500}, Provenance("ledger-a", 0))
        o2 = Observation({"intent": i, "balance": 500}, Provenance("ledger-b", 0))
        claim = Claim(f"transfer {i} is covered", [Evidence(provenance=Provenance("bank", 0), valid_from=0, valid_until=100,
                                                            observation=o) for o in (o1, o2)])
        auth = Authorization(action="transfer", claim_id=claim.id, issued_by="ops", valid_from=0, valid_until=100,
                             required_verifiers=("funds",), min_independent_roots=2)
        gate = Gate([Always("funds")])
        effects.append(sum(gate.decide(claim, auth, "transfer", 10).decision == "ALLOW" for _ in range(2)))
    return {"n": N_B, "effects_per_intent": sorted(set(effects)), "intents_with_2": effects.count(2)}


def _sv():
    try:
        from sovereign_veritas.capability import Capability
        from sovereign_veritas.evidence import Ledger, LedgerSink
        from sovereign_veritas.idempotency import FileReservations, ReservationRefused
        from sovereign_veritas.interfaces.contracts import ActionProposal, Prediction
        from sovereign_veritas.runtime import RuntimeState
        from sovereign_veritas.workflow import EvidenceWorkflow
    except ImportError:
        return None
    return locals()


class _Stubs:
    def observe(self):
        return "obs"

    def predict(self, o):
        from sovereign_veritas.interfaces.contracts import Prediction
        return Prediction(value="transfer", uncertainty=0.0, model_id="scripted")

    def verify(self, o, p):
        return {"status": "PASS"}


def _workflow(sv, effect_log, lock, sink, store):
    class Executor:
        def execute(self, action):
            with lock:
                effect_log.append(action.parameters["intent"])
            return "done"
    s = _Stubs()
    return sv["EvidenceWorkflow"](sensor=s, predictor=s, verifier=s, executor=Executor(), evidence_sink=sink,
                                  reservations=store)


def _run_wf(sv, wf, record_id, intent, key):
    return wf.run(record_id=record_id, input_digest="sim1", capability=sv["Capability"]("transfer", authorized=True),
                  runtime=sv["RuntimeState"]("sim", "3"),
                  action=sv["ActionProposal"](capability="transfer", requested="transfer", parameters={"intent": intent}),
                  idempotency_key=key)


class LockedSink:
    def __init__(self, sv, fail=False):
        self.inner, self.lock, self.fail = sv["LedgerSink"](sv["Ledger"]()), threading.Lock(), fail

    def has_record(self, rid):
        with self.lock:
            return self.inner.has_record(rid)

    def record(self, rec):
        if self.fail:
            raise OSError("simulated ledger write failure")
        with self.lock:
            return self.inner.record(rec)

    def intents(self):
        return [r.action["parameters"]["intent"] for r in self.inner.ledger.all() if r.action]


def run_b2(fresh_key_per_thread: bool) -> dict | None:
    sv = _sv()
    if sv is None:
        return None
    log, lock = [], threading.Lock()
    with tempfile.TemporaryDirectory() as tmp:
        store = sv["FileReservations"](Path(tmp) / "res")
        sink = LockedSink(sv)
        for i in range(N_B):
            barrier = threading.Barrier(THREADS)

            def attempt(t, i=i, barrier=barrier):
                wf = _workflow(sv, log, lock, sink, store)
                barrier.wait()
                try:
                    _run_wf(sv, wf, f"b2-{i}-{t}", i, f"intent-{i}-{t}" if fresh_key_per_thread else f"intent-{i}")
                except sv["ReservationRefused"]:
                    pass
            threads = [threading.Thread(target=attempt, args=(t,)) for t in range(THREADS)]
            for th in threads:
                th.start()
            for th in threads:
                th.join()
    counts = [log.count(i) for i in range(N_B)]
    dup = sum(c > 1 for c in counts)
    return {"n": N_B, "threads": THREADS, "intents_duplicated": dup, "dup_ci95": clopper_pearson(dup, N_B),
            "effects_per_intent": sorted(set(counts))}


def run_b3(sink_fails: bool) -> dict | None:
    sv = _sv()
    if sv is None:
        return None
    log, lock = [], threading.Lock()
    with tempfile.TemporaryDirectory() as tmp:
        store = sv["FileReservations"](Path(tmp) / "res")
        sink = LockedSink(sv, fail=sink_fails)
        for i in range(N_B):
            try:
                _run_wf(sv, _workflow(sv, log, lock, sink, store), f"b3-{i}", i, f"b3-intent-{i}")
            except OSError:
                pass
        recorded = set(sink.intents())
    unrecorded = [i for i in log if i not in recorded]  # the independent observer: effect log vs ledger
    return {"n": N_B, "effects": len(log), "effects_without_record": len(unrecorded), "observer_flags": len(unrecorded)}


# ---- Scenario C: records and authority ---------------------------------------------------------------------------
N_C = 50


class ConsentAgreed(Verifier):
    def check(self, claim, at):
        vals = [_root_observations(e)[0].payload["consent"] for e in claim.evidence]
        return Outcome.SUPPORTED if all(v is True for v in vals) else Outcome.NOT_SUPPORTED


class AnyConsent(Verifier):
    def check(self, claim, at):
        vals = [_root_observations(e)[0].payload["consent"] for e in claim.evidence]
        return Outcome.SUPPORTED if any(v is True for v in vals) else Outcome.NOT_SUPPORTED


def run_c(cell: str) -> dict:
    allows = 0
    for i in range(N_C):
        conflicting = cell in ("C3", "C3c")
        obs = [Observation({"record": i, "consent": True}, Provenance("registry-a", 0)),
               Observation({"record": i, "consent": not conflicting}, Provenance("registry-b", 0))]
        claim = Claim(f"record {i} may be released", [Evidence(provenance=Provenance("clerk", 0), valid_from=0,
                                                               valid_until=1000, observation=o) for o in obs])
        other = Claim(f"record {i + 1000} may be released", [Evidence(provenance=Provenance("clerk", 0), valid_from=0,
                                                                      valid_until=1000, observation=obs[0])])
        auth = Authorization(action="release_record", claim_id=(other if cell == "C2" else claim).id, issued_by="dpo",
                             valid_from=0, valid_until=50 if cell == "C1" else 1000,
                             required_verifiers=("consent",), min_independent_roots=2)
        verifier = AnyConsent("consent") if cell == "C3c" else ConsentAgreed("consent")
        allows += Gate([verifier]).decide(claim, auth, "release_record", 100).decision == "ALLOW"
    return {"n": N_C, "allow": allows}


# ---- runner ------------------------------------------------------------------------------------------------------


def main() -> int:
    sabotage = "--sabotage" in sys.argv
    out, results, verdicts = None, {}, {}
    if "--json" in sys.argv:
        out = sys.argv[sys.argv.index("--json") + 1]
    a0 = None
    for cell in A_CELLS:
        r = run_a(cell, sabotage=sabotage and cell == "A0")
        if cell == "A0":
            a0 = r
        verdicts[cell] = judge_a(cell, r, a0)
        lo, hi = r["unsafe_ci95"]
        print(f"  {cell:<4} N={r['n']} ALLOW={r['allow']:<3} effects={r['effects']:<3} unsafe={r['unsafe']:<3} "
              f"95% CI [{lo:.4f}, {hi:.4f}]  {'HELD' if verdicts[cell] else 'REFUTED'}")
        results[cell] = {k: v for k, v in r.items() if k != "decisions"}
    b1 = run_b1()
    verdicts["B1"] = b1["intents_with_2"] == N_B
    results["B1"] = b1
    print(f"  B1   N={N_B} effects per intent {b1['effects_per_intent']}  {'HELD' if verdicts['B1'] else 'REFUTED'}")
    for cell, fn, judge in (("B2", lambda: run_b2(False), lambda r: r["intents_duplicated"] == 0),
                            ("B2c", lambda: run_b2(True), lambda r: r["intents_duplicated"] >= 1),
                            ("B3", lambda: run_b3(True), lambda r: r["effects_without_record"] == N_B
                             and r["observer_flags"] == N_B),
                            ("B3c", lambda: run_b3(False), lambda r: r["observer_flags"] == 0)):
        r = fn()
        if r is None:
            print(f"  {cell:<4} NOT RUN (sovereign_veritas not importable)")
            continue
        verdicts[cell] = judge(r)
        results[cell] = r
        print(f"  {cell:<4} {json.dumps(r, sort_keys=True)}  {'HELD' if verdicts[cell] else 'REFUTED'}")
    for cell, expect in (("C1", 0), ("C2", 0), ("C3", 0), ("C3c", N_C)):
        r = run_c(cell)
        verdicts[cell] = r["allow"] == expect
        results[cell] = r
        print(f"  {cell:<4} N={N_C} ALLOW={r['allow']}  {'HELD' if verdicts[cell] else 'REFUTED'}")
    digest = hashlib.sha256(json.dumps(results, sort_keys=True).encode()).hexdigest()
    held = sum(verdicts.values())
    print(f"mode: {'SABOTAGE (A0 has no Gate)' if sabotage else 'registered'}")
    print(f"RESULTS_SHA256 {digest}")
    print(f"VERDICT  {held} of {len(verdicts)} as registered")
    if out:
        Path(out).write_text(json.dumps({"results": results, "verdicts": verdicts, "sha256": digest}, indent=1,
                                        sort_keys=True) + "\n")
    return 0 if held == len(verdicts) else 1


if __name__ == "__main__":
    sys.exit(main())
