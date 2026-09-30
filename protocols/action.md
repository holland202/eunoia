# Protocol: Action

**Status:** PROPOSAL

## Purpose

Define how an ALLOW decision becomes an executed action and how outcomes are captured.

## Sequence

1. Gate returns ALLOW with attestation ID.
2. Executor receives the authorized action package.
3. Executor performs the action within resource and constraint bounds.
4. Outcome is observed.
5. Verification protocol runs.
6. Attestation records success, failure, or partial completion.

## Rules

- No execution without ALLOW.
- Executor does not self-authorize.
- Partial failure is recorded; it is not silently coerced to success.
- Resource exhaustion mid-action is attested and surfaces as failure or controlled abort per policy.
