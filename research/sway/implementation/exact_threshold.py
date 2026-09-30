"""
Exact threshold comparison (Amendment 1, Item 3).
If the scientific claim depends on an exact boundary, the computational
representation must preserve that boundary.

Inputs must be exact: int, Fraction, or a decimal string such as "0.05". A float is
refused (TypeError), because Fraction(0.05) is the binary float 0.05000000000000000277...,
the same class of error Item 3 exists to prevent. Synthetic demonstration only.
"""

from enum import Enum
from fractions import Fraction


class Bound(Enum):
    INCLUSIVE = "inclusive"  # >=
    EXCLUSIVE = "exclusive"  # >


def exact(x) -> Fraction:
    if isinstance(x, bool) or isinstance(x, float):
        raise TypeError(f"refusing {type(x).__name__} {x!r}: pass an int, Fraction or decimal string")
    if isinstance(x, (int, Fraction, str)):
        return Fraction(x)
    raise TypeError(f"refusing {type(x).__name__}")


def compare(score, baseline, bound, kind: Bound) -> bool:
    diff = exact(score) - exact(baseline)
    b = exact(bound)
    if kind is Bound.INCLUSIVE:
        return diff >= b
    if kind is Bound.EXCLUSIVE:
        return diff > b
    raise ValueError(f"unknown bound kind {kind!r}")


if __name__ == "__main__":
    print("float:", 8 / 20 - 7 / 20, "<= 0.05 ->", 8 / 20 - 7 / 20 <= 0.05)
    print("exact:", exact("8/20") - exact("7/20"), "inclusive ->",
          compare(Fraction(8, 20), Fraction(7, 20), "1/20", Bound.INCLUSIVE))
