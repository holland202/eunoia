# SUB-3 — An origin state on Evidence, from evidence-ledger: registration

**Status:** REGISTRATION. Nothing built or run at the commit that adds this file.
**Date:** 2026-10-05
**Base:** `ef570a8` (branch `experiment/sub2-gate-out`; SUB-2 results). Baseline at the base, run before
this file: 50 tests pass; `tools/sub2_run.py` prints `VERDICT 5 of 5` and
`DIGEST 2c04d80e5dd249cce1c578a6d825fb38965c21f0570fa8c2cdec307e3f5a8e87`.
**Go-ahead:** Chad Holland, 2026-10-05 05:43 CDT ("You make the best decision").

## Question

Eunoia's `Evidence` has a validity state (AUTHENTIC, UNVERIFIED, INVALID, EXPIRED, SUPERSEDED) but no
record of **where the value came from**: measured, typed in by a person, computed, defaulted, absent.
`holland202/evidence-ledger` defines exactly that dimension (SPEC.md §2, commit `4852882`, "evidence
states"). Can Eunoia carry it without changing any SUB-1 or SUB-2 result, and does a rule set then see
it and act on it?

Note on names: evidence-ledger calls this dimension `evidence_state`. Eunoia already uses `state` for a
different dimension (closer to evidence-ledger's provenance/authenticity status, §2.5). Here it is called
`origin` so the two cannot be confused. The two vocabularies being orthogonal is itself a finding worth
checking against evidence-ledger's author before anything is merged.

## Design (fixed before building)

- `ORIGIN_STATES` = evidence-ledger §2's eight: MEASURED, OPERATOR, DERIVED, INFERRED, ABSENT, DEFAULTED,
  NEVER_WIRED, UNVERIFIED.
- `Evidence.origin: Optional[str] = None`. `None` means not declared. Any other value outside
  `ORIGIN_STATES` raises `ValueError`.
- When declared, `origin` is added to that evidence's entry in the gate view and to its dependency hash.
  When `None`, neither changes: views, records and digests are byte-identical to SUB-2's.
- `Gate`, `replay` and `OracleGate` are otherwise unchanged. The package still ships no rule (SUB-2).
- A second test oracle, `OriginOracleGate` (rule set `eunoia-test-oracle/r1-r9+r5o`), in
  `tests/substrate/oracle.py`. It runs R1–R9 unchanged. If they reach R6 or later (R1–R5 passed) and any
  evidence declares origin ABSENT, DEFAULTED, NEVER_WIRED or UNVERIFIED, it returns DEFER, rule `R5o`.
  INFERRED, OPERATOR, DERIVED and MEASURED do not trigger it. Which states should block is a policy
  choice. The point here is that the dimension reaches the rule set.

## Predictions

- **S1.** `Evidence(..., origin=x)` accepts `None` and each of the 8 states and raises `ValueError`
  for `"measured"` (lower case) and `"OBSERVED"`.
- **S2 (no regression).** All 50 existing tests pass unchanged. `tools/sub2_run.py` prints the same
  verdict and the same digest `2c04d80e…` as at the base. `tools/sub2_no_rules.py src` reports 0.
- **S3 (the dimension reaches the rules).** On SUB-1's case C1 (otherwise ALLOW), with origin set to each
  of the 8 states in turn, `OriginOracleGate` gives ALLOW (R9) for MEASURED, OPERATOR, DERIVED and
  INFERRED and DEFER (R5o) for ABSENT, DEFAULTED, NEVER_WIRED and UNVERIFIED. `OracleGate` gives ALLOW for
  all 8. That is the control: the clause, not the field alone, changes the outcome.
- **S4 (origin is a dependency).** For a C1 record with origin MEASURED, editing that evidence's origin
  to DEFAULTED in `record["inputs"]` makes `replay(record, OriginOracleGate())` report mismatches
  including `"evidence"` and `"decision"`. Editing it on a record with origin `None` (adding the key) is
  also caught (`"evidence"`).
- **S5 (door, unrun).** Undeclared origin. Evidence-ledger §12 forbids treating missing evidence as a
  positive result. Making `None` block ALLOW would change SUB-1's registered matrix. That is a decision
  for Chad, not run here.

## Limits

- Self-tested: Claude (Opus 5.5, Anthropic) writes the registration, code and tests.
- This copies a vocabulary. It does not make evidence-ledger and Eunoia interoperate (no shared schema,
  no import). Whether Eunoia should depend on evidence-ledger rather than copy it is open.
- `origin` is declared by whoever builds the Evidence. Eunoia cannot check that a value labelled
  MEASURED was measured. That is evidence-ledger's §2.5 point (HASH_MATCH ≠ SOURCE_AUTHENTICITY), and it
  applies here unchanged.

## Provenance

Vocabulary: evidence-ledger SPEC.md §2 (Chad Holland's repo). Registration by Claude (Opus 5.5,
Anthropic); direction by Chad Holland, no line review before this commit.
