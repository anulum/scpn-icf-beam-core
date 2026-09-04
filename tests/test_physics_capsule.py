# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN ICF Beam Core — capsule inventory tests

"""Tests of the mass inventory and the energy its fuel can release."""

from __future__ import annotations

import math

import pytest

from physics_fixtures import (
    PRINTED_HO_ABLATOR_DENSITY_G_CM3,
    PRINTED_HO_FUEL_DENSITY_G_CM3,
    PRINTED_HO_FUEL_INNER_RADIUS_MM,
    PRINTED_HO_FUEL_OUTER_RADIUS_MM,
    PRINTED_HO_PELLET_RADIUS_MM,
    PRINTED_HO_VAPOUR_DENSITY_G_CM3,
    PRINTED_HO_YIELD_MJ,
)
from scpn_icf_beam_core.errors import DeviceConfigurationError
from scpn_icf_beam_core.physics.capsule import (
    DT_FUSION_ENERGY_MEV,
    areal_density_g_cm2,
    burnup_from_yield,
    dt_specific_energy_j_per_g,
    fusion_yield_mj,
    require_fraction,
    shell_mass_mg,
    sphere_mass_mg,
)

#: The inventory of the filed design, measured from its printed radii
#: and densities. Milligrams.
MEASURED_FUEL_MASS_MG = 3.870576190509178
MEASURED_VAPOUR_MASS_MG = 0.00732870734229427
MEASURED_ABLATOR_MASS_MG = 25.45458943737721
#: The burn-up fraction the printed yield implies for that inventory.
MEASURED_BURNUP_FRACTION = 0.32857249824724294


def test_the_specific_energy_is_built_from_the_masses_and_the_release() -> None:
    """The constant is derived, not typed.

    Measured at 3.3747e11 J/g. It is a definition, not a claim: one
    deuteron and one triton release 17.59 MeV, so a gram of equimolar
    fuel carries one pair per combined nuclear mass.
    """
    assert math.isclose(dt_specific_energy_j_per_g(), 3.3747e11, rel_tol=1e-4)
    assert DT_FUSION_ENERGY_MEV == 17.59


def test_the_three_layer_masses_are_recovered_from_the_printed_capsule() -> None:
    """Every mass comes out of radii and densities the review prints."""
    ablator = shell_mass_mg(
        PRINTED_HO_PELLET_RADIUS_MM,
        PRINTED_HO_FUEL_OUTER_RADIUS_MM,
        PRINTED_HO_ABLATOR_DENSITY_G_CM3,
    )
    fuel = shell_mass_mg(
        PRINTED_HO_FUEL_OUTER_RADIUS_MM,
        PRINTED_HO_FUEL_INNER_RADIUS_MM,
        PRINTED_HO_FUEL_DENSITY_G_CM3,
    )
    vapour = sphere_mass_mg(
        PRINTED_HO_FUEL_INNER_RADIUS_MM, PRINTED_HO_VAPOUR_DENSITY_G_CM3
    )
    assert math.isclose(ablator, MEASURED_ABLATOR_MASS_MG, rel_tol=1e-12)
    assert math.isclose(fuel, MEASURED_FUEL_MASS_MG, rel_tol=1e-12)
    assert math.isclose(vapour, MEASURED_VAPOUR_MASS_MG, rel_tol=1e-12)


def test_the_ablator_outweighs_the_fuel_it_carries() -> None:
    """A beryllium ablator is most of the capsule's mass.

    Measured: 25.45 mg of ablator against 3.88 mg of fuel and vapour
    together, a factor of 6.6. It is asserted because it is the sanity
    check a reader of the record makes first.
    """
    assert MEASURED_ABLATOR_MASS_MG > 6.0 * (
        MEASURED_FUEL_MASS_MG + MEASURED_VAPOUR_MASS_MG
    )


def test_the_vapour_is_a_thousandth_of_the_solid_fuel() -> None:
    """The cavity holds fuel, and almost none of the inventory."""
    assert MEASURED_VAPOUR_MASS_MG < MEASURED_FUEL_MASS_MG / 500.0


def test_a_shell_of_zero_thickness_is_refused() -> None:
    """Equal radii would be a zero mass reported as a shell."""
    with pytest.raises(DeviceConfigurationError, match="outer_radius_mm"):
        shell_mass_mg(2.12, 2.12, 0.25)


def test_an_inverted_shell_is_refused() -> None:
    """A negative thickness would be a negative mass."""
    with pytest.raises(DeviceConfigurationError, match="must exceed"):
        shell_mass_mg(1.8, 2.12, 0.25)


@pytest.mark.parametrize(
    ("outer", "inner", "density", "field"),
    [
        (0.0, 1.0, 0.25, "outer_radius_mm"),
        (2.12, 0.0, 0.25, "inner_radius_mm"),
        (2.12, 1.8, 0.0, "density_g_cm3"),
    ],
)
def test_every_shell_input_must_be_positive(
    outer: float, inner: float, density: float, field: str
) -> None:
    """Each is refused by its own name."""
    with pytest.raises(DeviceConfigurationError, match=field):
        shell_mass_mg(outer, inner, density)


@pytest.mark.parametrize(
    ("radius", "density", "field"),
    [(0.0, 0.25, "radius_mm"), (1.8, 0.0, "density_g_cm3")],
)
def test_every_sphere_input_must_be_positive(
    radius: float, density: float, field: str
) -> None:
    """A sphere needs a radius and a density, both positive."""
    with pytest.raises(DeviceConfigurationError, match=field):
        sphere_mass_mg(radius, density)


def test_the_printed_yield_implies_a_burn_up_fraction_the_review_never_prints() -> None:
    """The direction the source forces, and the number it gives.

    Measured at 0.3286 of the inventory. The review prints 430 MJ and
    never says what fraction of its fuel burned, so this is the only
    direction available and the record labels the result as implied.
    """
    inventory = MEASURED_FUEL_MASS_MG + MEASURED_VAPOUR_MASS_MG
    fraction = burnup_from_yield(PRINTED_HO_YIELD_MJ, inventory)
    assert math.isclose(fraction, MEASURED_BURNUP_FRACTION, rel_tol=1e-12)


def test_the_implied_fraction_returns_the_printed_yield() -> None:
    """Yield and burn-up are inverses of each other, and close."""
    inventory = MEASURED_FUEL_MASS_MG + MEASURED_VAPOUR_MASS_MG
    fraction = burnup_from_yield(PRINTED_HO_YIELD_MJ, inventory)
    assert math.isclose(
        fusion_yield_mj(inventory, fraction), PRINTED_HO_YIELD_MJ, rel_tol=1e-12
    )


def test_a_full_burn_of_the_inventory_is_four_hundred_times_the_yield_scale() -> None:
    """The inventory could release far more than the design does.

    Measured: 1308.7 MJ on a complete burn against the printed 430 MJ.
    Stating the ceiling is what makes the implied fraction readable.
    """
    inventory = MEASURED_FUEL_MASS_MG + MEASURED_VAPOUR_MASS_MG
    assert math.isclose(fusion_yield_mj(inventory, 1.0), 1308.7, rel_tol=1e-4)


def test_a_burn_up_fraction_above_one_is_refused() -> None:
    """More cannot be consumed than exists."""
    with pytest.raises(DeviceConfigurationError, match=r"must not exceed 1\.0"):
        fusion_yield_mj(3.88, 1.5)


def test_a_burn_up_fraction_of_exactly_one_is_admitted() -> None:
    """A complete burn is a bound, not an error."""
    assert require_fraction("burnup_fraction", 1.0) == 1.0


@pytest.mark.parametrize(
    ("mass", "fraction", "field"),
    [(0.0, 0.3, "fuel_mass_mg"), (3.88, 0.0, "burnup_fraction")],
)
def test_every_yield_input_must_be_positive(
    mass: float, fraction: float, field: str
) -> None:
    """A zero inventory or a zero burn releases nothing to compute."""
    with pytest.raises(DeviceConfigurationError, match=field):
        fusion_yield_mj(mass, fraction)


@pytest.mark.parametrize(
    ("yield_mj", "mass", "field"),
    [(0.0, 3.88, "yield_mj"), (430.0, 0.0, "fuel_mass_mg")],
)
def test_every_burn_up_input_must_be_positive(
    yield_mj: float, mass: float, field: str
) -> None:
    """The inverse relation validates its own inputs too."""
    with pytest.raises(DeviceConfigurationError, match=field):
        burnup_from_yield(yield_mj, mass)


def test_an_implied_fraction_above_one_is_returned_rather_than_refused() -> None:
    """A yield an inventory cannot produce is an answer, not an error.

    The relation is a measurement of two declared numbers. Refusing it
    would hide the finding that they disagree; returning it lets the
    caller decide.
    """
    assert burnup_from_yield(PRINTED_HO_YIELD_MJ, 0.1) > 1.0


def test_the_areal_density_is_the_density_times_the_path() -> None:
    """Grams per square centimetre from millimetres and g/cm3.

    The fuel layer of the filed design is 0.32 mm of 0.25 g/cm3, which
    is 0.008 g/cm2.
    """
    thickness = PRINTED_HO_FUEL_OUTER_RADIUS_MM - PRINTED_HO_FUEL_INNER_RADIUS_MM
    assert math.isclose(
        areal_density_g_cm2(thickness, PRINTED_HO_FUEL_DENSITY_G_CM3),
        0.008,
        rel_tol=1e-12,
    )


@pytest.mark.parametrize(
    ("path", "density", "field"),
    [(0.0, 0.25, "path_length_mm"), (0.32, 0.0, "density_g_cm3")],
)
def test_every_areal_density_input_must_be_positive(
    path: float, density: float, field: str
) -> None:
    """A zero path or a zero density is refused by name."""
    with pytest.raises(DeviceConfigurationError, match=field):
        areal_density_g_cm2(path, density)
