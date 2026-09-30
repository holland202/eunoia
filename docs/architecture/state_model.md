# State Model

**Status:** PROPOSAL
**Schema:** schemas/state.schema.json

Core fields: OBJECTIVE, WORLD_MODEL, KNOWN_INFORMATION, UNKNOWN_INFORMATION, EVIDENCE, ACTIVE_CONSTRAINTS, AUTHORITY, AVAILABLE_CAPABILITIES, CANDIDATE_PLANS, RESOURCE_BUDGET, UNCERTAINTY, VERIFICATION_STATE, TELEMETRY, ATTESTATION.

Protected state is not silently writable by the model. Missing required fields for a transition → fail closed.
