# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN ICF Beam Core — tier-G1 device model tests

"""Tests of the tessellated device model.

Reproducing a printed value is an anchor, never a claim about that
machine.
"""

from __future__ import annotations

import dataclasses
import json

import pytest

from geometry_fixtures import (
    ANCHOR_CAVITY_RADIUS_M,
    ANCHOR_FUEL_OUTER_RADIUS_M,
    ANCHOR_PELLET_RADIUS_M,
    ANCHOR_RINGS,
    ANCHOR_SEGMENTS,
    PRINTED_HO_FUEL_INNER_RADIUS_MM,
    PRINTED_HO_FUEL_OUTER_RADIUS_MM,
    PRINTED_HO_PELLET_RADIUS_MM,
    anchor_capsule,
    anchor_configuration,
)
from scpn_icf_beam_core.errors import DeviceConfigurationError, DeviceGeometryError
from scpn_icf_beam_core.geometry import MILLIMETRE_M
from scpn_icf_beam_core.geometry.model import (
    BODY_ABLATOR_SHELL,
    BODY_FUEL_ICE_SHELL,
    BODY_FUEL_VAPOUR_CORE,
    BODY_NAMES_BY_IDENTIFIER,
    CAPSULE_BODY_NAMES,
    MATERIAL_BERYLLIUM_ABLATOR,
    MATERIAL_FUEL_VAPOUR,
    MATERIAL_SOLID_FUEL,
    MODEL_NON_CLAIMS,
    MODEL_SCHEMA,
    MODEL_SCHEMA_VERSION,
    MODEL_UNITS,
    ROLE_ABLATOR,
    ROLE_FUEL,
    DeviceModel3D,
    build_device_model,
    capsule_radii_m,
)
from scpn_icf_beam_core.physics.level0 import CapsuleDeclaration

OWNED_IDENTIFIERS = ("ion_beam_icf", "pulsed_electron_beam_icf")

#: Largest relative departure admitted when a printed millimetre
#: thickness is recovered from two metre-scale radii. Measured: the
#: ablator returns 0.2199999999999997 and the fuel layer
#: 0.3200000000000002, at 1.4e-15 and 5.2e-16 relative.
THICKNESS_RECOVERY_TOLERANCE = 1.0e-14


def anchor_model(*, identifier: str = "ion_beam_icf") -> DeviceModel3D:
    """Build the anchor model of one owned configuration.

    Parameters
    ----------
    identifier
        Which owned configuration to build.

    Returns
    -------
    DeviceModel3D
        The three capsule bodies at the anchor resolutions.
    """
    return build_device_model(
        anchor_configuration(identifier=identifier),
        anchor_capsule(),
        ANCHOR_SEGMENTS,
        ANCHOR_RINGS,
    )


def pole_radius_m(model: DeviceModel3D, name: str) -> float:
    """Return the outermost pole height of one body of a model.

    Parameters
    ----------
    model
        The built model.
    name
        Body name to read.

    Returns
    -------
    float
        The largest ``z`` over that body's vertices. Every body here is
        centred on the origin and its profile places a vertex at exactly
        ``+radius``, so this is the body's outer radius rather than an
        approximation of it.
    """
    body = next(mesh for mesh in model.meshes if mesh.name == name)
    return max(z for _, _, z in body.vertices)


@pytest.mark.parametrize("identifier", OWNED_IDENTIFIERS)
def test_every_owned_configuration_draws_the_same_three_bodies(
    identifier: str,
) -> None:
    """Neither owned configuration has an enclosure to draw.

    The laser-ICF family varies its body set by identifier because a
    filed precursor prints dimensionless enclosure geometry it can
    anchor against. Nothing of the kind exists here: both filed sources
    describe a radiation enclosure and neither prints a dimension of
    one, so drawing a case would mean inventing every number in it.
    """
    assert tuple(mesh.name for mesh in anchor_model(identifier=identifier).meshes) == (
        BODY_ABLATOR_SHELL,
        BODY_FUEL_ICE_SHELL,
        BODY_FUEL_VAPOUR_CORE,
    )


def test_every_owned_configuration_has_a_body_set() -> None:
    """The map covers exactly the configurations this repository owns."""
    from scpn_icf_beam_core import OWNED_CONFIGURATIONS

    assert sorted(BODY_NAMES_BY_IDENTIFIER) == sorted(OWNED_CONFIGURATIONS)
    assert set(BODY_NAMES_BY_IDENTIFIER.values()) == {CAPSULE_BODY_NAMES}


def test_the_electron_beam_class_is_drawn_from_a_declaration_and_no_source() -> None:
    """A body set exists for it, and no filed source stands behind it.

    Both acquired sources are heavy-ion. The electron-beam class builds
    because its dimensions are declared by whoever configures it, and
    the record says so in its non-claims rather than letting the
    identical geometry imply identical evidence.
    """
    ion = anchor_model()
    electron = anchor_model(identifier="pulsed_electron_beam_icf")
    assert electron.digest_sha256() != ion.digest_sha256()
    assert electron.capsule_digest_sha256 == ion.capsule_digest_sha256
    assert any("electron-beam driver" in claim for claim in MODEL_NON_CLAIMS)


def test_the_three_printed_radii_are_recovered_from_the_built_bodies() -> None:
    """Each surface is exactly where the source prints it.

    The sphere profile places a vertex at exactly the centre plus the
    radius and the capsule is centred on the origin, so these are
    equalities rather than comparisons within a tolerance.

    All three come from the source. That is what separates this family
    from the laser one, whose review prints an outer radius and two
    thicknesses and leaves the cavity to be derived.
    """
    model = anchor_model()
    assert pole_radius_m(model, BODY_ABLATOR_SHELL) == ANCHOR_PELLET_RADIUS_M
    assert pole_radius_m(model, BODY_FUEL_ICE_SHELL) == ANCHOR_FUEL_OUTER_RADIUS_M
    assert pole_radius_m(model, BODY_FUEL_VAPOUR_CORE) == ANCHOR_CAVITY_RADIUS_M


def test_the_layer_thicknesses_come_back_but_not_exactly() -> None:
    """Neither thickness returns exactly, and the reason is the source.

    Measured: the ablator returns 0.2199999999999997 against a printed
    0.22, and the fuel layer 0.3200000000000002 against 0.32.

    The cause is the opposite of the laser family's. There the source
    prints integer micrometres, the layer arithmetic is exact, and the
    conversion to metres introduces the rounding. Here the source prints
    millimetres to two decimals, and 2.34, 2.12 and 1.8 are already
    inexact in binary before any conversion happens: 2.34 - 2.12 is
    0.21999999999999975 in millimetres alone. So this is a bound, and it
    was measured before it was written.
    """
    model = anchor_model()
    ablator = (
        pole_radius_m(model, BODY_ABLATOR_SHELL)
        - pole_radius_m(model, BODY_FUEL_ICE_SHELL)
    ) / MILLIMETRE_M
    fuel = (
        pole_radius_m(model, BODY_FUEL_ICE_SHELL)
        - pole_radius_m(model, BODY_FUEL_VAPOUR_CORE)
    ) / MILLIMETRE_M
    printed_ablator = PRINTED_HO_PELLET_RADIUS_MM - PRINTED_HO_FUEL_OUTER_RADIUS_MM
    printed_fuel = PRINTED_HO_FUEL_OUTER_RADIUS_MM - PRINTED_HO_FUEL_INNER_RADIUS_MM
    assert ablator != printed_ablator
    assert abs(ablator - printed_ablator) <= (
        THICKNESS_RECOVERY_TOLERANCE * printed_ablator
    )
    assert abs(fuel - printed_fuel) <= THICKNESS_RECOVERY_TOLERANCE * printed_fuel


def test_the_ablator_is_the_thinnest_layer_of_the_three() -> None:
    """The printed capsule is mostly fuel and cavity, measured.

    The ablator spans 0.22 mm, the fuel layer 0.32 mm and the cavity
    reaches 1.8 mm. Stating it here is the sanity check a reader of the
    record makes first, and it is read off the built bodies.
    """
    model = anchor_model()
    outer = pole_radius_m(model, BODY_ABLATOR_SHELL)
    fuel_outer = pole_radius_m(model, BODY_FUEL_ICE_SHELL)
    cavity = pole_radius_m(model, BODY_FUEL_VAPOUR_CORE)
    assert outer - fuel_outer < fuel_outer - cavity
    assert fuel_outer - cavity < cavity


def test_the_vapour_is_drawn_although_it_is_a_gas() -> None:
    """The cavity carries a body because the source declares what fills it."""
    body = next(
        mesh for mesh in anchor_model().meshes if mesh.name == BODY_FUEL_VAPOUR_CORE
    )
    assert body.role == ROLE_FUEL
    assert body.signed_volume_m3() > 0.0


def test_the_capsule_radii_are_converted_in_one_place() -> None:
    """The single conversion returns the three radii the bodies are built at."""
    assert capsule_radii_m(anchor_configuration(), anchor_capsule()) == (
        ANCHOR_PELLET_RADIUS_M,
        ANCHOR_FUEL_OUTER_RADIUS_M,
        ANCHOR_CAVITY_RADIUS_M,
    )


def test_a_fuel_layer_that_fills_the_pellet_is_refused_by_the_physics_relation() -> (
    None
):
    """The geometry cannot draw a capsule the level-0 record would refuse.

    The refusal comes from the level-0 relation itself rather than from
    a copy of its rule, so the two can never disagree about what fits.
    """
    with pytest.raises(DeviceConfigurationError, match="leaves no ablator"):
        build_device_model(
            anchor_configuration(),
            dataclasses.replace(anchor_capsule(), fuel_outer_radius_mm=2.34),
            ANCHOR_SEGMENTS,
            ANCHOR_RINGS,
        )


def test_swapping_the_anchor_resolutions_is_refused_by_the_segment_rule() -> None:
    """At the anchor counts the swap happens to be caught, and only there.

    Segments must be a multiple of eight and the anchor ring count is
    not one, so handing the ring count to the segments is refused. That
    is a property of these two particular numbers, not a guard against
    the mistake: the next test builds the same swap from two counts that
    are both legal and nothing objects.
    """
    with pytest.raises(DeviceGeometryError, match="multiple of 8"):
        build_device_model(
            anchor_configuration(), anchor_capsule(), ANCHOR_RINGS, ANCHOR_SEGMENTS
        )


def test_the_rings_and_the_segments_are_not_interchangeable() -> None:
    """Swapping two legal resolutions builds a different body, unnoticed.

    The rings sample the profile and the segments sample the
    revolution. Where both counts are legal, nothing in either would
    object to being handed the other and no gate downstream would
    notice, so the difference is asserted here.
    """
    upright = build_device_model(anchor_configuration(), anchor_capsule(), 8, 16)
    swapped = build_device_model(anchor_configuration(), anchor_capsule(), 16, 8)
    assert swapped.digest_sha256() != upright.digest_sha256()


def test_a_finer_profile_encloses_more_volume() -> None:
    """More rings inscribe more of the surface they approximate."""
    coarse = build_device_model(
        anchor_configuration(), anchor_capsule(), ANCHOR_SEGMENTS, 16
    )
    assert (
        anchor_model().meshes[2].signed_volume_m3()
        > coarse.meshes[2].signed_volume_m3()
    )


@pytest.mark.parametrize(("segments", "rings"), [(7, 64), (8, 1)])
def test_an_invalid_resolution_is_refused_under_the_device_error(
    segments: int, rings: int
) -> None:
    """The library's refusal arrives as this package's error type."""
    with pytest.raises(DeviceGeometryError):
        build_device_model(anchor_configuration(), anchor_capsule(), segments, rings)


def test_an_unknown_identifier_is_refused() -> None:
    """A model can only be built for a body set this family owns."""
    with pytest.raises(DeviceGeometryError, match="identifier"):
        dataclasses.replace(anchor_model(), identifier="beam_icf_unknown")


def test_a_body_set_in_the_wrong_order_is_refused() -> None:
    """The order is part of the contract, not an accident of construction."""
    model = anchor_model()
    with pytest.raises(DeviceGeometryError, match="in order"):
        dataclasses.replace(model, meshes=tuple(reversed(model.meshes)))


def test_the_record_states_its_schema_units_and_non_claims() -> None:
    """The record carries what a consumer needs to read it correctly."""
    record = anchor_model().to_record()
    assert record["schema"] == MODEL_SCHEMA
    assert record["schema_version"] == MODEL_SCHEMA_VERSION
    assert record["units"] == dict(MODEL_UNITS)
    assert record["non_claims"] == list(MODEL_NON_CLAIMS)
    assert record["rings"] == ANCHOR_RINGS
    assert record["segments"] == ANCHOR_SEGMENTS


def test_the_record_states_that_no_enclosure_is_drawn() -> None:
    """The absence of a body is declared, not left to be noticed.

    A consumer that sees three bodies and knows the design has a
    hohlraum must be able to find out from the record why the case is
    missing, rather than concluding the model is incomplete.
    """
    non_claims = anchor_model().to_record()["non_claims"]
    assert any("no radiation enclosure is drawn" in claim for claim in non_claims)
    assert any("equal area" in claim for claim in non_claims)


def test_every_body_reports_its_identity_and_its_measures() -> None:
    """Each body entry carries its name, role, material and measures."""
    record = anchor_model().to_record()
    identities = {
        body["name"]: (body["role"], body["material_identifier"])
        for body in record["bodies"]
    }
    assert identities == {
        BODY_ABLATOR_SHELL: (ROLE_ABLATOR, MATERIAL_BERYLLIUM_ABLATOR),
        BODY_FUEL_ICE_SHELL: (ROLE_FUEL, MATERIAL_SOLID_FUEL),
        BODY_FUEL_VAPOUR_CORE: (ROLE_FUEL, MATERIAL_FUEL_VAPOUR),
    }
    for body in record["bodies"]:
        assert body["volume_m3"] > 0.0
        assert body["surface_area_m2"] > 0.0
        assert body["vertex_count"] > 0
        assert body["face_count"] > 0


def test_the_ablator_is_beryllium_and_not_the_plastic_of_the_laser_family() -> None:
    """The material token follows the source, which prints beryllium."""
    assert MATERIAL_BERYLLIUM_ABLATOR == "beryllium_ablator"


def test_the_canonical_bytes_are_sorted_minimal_and_newline_terminated() -> None:
    """The model serialises the way every other record here does."""
    data = anchor_model().canonical_bytes()
    assert data.endswith(b"\n")
    decoded = json.loads(data)
    assert list(decoded) == sorted(decoded)
    reencoded = json.dumps(decoded, sort_keys=True, separators=(",", ":")) + "\n"
    assert data == reencoded.encode("utf-8")


def test_the_digest_identifies_the_exact_model() -> None:
    """The same design digests the same; a different capsule does not."""
    assert anchor_model().digest_sha256() == anchor_model().digest_sha256()
    thinner = build_device_model(
        anchor_configuration(),
        dataclasses.replace(anchor_capsule(), fuel_inner_radius_mm=1.7),
        ANCHOR_SEGMENTS,
        ANCHOR_RINGS,
    )
    assert thinner.digest_sha256() != anchor_model().digest_sha256()
    assert thinner.capsule_digest_sha256 != anchor_model().capsule_digest_sha256


def test_the_capsule_digest_follows_the_declaration_and_not_the_configuration() -> None:
    """The two digests answer two different questions.

    A configuration change that leaves the layering alone must move the
    configuration digest and leave the capsule digest where it was, or
    a consumer cannot tell which input changed.
    """
    louder = build_device_model(
        anchor_configuration(identifier="pulsed_electron_beam_icf"),
        anchor_capsule(),
        ANCHOR_SEGMENTS,
        ANCHOR_RINGS,
    )
    baseline = anchor_model()
    assert louder.configuration_digest_sha256 != baseline.configuration_digest_sha256
    assert louder.capsule_digest_sha256 == baseline.capsule_digest_sha256


def test_a_declaration_the_configuration_contradicts_cannot_be_drawn() -> None:
    """A capsule declared for one pellet is refused against another.

    The pellet radius lives in the configuration and the fuel radii in
    the declaration, so the two can be combined into a capsule that no
    source describes. The level-0 relation refuses it and the geometry
    inherits the refusal.
    """
    smaller = dataclasses.replace(
        anchor_configuration(),
        target=dataclasses.replace(
            anchor_configuration().target, pellet_radius_um=2000.0
        ),
    )
    with pytest.raises(DeviceConfigurationError, match="leaves no ablator"):
        build_device_model(smaller, anchor_capsule(), ANCHOR_SEGMENTS, ANCHOR_RINGS)


def test_a_layering_whose_radii_are_inverted_never_reaches_the_geometry() -> None:
    """The declaration refuses itself before a model can be asked for."""
    with pytest.raises(DeviceConfigurationError, match="fuel_outer_radius_mm"):
        CapsuleDeclaration(
            ablator_density_g_cm3=1.85,
            fuel_outer_radius_mm=1.8,
            fuel_inner_radius_mm=2.12,
            fuel_density_g_cm3=0.25,
            vapour_density_g_cm3=0.3e-3,
        )
