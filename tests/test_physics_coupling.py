# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN ICF Beam Core — coupling chain tests

"""Tests of the chain of efficiencies between a beam and a yield."""

from __future__ import annotations

import math

import pytest

from physics_fixtures import (
    PRINTED_CALLAHAN_CASES,
    PRINTED_HO_ABSORBED_ENERGY_MJ,
    PRINTED_HO_AREA_RATIO,
    PRINTED_HO_COUPLING_EFFICIENCY,
    PRINTED_HO_PELLET_RADIUS_MM,
    PRINTED_HO_SYSTEM_GAIN,
    PRINTED_HO_YIELD_MJ,
)
from scpn_icf_beam_core.errors import DeviceConfigurationError
from scpn_icf_beam_core.physics.coupling import (
    absorbed_energy_mj,
    capsule_gain,
    enclosure_area_mm2,
    equivalent_enclosure_radius_mm,
    implied_conversion_efficiency,
    require_species,
    sphere_area_mm2,
    target_gain,
)

#: The conversion efficiency the review's own four numbers require.
MEASURED_IMPLIED_CONVERSION_EFFICIENCY = 0.8859357696567


def test_the_printed_capsule_gain_is_exact_from_the_printed_energies() -> None:
    """430 megajoules out of 1 megajoule absorbed is a gain of 430.

    Both are printed and their quotient is exact in binary, so this is
    an equality.
    """
    assert capsule_gain(PRINTED_HO_YIELD_MJ, PRINTED_HO_ABSORBED_ENERGY_MJ) == 430.0


def test_the_chain_closes_only_at_a_conversion_efficiency_the_review_plots() -> None:
    """What the four printed numbers require of the fifth.

    The review prints a yield of 430 MJ, an absorbed energy of about
    1 MJ, a coupling efficiency of 21 % and a system gain of up to 80.
    Those four fix the conversion efficiency: measured, the chain closes
    at 0.8859. The review plots that efficiency against converter radius
    in a figure and never prints a number for it, so this is a
    requirement its own numbers impose and not a value reproduced from
    it.
    """
    efficiency = implied_conversion_efficiency(
        PRINTED_HO_SYSTEM_GAIN,
        capsule_gain(PRINTED_HO_YIELD_MJ, PRINTED_HO_ABSORBED_ENERGY_MJ),
        PRINTED_HO_COUPLING_EFFICIENCY,
    )
    assert math.isclose(
        efficiency, MEASURED_IMPLIED_CONVERSION_EFFICIENCY, rel_tol=1e-12
    )
    assert efficiency < 1.0


def test_the_factorisation_is_consistent_in_both_directions() -> None:
    """Absorbed energy and the gain chain agree by construction."""
    capsule = capsule_gain(PRINTED_HO_YIELD_MJ, PRINTED_HO_ABSORBED_ENERGY_MJ)
    conversion = implied_conversion_efficiency(
        PRINTED_HO_SYSTEM_GAIN, capsule, PRINTED_HO_COUPLING_EFFICIENCY
    )
    driver = PRINTED_HO_YIELD_MJ / PRINTED_HO_SYSTEM_GAIN
    absorbed = absorbed_energy_mj(driver, conversion, PRINTED_HO_COUPLING_EFFICIENCY)
    assert math.isclose(absorbed, PRINTED_HO_ABSORBED_ENERGY_MJ, rel_tol=1e-12)
    assert math.isclose(
        target_gain(PRINTED_HO_YIELD_MJ, driver),
        PRINTED_HO_SYSTEM_GAIN,
        rel_tol=1e-12,
    )


def test_every_printed_gain_of_the_illumination_review_is_a_truncation() -> None:
    """Its three printed gains are floors of its own quotients.

    Measured: 370/6.35 is 58.2677 and it prints 58; 413/7.4 is 55.8108
    and it prints 55; 436/3.3 is 132.1212 and it prints 132. All three
    are the floor. The middle one is **not** the rounded value — 55.8108
    rounds to 56 — so the review truncates rather than rounds, and a
    test that asserted rounding would have failed on it.
    """
    for driver, released, printed in PRINTED_CALLAHAN_CASES:
        computed = target_gain(released, driver)
        if printed is None:
            continue
        assert math.floor(computed) == printed
    middle = target_gain(413.0, 7.4)
    assert round(middle) != 55
    assert math.floor(middle) == 55


def test_the_case_without_a_printed_gain_is_left_without_one() -> None:
    """The review prints a yield and a driver energy and no gain here.

    Measured at 66.10. It is computed and recorded, and nothing is
    attributed to the review that the review does not say.
    """
    driver, released, printed = PRINTED_CALLAHAN_CASES[3]
    assert printed is None
    assert math.isclose(target_gain(released, driver), 66.1017, abs_tol=5e-5)


def test_the_printed_area_ratio_fixes_an_equivalent_enclosure_radius() -> None:
    """The only length a bare area ratio determines.

    Measured: a capsule of 2.34 mm at a capsule-to-enclosure area ratio
    of 0.075 gives a sphere of 8.544 mm. A real enclosure is a cylinder
    with converters and shields in it, so this is not its radius; it is
    the radius of the sphere of equal area, which is what makes the
    printed ratio comparable at all.
    """
    radius = equivalent_enclosure_radius_mm(
        PRINTED_HO_PELLET_RADIUS_MM, PRINTED_HO_AREA_RATIO
    )
    assert math.isclose(radius, 8.54447189708059, rel_tol=1e-12)
    capsule_area = sphere_area_mm2(PRINTED_HO_PELLET_RADIUS_MM)
    assert math.isclose(
        sphere_area_mm2(radius),
        enclosure_area_mm2(capsule_area, PRINTED_HO_AREA_RATIO),
        rel_tol=1e-12,
    )


def test_the_two_families_area_ratios_are_not_the_same_quantity() -> None:
    """The ion ratio's reciprocal is not the laser family's band.

    The ion review prints capsule-to-enclosure 0.075, whose reciprocal
    is 13.33. The laser family's filed precursor prints
    enclosure-to-capsule 15 to 25. They are different quantities in
    different drive schemes; 13.33 lying below 15 is not an error to be
    reconciled, and neither figure is used to check the other. The
    assertion here is only that they do disagree, so that nobody later
    treats the two as one number.
    """
    reciprocal = 1.0 / PRINTED_HO_AREA_RATIO
    assert math.isclose(reciprocal, 13.333333333333334, rel_tol=1e-12)
    assert reciprocal < 15.0


def test_an_enclosure_smaller_than_its_capsule_is_refused() -> None:
    """A ratio above one puts the capsule outside the case."""
    with pytest.raises(DeviceConfigurationError, match="area_ratio"):
        enclosure_area_mm2(68.8, 1.5)


def test_an_area_ratio_of_exactly_one_is_admitted() -> None:
    """A capsule filling its enclosure is a bound, not an error."""
    assert enclosure_area_mm2(68.8, 1.0) == 68.8


@pytest.mark.parametrize(
    ("system", "capsule", "coupling", "field"),
    [
        (0.0, 430.0, 0.21, "system_gain"),
        (80.0, 0.0, 0.21, "capsule_gain_value"),
        (80.0, 430.0, 0.0, "coupling_efficiency"),
        (80.0, 430.0, 1.5, "coupling_efficiency"),
    ],
)
def test_every_chain_input_is_validated_by_name(
    system: float, capsule: float, coupling: float, field: str
) -> None:
    """Each refusal names the quantity that failed."""
    with pytest.raises(DeviceConfigurationError, match=field):
        implied_conversion_efficiency(system, capsule, coupling)


def test_an_implied_efficiency_above_one_is_returned_rather_than_refused() -> None:
    """Three numbers that cannot describe one design say so.

    A system gain of 400 against a capsule gain of 430 at 21 % coupling
    would need a conversion efficiency of 4.4. Returning it is what
    makes the contradiction visible.
    """
    assert implied_conversion_efficiency(400.0, 430.0, 0.21) > 1.0


@pytest.mark.parametrize(
    ("driver", "conversion", "coupling", "field"),
    [
        (0.0, 0.9, 0.21, "driver_energy_mj"),
        (5.4, 0.0, 0.21, "conversion_efficiency"),
        (5.4, 1.5, 0.21, "conversion_efficiency"),
        (5.4, 0.9, 0.0, "coupling_efficiency"),
    ],
)
def test_every_absorbed_energy_input_is_validated_by_name(
    driver: float, conversion: float, coupling: float, field: str
) -> None:
    """The forward direction validates the same way the inverse does."""
    with pytest.raises(DeviceConfigurationError, match=field):
        absorbed_energy_mj(driver, conversion, coupling)


@pytest.mark.parametrize(
    ("released", "reference", "field"),
    [(0.0, 1.0, "yield_mj"), (430.0, 0.0, "absorbed_energy_mj")],
)
def test_capsule_gain_validates_both_energies(
    released: float, reference: float, field: str
) -> None:
    """A gain needs two positive energies."""
    with pytest.raises(DeviceConfigurationError, match=field):
        capsule_gain(released, reference)


@pytest.mark.parametrize(
    ("released", "reference", "field"),
    [(0.0, 5.4, "yield_mj"), (430.0, 0.0, "driver_energy_mj")],
)
def test_target_gain_validates_both_energies(
    released: float, reference: float, field: str
) -> None:
    """The system gain validates its own inputs too."""
    with pytest.raises(DeviceConfigurationError, match=field):
        target_gain(released, reference)


def test_a_zero_radius_has_no_area() -> None:
    """The sphere area refuses a degenerate radius."""
    with pytest.raises(DeviceConfigurationError, match="radius_mm"):
        sphere_area_mm2(0.0)


@pytest.mark.parametrize(
    ("capsule_radius", "ratio", "field"),
    [(0.0, 0.075, "capsule_radius_mm"), (2.34, 0.0, "area_ratio")],
)
def test_the_equivalent_radius_validates_its_inputs(
    capsule_radius: float, ratio: float, field: str
) -> None:
    """Both a radius and a ratio are required, both in range."""
    with pytest.raises(DeviceConfigurationError, match=field):
        equivalent_enclosure_radius_mm(capsule_radius, ratio)


def test_a_relation_stated_for_ions_refuses_an_electron_driver() -> None:
    """Neither filed source describes an electron beam.

    Both are heavy-ion papers. Carrying their efficiencies across to the
    electron-beam configuration would move a number past the boundary
    its source drew, so the guard exists and is exercised.
    """
    assert require_species("ion", "ion") == "ion"
    with pytest.raises(DeviceConfigurationError, match="stated for"):
        require_species("electron", "ion")
