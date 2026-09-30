# Epistemic Invariants E1–E8

**Status:** FROZEN as top-level constraints of the Eunoia consciousness module
**Version:** 0.1
**Rule:** These are not README prose. Implementations and UIs must not violate them.

## The eight invariants

| ID | Invariant |
|----|-----------|
| **E1** | Observation ≠ Interpretation ≠ Theory ≠ Ontological Conclusion |
| **E2** | Intelligence ≠ Consciousness |
| **E3** | Agency ≠ Consciousness |
| **E4** | Self-Report ≠ Direct Access to Experience |
| **E5** | P(C \| E,T,A) ≠ Measured Amount of Consciousness |
| **E6** | Consciousness Evidence ≠ Governance Authority |
| **E7** | NOT_SUPPORTED ≠ REFUTED |
| **E8** | Theory-Conditional Credence ≠ Theory-Independent Probability |

## E8 (critical UI/API constraint)

Forbidden: posterior 0.73 silently displayed as "Consciousness: 73%".

Required: value + theory + assumptions + evidence_set + model_version + epistemic_status.

## Architectural boundary

Assessment ↛ Authority.

Consciousness assessment is not a Veritas Gate decision variable. Assessment may inform eligibility only through explicit policy.

## Machine-checkable expectations (v0.1)

- Posterior lacking theory or assumptions → reject as probability of consciousness
- Label conscious/not conscious without epistemic_status → reject
- Self-report promoted to phenomenal access → reject
- Assessment grants capability or Gate ALLOW → reject (E6)
- NOT_SUPPORTED stored as REFUTED → reject (E7)

## Freeze policy

Framework first, claims later.
Amending E1–E8 requires Doors-qualified defect, not elegance alone.
