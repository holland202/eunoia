"""
Exact threshold comparison (Amendment 1, Item 3).
If the scientific claim depends on an exact boundary, the computational
representation must preserve that boundary.
Synthetic demonstration only.
"""

from fractions import Fraction
from enum import Enum


class Bound(Enum):
    INCLUSIVE = "inclusive"  # >=
    EXCLUSIVE = "exclusive"  # >


def compare(score, baseline, bound, kind: Bound) -> bool:
    score = Fraction(score)
    baseline = Fraction(baseline)
    bound = Fraction(bound)
    diff = score - baseline
    if kind is Bound.INCLUSIVE:
        return diff >= bound
    return diff > bound


if __name__ == "__main__":
    assert Fraction(8, 20) - Fraction(7, 20) == Fraction(1, 20)
    assert compare(Fraction(8, 20), Fraction(7, 20), Fraction(1, 20), Bound.INCLUSIVE) is True
    assert compare(Fraction(8, 20), Fraction(7, 20), Fraction(1, 20), Bound.EXCLUSIVE) is False
