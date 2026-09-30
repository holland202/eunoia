# Protocol: Attestation

**Status:** PROPOSAL

## Purpose

Produce an append-only record of what occurred.

## Minimum contents

- attestation ID
- timestamp
- subject (action, claim, evidence admission, …)
- inputs (hashes / references)
- decision or outcome
- verification state
- actor / component IDs
- resource usage snapshot if relevant

## Rules

1. Attestations are append-only.
2. Correction is a new attestation that references the old one; it does not erase history.
3. Missing attestation for an authority-affecting transition is a protocol failure.
