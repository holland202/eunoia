# Status

**Last updated:** 2026-09-30
**Rule:** Do not fabricate evidence. Do not silently resolve OPEN items.

## Component evidence table

| Component | Status | Evidence class | Notes |
|-----------|--------|----------------|-------|
| Sovereign Veritas | Existing implementation/research | Implementation + measured tests | Conformance ≠ scientific validity of policy |
| Veritas Gate (`sv.gate/0`) | Implemented / tested | MEASURED conformance on 4,690 vectors | Policy validity NOT ESTABLISHED; mutants pending |
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
| Core invariants (Γ/Θ/E, Evidence DAG, capability, verification budgets) | PROPOSED constraints | docs/invariants/CORE_INVARIANTS.md | Not verified by reference implementation yet |
| Taxonomy-bounded support | PROPOSED | Support(C\|T,π); expansion → REQUIRES_REVERIFICATION | Do not auto-falsify prior support |
| Verification resource scheduler | PROPOSAL Phase 0–4 | Per-request + epoch budgets; DEFER_RESOURCE_BUDGET | Identity not required for safety |
| Capability = host-issued opaque token | PROPOSAL | UntrustedCode ↛ Capability | Rust privacy alone is insufficient |
| Eunoia integration | Proposed | This repository v0.1 + refinements | Foundational architecture only |

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

Machine-readable: `research/sway/state.json`
Schema: `schemas/sway.schema.json`

## Founding principle (from SWAY self-application)

> Detection creates evidence. It does not create authority.

## Architecture refinements (proposed, not frozen as verified)

See:
- docs/invariants/CORE_INVARIANTS.md
- docs/architecture/evidence_dag.md
- docs/architecture/verification_resources.md
- docs/architecture/capability_model.md
- docs/architecture/constitutional_hierarchy.md

Next executable target: Rust reference model of T→T' taxonomy expansion/taint with scheduler/resource-budget semantics included from the start.
