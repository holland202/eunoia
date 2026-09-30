# Adoption Rule (Doors Principle)

**Status:** ADOPTED under SWAY
**Eunoia treatment:** Foundational methodological concept

## Rule

> A tool is adopted only after it catches a real defect in this estate.

```
proposal
   ↓
does it catch a real failure that the method as written did not catch?
   │
   ├── YES → eligible for adoption
   │
   └── NO  → DOOR
```

Formal sketch:

```
Adopt(A) ⟺ ∃ f ∈ F : catches(A, f) ∧ ¬catches(M, f)
```

## Meaning of DOOR

A door is not rejected, false, useless, or disproven.
A door means: proposed, retained, available for future promotion, but not adopted.

## Anti-bootstrap

Discovery of a defect in a methodology does not automatically authorize modifying that methodology.

**Eunoia principle:** Detection creates evidence. It does not create authority.
