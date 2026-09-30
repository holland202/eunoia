# Status

**Last updated:** 2026-09-30
**Rule:** Do not fabricate evidence. Do not silently resolve OPEN items.

## Component evidence table

| Component | Status | Evidence class | Notes |
|-----------|--------|----------------|-------|
| Sovereign Veritas | Existing implementation/research | Implementation + measured tests | Conformance ≠ scientific validity of policy |
| Veritas Gate (`sv.gate/0`) | Implemented / tested | MEASURED conformance on 4,690 vectors | Policy validity NOT ESTABLISHED. Verifier mutants: 27 of 27 KILLED (x86_64 container, 2026-09-30, `tools/verifier_mutants.py`); on the S25: NOT VALIDATED |
| **SWAY** | **Adopted methodology (Amendment 1)** | Failure-earned items; self-application recorded | **Not VALIDATED.** See research/sway/CURRENT_STATE.md |
| SWAY Amendment 1 | ADOPTED 2026-09-30 | Seven incidents → nine items | E2 confirmed; E1 PENDING; O1 OPEN; P5 OPEN/UNRUN |
| SWAY boundary test | DOOR | Provisional classification instrument | Not adopted |
| DECAY | Frozen research specification | Specification document | Experiments required |
| GROWTH | Frozen research specification | Specification document | Experiments required |
| Veritas Companion | Experimental | Existing benchmarks | Do not overgeneralize |
| Topology / veritas-holo | Experimental | Finite experiments | Observed invariance ≠ general theory |
| Information geometry | Research / hypothesis | — | No established results here |
| Constitutional geometry | Experimental | Object-bound certificates | Certificates do not generalize |
| Token economics | Research | — | Baseline + treatment + cost + quality required |
| Geometry–consciousness module | Research package (proposed) | Protocol + claim ledger + draft prereg | Layers separated; substrate claims NOT_SUPPORTED by B-layer success |
| **Consciousness assessment module** | **Foundational specification v0.1** | research/consciousness/ | **Unvalidated; no consciousness claims; P(C\|E,T,A) only** |
| Core invariants (Γ/Θ/E, Evidence DAG, capability, verification budgets) | PROPOSED constraints | docs/invariants/CORE_INVARIANTS.md | Not verified by reference implementation yet |
| Taxonomy-bounded support | PROPOSED | Support(C\|T,π); expansion → REQUIRES_REVERIFICATION | Do not auto-falsify prior support |
| Verification resource scheduler | PROPOSAL Phase 0–4 | Per-request + epoch budgets; DEFER_RESOURCE_BUDGET | Identity not required for safety |
| Capability = host-issued opaque token | PROPOSAL | UntrustedCode ↛ Capability | Rust privacy alone is insufficient |
| Eunoia integration | Proposed | This repository v0.1 + refinements | Foundational architecture only |

## Fixed 2026-09-30 (review of this repository)

| defect | effect | fix | check |
|---|---|---|---|
| `schemas/sway.schema.json` said OPEN items must not be encoded as resolved, but did not enforce it | a state with O1 `RESOLVED` and P5 `HELD` validated (3 of 4 such mutants accepted) | status enums, and `evidence` required to settle an observation or prediction | `tests/invariants/test_sway_state.py`: 3 fail on the old schema, all pass now |
| `exact_threshold.compare` accepted floats | `compare(0.3, 0.1, 0.2, inclusive)` returned False; exact answer True (Item 3's own failure class) | floats and bools refused with TypeError | `tests/invariants/test_sway_implementation.py` |
| `noise.py` used floats and `assert` for its n ≥ 3 rule | the rule vanished under `python -O` | exact scores, ValueError | same file |
| `test_forbidden_inflation_tokens` scanned a hard-coded sentence | could never fail (vacuous guard) | replaced by a check of every status in `research/sway/state.json` | `tests/invariants/test_epistemic_status_required.py` |
| no CI | nothing ran on push | `.github/workflows/check.yml` (Linux, macOS, Windows) | this commit |

## SWAY state (must not be collapsed)

```
Amendment 1: ADOPTED
Items 1–9: ADOPTED
E2: CONFIRMED / NON-SUBSTANTIVE BY INSPECTION
E1: PENDING CLASSIFICATION CHECK
O1: OPEN (O1.1, O1.2, O1.3)
P5: OPEN / UNRUN
Boundary test: DOOR
```

## Founding principles

> Detection creates evidence. It does not create authority.

> Evidence about consciousness is not consciousness itself.

## Next executable targets

1. Rust reference model: T→T' taxonomy expansion/taint + verification resource scheduler
2. Consciousness module: formal schemas + reference-case suite (thermostat … human) + preregistered pilot
