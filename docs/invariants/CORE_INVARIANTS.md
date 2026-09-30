# Core Invariants

**Status:** PROPOSED CONSTRAINTS — not yet verified claims
**Source:** Adversarial refinement pass (2026-09-30)

## Foundational separations

Proposal ≠ Evidence ≠ Authority ≠ Execution

Evidence → Eligibility
Evidence ↛ Authority
Γ → Authority

## Capability isolation

UntrustedCode ↛ Capability

Host-issued opaque tokens only. No public constructor/deserializer. Not reconstructible from bytes. Unique nonce, issuer, issuance event, evidence snapshot, policy version, expiry.

## Execution

Execute(a) ⇒ Authorized(a) ∧ Admissible(a, t_commit) ∧ ResourcePermitted(a, t_commit)

## Taxonomy-bounded support

Supported(C) ⇒ Supported(C | T)

Support(C | T, π). Taxonomy expansion T_old ⊂ T_new maps SUPPORTED_BOUNDED_BY(T_old) → REQUIRES_REVERIFICATION(T_new). Do not automatically call old evidence false.

TID = H(Canonicalize(T)); claims carry taxonomy_id, version, hash.

## Historical authorization ≠ current validity

DecisionState: DEFER | ALLOW | REFUSE | CONTAIN
ExecutionState: NOT_STARTED | RUNNING | COMPLETED | ABORTED
AuthorizationRecord: AUTHORIZED_AT(t, evidence_hash, policy_hash, capability_id)
CurrentValidity: VALID | TAINTED | INVALIDATED | REQUIRES_REVERIFICATION

## Verification resources

VerificationCost(p) > B_request ⇒ REFUSE_EXCEEDS_BOUNDS
BudgetUnavailable(p) ⇒ DEFER_RESOURCE_BUDGET

Bounded per-request ≠ aggregate exhaustion protection. Epoch budget + deterministic scheduler. DEFER is not epistemic rejection. Identity not required for Phase 0–4 safety.

## Constitutional hierarchy

Γ ≻ Θ ≻ E

Γ immutable within epoch; amendable only via external-authority constitutional protocol. E ↛ Γ.

## Master rule

Every epistemic guarantee is relative to an explicitly identified boundary.

These invariants are proposed, not claimed empirically verified until the executable reference model measures them.
