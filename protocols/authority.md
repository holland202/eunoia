# Protocol: Authority

**Status:** PROPOSAL

## Purpose

Bind actors to permitted actions under explicit conditions.

## Principles

1. Authority is granted, not assumed from capability.
2. Missing authority → REFUSE.
3. Authority bindings are inspectable and attestable.
4. Escalation requires a higher binding, not model confidence.

## Minimum binding contents

- principal (who)
- action class (what)
- constraints (when / under what conditions)
- evidence requirements
- expiry or scope limits
- attestation of issuance

## Integration with Gate

The Gate evaluates authority bindings as one of its required inputs.
A proposal without a matching binding cannot receive ALLOW.
