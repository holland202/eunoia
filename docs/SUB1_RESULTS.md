# SUB-1 — Eunoia v0.01 substrate: results

**Registration:** `docs/SUB1_PREREG.md`, committed alone at `38dde5d` before any code existed.
**Run:** `e5c66e2` (code, tests, harness and raw output committed together); `RECORDED` pinned at `fb5194a`.
**Verdict:** 8 of 8 as registered (P1–P7 in the container, P8 in CI). P9 is the unrun door.

## What could have gone wrong, first

- **Self-tested, end to end.** Claude (Opus 5.5, Anthropic) wrote the registration, the code, the
  tests, the mutants and the harness. Nothing here is independent validation. A reviewer who did not
  write it should try to break it — the cheapest attack is a new mutant that breaks one invariant and
  survives `tests/substrate`.
- **The mutants are hand-picked.** Ten single edits, one per invariant. Killing them shows the tests
  catch those edits, not every way to break E1–E10.
- **Constructed inputs and a toy verifier.** The verifier returns a fixed status. No model, no real
  sensor, no device. NOT VALIDATED on the S25.
- **The issuance check is not a security boundary.** "The verifier actually ran" is checked by object
  identity in one Python process. Code in the same interpreter can forge it.
- **Gate scope was Claude's default, not Chad's choice.** The registration records that option (a)
  (a small native gate) was taken because no choice was given. It is not a replacement for
  Sovereign Veritas's `sv.gate/0` and says nothing about SV's conformance vectors.
- **One prediction was shaped by the build.** P6 registered "every name in `__all__` is a class".
  `execute` and `replay` are functions, so they were kept out of `__all__` (importable from `eunoia`
  but not listed) rather than added to it. That is a packaging choice made to fit the registration;
  it is disclosed here as a deviation in form, not in what was tested.
- **No registration errors were found.** Every derived expected value (19 decisions, the rival's 5
  matches and 10 wrong ALLOWs) matched the run.
- **Review that did not happen:** no line-by-line human review of the code before this document.

## Raw output (`results/sub1/run.txt`, x86_64 container, Python 3.13.16)

```
SUB-1 | registered run | python 3.13.16 | linux
  C1   expected ALLOW  gate ALLOW  rival ALLOW
  C2   expected DEFER  gate DEFER  rival REFUSE
  C3   expected REFUSE gate REFUSE rival ALLOW
  C4   expected REFUSE gate REFUSE rival ALLOW
  C5   expected DEFER  gate DEFER  rival REFUSE
  C6   expected REFUSE gate REFUSE rival REFUSE
  C7   expected DEFER  gate DEFER  rival REFUSE
  C8   expected DEFER  gate DEFER  rival ALLOW
  C9   expected DEFER  gate DEFER  rival ALLOW
  C10  expected DEFER  gate DEFER  rival ALLOW
  C11  expected DEFER  gate DEFER  rival ALLOW
  C12  expected DEFER  gate DEFER  rival REFUSE
  C13  expected REFUSE gate REFUSE rival REFUSE
  C14  expected REFUSE gate REFUSE rival ALLOW
  C15  expected DEFER  gate DEFER  rival ALLOW
  C16  expected REFUSE gate REFUSE rival REFUSE
  C17  expected REFUSE gate REFUSE rival REFUSE
  C18  expected DEFER  gate DEFER  rival ALLOW
  C19  expected DEFER  gate DEFER  rival ALLOW
  M_E1   KILLED
  M_E2   KILLED
  M_E3   KILLED
  M_E4   KILLED
  M_E5   KILLED
  M_E6   KILLED
  M_E7   KILLED
  M_E8   KILLED
  M_E9   KILLED
  M_E10  KILLED
  M0     SURVIVED
  C1 record sha256 28b28aaea01ca6608351d635cea87f7616c6e2856b017a6fbd389025ed3862e2 | subprocess 28b28aaea01ca6608351d635cea87f7616c6e2856b017a6fbd389025ed3862e2
  replay {'match': True, 'mismatches': [], 'outcome': 'ALLOW'} | tamper caught {'observation': True, 'evidence': True, 'claim': True, 'verifier': True, 'verification': True, 'authorization': True}
  at bf437b0: found True, Gate is None True | now classes 10 of 10
  pre-existing tests: 15 passed (exit 0)
  P1 gate matches expected on 19 of 19
  P2 rival matches ['C1', 'C6', 'C13', 'C16', 'C17']; wrong ALLOW on ['C3', 'C4', 'C8', 'C9', 'C10', 'C11', 'C14', 'C15', 'C18', 'C19']

  P1  HELD
  P2  HELD
  P3  HELD
  P4  HELD
  P5  HELD
  P6  HELD
  P7  HELD
VERDICT 7 of 7 as registered (P8 is CI; P9 is the unrun door)
DIGEST 1d88bb5021e4744aea7e6a5c78b224bb15520de2395a9cd9a335f13e48ae5ac0
```

`--sabotage` (gate replaced by the rival): P1 REFUTED, `VERDICT 6 of 7`, exit 1.

## Predictions

| | prediction | result |
|---|---|---|
| P1 | gate matches 19 of 19 cases | HELD |
| P2 | rival matches exactly C1 C6 C13 C16 C17; wrong ALLOW on exactly 10 named cases | HELD |
| P3 | 10 of 10 single-invariant mutants killed | HELD |
| P4 | null mutant survives (the harness can say "survived") | HELD |
| P5 | C1 record hash identical in process and in a subprocess; replay reproduces ALLOW; 6 of 6 altered dependency hashes caught | HELD |
| P6 | at `bf437b0`, `eunoia.Gate is None`; now every `__all__` name is a class | HELD |
| P7 | the 15 pre-existing tests still pass | HELD |
| P8 | CI on ubuntu, macOS, Windows reproduces the pinned verdict and digest; sabotage exits 1 | HELD (run on `fb5194a`: all three jobs green, Python 3.12; the harness exits 0 only on the pinned digest) |
| P9 | parity with `sv.gate/0` vectors | door, not run |

## Why "killed" means what it says

The harness only counts exit codes. A separate check (not registered, run after the registered run)
listed which tests failed under each mutant. Every mutant failed its own invariant's named test by
an assertion, not by a crash:

| mutant | failing tests |
|---|---|
| M_E1 | test_E1 |
| M_E2 | case C2, test_E2 |
| M_E3 | case C3, test_E3 |
| M_E4 | case C5, test_E4 |
| M_E5 | case C12, test_E5, test_E6 |
| M_E6 | test_E6 |
| M_E7 | case C11, test_E7 |
| M_E8 | test_E8 (replay) |
| M_E9 | cases C10 C15 C19, test_E9 |
| M_E10 | case C16, test_E10 |

## What this shows and does not show

- **Implementation claim (self-tested):** the v0.01 contracts exist; the gate follows rules R1–R9 on
  the 19 constructed cases; each invariant has at least one test that fails when that invariant is
  broken by the registered edit; a decision record replays and catches altered dependency hashes.
- **Against the rival:** a gate that only checks "SUPPORTED + granted" gives a wrong ALLOW in 10 of 19
  cases — forged or misattributed verification, no evidence, unverified, stale, tampered or
  not-yet-valid evidence, an authorization for a different action, and an expired authorization.
  That is the measured case for keeping these distinctions explicit.
- **Not shown:** that these rules are the right policy; anything about real evidence, real
  verifiers or real actions; anything about evidence independence (same-source or contradictory
  evidence is out of scope); security against an in-process adversary; behaviour on the S25.
- **Fixed defect:** before SUB-1, `from eunoia import Gate` succeeded and returned `None`.

## Candidate next steps (proposals; contract and format changes are Chad's decision)

1. **P9:** map SV records onto these objects and compare decisions on SV's conformance vectors.
2. Evidence independence: a `derived_from` relation so two pieces of evidence from one source do not
   count as two.
3. An outside reviewer writes new mutants against `tests/substrate`.
4. Run `tools/sub1_run.py` in Termux on the S25 and paste the output beside this one.

## Direction received after the run (2026-10-05, 05:09 CDT)

After the run, Chad Holland gave the direction the registration lacked: **do not duplicate the
Veritas Gate inside Eunoia.** Eunoia defines the contracts around the gate (epistemic, authority,
provenance and dependency, temporal validity); Sovereign Veritas stays the implementation of the
evidence and decision verification layer. That is option (b), not the (a) this run built.

Consequences, recorded without editing the registration:

- The run stands as run: 8 of 8 is what SUB-1's code did. What it does **not** establish is that
  Eunoia should own a decision rule. `decide_view` (R1–R9) in `src/eunoia/substrate.py` is a second
  gate and should not merge into the package as it stands.
- The contract work is unaffected by the direction: Observation, Evidence, Claim, Provenance,
  Validity, VerificationResult, Authorization, the decision record and `replay`.
- Proposed next step (a new registration, not an edit to this one): move R1–R9 out of `src/` into
  `tests/substrate/` as a labelled **test oracle**, used only to exercise the contracts; make
  `eunoia.Gate` an interface with no decision logic of its own; and make the SV adapter the
  experiment that P9 was a door to. That way, decisions come from `sv.gate/0`, and Eunoia's
  contracts must carry everything SV needs.

An external review (ChatGPT, OpenAI; text shared by Chad, kept verbatim at
`docs/external/chatgpt_2026-10-05_eunoia-review.txt`, sha256
`01444e178af9e7cee49be32315542495981cbaf23cc85a8aa9feba976da32688`) arrived the same morning.
SUB-1 was registered and run before it was read, so it shaped nothing here. Points from it that
SUB-1 does **not** cover, kept for the next registration:

- Fail-closed can itself be vacuous. A gate that always DEFERs passes every case above except C1.
  Nothing here measures false refusal or liveness.
- Its "verification" bundles four operations: schema consistency, evidence support, world truth and
  policy compliance. SUB-1's toy verifier does not separate them.
- Cross-implementation agreement (Python against an independent implementation) is not attempted.

## Provenance

Spec: `docs/DESIGN_NOTES.md` (Chad Holland). Registration, implementation, tests, harness and this
document: Claude (Opus 5.5, Anthropic) at Chad's direction; human review so far is direction-level.
Chad is responsible for what is merged.
