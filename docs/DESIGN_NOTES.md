# Design Notes — Eunoia v0.01

**Status:** PROPOSAL / architectural research prototype  
**Date recorded:** 2026-09-30  
**Source:** Rough draft for minimal executable substrate

## Purpose of v0.01

Establish a minimal evidence-bounded substrate for reasoning, claims, verification, decisions, provenance, and continuity.

The first version answers one narrow question:

> Can an AI-oriented system represent a decision as a traceable dependency graph in which observations, evidence, claims, verification, authorization, and action are explicitly distinct?

Not AGI.  
Not a memory solution.  
Not a complete governance framework.  
Not a replacement for Sovereign Veritas.

It is the common substrate those projects can eventually share.

## v0.01 Control Flow

```
INPUT / OBSERVATION
        │
        ▼
     EVIDENCE
  (provenance + source)
        │
        ▼
      CLAIM
 (supported / unknown)
        │
        ▼
   VERIFICATION
 (independent check)
        │
        ▼
  ADMISSIBILITY
 (can this be relied upon for this use?)
        │
        ▼
  AUTHORIZATION
 (may this action occur?)
        │
        ▼
     DECISION
 (ALLOW / DEFER / REFUSE)
        │
        ▼
      ACTION
        │
        ▼
      RESULT
 (observed outcome)
        │
        └──────────► new evidence
```

Underneath everything:

```
PROVENANCE
     │
DEPENDENCIES
     │
  VALIDITY
```

## Core Objects (minimal set)

### Observation
Something the system received or measured.  
**Observation is not automatically a fact.**

### Evidence
Wraps an observation or artifact with provenance.  
Potential states (keep minimal in v0.01): AUTHENTIC, UNVERIFIED, INVALID, EXPIRED, SUPERSEDED.

### Claim
A proposition the system records as evaluable.  
**Claim ≠ Evidence**  
**Claim ≠ Truth**

### VerificationResult
Independent evaluation.  
Statuses: SUPPORTED, NOT_SUPPORTED, REFUTED, ERROR.  
**NOT_SUPPORTED ≠ REFUTED** (retained from day one).

### Provenance
Source, created_at, parent_refs, content_hash.  
Hash establishes identity/integrity, not truth.  
**AUTHENTIC ≠ TRUE**

### Authorization
Separate from verification.  
**VERIFIED ≠ AUTHORIZED**

### Gate
Produces Decision: ALLOW / DEFER / REFUSE.  
Must distinguish “caller says verified” from “verifier actually ran”.

### Decision Record
Replayable record linking claim, evidence, verification, authorization, provenance.

### Dependency Graph
Every decision declares explicit dependencies (claim → evidence → observation; plus verifier, model, runtime, etc.).

### Validity
`valid_from` / `valid_until`.  
`is_valid_at(timestamp)` rather than a boolean “valid”.

## Memory

Do **not** implement sophisticated memory in v0.01.  
Represent memory as persisted evidence/claims with dependency and provenance relationships.  
Long-term memory management, contradiction resolution, forgetting, and automatic revalidation remain research problems.

## v0.01 Invariants

- **E1** Observation ≠ Evidence
- **E2** Evidence ≠ Truth
- **E3** Claim ≠ Verification
- **E4** NOT_SUPPORTED ≠ REFUTED
- **E5** Verification ≠ Authorization
- **E6** Authorization ≠ Execution
- **E7** Provenance is not truth (AUTHENTIC ≠ TRUE)
- **E8** Every decision has an explicit dependency graph
- **E9** Time matters (`valid_at(t)`)
- **E10** Unsupported states fail closed (ALLOW is never the default when required evidence or authorization is absent)

These align with and extend the existing CORE_INVARIANTS.md and EPISTEMIC_POLICY.md.

## What v0.01 Explicitly Does Not Claim

Eunoia v0.01 is an architectural research prototype. It does not establish truth, consciousness, general intelligence, safe autonomy, reliable long-term memory, or complete AI governance. It provides explicit software representations for observations, evidence, claims, verification, authorization, decisions, provenance, dependencies, and temporal validity.

## Success Criterion

Given a simple consequential decision, Eunoia can represent the complete dependency chain from observation → evidence → claim → verification → authorization → decision, preserve provenance and temporal validity, reject missing/invalid prerequisites, and produce a deterministic decision record that can be independently inspected.

If this can be demonstrated cleanly with a focused set of tests, we have something worth building on.
