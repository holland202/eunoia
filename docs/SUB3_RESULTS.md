# SUB-3 — An origin state on Evidence: results

**Status:** Draft, self-tested. 4 of 4 testable predictions held (S1–S4); S5 is the unrun door.
**Registration:** `docs/SUB3_PREREG.md` (`db37c6d`). **Code:** `dde774e`. **CI:** `check` passed on
Ubuntu, macOS and Windows at `dde774e`.

## What broke or was wrong

Nothing in SUB-3's own predictions. Two things are worth leading with anyway:

- **The vocabulary is copied, not shared.** `ORIGIN_STATES` is evidence-ledger SPEC.md §2 typed out again.
  If evidence-ledger changes §2, Eunoia will not notice. No test ties the two.
- **Undeclared origin still passes.** Evidence with `origin=None` can support ALLOW under
  `OriginOracleGate`. That keeps SUB-1 and SUB-2 byte-identical, but evidence-ledger §12 forbids treating
  missing evidence as a positive result, and an undeclared origin arguably is missing evidence. This is
  S5, left open on purpose.

## Results

| | prediction | result |
|---|---|---|
| S1 | `None` and the 8 states accepted; `"measured"` and `"OBSERVED"` raise `ValueError` | HELD (`test_S1_origin_vocabulary`) |
| S2 | 50 existing tests pass; SUB-2 harness same verdict and digest; detector 0 | HELD: 61 passed (50 + 11 new); `VERDICT 5 of 5`, `DIGEST 2c04d80e5dd249cce1c578a6d825fb38965c21f0570fa8c2cdec307e3f5a8e87` (same as base); `0 decision-rule returns under src` |
| S3 | `OriginOracleGate` on C1: ALLOW for MEASURED/OPERATOR/DERIVED/INFERRED, DEFER (R5o) for ABSENT/DEFAULTED/NEVER_WIRED/UNVERIFIED; `OracleGate` ALLOW for all 8 | HELD (8 parametrised cases) |
| S4 | editing origin in a record is caught by `replay` (`evidence` and `decision`; adding the key: `evidence`) | HELD |

**Anti-vacuity (mutants on the new tests, run locally, not registered):**

```
M1 no R5o: 5 failed, 6 passed in 0.05s
M2 no dep: 1 failed, 10 passed in 0.04s
M3 no check: 1 failed, 10 passed in 0.04s
M4 not in view: 8 failed, 3 passed in 0.05s
M0 null: 11 passed in 0.03s
```

M1 removes the R5o clause, M2 drops origin from the dependency hash, M3 removes the vocabulary check, M4
keeps origin out of the gate view. Each is caught. M0 (no change) passes.

## What this shows and does not

It shows the substrate can carry evidence-ledger's origin dimension without disturbing SUB-1/SUB-2, and
that a rule set sees and acts on it. It does not show that any particular set of blocking states is
right (that is policy), that a declared origin is true (Eunoia cannot check that MEASURED was measured;
evidence-ledger §2.5's HASH_MATCH ≠ SOURCE_AUTHENTICITY applies unchanged), or that Eunoia and
evidence-ledger interoperate.

## Doors

- **S5:** should undeclared origin block ALLOW? Changes SUB-1's matrix. Chad's decision.
- Tie the copy to the source: a test that reads evidence-ledger's SPEC §2 at a pinned commit and fails if
  the eight states differ.
- Corroboration (source independence) and execution binding have no state in evidence-ledger §2 either.

## Provenance

AI participation: Claude (Opus 5.5, Anthropic) wrote the registration, code, tests and this file. Human
validation: Chad Holland directed the work ("You make the best decision"); review was of the summary and
CI, not line by line. Chad is responsible for the final artifact.
