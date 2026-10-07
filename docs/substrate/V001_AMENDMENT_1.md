# V001 Amendment 1 — derived evidence inherits its ancestors' validity

**Status:** registered before any V001 code was run or any test executed. `V001_PREREG.md` is
unchanged.

**What prompted it.** While writing `Evidence`, before running anything: under the registered
definition ("valid at `t` iff `valid_from <= t < valid_until`", on the item alone), an item derived
from stale evidence can carry a fresh interval of its own. Deriving one new item from expired
evidence would then restore its validity: staleness laundering, the temporal form of the
"common-root independent source" problem P5 already targets.

**Change.** An `Evidence` item is valid at `t` iff `valid_from <= t < valid_until` holds for it
**and for every ancestor it is derived from** (the intersection of the intervals on its derivation
paths). Observations carry no interval of their own. Nothing else in the registration changes.

**Added prediction.**

| ID | Prediction | Refuted if |
|---|---|---|
| P13 | Evidence `S` valid on `[0, 10)`, and `D` derived from `S` with interval `[0, 100)`: at `t = 50`, `D` is not valid and the Gate DEFERs with `insufficient_independent_evidence`; at `t = 5` it is valid and the Gate ALLOWs | `D` counts as valid at 50 |
