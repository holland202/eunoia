# Single Typed Evidence DAG

**Status:** PROPOSAL

G = (V, E), E ⊆ V × R × V

R includes: PROVENANCE, DEPENDS_ON, SUPPORTS, CONTRADICTS, DERIVED_FROM, ATTESTS, INDEPENDENCE_CLAIM, TAINTS, SUPERSEDES.

One canonical graph. Every semantic relationship affecting admissibility, authority, validity, or auditability is an explicitly typed edge.

Edge type alone is insufficient: each needs schema and validity rules (INDEPENDENCE_CLAIM must not be decorative).

Support is taxonomy-bounded: Support(C | T, π). Expansion → REQUIRES_REVERIFICATION without auto-falsifying prior support.
TID = H(Canonicalize(T)).
