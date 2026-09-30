# Architecture

**Status:** PROPOSAL / SPECIFICATION
**Version:** 0.1

## Design goals

1. Evidence before authority.
2. Fail closed.
3. Role separation (model, reasoner, verifier, authority, executor, attester).
4. Local-first.
5. Epistemic honesty.
6. Measurable cost.

## Layered stack

EUNOIA LAYER → VERITAS GATE (ALLOW/DEFER/REFUSE) → SWAY / DECAY / GROWTH → SOVEREIGN VERITAS (evidence substrate) → EDGE COMPUTE

Existing research repositories remain independent. Eunoia integrates through adapters that consume validated interfaces only.

## Control loop

OBSERVE → INTERPRET → HYPOTHESIZE → PLAN → CHECK EVIDENCE → CHECK AUTHORITY → CHECK CONSTRAINTS → CHECK RESOURCES → PROPOSE ACTION → VERIFY AUTHORIZATION → EXECUTE → OBSERVE OUTCOME → VERIFY → ATTEST → UPDATE STATE

## Veritas Gate

Governance boundary between proposal and authorized action. Primary decisions: ALLOW, DEFER, REFUSE.

Implementation conformance of a particular gate contract is not scientific validation of the policy it encodes.

## Research instruments

SWAY — How do we know an intervention produced the claimed effect? (Adopted; not validated)
DECAY — What survives removal? (Frozen specification)
GROWTH — What pays when added? (Frozen specification)

## What v0.1 deliberately omits

Full autonomous agent runtime; learned world models claimed as accurate; hardware acceleration claimed without measurement; merged codebases of prior repositories; any claim that the architecture solves safety or alignment.
