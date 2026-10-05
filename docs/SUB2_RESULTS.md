# SUB-2 — Move the decision rules out of Eunoia's package: results

**Registration:** `docs/SUB2_PREREG.md`, committed alone at `f4614d1`.
**Run:** `7220163` (code and raw output together); `RECORDED` pinned and CI extended at `fa35a21`.
**Verdict:** 6 of 6 as registered (P1–P5 in the container, P6 in CI on `fa35a21`). P7 is the door.

## What could have gone wrong, first

- **Self-tested.** Claude (Opus 5.5, Anthropic) wrote the registration, the move, the detector and the
  re-anchored mutants.
- **A derived value was corrected before the registration commit.** The first draft said the
  detector would find 17 rule returns at `fb5194a`. Counting SUB-1's existing source gave 14, and
  the file was committed with 14. The count came from the existing code, not from running the
  detector, but it is a number fitted to code that already existed, and is disclosed as such.
- **The detector is a tripwire for one form.** It finds `return "ALLOW"/"DEFER"/"REFUSE", ...`. A rule
  written as a lookup table or a computed string would pass it. "0 hits" means no rule written in
  SUB-1's form, not "no policy anywhere".
- **The rules still live in this repository**, in `tests/substrate/oracle.py`. The registered claim
  is narrower: the installable package `eunoia` holds no decision rule.
- **SUB-1's harness left the tree.** `tools/sub1_run.py` imported the old concrete `Gate`, so it
  could not run against the new package. It was removed from HEAD rather than edited. CI checks out
  `fb5194a` in a separate worktree and runs it there, unchanged, and it still reproduces its pinned
  digest on all three operating systems.

## Raw output (`results/sub2/run.txt`, x86_64 container, Python 3.13.16)

```
SUB-2 | registered run | python 3.13.16 | linux
  detector at fb5194a: 14 hits in ['eunoia/substrate.py']; now: 0
  Gate() abstract: True | OracleGate matrix 19 of 19
  M_E1   KILLED   src/eunoia/substrate.py
  M_E2   KILLED   tests/substrate/oracle.py
  M_E3   KILLED   tests/substrate/oracle.py
  M_E4   KILLED   tests/substrate/oracle.py
  M_E5   KILLED   tests/substrate/oracle.py
  M_E6   KILLED   src/eunoia/substrate.py
  M_E7   KILLED   tests/substrate/oracle.py
  M_E8   KILLED   src/eunoia/substrate.py
  M_E9   KILLED   src/eunoia/substrate.py
  M_E10  KILLED   tests/substrate/oracle.py
  M0     SURVIVED -
  replay oracle {'match': True, 'mismatches': [], 'outcome': 'ALLOW'} | always_defer ['rule_set', 'decision'] | tamper caught 6 of 6
  tests/invariants: 15 passed (exit 0) | tests/substrate: 35 passed (exit 0)

  P1  HELD
  P2  HELD
  P3  HELD
  P4  HELD
  P5  HELD
VERDICT 5 of 5 as registered (P6 is CI; P7 is the unrun door)
DIGEST 2c04d80e5dd249cce1c578a6d825fb38965c21f0570fa8c2cdec307e3f5a8e87
```

`--sabotage` (detector pointed at SUB-1's `src/`): P1 REFUTED, exit 1.

| | prediction | result |
|---|---|---|
| P1 | detector: 14 hits at `fb5194a`, 0 now | HELD |
| P2 | `Gate()` raises TypeError; `OracleGate` 19 of 19 | HELD |
| P3 | SUB-1's 10 mutants killed after re-anchoring (6 now in the oracle, 4 in `src/`); M0 survives | HELD |
| P4 | replay with the oracle matches; with `always_defer` reports `rule_set` and `decision`; 6 of 6 tampered hashes caught | HELD |
| P5 | 15 pre-existing tests and the substrate tests (35, of which 32 are SUB-1's) pass | HELD |
| P6 | CI, 3 OSes: SUB-1 at `fb5194a` reproduces; detector clean; SUB-2 reproduces; sabotage exits 1 | HELD |
| P7 | SV adapter `SVGate(Gate)` | door, not run |

## What this shows and does not show

- **Shows (self-tested):** `eunoia.Gate` is now an abstract record-builder. The decision comes from a
  rule set a subclass supplies and names, and replay notices when a record is replayed under a
  different rule set. Moving the rules did not weaken the tests: every SUB-1 mutant is still killed.
- **Does not show:** that Eunoia's contracts can carry what `sv.gate/0` needs. That is DEC-1's
  question and P7's adapter.
- **New behaviour:** a rule set that returns something other than ALLOW/DEFER/REFUSE is recorded as
  REFUSE (`test_SUB2_rule_set_returning_garbage_fails_closed`).

## Provenance

Direction: Chad Holland (2026-10-05). Implementation and this document: Claude (Opus 5.5, Anthropic);
direction-level human review. Chad is responsible for what is merged.
