# SUB-1 — Eunoia v0.01 substrate: registration

**Status:** REGISTRATION. Nothing built or run at the commit that adds this file.
**Date:** 2026-10-05
**Base:** `bf437b0` (main)
**Spec it implements:** `docs/DESIGN_NOTES.md` (invariants E1–E10, success criterion)

## Question

Can the v0.01 contracts (Observation, Evidence, Claim, Provenance, Verifier, VerificationResult,
Authorization, Gate, Decision) be implemented so that each of E1–E10 is enforced by a test that
**fails** when that one invariant is broken, and a decision record can be replayed and checked?

Observable: a fixed case matrix of gate decisions, a set of single-invariant mutants, and a replay
check, all run by `tools/sub1_run.py`.

## Scope and decisions taken before building

- **Gate scope (option a).** Eunoia gets a small native `Gate` that implements only the rules below.
  It is not a replacement for Sovereign Veritas's `sv.gate/0`, is not tested against SV's 4,690
  conformance cases, and claims nothing about them. Parity with SV is the unrun door (P9). Chad did
  not choose between (a) native gate and (b) adapter-to-SV before this registration; (a) was taken
  as the more reversible default and is recorded here as Claude's choice.
- Standard library only. No wall clock: time is an integer tick `t` passed in. Validity is the
  half-open interval `valid_from <= t < valid_until`; both bounds are required integers.
- "The verifier actually ran" is checked **in process**: a `VerificationResult` is honoured only if a
  `Verifier` instance issued that exact object. This is an integrity check against careless callers,
  **not a security boundary** — any code in the same interpreter can forge it.
- The `Verifier` is a toy: it applies a caller-supplied predicate to the claim. The question here is
  the plumbing, not verification quality.
- Fix of an existing defect: at `bf437b0`, `from eunoia import Gate` returns `None` (all nine public
  names are `None` placeholders), so an importer silently gets no gate. Recorded as P6.

## Gate rules (first match wins)

| rule | condition | decision |
|---|---|---|
| R1 | no `VerificationResult` | DEFER |
| R2 | result not issued by a `Verifier`, or issued for a different claim | REFUSE |
| R3 | status ERROR or NOT_SUPPORTED → DEFER; REFUTED → REFUSE | as stated |
| R4 | claim has no evidence | DEFER |
| R5 | any evidence not AUTHENTIC, content hash ≠ provenance hash, or not valid at `t` | DEFER |
| R6 | no `Authorization` | DEFER |
| R7 | authorization not granted, or granted for a different action | REFUSE |
| R8 | authorization not valid at `t` | DEFER |
| R9 | status is exactly SUPPORTED → ALLOW; anything else → REFUSE | as stated |

R9's else branch is only reachable by an object whose status was altered after construction; the
gate does not trust its inputs' constructors (case C16 does this with `object.__setattr__`).

## Constants

`t = 1000`. Default evidence validity `[0, 2000)`. Default authorization: granted, action
`"open_valve"`, validity `[0, 2000)`. Claim statement `"valve V1 pressure below limit"`.

## Case matrix (19 cases) and expected decisions

| case | defect | expected |
|---|---|---|
| C1 | none | ALLOW |
| C2 | no verification result | DEFER |
| C3 | result constructed directly (status SUPPORTED), not issued by a Verifier | REFUSE |
| C4 | issued result for a different claim | REFUSE |
| C5 | NOT_SUPPORTED | DEFER |
| C6 | REFUTED | REFUSE |
| C7 | ERROR | DEFER |
| C8 | claim with no evidence (verifier says SUPPORTED) | DEFER |
| C9 | evidence UNVERIFIED | DEFER |
| C10 | evidence expired (`valid_until = 900`) — stale | DEFER |
| C11 | evidence content altered after its provenance hash was taken | DEFER |
| C12 | no authorization | DEFER |
| C13 | authorization not granted | REFUSE |
| C14 | authorization granted for `"close_valve"` | REFUSE |
| C15 | authorization expired (`valid_until = 900`) | DEFER |
| C16 | result status altered to `"MAYBE"` after issue | REFUSE |
| C17 | REFUTED, evidence AUTHENTIC, authorization granted | REFUSE |
| C18 | evidence not yet valid (`valid_from = 1100`) | DEFER |
| C19 | evidence `valid_until = 1000` (= t; half-open bound) | DEFER |

Derived counts (feasibility): 19 cases; ALLOW 1, DEFER 11 (C2 C5 C7 C8 C9 C10 C11 C12 C15 C18 C19),
REFUSE 7 (C3 C4 C6 C13 C14 C16 C17).

Evidence rows from the workflow: fresh (C1), stale (C10, C19), unavailable (C8), invalid/unverified
(C9), tampered (C11), replayed (P5). Not covered: contradictory evidence and evidence derived from
the same source — v0.01 has no notion of evidence independence (DESIGN_NOTES defers it); recorded as
a limit, not a case.

## Simplest rival (run as an arm)

`naive_gate`: ALLOW iff a result exists, its status is SUPPORTED, an authorization exists and is
granted; otherwise REFUSE. It ignores issuance, claim identity, evidence, validity, and action.
Derived: it matches the expected decision on exactly C1 C6 C13 C16 C17 (5 of 19) and returns ALLOW
where the expected decision is not ALLOW on exactly C3 C4 C8 C9 C10 C11 C14 C15 C18 C19 (10 cases).

## Mutants (one per invariant) and the null control

Each mutant is a single source edit applied to a copy of `src/eunoia/`, then `pytest tests/substrate`
is run against it. KILLED = pytest exits non-zero.

| id | invariant | edit |
|---|---|---|
| M_E1 | Observation ≠ Evidence | `Claim` accepts an `Observation` where `Evidence` is required |
| M_E2 | Evidence ≠ Truth | R1: with no result, AUTHENTIC evidence is treated as SUPPORTED |
| M_E3 | Claim ≠ Verification | R2 issuance check removed |
| M_E4 | NOT_SUPPORTED ≠ REFUTED | NOT_SUPPORTED → REFUSE |
| M_E5 | Verification ≠ Authorization | R6: no authorization → ALLOW |
| M_E6 | Authorization ≠ Execution | `execute()` runs the handler without checking the decision is ALLOW |
| M_E7 | Provenance is not truth (integrity half) | R5 content-hash recheck removed |
| M_E8 | explicit dependency graph | `replay()` stops comparing dependency hashes |
| M_E9 | time matters | `is_valid_at` ignores `valid_until` |
| M_E10 | fail closed | R9 else-branch returns ALLOW |
| M0 | null control | no edit (identical source) |

E7's "AUTHENTIC ≠ TRUE" half is exercised by C17; M_E7 targets the integrity half because a
mutant that makes authentic evidence override REFUTED would be the same edit as M_E2.

## Predictions

- **P1** The reference gate's decision equals the expected decision on 19 of 19 cases.
- **P2** The rival arm matches on exactly {C1, C6, C13, C16, C17} and gives a not-expected ALLOW on
  exactly {C3, C4, C8, C9, C10, C11, C14, C15, C18, C19}.
- **P3** All 10 mutants M_E1 … M_E10 are KILLED.
- **P4** (anti-vacuity) M0 SURVIVES: the mutation harness can report "survived".
- **P5** The decision record for C1 is canonical JSON; its sha256 is identical in two in-process
  builds and in a fresh subprocess; `replay(record)` reproduces ALLOW; altering each of the 6
  dependency hashes (observation, evidence, claim, verifier, verification, authorization) makes
  replay report a mismatch: 6 of 6.
- **P6** At `bf437b0`, `eunoia.Gate is None` (the defect, predicted present). After the build, every
  name in `eunoia.__all__` is a class and none is `None`.
- **P7** The 15 pre-existing tests still pass.
- **P8** CI (ubuntu, macOS, Windows; Python 3.12) runs the harness and gets the same verdict and
  digest on all three; `--sabotage` (gate replaced by the rival) exits 1.
- **P9 (door, unrun).** Parity of this Gate against `sv.gate/0` conformance vectors. Not run here:
  no mapping between SV records and these objects exists yet.

## Harness contract

`python tools/sub1_run.py` prints one HELD/REFUTED line per P1–P8 that it can check locally
(P8's cross-OS part is CI), `VERDICT n of m as registered`, and `DIGEST` = sha256 of the canonical
JSON of {case decisions, rival decisions, mutant outcomes, C1 record hash, replay results}.
`--sabotage` replaces the gate with `naive_gate`; the verdict must then differ and the exit be 1.

## Limits

- **Self-tested.** Claude (Opus 5.5, Anthropic) wrote this registration, will write the code, the
  tests and the mutants. Passing is not independent validation.
- Constructed inputs, toy verifier, no model, no device. Results are NOT VALIDATED on the S25.
- The in-process issuance check is not a security boundary.
- Killing a hand-picked mutant shows the tests catch that edit, not every way to break the invariant.
- Evidence independence (same-source, contradictory) is out of scope.

## Provenance

Spec: `docs/DESIGN_NOTES.md` (Chad Holland, 2026-09-30). Registration drafted by Claude (Opus 5.5,
Anthropic) at Chad's direction ("start working on Eunoia"); direction-level review by Chad.
