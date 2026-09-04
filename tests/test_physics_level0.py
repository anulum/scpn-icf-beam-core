# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN ICF Beam Core — level-0 physics record tests

"""Tests of the composed level-0 physics record."""

from __future__ import annotations

import json
import math

import pytest

from physics_fixtures import (
    PRINTED_CALLAHAN_MAIN_BEAMS_PER_SIDE,
    PRINTED_HO_AREA_RATIO,
    PRINTED_HO_FUEL_INNER_RADIUS_MM,
    PRINTED_HO_FUEL_OUTER_RADIUS_MM,
    PRINTED_HO_PELLET_RADIUS_MM,
    PRINTED_HO_SYSTEM_GAIN,
    PRINTED_HO_YIELD_MJ,
    RECONSTRUCTED_HO_DRIVER_ENERGY_MJ,
    anchor_capsule,
    anchor_configuration,
    anchor_illumination,
    anchor_shot,
)
from scpn_icf_beam_core.errors import DeviceConfigurationError
from scpn_icf_beam_core.physics.level0 import (
    LEVEL0_NON_CLAIMS,
    LEVEL0_SCHEMA,
    LEVEL0_SCHEMA_VERSION,
    CapsuleDeclaration,
    IlluminationDeclaration,
    Level0Physics,
    ShotDeclaration,
    ablator_thickness_mm,
    level0_physics,
    pellet_radius_mm,
)

#: The ablator thickness the printed radii give once both have been
#: through the micrometre-to-millimetre boundary. Not 0.22.
MEASURED_ABLATOR_THICKNESS_MM = 0.21999999999999975
#: The fuel thickness the two printed radii give. Not 0.32 either.
MEASURED_FUEL_THICKNESS_MM = 0.32000000000000006


def anchor_record() -> Level0Physics:
    """Build the composed record the anchors are read from.

    Returns
    -------
    Level0Physics
        The heavy-ion design of both filed sources.
    """
    return level0_physics(
        anchor_configuration(),
        anchor_capsule(),
        anchor_illumination(),
        anchor_shot(),
    )


def test_the_pellet_radius_survives_the_unit_boundary_exactly() -> None:
    """Micrometres in, millimetres out, and back to the printed value.

    Measured before it was written: 2.34 times a thousand is exactly
    2340, and dividing it back gives exactly 2.34, so this is an
    equality rather than a bound.
    """
    assert pellet_radius_mm(anchor_configuration()) == PRINTED_HO_PELLET_RADIUS_MM


def test_neither_layer_thickness_comes_back_exactly() -> None:
    """The printed radii are decimals and their differences are not.

    Measured: the ablator is 0.21999999999999975 rather than 0.22, and
    the fuel layer 0.32000000000000006 rather than 0.32. This is the
    opposite of the sibling laser family, whose printed radii are whole
    micrometres and whose layer arithmetic is therefore exact. The
    equality was measured before it was written, it does not hold in
    either case, and these are bounds.
    """
    record = anchor_record()
    point = record.operating_point
    assert point.ablator_thickness_mm == MEASURED_ABLATOR_THICKNESS_MM
    assert point.fuel_thickness_mm == MEASURED_FUEL_THICKNESS_MM
    assert abs(point.ablator_thickness_mm - 0.22) < 1e-15
    assert abs(point.fuel_thickness_mm - 0.32) < 1e-15


def test_the_ablator_thickness_is_built_from_two_different_homes() -> None:
    """The pellet radius is the configuration's and the fuel radius is not.

    The subtraction exists in neither object, which is the point: the
    record builds it rather than being told it.
    """
    thickness = ablator_thickness_mm(anchor_configuration(), anchor_capsule())
    assert thickness == (PRINTED_HO_PELLET_RADIUS_MM - PRINTED_HO_FUEL_OUTER_RADIUS_MM)


def test_a_fuel_layer_that_reaches_the_surface_is_refused() -> None:
    """A capsule with no ablator is not the one the configuration declares."""
    with pytest.raises(DeviceConfigurationError, match="no ablator"):
        ablator_thickness_mm(
            anchor_configuration(),
            CapsuleDeclaration(
                ablator_density_g_cm3=1.85,
                fuel_outer_radius_mm=PRINTED_HO_PELLET_RADIUS_MM,
                fuel_inner_radius_mm=1.8,
                fuel_density_g_cm3=0.25,
                vapour_density_g_cm3=0.3e-3,
            ),
        )


def test_a_fuel_layer_outside_the_pellet_is_refused() -> None:
    """Beyond the surface is refused in the same direction as at it."""
    with pytest.raises(DeviceConfigurationError, match="no ablator"):
        ablator_thickness_mm(
            anchor_configuration(),
            CapsuleDeclaration(
                ablator_density_g_cm3=1.85,
                fuel_outer_radius_mm=3.0,
                fuel_inner_radius_mm=1.8,
                fuel_density_g_cm3=0.25,
                vapour_density_g_cm3=0.3e-3,
            ),
        )


def test_the_record_carries_the_measured_inventory_and_the_implied_fraction() -> None:
    """The three masses and the burn-up fraction the yield implies."""
    point = anchor_record().operating_point
    assert math.isclose(point.ablator_mass_mg, 25.45458943737721, rel_tol=1e-12)
    assert math.isclose(point.fuel_mass_mg, 3.870576190509178, rel_tol=1e-12)
    assert math.isclose(point.vapour_mass_mg, 0.00732870734229427, rel_tol=1e-12)
    assert point.fuel_inventory_mg == point.fuel_mass_mg + point.vapour_mass_mg
    assert math.isclose(point.burnup_fraction, 0.3285724982472429, rel_tol=1e-12)


def test_the_record_carries_the_illumination_the_review_prints() -> None:
    """Thirty-two beams, and the energy each of them carries."""
    point = anchor_record().operating_point
    assert point.total_beam_count == 2 * PRINTED_CALLAHAN_MAIN_BEAMS_PER_SIDE
    assert point.energy_per_beam_mj == (
        RECONSTRUCTED_HO_DRIVER_ENERGY_MJ / point.total_beam_count
    )
    assert math.isclose(
        point.effective_spot_radius_mm, 2.7331300737432898, rel_tol=1e-12
    )


def test_the_system_gain_is_a_round_trip_and_is_not_an_anchor() -> None:
    """The driver energy was reconstructed from this gain, so it returns it.

    Neither source prints the driver energy of this design. It is
    obtained by dividing the printed yield by the printed system gain,
    which means recovering that gain from it proves arithmetic and
    nothing about the design. The test exists to say so, and the
    fixtures name the value ``RECONSTRUCTED_`` for the same reason.
    """
    point = anchor_record().operating_point
    assert math.isclose(point.target_gain, PRINTED_HO_SYSTEM_GAIN, rel_tol=1e-12)
    assert RECONSTRUCTED_HO_DRIVER_ENERGY_MJ == (
        PRINTED_HO_YIELD_MJ / PRINTED_HO_SYSTEM_GAIN
    )


def test_the_record_carries_the_conversion_efficiency_the_chain_requires() -> None:
    """Measured at 0.8859, which the review plots and never prints."""
    point = anchor_record().operating_point
    assert math.isclose(
        point.implied_conversion_efficiency, 0.8859357696567, rel_tol=1e-12
    )


def test_the_record_carries_the_enclosure_the_area_ratio_implies() -> None:
    """The equivalent sphere, and its area against the capsule's."""
    point = anchor_record().operating_point
    assert math.isclose(
        point.enclosure_area_mm2 * PRINTED_HO_AREA_RATIO,
        point.capsule_area_mm2,
        rel_tol=1e-12,
    )
    assert math.isclose(
        point.equivalent_enclosure_radius_mm, 8.54447189708059, rel_tol=1e-12
    )


@pytest.mark.parametrize("identifier", ["ion_beam_icf", "pulsed_electron_beam_icf"])
def test_every_owned_configuration_composes_a_record(identifier: str) -> None:
    """The relations are generic even where the anchors are not.

    Nothing in the composition is ion-specific: masses, gains and
    fluences do not know what the beam is made of. What is ion-specific
    is the evidence, and the record's non-claims carry that boundary
    rather than a refusal here.
    """
    record = level0_physics(
        anchor_configuration(identifier=identifier),
        anchor_capsule(),
        anchor_illumination(),
        anchor_shot(),
    )
    assert record.operating_point.fuel_inventory_mg > 0.0


def test_the_non_claims_state_that_the_sources_are_ion_only() -> None:
    """The boundary is written into the record a consumer receives."""
    assert any("heavy-ion drivers" in claim for claim in LEVEL0_NON_CLAIMS)
    assert any("implied by" in claim for claim in LEVEL0_NON_CLAIMS)


@pytest.mark.parametrize(
    "field_name",
    [
        "ablator_density_g_cm3",
        "fuel_outer_radius_mm",
        "fuel_inner_radius_mm",
        "fuel_density_g_cm3",
        "vapour_density_g_cm3",
    ],
)
def test_every_capsule_field_must_be_positive(field_name: str) -> None:
    """Each declared quantity is refused by its own name."""
    values = dict(anchor_capsule().to_record())
    values[field_name] = 0.0
    with pytest.raises(DeviceConfigurationError, match=field_name):
        CapsuleDeclaration(**values)


def test_a_capsule_whose_fuel_radii_are_not_ordered_is_refused() -> None:
    """The fuel layer's outer boundary must be outside its inner one."""
    values = dict(anchor_capsule().to_record())
    values["fuel_inner_radius_mm"] = values["fuel_outer_radius_mm"]
    with pytest.raises(DeviceConfigurationError, match="must exceed"):
        CapsuleDeclaration(**values)


@pytest.mark.parametrize("field_name", ["major_semi_axis_mm", "minor_semi_axis_mm"])
def test_every_illumination_semi_axis_must_be_positive(field_name: str) -> None:
    """A degenerate spot is refused where it is declared."""
    values = dict(anchor_illumination().to_record())
    values[field_name] = 0.0
    with pytest.raises(DeviceConfigurationError, match=field_name):
        IlluminationDeclaration(**values)


def test_an_illumination_without_beams_is_refused() -> None:
    """The beam count is validated where it is declared."""
    values = dict(anchor_illumination().to_record())
    values["beams_per_side"] = 0
    with pytest.raises(DeviceConfigurationError, match="beams_per_side"):
        IlluminationDeclaration(**values)


@pytest.mark.parametrize(
    ("field_name", "value"),
    [
        ("absorbed_energy_mj", 0.0),
        ("yield_mj", 0.0),
        ("coupling_efficiency", 0.0),
        ("coupling_efficiency", 1.5),
        ("capsule_to_enclosure_area_ratio", 0.0),
        ("capsule_to_enclosure_area_ratio", 1.5),
    ],
)
def test_every_shot_field_is_validated_where_it_is_declared(
    field_name: str, value: float
) -> None:
    """A record can never be built from a set the relations would refuse."""
    values = dict(anchor_shot().to_record())
    values[field_name] = value
    with pytest.raises(DeviceConfigurationError, match=field_name):
        ShotDeclaration(**values)


def test_the_fuel_thickness_helper_agrees_with_the_record() -> None:
    """One relation, one home."""
    capsule = anchor_capsule()
    assert capsule.fuel_thickness_mm() == (
        PRINTED_HO_FUEL_OUTER_RADIUS_MM - PRINTED_HO_FUEL_INNER_RADIUS_MM
    )


def test_the_record_states_its_schema_and_its_non_claims() -> None:
    """The serialised record carries what a consumer needs to read it."""
    record = anchor_record().to_record()
    assert record["schema"] == LEVEL0_SCHEMA
    assert record["schema_version"] == LEVEL0_SCHEMA_VERSION
    assert record["non_claims"] == list(LEVEL0_NON_CLAIMS)
    assert set(record) == {
        "schema",
        "schema_version",
        "configuration_digest_sha256",
        "capsule",
        "illumination",
        "shot",
        "operating_point",
        "non_claims",
    }


def test_the_canonical_bytes_are_sorted_and_newline_terminated() -> None:
    """The record serialises the way every other record here does."""
    data = anchor_record().canonical_bytes()
    assert data.endswith(b"\n")
    decoded = json.loads(data)
    assert list(decoded) == sorted(decoded)
    reencoded = json.dumps(decoded, sort_keys=True, separators=(",", ":")) + "\n"
    assert data == reencoded.encode("utf-8")


def test_the_digest_identifies_the_exact_record() -> None:
    """The same declarations digest the same; a different shot does not."""
    assert anchor_record().digest_sha256() == anchor_record().digest_sha256()
    other = level0_physics(
        anchor_configuration(),
        anchor_capsule(),
        anchor_illumination(),
        ShotDeclaration(
            absorbed_energy_mj=1.0,
            yield_mj=400.0,
            coupling_efficiency=0.21,
            capsule_to_enclosure_area_ratio=0.075,
        ),
    )
    assert other.digest_sha256() != anchor_record().digest_sha256()


def test_the_record_carries_the_digest_of_the_configuration_it_was_built_from() -> None:
    """A record names its input rather than restating it."""
    configuration = anchor_configuration()
    record = level0_physics(
        configuration, anchor_capsule(), anchor_illumination(), anchor_shot()
    )
    assert record.configuration_digest_sha256 == configuration.digest_sha256()
