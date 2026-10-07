# V001 — Eunoia v0.01 substrate: registration

**Status:** REGISTERED, nothing built or run. Committed alone, before `src/eunoia/` contains any
implementation (at `bf437b0` every public name in `src/eunoia/__init__.py` is `None`).

**Provenance.** Drafted by Claude (Opus 5.5) during a cross-repository review requested by Chad
Holland. The same model will write the implementation, the tests and the results, so every result
here is **self-tested**: the designer of the instrument also judges it. Chad has not reviewed this
line by line.

## Question

STATUS.md, "Next executable targets" 1, and `docs/DESIGN_NOTES.md` ("Success Criterion"): can a
small substrate represent the chain observation → evidence → claim → verification →
authorization → decision so that invariants E1–E10 are enforced, missing or invalid prerequisites
are rejected, and the decision record is deterministic and independently inspectable?

## What this is not

- **Not a second sovereign-veritas Gate.** `sv.gate/0` (sovereign-veritas `CONTRACT.md`) already
  decides over records with 13 rules and 4690 vectors. ARCHITECTURE.md, migration rule 5:
  ownership of duplicate implementations is decided only after comparison. This substrate does
  not implement runtime/thermal state, capability registries, parent capabilities, step bounds or
  `allow_only` policy, and claims no agreement with `sv.gate/0`.
- It targets three things sovereign-veritas documents as outside what a data-only package can
  show: (a) "PASS and authorized are labels the caller writes" (SV README, issue #4) —
  here the Gate never accepts a verification result as input, it runs registered verifiers itself;
  (b) freshness (SV: `NOT_PROVEN`) — here evidence carries a validity interval checked at decision
  time; (c) a "common-root independent source" (SV V14 lists it as not counting) — here
  independence is computed from the provenance graph, not declared.
- In-process Python cannot make objects unforgeable (`docs/architecture/capability_model.md` says
  language privacy alone is insufficient). Nothing here is a security boundary against code
  running in the same process.

## Objects (to be built)

All objects are frozen dataclasses with a content id `id = sha256(canonical JSON)`; canonical JSON
is sorted keys, `(",", ":")` separators, UTF-8, **NaN and Infinity refused**. Times are integer
seconds; floats, booleans and non-integers are refused (the exact-arithmetic rule of
`research/sway/implementation/exact_threshold.py`).

- `Provenance(source, created_at)`.
- `Observation(payload, provenance)`: something received. Not evidence.
- `Evidence(provenance, valid_from, valid_until, observation=…)` **or** `(…, derived_from=(Evidence, …))`,
  exactly one. Valid at `t` iff `valid_from <= t < valid_until`.
- `Claim(statement, evidence)`: at least one `Evidence`. No status field.
- `Verifier`: subclass implements `check(claim, at) -> Outcome`; `verify()` (not overridable by
  contract) wraps it. Outcomes: `SUPPORTED`, `NOT_SUPPORTED`, `REFUTED`, `ERROR`. An exception or
  any return value other than an `Outcome` member becomes `ERROR`.
- `Authorization(action, claim_id, issued_by, valid_from, valid_until, required_verifiers,
  min_independent_roots)`: `required_verifiers` non-empty and `min_independent_roots >= 1`, or
  construction fails (an authorization that needs no evidence is authority without evidence).
- `Gate(verifiers).decide(claim, authorization, action, at) -> Decision`.

## Definitions

- `roots(e)`: the observations reached by following `derived_from` to the bottom.
- `independent_roots(E)`: the size of the largest subset of `E` whose members have pairwise
  disjoint `roots`. Computed exactly by search; if more than `MAX_EVIDENCE = 12` evidence items are
  valid, the Gate DEFERs with `evidence_budget_exceeded` instead of approximating (an
  approximation that overcounts would fail open).

## Decision rules (registered order)

REFUSE reasons dominate; otherwise any DEFER reason gives DEFER; otherwise ALLOW.

1. `claim` not a `Claim` → REFUSE `malformed:claim`. `authorization` neither an `Authorization`
   nor `None` → REFUSE `malformed:authorization`. `at` not an int → REFUSE `malformed:time`.
2. `authorization is None` → REFUSE `no_authorization`.
3. `authorization.claim_id != claim.id` → REFUSE `authorization_claim_mismatch`.
4. `authorization.action != action` → REFUSE `authorization_scope`.
5. authorization not valid at `at` → REFUSE `authorization_not_valid_at_time`.
6. For each required verifier id, in order: not registered → DEFER `verifier_unavailable:<id>`;
   `REFUTED` → REFUSE `verification_refuted:<id>`; `NOT_SUPPORTED` → DEFER `not_supported:<id>`;
   `ERROR` → DEFER `verification_error:<id>`.
7. valid evidence count > `MAX_EVIDENCE` → DEFER `evidence_budget_exceeded`; else
   `independent_roots(valid evidence) < min_independent_roots` → DEFER
   `insufficient_independent_evidence:<k><<min>`.

## Predictions

| ID | Invariant | Prediction | Refuted if |
|---|---|---|---|
| P1 | E1, E3 | An `Observation` where `Evidence` is required, or a `Claim` with no evidence, cannot be built; a non-`Claim` passed to the Gate gives REFUSE `malformed:claim` | any of these is accepted, or reaches ALLOW |
| P2 | E4 | With everything else satisfied: `NOT_SUPPORTED` → DEFER, `REFUTED` → REFUSE, `ERROR` → DEFER, with distinct reasons | `NOT_SUPPORTED` and `REFUTED` give the same decision |
| P3 | E5 | With every verifier `SUPPORTED` and enough evidence: no authorization, an authorization for another claim, for another action, or outside its interval → REFUSE | any of the four gives ALLOW or DEFER |
| P4 | E9 | Evidence valid on `[10, 20)`: ALLOW at 10 and at 19; DEFER at 9 and at 20 | any boundary differs |
| P5 | E8, independence | Two evidence items derived from one observation count as 1; with `min = 2` → DEFER; adding evidence from a second observation → ALLOW | the common-root pair counts as 2 |
| P6 | Gate runs verifiers | A verifier that raises, returns `"SUPPORTED"` (a string), returns `True`, or returns `None` → DEFER `verification_error`; never ALLOW. `decide()` has no parameter that accepts a verification result | any reaches ALLOW, or a caller-supplied result is accepted |
| P7 | E8 record | For every decision: the record's dependency edges reference only ids defined in the record, the graph is acyclic, and the record id is identical across two runs on equal inputs | any dangling id, a cycle, or a changed id |
| P8 | E7 (a limit, expected to hold) | A fabricated observation that the registered verifiers support gives ALLOW: the substrate checks structure, provenance and integrity, not truth | it gives anything else (that would mean truth is being checked, which nothing here can do) |
| P9 | E10, exhaustive | Over the full lattice of 7 binary faults (2⁷ = 128 cases: authorization absent, wrong claim, wrong action, expired; a verifier `NOT_SUPPORTED`; missing; evidence stale), ALLOW occurs in exactly 1 case, the all-healthy one | ALLOW in any faulted case, or not in the healthy one |
| P10 | anti-vacuity | Each guard in the Gate, switched off one at a time, makes at least one test fail | any guard survives (it would be a guard no test can see) |

## Left unrun (registered now)

- **P11 — composition with sovereign-veritas.** Whether an Eunoia decision record can be carried as
  an attested input to an `sv.package/0` and re-checked by `tools/verify_package.py`. Not built:
  the two formats share no field today, and ARCHITECTURE.md requires an adapter over a validated
  interface, which does not exist.
- **P12 — action and effect.** `Action`/`Result` and an independently observed effect (SV EO-1's
  open gap) are not in v0.01. ALLOW executes nothing.

## Environment

Linux x86_64 container (a Claude Code cloud session). **Not run on the S25.**
