# SUB-2 — Move the decision rules out of Eunoia's package: registration

**Status:** REGISTRATION. Nothing built or run at the commit that adds this file.
**Date:** 2026-10-05
**Base:** `5502b31` (branch `experiment/sub1-substrate`; SUB-1 results)
**Direction:** Chad Holland, 2026-10-05 05:09 CDT: decision rules belong to Sovereign Veritas, not Eunoia.
Go-ahead for this restructure: 05:15 CDT.

## Question

Can Eunoia keep its contracts (types, the decision record, the dependency graph, `replay`) while its
package holds **no** ALLOW/DEFER/REFUSE rule of its own, and can that absence be checked by
something that would notice it coming back?

## Design (fixed before building)

- `eunoia.Gate` becomes an abstract base class. It builds the input view and the decision record
  (Eunoia's job: dependencies, provenance, time) and calls an abstract `rules(view)` that a
  subclass supplies. `Gate()` cannot be instantiated.
- SUB-1's rules R1–R9 move, unchanged in logic, to `tests/substrate/oracle.py` as `OracleGate`,
  labelled a **test oracle**: it exists to exercise the contracts and is not shipped in `src/`.
- `replay(record, rules)` takes the rule function explicitly. A record names the rule set that
  produced it (`record["rule_set"]`), and `replay` reports a mismatch when the rule set's name differs.
- The intended production rule set is Sovereign Veritas's `sv.gate/0` through an adapter. Building
  that adapter is **not** part of SUB-2.
- SUB-1's registered result stays reproducible: CI checks out `fb5194a` (SUB-1's pinned commit) in a
  separate worktree and runs its harness unchanged.

## The detector (`tools/sub2_no_rules.py`)

Parses every `.py` file under a given `src/` with `ast` and reports each `return` statement whose
returned value is, or is a tuple starting with, one of the string constants `"ALLOW"`, `"DEFER"`,
`"REFUSE"`. That is how SUB-1's rules were written. It does not catch rules written any other way
(a lookup table, a computed string); that is a limit, not a guarantee.

## Predictions

- **P1 (anti-vacuity of the detector).** On SUB-1's `src/` at `fb5194a` the detector reports
  exactly 14 returns, all in `substrate.py` (the 14 `return "<OUTCOME>", "R<n>", …` lines of
  `decide_view`). On the restructured `src/` it reports 0.
- **P2.** `Gate()` raises `TypeError`. `OracleGate` decides SUB-1's 19-case matrix 19 of 19 as
  SUB-1 registered.
- **P3.** SUB-1's ten single-invariant mutants, re-anchored to wherever each line now lives
  (`src/` or `tests/substrate/oracle.py`), are all killed (10 of 10), and the null mutant M0
  survives. The mutant edits are byte-identical to SUB-1's; only the file they apply to may change.
- **P4.** Replaying the C1 record with `OracleGate.rules` reproduces ALLOW with no mismatches.
  Replaying it with an always-DEFER rule set named `"always_defer"` reports mismatches including
  `"rule_set"` and `"decision"`. Altering each of the 6 dependency hashes is still caught (6 of 6).
- **P5.** All pre-existing tests pass: the 15 from before SUB-1, and SUB-1's 32 substrate tests
  pointed at `OracleGate`.
- **P6 (CI).** On ubuntu, macOS and Windows, SUB-1's harness at `fb5194a` still reproduces its pinned
  verdict and digest; SUB-2's harness reproduces its own pinned outcome; `--sabotage` (the detector
  pointed at SUB-1's `src/` in place of the current one) exits 1.
- **P7 (door, unrun).** The SV adapter: `SVGate(Gate)` whose `rules` map the view onto an `sv.gate/0`
  input and return SV's decision. Registered as DEC-1's follow-on, not run here.

## Limits

- Self-tested: Claude (Opus 5.5, Anthropic) writes the registration, code, detector and mutants.
- The detector only knows one way of writing a rule. A check that knows one form is a tripwire,
  not a proof that the package holds no policy.
- Moving rules into `tests/` keeps them in the repository. The claim is narrower: the installable
  package `eunoia` holds no decision rule.

## Provenance

Direction: Chad Holland. Registration drafted by Claude (Opus 5.5, Anthropic); direction-level review.
