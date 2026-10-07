"""Dependency graphs and temporal validity. Memory is not implemented here."""
from __future__ import annotations

from typing import Iterable

from ..evidence import Evidence

MAX_EVIDENCE = 12


class EvidenceBudgetExceeded(ValueError):
    pass


def independent_roots(evidence: Iterable[Evidence], max_items: int = MAX_EVIDENCE) -> int:
    """Size of the largest subset whose members have pairwise disjoint root-observation sets.

    Exact (maximum set packing by search). Above max_items it raises instead of approximating: an
    approximation that overcounts would let a common-root pair pass as two independent lines."""
    items = list({e.id: e for e in evidence}.values())
    if len(items) > max_items:
        raise EvidenceBudgetExceeded(f"{len(items)} evidence items > budget {max_items}")
    roots = sorted((e.roots for e in items), key=len)

    def best(i: int, used: frozenset) -> int:
        if i == len(roots):
            return 0
        skip = best(i + 1, used)
        if roots[i] & used:
            return skip
        return max(skip, 1 + best(i + 1, used | roots[i]))

    return best(0, frozenset())
