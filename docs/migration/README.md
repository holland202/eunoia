# Migration & Consolidation Guidance

**Status:** PROPOSAL  
**Rule:** Research lineage must not be erased by consolidation.

## Goal

Eunoia becomes the canonical research and runtime umbrella. Existing repositories become provenance-bearing source modules, experiments, historical records, or independent external projects depending on what they actually contain.

The target is **not** “merge 23 repositories into one.” That would destroy the distinctions that make the experiments auditable.

## Provisional classification (to be validated by code inspection)

| Repository | Initial destination | Treatment |
|------------|---------------------|-----------|
| eunoia | Core | Existing canonical root |
| sovereign-veritas | research/sovereign_veritas → eventual core components | Major extraction candidate |
| evidence-ledger | src/eunoia/evidence + provenance | Core candidate |
| veritas-science | research/veritas_science | Research framework |
| veritas-holo | research/veritas_holo | Experimental mathematical substrate |
| veritas-companion | research/veritas_companion | Efficiency experiment |
| principia-artificialis | research/principia | Broad exploratory research |
| veritas-eval-harness | research/eval_harness | Evaluation infrastructure |
| eace | research/eace | Adversarial evaluation |
| Other edge / robotics / quantum | domains/ or research/ | Needs dependency inspection |

This is a provisional map, not a claim of actual dependency boundaries.

## Binding rules

1. **Preserve provenance.** Every migrated component records origin repository, commit SHA, original path, migration commit, semantic_change flag, and parity status.
2. **Never migrate and refactor simultaneously.** Sequence: IMPORT → PARITY → VERIFY → REFACTOR → VERIFY AGAIN.
3. **Preserve negative results.** FAILED, REFUTED, INSUFFICIENT_EVIDENCE, NON-REPRODUCIBLE, SUPERSEDED remain first-class.
4. **Core stays small.** Only mechanisms with clear reusable contracts enter src/eunoia. Experiments stay under research/ or experiments/.
5. **Dependency direction is one-way.** Domains and experiments may depend on core; core must not depend on them.
6. **Ownership is decided after comparison.** Duplicate implementations remain TBD until measured.

## First implementation priority

Before moving code, build an audit tool that produces a migration manifest (repository, HEAD, languages, dependencies, tests, experiments, recommended destination, migration risk).

Only then proceed to Phase 1 inventory and Phase 2 semantic classification.

## What must not happen

- Delete old repositories immediately
- Rewrite everything into one style while importing
- Convert exploratory code into core functionality
- Collapse NOT_SUPPORTED and REFUTED
- Treat passing tests as proof of the underlying scientific claim
- Claim that consolidation has solved continuity or long-term memory
