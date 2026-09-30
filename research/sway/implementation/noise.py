"""
Same-input noise screening (Amendment 1, Item 4).
Screening rule only: not a power analysis, not a hypothesis test, not an alpha level.
spread = max(Y) - min(Y) over n >= 3 runs of the same input.
If the registered tolerance is smaller than the spread, the bound is UNRESOLVABLE at this n.
Scores are exact (int, Fraction or decimal string); floats are refused, as in exact_threshold.
Synthetic demonstration only.
"""

from fractions import Fraction

try:
    from .exact_threshold import exact
except ImportError:  # run as a script
    from exact_threshold import exact


def measure_spread(scores):
    scores = [exact(s) for s in scores]
    if len(scores) < 3:  # a real check, not an assert: asserts vanish under python -O
        raise ValueError(f"need at least 3 runs of the same input, got {len(scores)}")
    return max(scores) - min(scores)


def resolvable(bound, spread) -> bool:
    return exact(bound) >= exact(spread)


if __name__ == "__main__":
    # C006b: the same prompt 3 times at temperature 0 scored 13, 15 and 14 of 20 on one question type
    s = measure_spread([Fraction(13, 20), Fraction(15, 20), Fraction(14, 20)])
    print("spread", s, "| 0.05 resolvable:", resolvable("0.05", s), "| 1/60 resolvable:", resolvable(Fraction(1, 60), s))
