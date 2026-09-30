"""
Same-input noise screening (Amendment 1, Item 4).
Screening rule only — not a power analysis, not a conventional hypothesis
test, not an α-level assignment.
spread = max(Y) - min(Y) for n >= 3
If registered tolerance < spread → UNRESOLVABLE at this n.
Synthetic demonstration only.
"""


def measure_spread(scores):
    assert len(scores) >= 3
    return max(scores) - min(scores)


def resolvable(bound, spread) -> bool:
    return bound >= spread


if __name__ == "__main__":
    scores = [13 / 20, 14 / 20, 15 / 20]
    spread = measure_spread(scores)
    assert abs(spread - 0.10) < 1e-12
    assert not resolvable(0.05, spread)
    assert not resolvable(1 / 60, spread)
