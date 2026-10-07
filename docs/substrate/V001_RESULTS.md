# V001 results — Eunoia v0.01 substrate

Registration: [`V001_PREREG.md`](V001_PREREG.md) (`7a07b2d`, committed alone), Amendment 1
[`V001_AMENDMENT_1.md`](V001_AMENDMENT_1.md) (`cd264f0`, before any code ran). Implementation
`edefb36`. Linux x86_64 container, Python 3.13.16. **NOT VALIDATED on the S25.**

**Provenance.** Claude (Opus 5.5) wrote the registration, the code, the tests, the mutant runner,
the attacks and this report, during a cross-repository review Chad Holland requested. Every result
below is **self-tested**: the instrument's designer judged it. No human has reviewed it line by
line; no second model has reviewed it.

## What went wrong, first

- **P10 is REFUTED as registered.** The registration said "refuted if any guard survives". One does:
  the defensive branch `elif result.outcome is not Outcome.SUPPORTED` in rule 6. It cannot be
  reached, since all four `Outcome` members are handled above it, so switching it off changes
  nothing a test can see. The registration did not exempt unreachable branches, so the verdict
  stands as REFUTED. The branch is kept, not deleted to flip the result. Every reachable guard is
  killed (below).
- **The registration had a hole, closed before anything ran.** As registered, a derived evidence
  item had its own validity interval, so stale evidence could be laundered into fresh evidence by
  one derivation. Found while writing the code; Amendment 1 (ancestors' validity is inherited) was
  committed before any test executed. P13 tests it.
- **A defect found after the registered run (self-attack A4).** `Frozen._set`, the constructor's
  internal setter, still worked after construction: `o._set("provenance", …)` changed a field and
  left `o.id` naming content the object no longer had. Fixed by sealing the setter once `id`
  exists; regression test `test_constructed_objects_cannot_be_reset_through_the_internal_setter`
  failed before the fix and passes after. Python's `object.__setattr__` still bypasses this: none of
  it is a security boundary against code in the same process (registration, "What this is not").
- **All registered predictions except P10 held on the first run.** That is agreement between a
  designer and his own instrument, not evidence the substrate is right; P10's mutants are the only
  evidence here that the tests can fail at all.

## Outcome

| ID | Invariant | Result |
|---|---|---|
| P1 | E1, E3 | **HELD.** `Observation` refused as claim evidence, as an `Evidence.observation` value and in `derived_from`; empty claim refused; non-`Claim` → REFUSE `malformed:claim` (4 inputs); non-`Authorization` (3) and non-int time (4) refuse |
| P2 | E4 | **HELD.** `NOT_SUPPORTED` → DEFER `not_supported:v1`; `REFUTED` → REFUSE `verification_refuted:v1`; `ERROR` → DEFER `verification_error:v1` |
| P3 | E5 | **HELD.** No authorization, another claim's, another action's, and outside its interval (3 times) all REFUSE; verifiers are not called under a refused authorization |
| P4 | E9 | **HELD.** Evidence on `[10, 20)`: DEFER at 9, ALLOW at 10 and 19, DEFER at 20 |
| P5 | E8 | **HELD.** Two evidence items over one observation → 1 line, DEFER `1<2`; a second observation → ALLOW. Two derivations of one source → 1. `independent_roots` is exact where largest-first greedy is not (`[{a,b}, {a}, {b}]` → 2). 13 items → DEFER `evidence_budget_exceeded` |
| P6 | Gate runs verifiers | **HELD.** Raising, returning `"SUPPORTED"`, `True`, `None` or `"Outcome.SUPPORTED"` → DEFER `verification_error`. A subclass overriding `verify()` to return a forged SUPPORTED, while its `check()` says REFUTED, gets REFUSE. `decide()` takes only `claim, authorization, action, at` |
| P7 | E8 record | **HELD.** 6 decisions (ALLOW, 3 REFUSE kinds, REFUTED, nested derivation) and all 128 of P9: `check_record` finds no dangling id and no cycle; ids identical across runs. `check_record` can fail: a changed payload, a deleted node, an added cycle and a relabelled decision are each reported |
| P8 | E7 (limit) | **HELD, as expected.** A fabricated observation ("the moon is made of cheese") that the registered verifier supports → ALLOW. The substrate checks structure, integrity and time, not truth |
| P9 | E10 | **HELD.** 2⁷ = 128 fault combinations; ALLOW in exactly one, the all-healthy one |
| P10 | anti-vacuity | **REFUTED as registered** (see above). 26 of 26 reachable guards killed, 1 unreachable survives. After the A4 fix the seal was added as a 27th guard: **27 of 27 reachable killed**. `--sabotage` adds a no-op mutant, which survives as it must |
| P13 | Amendment 1 | **HELD.** Source valid `[0, 10)`, derivation claims `[0, 100)`: ALLOW at 5, DEFER at 50 |
| P11, P12 | — | **Not run** (registered as left unrun) |

## Raw output

Pre-change (`src/` at `bf437b0`, new tests present): `ERROR tests/substrate/test_v001.py ... 1 error
during collection`: none of the new tests can run against the skeleton.

Registered run: `65 passed in 0.23s` (15 pre-existing, 50 new). After the A4 fix: `66 passed`.

Mutants (`python tools/substrate_mutants.py`, final):

```
  rule1 time type                          KILLED
  rule1 claim type                         KILLED
  rule1 authorization type                 KILLED
  rule2 no authorization                   KILLED
  rule3 claim mismatch                     KILLED
  rule4 action scope                       KILLED
  rule5 authorization time                 KILLED
  rule6 verifier unavailable               KILLED
  rule6 refuted                            KILLED
  rule6 not supported                      KILLED
  rule6 error                              KILLED
  rule6 unknown outcome (unreachable)      SURVIVED
  rule6 unbound verify                     KILLED
  rule7 budget                             KILLED
  rule7 independence                       KILLED
  verdict DEFER                            KILLED
  auth needs a verifier                    KILLED
  auth needs >= 1 root                     KILLED
  auth bool roots                          KILLED
  evidence own interval                    KILLED
  evidence ancestors (Amendment 1)         KILLED
  claim refuses observation                KILLED
  claim needs evidence                     KILLED
  verify: exception is ERROR               KILLED
  verify: non-Outcome is ERROR             KILLED
  independence: disjointness               KILLED
  independence: budget                     KILLED
  seal after id (A4)                       KILLED
VERDICT  27 of 27 reachable guards killed, 1 listed as unreachable, 0 survived, 0 could not apply
```

## Self-attack (unregistered; the builder attacking his own work is the weakest kind of attack)

| Attack | Observed | Reading |
|---|---|---|
| A1 the caller picks `at` | evidence valid `[0, 40)`: DEFER at 50, ALLOW at a declared 30 | **Limit.** E9 holds relative to a *declared* time; nothing here reads or proves a clock. Same class as sovereign-veritas's caller-declared runtime state |
| A2 evidence swapped after authorization | REFUSE `authorization_claim_mismatch` | Held: the authorization names the claim's content id, which covers its evidence set |
| A3 one reading relabelled with a second source | `independent_roots = 2`, ALLOW | **Limit.** Independence is computed from *declared* provenance. A copy with a new source label counts as independent. Detecting that needs authenticated sources, which v0.01 does not have |
| A4 internal setter after construction | field changed, id stale | **Defect, fixed** (above) |

## What this does and does not show

It shows that, in one process, with honest provenance labels and a truthful clock, these objects
keep observation, evidence, claim, verification and authorization distinct, refuse the registered
malformed and missing cases, and produce a record whose structure a second function can recheck.
It does not show that any recorded content is true (P8), that provenance is authentic (A3), that the
time is real (A1), that the verifiers are correct, or that anything here resists code running in
the same process. It has no action, effect or replay of a decision from its record.

## Next unrun tests

- P11 (registered): carry an Eunoia decision record into an `sv.package` through an adapter, and
  check it with sovereign-veritas's verifier. Blocked on an adapter neither repository has.
- From A1: take `at` from an external time witness and register what a stale witness does.
- From A3: require that two roots count as independent only if their sources are distinct
  *authenticated* identities (e.g. ssh signatures, as sovereign-veritas uses), and rerun A3.
- Replay: recompute the decision from the record alone, given the recorded verifier outcomes
  (DESIGN_NOTES calls the record "replayable"; v0.01 does not do this yet).
