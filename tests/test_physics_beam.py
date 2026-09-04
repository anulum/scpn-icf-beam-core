# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN ICF Beam Core — beam illumination tests

"""Tests of the illumination geometry and the range-and-energy pairs."""

from __future__ import annotations

import math

import pytest

from physics_fixtures import (
    PRINTED_CALLAHAN_CLOSE_EFFECTIVE_RADIUS_MM,
    PRINTED_CALLAHAN_CLOSE_MAJOR_SEMI_AXIS_MM,
    PRINTED_CALLAHAN_CLOSE_MINOR_SEMI_AXIS_MM,
    PRINTED_CALLAHAN_EFFECTIVE_RADIUS_MM,
    PRINTED_CALLAHAN_FOOT_BEAMS_PER_SIDE,
    PRINTED_CALLAHAN_MAIN_BEAMS_PER_SIDE,
    PRINTED_CALLAHAN_MAJOR_SEMI_AXIS_MM,
    PRINTED_CALLAHAN_MINOR_SEMI_AXIS_MM,
    PRINTED_CALLAHAN_RANGE_PAIRS,
)
from scpn_icf_beam_core.errors import DeviceConfigurationError
from scpn_icf_beam_core.physics.beam import (
    ILLUMINATION_SIDES,
    MIN_BEAMS_PER_SIDE,
    effective_spot_radius_mm,
    elliptical_spot_area_mm2,
    energy_per_beam_mj,
    range_energy_exponent,
    require_beam_count,
    spot_fluence_mj_per_mm2,
    total_beam_count,
)


def test_the_effective_radius_is_the_geometric_mean_of_the_semi_axes() -> None:
    """The definition itself, on a pair whose mean is exact.

    Semi-axes of 4 and 1 give a geometric mean of exactly 2, so this
    states the relation without a tolerance getting in the way of it.
    """
    assert effective_spot_radius_mm(4.0, 1.0) == 2.0


def test_the_effective_radius_is_the_radius_of_the_circle_of_equal_area() -> None:
    """The geometric mean is what makes the two areas agree."""
    radius = effective_spot_radius_mm(
        PRINTED_CALLAHAN_MAJOR_SEMI_AXIS_MM, PRINTED_CALLAHAN_MINOR_SEMI_AXIS_MM
    )
    ellipse = elliptical_spot_area_mm2(
        PRINTED_CALLAHAN_MAJOR_SEMI_AXIS_MM, PRINTED_CALLAHAN_MINOR_SEMI_AXIS_MM
    )
    assert math.isclose(math.pi * radius**2, ellipse, rel_tol=1e-15)


def test_both_printed_effective_radii_are_reproduced_at_their_own_precision() -> None:
    """The review's two answers come back from its own semi-axes.

    Measured, and the precision matters. The main-pulse pair gives
    2.7331300737432898, which the review prints as 2.7 — one decimal.
    The close-coupled pair gives 1.6673332000533065, which it prints as
    1.67 — two decimals. Each is reproduced at the precision it is
    printed at, and asserting equality against either printed figure
    would be asserting the rounding rather than the relation.
    """
    main = effective_spot_radius_mm(
        PRINTED_CALLAHAN_MAJOR_SEMI_AXIS_MM, PRINTED_CALLAHAN_MINOR_SEMI_AXIS_MM
    )
    close = effective_spot_radius_mm(
        PRINTED_CALLAHAN_CLOSE_MAJOR_SEMI_AXIS_MM,
        PRINTED_CALLAHAN_CLOSE_MINOR_SEMI_AXIS_MM,
    )
    assert round(main, 1) == PRINTED_CALLAHAN_EFFECTIVE_RADIUS_MM
    assert round(close, 2) == PRINTED_CALLAHAN_CLOSE_EFFECTIVE_RADIUS_MM


def test_the_semi_axes_may_be_given_in_either_order() -> None:
    """Which semi-axis is the larger depends on the focusing plane."""
    forward = effective_spot_radius_mm(4.15, 1.8)
    reversed_pair = effective_spot_radius_mm(1.8, 4.15)
    assert forward == reversed_pair


def test_the_printed_beam_counts_double_into_the_printed_totals() -> None:
    """Eight and sixteen per side are the review's sixteen and thirty-two."""
    assert total_beam_count(PRINTED_CALLAHAN_FOOT_BEAMS_PER_SIDE) == 16
    assert total_beam_count(PRINTED_CALLAHAN_MAIN_BEAMS_PER_SIDE) == 32
    assert ILLUMINATION_SIDES == 2


def test_a_cone_with_no_beam_in_it_is_refused() -> None:
    """An arrangement must illuminate something."""
    with pytest.raises(DeviceConfigurationError, match="beams_per_side"):
        require_beam_count(MIN_BEAMS_PER_SIDE - 1)


def test_the_minimum_arrangement_is_the_two_beam_one() -> None:
    """One beam per side is the arrangement the review starts from."""
    assert total_beam_count(MIN_BEAMS_PER_SIDE) == 2


def test_the_energy_is_split_equally_among_every_beam() -> None:
    """The split is over both cones, not over one."""
    assert energy_per_beam_mj(3.2, 8) == 3.2 / 16


@pytest.mark.parametrize(("energy", "beams"), [(0.0, 8), (-1.0, 8), (float("nan"), 8)])
def test_an_impossible_energy_is_refused(energy: float, beams: int) -> None:
    """A driver that delivers nothing is refused, not divided."""
    with pytest.raises(DeviceConfigurationError, match="total_energy_mj"):
        energy_per_beam_mj(energy, beams)


def test_the_spot_area_is_the_ellipse_and_not_its_bounding_circle() -> None:
    """``pi a b``, which for unequal semi-axes is not ``pi r^2``."""
    assert elliptical_spot_area_mm2(4.0, 1.0) == math.pi * 4.0


@pytest.mark.parametrize("field", ["major_semi_axis_mm", "minor_semi_axis_mm"])
def test_a_degenerate_spot_is_refused(field: str) -> None:
    """A spot with a zero semi-axis has no area to spread energy over."""
    axes = {"major_semi_axis_mm": 4.15, "minor_semi_axis_mm": 1.8}
    axes[field] = 0.0
    with pytest.raises(DeviceConfigurationError, match=field):
        elliptical_spot_area_mm2(**axes)


def test_the_fluence_is_the_energy_over_the_whole_ellipse() -> None:
    """Spot-averaged, because the review's beams are Gaussian."""
    fluence = spot_fluence_mj_per_mm2(1.0, 4.0, 1.0)
    assert fluence == 1.0 / (math.pi * 4.0)


def test_the_range_exponent_of_two_printed_pairs_is_measured() -> None:
    """The exponent joining the review's first two range pairs.

    Measured at 1.1200. It is the exponent of those two points and of
    nothing else.
    """
    (low_energy, low_range), (high_energy, high_range) = (
        PRINTED_CALLAHAN_RANGE_PAIRS[0],
        PRINTED_CALLAHAN_RANGE_PAIRS[1],
    )
    exponent = range_energy_exponent(low_energy, low_range, high_energy, high_range)
    assert math.isclose(exponent, 1.1200, abs_tol=5e-5)


def test_no_single_power_law_joins_the_three_printed_pairs() -> None:
    """The review prints three pairs and they do not lie on one line.

    Measured: 1.1200 between the first two, 1.2544 between the second
    and third, and 1.1926 across the outer two. Fitting a power law
    through them and calling it the range would be inventing a relation
    the review does not state, so this test asserts the disagreement
    instead of hiding it in a tolerance.
    """
    (first, second, third) = PRINTED_CALLAHAN_RANGE_PAIRS
    lower = range_energy_exponent(*first, *second)
    upper = range_energy_exponent(*second, *third)
    across = range_energy_exponent(*first, *third)
    assert math.isclose(upper, 1.2544, abs_tol=5e-5)
    assert math.isclose(across, 1.1926, abs_tol=5e-5)
    assert lower < across < upper
    assert upper - lower > 0.1


def test_an_unordered_pair_of_energies_is_refused() -> None:
    """Equal energies would divide by the logarithm of one."""
    with pytest.raises(DeviceConfigurationError, match="upper_energy_gev"):
        range_energy_exponent(4.0, 0.035, 4.0, 0.05)


@pytest.mark.parametrize(
    "field_name",
    [
        "lower_energy_gev",
        "lower_range_g_cm2",
        "upper_energy_gev",
        "upper_range_g_cm2",
    ],
)
def test_every_range_pair_value_must_be_positive(field_name: str) -> None:
    """A zero range or a zero energy is refused by name."""
    values = {
        "lower_energy_gev": 4.0,
        "lower_range_g_cm2": 0.035,
        "upper_energy_gev": 8.0,
        "upper_range_g_cm2": 0.08,
    }
    values[field_name] = 0.0
    with pytest.raises(DeviceConfigurationError, match=field_name):
        range_energy_exponent(**values)
