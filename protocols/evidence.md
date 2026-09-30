# Protocol: Evidence

**Status:** PROPOSAL

## Purpose

Define how observations and measurements become admissible evidence and how they may support claims.

## Steps (conceptual)

1. Capture raw input with timestamp and source.
2. Validate structure (schema / parser isolation where applicable).
3. Admissibility decision (policy).
4. If admitted, assign evidence ID and provenance fields.
5. Link to claims only through explicit support relations.
6. Update verification / replication status under separate protocol.
7. Attest the admission or rejection.

## Invariants

- Rejected evidence is retained as rejected, not deleted.
- Model output is not evidence until admitted.
- Admissible ≠ sufficient.
- Provenance fields are not silently rewritten.
