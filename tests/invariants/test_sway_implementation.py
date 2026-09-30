"""Killers for the two Amendment 1 helpers: each guard has an attack that must flip it."""
from fractions import Fraction

import pytest

from research.sway.implementation.exact_threshold import Bound, compare, exact
from research.sway.implementation.noise import measure_spread, resolvable


def test_the_c006b_boundary_case_is_held_exactly():
    # in floats 8/20 - 7/20 = 0.050000000000000044 > 0.05, which printed FAILED in C006b
    assert 8 / 20 - 7 / 20 > 0.05
    assert compare(Fraction(8, 20), Fraction(7, 20), "0.05", Bound.INCLUSIVE) is True
    assert compare(Fraction(8, 20), Fraction(7, 20), "0.05", Bound.EXCLUSIVE) is False


@pytest.mark.parametrize("bad", [0.05, True, None, [1]])
def test_inexact_inputs_are_refused(bad):
    with pytest.raises(TypeError):
        exact(bad)


def test_noise_needs_three_runs_even_under_optimisation():
    with pytest.raises(ValueError):
        measure_spread(["13/20", "14/20"])


def test_bound_inside_noise_is_unresolvable_and_outside_is_resolvable():
    s = measure_spread([Fraction(13, 20), Fraction(15, 20), Fraction(14, 20)])
    assert s == Fraction(1, 10)
    assert not resolvable("0.05", s) and not resolvable(Fraction(1, 60), s)
    assert resolvable("0.10", s) and resolvable("0.25", s)
