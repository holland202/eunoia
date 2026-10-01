# Architecture

**Status:** PROPOSAL / SPECIFICATION  
**Version:** 0.1 (foundational) + v0.01 substrate plan

## Design goals

1. Evidence before authority.
2. Fail closed.
3. Role separation (model, reasoner, verifier, authority, executor, attester).
4. Local-first.
5. Epistemic honesty.
6. Measurable cost.
7. Explicit dependency graphs for decisions.
8. Temporal validity of evidence.

## Layered stack

```
EUNOIA LAYER
    → VERITAS GATE (ALLOW / DEFER / REFUSE)
        → SWAY / DECAY / GROWTH
            → SOVEREIGN VERITAS (evidence substrate)
                → EDGE COMPUTE
```

Existing research repositories remain independent. Eunoia integrates through adapters that consume validated interfaces only.

## v0.01 Substrate (next executable target)

A minimal set of contracts, not a feature-complete framework:

```
Observation → Evidence → Claim → Verification → Admissibility
    → Authorization → Decision → Action → Result → new Evidence
```

Supported by:

- Provenance (identity/integrity, not truth)
- Dependencies (explicit graph)
- Validity (`valid_at(t)`)

Public API surface for v0.01 remains deliberately tiny:

```python
from eunoia import (
    Observation,
    Evidence,
    Claim,
    Provenance,
    Verifier,
    VerificationResult,
    Authorization,
    Gate,
    Decision,
)
```

See [docs/DESIGN_NOTES.md](docs/DESIGN_NOTES.md) for the full rough draft.

## Control loop

```
OBSERVE → INTERPRET → HYPOTHESIZE → PLAN
  → CHECK EVIDENCE → CHECK AUTHORITY
  → CHECK CONSTRAINTS → CHECK RESOURCES
  → PROPOSE ACTION → VERIFY AUTHORIZATION
  → EXECUTE → OBSERVE OUTCOME
  → VERIFY → ATTEST → UPDATE STATE
```

Failure paths: INSUFFICIENT EVIDENCE → DEFER | UNAUTHORIZED → REFUSE | UNSAFE → CONTAIN | FAILED VERIFICATION → DO NOT PROMOTE

## Veritas Gate

Governance boundary between proposal and authorized action. Primary decisions: ALLOW, DEFER, REFUSE.

Implementation conformance of a particular gate contract is not scientific validation of the policy it encodes.

## Research instruments

| Instrument | Role | Status |
|------------|------|--------|
| SWAY | How do we know an intervention produced the claimed effect? | Adopted methodology; not validated |
| DECAY | What survives removal? | Frozen specification |
| GROWTH | What pays when added? | Frozen specification |

## Layer separation (consolidation rule)

When consolidating external repositories, preserve five distinct layers:

- **Layer A — Runtime primitives** (evidence, provenance, verification, authorization, decision records, resource limits, replay)
- **Layer B — Research frameworks** (SWAY, evaluation harness, adversarial testing, replication tooling)
- **Layer C — Experiments** (specific empirical questions)
- **Layer D — Exploratory mathematics** (unpromoted investigations)
- **Layer E — Domain implementations** (edge, robotics, quantum, ICS, etc.)

Core must not depend on experiments. Experiments may consume core.

## Migration rules (binding)

1. Research lineage must not be erased.
2. Never migrate and refactor simultaneously (IMPORT → PARITY → VERIFY → REFACTOR → VERIFY AGAIN).
3. Preserve failed, refuted, and insufficient-evidence outcomes.
4. Every migrated component carries origin (repository, commit, path) + migration record + parity status.
5. Ownership of duplicate implementations is decided only after comparison; TBD is a legitimate state.

See [docs/migration/](docs/migration/) for the working plan.

## What v0.1 / v0.01 deliberately omits

Full autonomous agent runtime; learned world models claimed as accurate; hardware acceleration claimed without measurement; merged codebases of prior repositories; any claim that the architecture solves safety or alignment; sophisticated long-term memory.
