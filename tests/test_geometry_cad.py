# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN ICF Beam Core — tier-G2 device model tests

"""Every branch of the tier-G2 model, and what its geometry is limited by.

The passing builds are cached: each costs several seconds, and
rebuilding one per test buys no evidence a single build does not already
carry. The builds that are supposed to fail are not cached, because what
they assert is the failure.
"""

from __future__ import annotations

import dataclasses
import functools
import json

import pytest
from scpn_reactor_kernels.cad import BodyEvidence

from geometry_fixtures import (
    ANCHOR_CAVITY_RADIUS_M,
    ANCHOR_RINGS,
    anchor_capsule,
    anchor_configuration,
)
from scpn_icf_beam_core.errors import DeviceGeometryError
from scpn_icf_beam_core.geometry import (
    BODY_ABLATOR_SHELL,
    BODY_FUEL_ICE_SHELL,
    BODY_FUEL_VAPOUR_CORE,
    BODY_NAMES_BY_IDENTIFIER,
    CAD_MODEL_NON_CLAIMS,
    CAD_MODEL_SCHEMA,
    CAD_MODEL_SCHEMA_VERSION,
    CAD_MODEL_UNITS,
    DEFAULT_ANGULAR_DEFLECTION_RAD,
    DEFAULT_LINEAR_DEFLECTION_M,
    DEFAULT_REFERENCE_MESH_SEGMENTS,
    DEFAULT_SPHERE_RINGS,
    DeviceModelCAD,
    build_device_cad,
)

#: The back-end's first refusal on this family's bodies, one step above
#: the default: forty-one is exact, forty-two is not. Asserting the step
#: immediately above the default is what locates it. Note that
#: forty-three is exact again — above the first refusal the counts
#: alternate by parity up to sixty-five — so this constant is the first
#: refusal and not an upper bound on what builds.
RINGS_AT_THE_FIRST_REFUSAL = 42
#: Linear deflection measured not to pass: below the exact threshold,
#: the vapour core's deficit exceeds the bound the deflection declares.
DEFLECTION_BELOW_THE_THRESHOLD_M = 1.0e-7
#: A second deflection that passes, used to show that the deficit does
#: not depend on the deflection at all.
DEFLECTION_ABOVE_THE_DEFAULT_M = 5.0e-7
#: The strongest guarantee any declared bound makes here. Measured: the
#: widest is the vapour core's at 0.0222 %.
BOUND_CEILING = 1.0e-3


@functools.cache
def anchor_cad() -> DeviceModelCAD:
    """Build and cache the anchor B-rep model.

    Returns
    -------
    DeviceModelCAD
        The three capsule bodies at the module defaults.
    """
    return build_device_cad(anchor_configuration(), anchor_capsule())


@functools.cache
def loose_cad() -> DeviceModelCAD:
    """Build and cache the same model at a looser linear deflection.

    Returns
    -------
    DeviceModelCAD
        The same bodies, checked against a weaker declared bound.
    """
    return build_device_cad(
        anchor_configuration(),
        anchor_capsule(),
        DEFAULT_REFERENCE_MESH_SEGMENTS,
        DEFAULT_SPHERE_RINGS,
        DEFLECTION_ABOVE_THE_DEFAULT_M,
    )


def body_named(model: DeviceModelCAD, name: str) -> BodyEvidence:
    """Return one body's evidence by name.

    Parameters
    ----------
    model
        The built model.
    name
        Body name to read.

    Returns
    -------
    BodyEvidence
        That body's checked evidence.
    """
    return next(body for body in model.bodies if body.name == name)


def test_both_tiers_draw_the_same_bodies_for_the_same_configuration() -> None:
    """The body set is a property of the identifier, at either tier."""
    assert (
        tuple(body.name for body in anchor_cad().bodies)
        == (BODY_NAMES_BY_IDENTIFIER["ion_beam_icf"])
    )


def test_every_body_measures_as_its_analytic_form_says_it_should() -> None:
    """The back-end's volume and area agree with the closed forms.

    The evidence kernel refuses at construction if they do not, so a
    model existing is already the assertion. This states the margin
    rather than restating the refusal: measured, every relative error
    here is at the level of floating-point noise.
    """
    for body in anchor_cad().bodies:
        assert body.volume_relative_error < 1e-12
        assert body.surface_area_relative_error < 1e-12


def test_every_faceted_body_clears_its_declared_deficit_bound() -> None:
    """The faceting loses less volume than the declared bound allows.

    Measured at the module's deflections: the worst body is the vapour
    core, at 0.57 of its bound.
    """
    for body in anchor_cad().bodies:
        assert body.faceted_volume_relative_deficit <= (
            body.faceted_volume_deficit_bound
        )
        assert body.faceted_volume_deficit_bound < BOUND_CEILING


def test_every_faceted_body_agrees_with_its_tier_one_twin() -> None:
    """The B-rep and the tessellation describe the same solid."""
    for body in anchor_cad().bodies:
        assert body.mesh_volume_relative_difference <= (
            body.mesh_volume_difference_bound
        )


def test_the_deficit_does_not_depend_on_the_linear_deflection() -> None:
    """The deflection moves the bound and leaves the model alone.

    This is the measurement the whole choice of deflection rests on. At
    2e-7 m and at 5e-7 m every body's faceted volume deficit is the
    same number, while the bound each is measured against differs by the
    ratio of the two deflections. So the deflection is not an accuracy
    knob at this scale — it is the strength of the claim being made.
    """
    tight = {b.name: b for b in anchor_cad().bodies}
    loose = {b.name: b for b in loose_cad().bodies}
    for name, body in tight.items():
        assert body.faceted_volume_relative_deficit == pytest.approx(
            loose[name].faceted_volume_relative_deficit, rel=1e-4
        )
        assert loose[name].faceted_volume_deficit_bound == pytest.approx(
            body.faceted_volume_deficit_bound
            * (DEFLECTION_ABOVE_THE_DEFAULT_M / DEFAULT_LINEAR_DEFLECTION_M)
        )


def test_the_exact_deflection_threshold_lies_between_the_two_tested_values() -> None:
    """The threshold is computable, and the default sits above it.

    Because the deficit is independent of the deflection and the bound
    is ``2 d / r``, the smallest deflection the worst body clears is
    exactly ``deficit * r / 2``. Measured, that is 1.13e-7 m for the
    vapour core — above the 1e-7 m the next test asserts is refused, and
    below the declared 2e-7 m. The declared value is therefore a stated
    margin rather than the strongest claim available, and this test is
    what makes that statement falsifiable.
    """
    vapour = body_named(anchor_cad(), BODY_FUEL_VAPOUR_CORE)
    threshold = vapour.faceted_volume_relative_deficit * ANCHOR_CAVITY_RADIUS_M / 2.0
    assert DEFLECTION_BELOW_THE_THRESHOLD_M < threshold < DEFAULT_LINEAR_DEFLECTION_M
    assert threshold == pytest.approx(1.1326e-7, rel=1e-3)


def test_the_ring_count_the_back_end_cannot_hold_is_refused() -> None:
    """At the first refusal the solid is wrong and the build refuses.

    On this family's bodies every count to forty-one is exact, and at
    forty-two the fuel shell departs by 8.2e-5 — four orders of
    magnitude above the library's measure tolerance. Nothing here was
    loosened to admit it: the evidence kernel refuses, naming the body
    and the bound.

    Forty-two is asserted rather than some larger count because only the
    step immediately above the default locates it. Above forty-two the
    counts alternate — odd exact, even refusing, to sixty-five — so a
    larger number would refuse for a reason this test could not
    distinguish from the one it means to record.
    """
    with pytest.raises(DeviceGeometryError, match="volume_relative_error"):
        build_device_cad(
            anchor_configuration(),
            anchor_capsule(),
            DEFAULT_REFERENCE_MESH_SEGMENTS,
            RINGS_AT_THE_FIRST_REFUSAL,
        )


def test_a_deflection_below_the_threshold_does_not_pass() -> None:
    """Below the computed threshold the declared bound is violated.

    Measured: the vapour core's deficit of 1.2585e-4 against a bound of
    1.1111e-4, over by thirteen per cent.
    """
    with pytest.raises(DeviceGeometryError, match="faceted_volume_relative_deficit"):
        build_device_cad(
            anchor_configuration(),
            anchor_capsule(),
            DEFAULT_REFERENCE_MESH_SEGMENTS,
            DEFAULT_SPHERE_RINGS,
            DEFLECTION_BELOW_THE_THRESHOLD_M,
        )


def test_an_invalid_deflection_arrives_as_the_device_error() -> None:
    """The library's refusal is re-raised under this package's error type."""
    with pytest.raises(DeviceGeometryError, match="strictly positive"):
        build_device_cad(
            anchor_configuration(),
            anchor_capsule(),
            DEFAULT_REFERENCE_MESH_SEGMENTS,
            DEFAULT_SPHERE_RINGS,
            0.0,
        )


def test_the_narrowest_body_gets_the_widest_bound() -> None:
    """Each bound follows its own body's radius, not one global value.

    Three bodies, three different bounds, ordered by radius: the ablator
    shell is the widest body and gets the tightest bound, the vapour
    core the narrowest and the loosest. A single copied deflection would
    have hidden that.
    """
    bounds = {
        body.name: body.faceted_volume_deficit_bound for body in anchor_cad().bodies
    }
    assert bounds[BODY_ABLATOR_SHELL] < bounds[BODY_FUEL_ICE_SHELL]
    assert bounds[BODY_FUEL_ICE_SHELL] < bounds[BODY_FUEL_VAPOUR_CORE]


def test_the_record_states_its_schema_units_and_non_claims() -> None:
    """The record carries what a consumer needs to read it correctly."""
    record = anchor_cad().to_record()
    assert record["schema"] == CAD_MODEL_SCHEMA
    assert record["schema_version"] == CAD_MODEL_SCHEMA_VERSION
    assert record["units"] == dict(CAD_MODEL_UNITS)
    assert record["non_claims"] == list(CAD_MODEL_NON_CLAIMS)
    assert record["rings"] == DEFAULT_SPHERE_RINGS
    assert record["linear_deflection_m"] == DEFAULT_LINEAR_DEFLECTION_M
    assert record["angular_deflection_rad"] == DEFAULT_ANGULAR_DEFLECTION_RAD


def test_the_record_carries_the_evidence_of_every_body() -> None:
    """Each body's checked evidence is in the record, in order."""
    record = anchor_cad().to_record()
    assert [body["name"] for body in record["bodies"]] == list(
        BODY_NAMES_BY_IDENTIFIER["ion_beam_icf"]
    )
    for body in record["bodies"]:
        assert body["analytic_volume_m3"] > 0.0
        assert body["faceted_volume_deficit_bound"] > 0.0


def test_the_two_tiers_agree_on_what_the_design_is() -> None:
    """Both tiers report the same digests for the same inputs."""
    model = anchor_cad()
    assert model.configuration_digest_sha256 == (anchor_configuration().digest_sha256())
    assert model.rings == ANCHOR_RINGS


def test_the_canonical_bytes_are_sorted_and_newline_terminated() -> None:
    """The model serialises the way every other record here does."""
    data = anchor_cad().canonical_bytes()
    assert data.endswith(b"\n")
    decoded = json.loads(data)
    assert list(decoded) == sorted(decoded)
    reencoded = json.dumps(decoded, sort_keys=True, separators=(",", ":")) + "\n"
    assert data == reencoded.encode("utf-8")


def test_the_digest_identifies_the_exact_model() -> None:
    """The record digests stably, and a different bound is a different record."""
    assert anchor_cad().digest_sha256() == anchor_cad().digest_sha256()
    assert anchor_cad().digest_sha256() != loose_cad().digest_sha256()


def test_the_step_export_is_deterministic_within_this_environment() -> None:
    """The normalised STEP bytes carry a digest of themselves."""
    model = anchor_cad()
    assert model.step_data
    assert model.step_sha256 == anchor_cad().step_sha256
    assert model.backend_versions


def test_the_faceted_meshes_are_the_bodies_that_were_checked() -> None:
    """The meshes the evidence came from are kept, in the same order."""
    model = anchor_cad()
    assert [mesh.name for mesh in model.faceted_meshes] == [
        body.name for body in model.bodies
    ]
    for mesh in model.faceted_meshes:
        assert mesh.signed_volume_m3() > 0.0


def test_an_unknown_identifier_is_refused() -> None:
    """A model can only exist for a body set this family owns."""
    with pytest.raises(DeviceGeometryError, match="identifier"):
        dataclasses.replace(anchor_cad(), identifier="beam_icf_unknown")


def test_a_manifest_of_the_wrong_schema_is_refused() -> None:
    """The assembly manifest must be the library's own."""
    model = anchor_cad()
    manifest = dict(model.assembly_manifest)
    manifest["schema"] = "something.else.v1"
    with pytest.raises(DeviceGeometryError, match=r"assembly_manifest\.schema"):
        dataclasses.replace(model, assembly_manifest=manifest)


def test_a_manifest_counting_the_wrong_number_of_bodies_is_refused() -> None:
    """The manifest's body count must match the identifier's body set."""
    model = anchor_cad()
    manifest = dict(model.assembly_manifest)
    manifest["body_count"] = 99
    with pytest.raises(DeviceGeometryError, match="body_count"):
        dataclasses.replace(model, assembly_manifest=manifest)


def test_a_body_set_in_the_wrong_order_is_refused() -> None:
    """The order is part of the contract at this tier too."""
    model = anchor_cad()
    with pytest.raises(DeviceGeometryError, match="in order"):
        dataclasses.replace(model, bodies=tuple(reversed(model.bodies)))
