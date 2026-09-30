# Verification Resource Bounds

**Status:** PROPOSAL
**Phase 0–4:** no identity required for safety.

Per-request bound prevents unbounded computation per proposal.
Epoch budget + deterministic admission scheduler prevents aggregate exhaustion.

Path: cost estimate → ≤ B_request? else REFUSE_EXCEEDS_BOUNDS → scheduler → budget available? else DEFER_RESOURCE_BUDGET → bounded verification (timeout → DEFER).

DEFER_RESOURCE_BUDGET is not epistemic rejection.

Federation adds fairness later; it is not required for verification safety.
