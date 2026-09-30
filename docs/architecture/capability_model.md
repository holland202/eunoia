# Capability Model

**Status:** PROPOSAL
**Invariant:** UntrustedCode ↛ Capability

Rust private-field witnesses are useful only under full boundary conditions (visibility, module isolation, WASM/capability boundary, no unsafe escape, host instantiation, no serialize/deserialize forgery).

Capability = HostIssuedOpaqueToken: no public constructor/deserializer; unique nonce; issuer; issuance event; evidence snapshot; policy version; expiry.

Host alone mints. Untrusted code may request, not mint.
