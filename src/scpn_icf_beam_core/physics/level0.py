# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN ICF Beam Core — level-0 physics record

"""Level-0 physics record of one validated beam-ICF configuration.

The configuration carries the driver and the pellet's outer radius, and
nothing else about the target. Three things it does not carry are
declared here in three objects that keep three different kinds of
declaration apart: what the capsule is made of, how the beams are
arranged on it, and what the shot did.

The record then evaluates the illumination geometry of
:mod:`~scpn_icf_beam_core.physics.beam`, the mass inventory and released
energy of :mod:`~scpn_icf_beam_core.physics.capsule`, and the
efficiency chain of :mod:`~scpn_icf_beam_core.physics.coupling` on that
set.

**Two quantities run backwards here, and deliberately.** The filed
sources print a yield and never a burn-up fraction, and they plot a
conversion efficiency and never print one. So the burn-up fraction is
obtained from the yield and the inventory, and the conversion efficiency
from the system gain, the capsule gain and the coupling efficiency. Both
are reported as what they are: quantities implied by other people's
numbers, not measurements of anything.

One cross-check is structural rather than declared: the fuel layer's
outer radius must lie inside the pellet the configuration declares, and
a layering that does not fit is refused rather than reported.

Design record: ADR 0005.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Final

from scpn_icf_beam_core.configuration import DeviceConfiguration
from scpn_icf_beam_core.errors import DeviceConfigurationError
from scpn_icf_beam_core.parameters import require_positive
from scpn_icf_beam_core.physics.beam import (
    effective_spot_radius_mm,
    elliptical_spot_area_mm2,
    energy_per_beam_mj,
    require_beam_count,
    spot_fluence_mj_per_mm2,
    total_beam_count,
)
from scpn_icf_beam_core.physics.capsule import (
    areal_density_g_cm2,
    burnup_from_yield,
    require_fraction,
    shell_mass_mg,
    sphere_mass_mg,
)
from scpn_icf_beam_core.physics.coupling import (
    capsule_gain,
    enclosure_area_mm2,
    equivalent_enclosure_radius_mm,
    implied_conversion_efficiency,
    sphere_area_mm2,
    target_gain,
)

LEVEL0_SCHEMA: Final = "scpn.beam-icf-level0-physics.v1"
LEVEL0_SCHEMA_VERSION: Final = "1.0.0"
#: Micrometres in a millimetre. The configuration carries the pellet
#: radius in micrometres and every relation here is stated in
#: millimetres; this is the only place the two meet.
MICROMETRES_PER_MILLIMETRE: Final = 1.0e3
LEVEL0_NON_CLAIMS: Final = (
    (
        "closed-form evaluation of published illumination geometry, mass "
        "inventory and efficiency definitions on a declared capsule, a "
        "declared illumination and a declared shot"
    ),
    (
        "no radiation hydrodynamics, no beam transport, no stopping-power "
        "calculation and no burn calculation is performed anywhere here"
    ),
    (
        "the capsule layering, the beam arrangement, the absorbed energy, "
        "the yield and the coupling efficiency are declared inputs; they "
        "come out of calculations and experiments this repository does not "
        "perform and could not check"
    ),
    (
        "the burn-up fraction and the conversion efficiency are implied by "
        "other declared quantities rather than measured, and either can come "
        "out above one, which says the declarations do not describe one "
        "design"
    ),
    (
        "the beams are split equally and their spot fluence is averaged over "
        "the whole ellipse; the sources' beams carry a Gaussian profile, so "
        "no value here is a peak"
    ),
    (
        "both filed sources describe heavy-ion drivers; nothing here is "
        "evidence about an electron-beam driver"
    ),
    (
        "no value describes or validates any real machine or shot; an anchor "
        "reproduces a number a filed source prints and nothing further"
    ),
)


@dataclass(frozen=True, slots=True)
class CapsuleDeclaration:
    """Declared layering of a capsule, before the shot.

    Parameters
    ----------
    ablator_density_g_cm3
        Density of the outer ablator; strictly positive.
    fuel_outer_radius_mm
        Outer radius of the solid fuel layer; strictly positive, and
        checked against the pellet radius the configuration declares.
    fuel_inner_radius_mm
        Inner radius of the solid fuel layer, which is the outer radius
        of the vapour cavity; strictly positive and below the outer.
    fuel_density_g_cm3
        Density of the solid fuel layer; strictly positive.
    vapour_density_g_cm3
        Density of the vapour filling the cavity; strictly positive.

    Raises
    ------
    DeviceConfigurationError
        If any value is non-finite or not strictly positive, or the fuel
        layer's radii are not ordered.
    """

    ablator_density_g_cm3: float
    fuel_outer_radius_mm: float
    fuel_inner_radius_mm: float
    fuel_density_g_cm3: float
    vapour_density_g_cm3: float

    def __post_init__(self) -> None:
        """Validate the declared layering.

        Raises
        ------
        DeviceConfigurationError
            If any value is non-finite or not strictly positive, or the
            fuel layer's radii are not ordered.
        """
        require_positive("ablator_density_g_cm3", self.ablator_density_g_cm3)
        require_positive("fuel_outer_radius_mm", self.fuel_outer_radius_mm)
        require_positive("fuel_inner_radius_mm", self.fuel_inner_radius_mm)
        require_positive("fuel_density_g_cm3", self.fuel_density_g_cm3)
        require_positive("vapour_density_g_cm3", self.vapour_density_g_cm3)
        if self.fuel_outer_radius_mm <= self.fuel_inner_radius_mm:
            raise DeviceConfigurationError(
                "fuel_outer_radius_mm: must exceed fuel_inner_radius_mm, got "
                f"{self.fuel_outer_radius_mm!r} <= {self.fuel_inner_radius_mm!r}"
            )

    def fuel_thickness_mm(self) -> float:
        """Return the thickness of the solid fuel layer.

        Returns
        -------
        float
            The difference of the two declared radii, in millimetres.
        """
        return self.fuel_outer_radius_mm - self.fuel_inner_radius_mm

    def to_record(self) -> dict[str, Any]:
        """Project the declaration to a JSON-serialisable record.

        Returns
        -------
        dict[str, Any]
            One key per declared field.
        """
        return {
            "ablator_density_g_cm3": self.ablator_density_g_cm3,
            "fuel_outer_radius_mm": self.fuel_outer_radius_mm,
            "fuel_inner_radius_mm": self.fuel_inner_radius_mm,
            "fuel_density_g_cm3": self.fuel_density_g_cm3,
            "vapour_density_g_cm3": self.vapour_density_g_cm3,
        }


@dataclass(frozen=True, slots=True)
class IlluminationDeclaration:
    """Declared beam arrangement on the target.

    Parameters
    ----------
    beams_per_side
        Beams in one illumination cone; at least one.
    major_semi_axis_mm, minor_semi_axis_mm
        Semi-axes of one beam's focal ellipse; both strictly positive.

    Raises
    ------
    DeviceConfigurationError
        If the count is below the minimum or a semi-axis is non-finite
        or not strictly positive.
    """

    beams_per_side: int
    major_semi_axis_mm: float
    minor_semi_axis_mm: float

    def __post_init__(self) -> None:
        """Validate the declared arrangement.

        Raises
        ------
        DeviceConfigurationError
            If the count is below the minimum or a semi-axis is
            non-finite or not strictly positive.
        """
        require_beam_count(self.beams_per_side)
        require_positive("major_semi_axis_mm", self.major_semi_axis_mm)
        require_positive("minor_semi_axis_mm", self.minor_semi_axis_mm)

    def to_record(self) -> dict[str, Any]:
        """Project the declaration to a JSON-serialisable record.

        Returns
        -------
        dict[str, Any]
            One key per declared field.
        """
        return {
            "beams_per_side": self.beams_per_side,
            "major_semi_axis_mm": self.major_semi_axis_mm,
            "minor_semi_axis_mm": self.minor_semi_axis_mm,
        }


@dataclass(frozen=True, slots=True)
class ShotDeclaration:
    """Declared outcome of one shot, and the coupling it assumed.

    Parameters
    ----------
    absorbed_energy_mj
        Energy the capsule absorbed; strictly positive.
    yield_mj
        Energy released; strictly positive.
    coupling_efficiency
        Fraction of the enclosure's radiation the capsule absorbed, in
        ``(0, 1]``.
    capsule_to_enclosure_area_ratio
        The capsule's surface area over the enclosure's, in ``(0, 1]``.

    Raises
    ------
    DeviceConfigurationError
        If an energy is not strictly positive or a fraction leaves its
        interval.
    """

    absorbed_energy_mj: float
    yield_mj: float
    coupling_efficiency: float
    capsule_to_enclosure_area_ratio: float

    def __post_init__(self) -> None:
        """Validate the declared shot.

        Raises
        ------
        DeviceConfigurationError
            If an energy is not strictly positive or a fraction leaves
            its interval. Each is validated here as well as inside the
            relation that consumes it, so a record can never be built
            from a set the relations would have refused one at a time.
        """
        require_positive("absorbed_energy_mj", self.absorbed_energy_mj)
        require_positive("yield_mj", self.yield_mj)
        require_fraction("coupling_efficiency", self.coupling_efficiency)
        require_fraction(
            "capsule_to_enclosure_area_ratio", self.capsule_to_enclosure_area_ratio
        )

    def to_record(self) -> dict[str, Any]:
        """Project the declaration to a JSON-serialisable record.

        Returns
        -------
        dict[str, Any]
            One key per declared field.
        """
        return {
            "absorbed_energy_mj": self.absorbed_energy_mj,
            "yield_mj": self.yield_mj,
            "coupling_efficiency": self.coupling_efficiency,
            "capsule_to_enclosure_area_ratio": self.capsule_to_enclosure_area_ratio,
        }


@dataclass(frozen=True, slots=True)
class OperatingPoint:
    """Composed level-0 operating point of one configuration.

    Parameters
    ----------
    beam_power_tw
        Driver power the configuration carries.
    total_beam_count
        Beams in both cones together.
    energy_per_beam_mj
        Driver energy divided equally among them.
    spot_area_mm2
        Area of one focal ellipse.
    effective_spot_radius_mm
        Radius of the circle of that area.
    spot_fluence_mj_per_mm2
        Energy per beam over the ellipse's full area.
    pellet_radius_mm
        Pellet outer radius, in the units the relations use.
    ablator_thickness_mm
        Pellet radius less the fuel layer's outer radius.
    fuel_thickness_mm
        Thickness of the solid fuel layer.
    fuel_areal_density_g_cm2
        Density times thickness of the solid fuel layer.
    ablator_mass_mg, fuel_mass_mg, vapour_mass_mg
        Masses of the three layers.
    fuel_inventory_mg
        Solid fuel plus vapour, which is what can burn.
    burnup_fraction
        Fraction of that inventory the declared yield implies.
    capsule_gain
        Yield over absorbed energy.
    target_gain
        Yield over delivered driver energy.
    implied_conversion_efficiency
        Conversion efficiency the two gains and the coupling efficiency
        require.
    capsule_area_mm2, enclosure_area_mm2
        The capsule's surface area and the enclosure's, from the
        declared ratio.
    equivalent_enclosure_radius_mm
        Radius of the sphere of the enclosure's area.
    """

    beam_power_tw: float
    total_beam_count: int
    energy_per_beam_mj: float
    spot_area_mm2: float
    effective_spot_radius_mm: float
    spot_fluence_mj_per_mm2: float
    pellet_radius_mm: float
    ablator_thickness_mm: float
    fuel_thickness_mm: float
    fuel_areal_density_g_cm2: float
    ablator_mass_mg: float
    fuel_mass_mg: float
    vapour_mass_mg: float
    fuel_inventory_mg: float
    burnup_fraction: float
    capsule_gain: float
    target_gain: float
    implied_conversion_efficiency: float
    capsule_area_mm2: float
    enclosure_area_mm2: float
    equivalent_enclosure_radius_mm: float

    def to_record(self) -> dict[str, Any]:
        """Project the operating point to a JSON-serialisable record.

        Returns
        -------
        dict[str, Any]
            One key per field, in the declaration order of the class.
        """
        return {
            "beam_power_tw": self.beam_power_tw,
            "total_beam_count": self.total_beam_count,
            "energy_per_beam_mj": self.energy_per_beam_mj,
            "spot_area_mm2": self.spot_area_mm2,
            "effective_spot_radius_mm": self.effective_spot_radius_mm,
            "spot_fluence_mj_per_mm2": self.spot_fluence_mj_per_mm2,
            "pellet_radius_mm": self.pellet_radius_mm,
            "ablator_thickness_mm": self.ablator_thickness_mm,
            "fuel_thickness_mm": self.fuel_thickness_mm,
            "fuel_areal_density_g_cm2": self.fuel_areal_density_g_cm2,
            "ablator_mass_mg": self.ablator_mass_mg,
            "fuel_mass_mg": self.fuel_mass_mg,
            "vapour_mass_mg": self.vapour_mass_mg,
            "fuel_inventory_mg": self.fuel_inventory_mg,
            "burnup_fraction": self.burnup_fraction,
            "capsule_gain": self.capsule_gain,
            "target_gain": self.target_gain,
            "implied_conversion_efficiency": self.implied_conversion_efficiency,
            "capsule_area_mm2": self.capsule_area_mm2,
            "enclosure_area_mm2": self.enclosure_area_mm2,
            "equivalent_enclosure_radius_mm": self.equivalent_enclosure_radius_mm,
        }


@dataclass(frozen=True, slots=True)
class Level0Physics:
    """Composed level-0 record of one configuration.

    Parameters
    ----------
    configuration_digest_sha256
        Digest of the configuration the record was built from.
    capsule
        The declared capsule layering.
    illumination
        The declared beam arrangement.
    shot
        The declared shot outcome.
    operating_point
        The composed operating point.
    """

    configuration_digest_sha256: str
    capsule: CapsuleDeclaration
    illumination: IlluminationDeclaration
    shot: ShotDeclaration
    operating_point: OperatingPoint

    def to_record(self) -> dict[str, Any]:
        """Project the record to a JSON-serialisable object.

        Returns
        -------
        dict[str, Any]
            The schema-tagged record with its non-claims.
        """
        return {
            "schema": LEVEL0_SCHEMA,
            "schema_version": LEVEL0_SCHEMA_VERSION,
            "configuration_digest_sha256": self.configuration_digest_sha256,
            "capsule": self.capsule.to_record(),
            "illumination": self.illumination.to_record(),
            "shot": self.shot.to_record(),
            "operating_point": self.operating_point.to_record(),
            "non_claims": list(LEVEL0_NON_CLAIMS),
        }

    def canonical_bytes(self) -> bytes:
        """Serialise the record canonically.

        Returns
        -------
        bytes
            UTF-8 JSON with sorted keys, minimal separators and a
            trailing newline; NaN and infinity are never emitted.
        """
        text = json.dumps(
            self.to_record(), sort_keys=True, separators=(",", ":"), allow_nan=False
        )
        return (text + "\n").encode("utf-8")

    def digest_sha256(self) -> str:
        """Identify the exact record.

        Returns
        -------
        str
            SHA-256 of :meth:`canonical_bytes` as lowercase hex.
        """
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


def pellet_radius_mm(configuration: DeviceConfiguration) -> float:
    """Return the pellet's outer radius in millimetres.

    Parameters
    ----------
    configuration
        Validated beam-ICF configuration.

    Returns
    -------
    float
        The radius the configuration declares, converted once.
    """
    return configuration.target.pellet_radius_um / MICROMETRES_PER_MILLIMETRE


def ablator_thickness_mm(
    configuration: DeviceConfiguration, capsule: CapsuleDeclaration
) -> float:
    """Return the thickness of the ablator around the fuel layer.

    Parameters
    ----------
    configuration
        Validated configuration supplying the pellet's outer radius.
    capsule
        Declared layering supplying the fuel layer's outer radius.

    Returns
    -------
    float
        The difference of the two, in millimetres.

    Raises
    ------
    DeviceConfigurationError
        If the fuel layer does not fit inside the pellet. This is
        refused rather than reported: a fuel layer at or beyond the
        pellet's surface describes a different capsule from the one the
        configuration declares.
    """
    outer = pellet_radius_mm(configuration)
    if capsule.fuel_outer_radius_mm >= outer:
        raise DeviceConfigurationError(
            "capsule: a fuel layer of outer radius "
            f"{capsule.fuel_outer_radius_mm!r} mm leaves no ablator inside a "
            f"pellet of radius {outer!r} mm"
        )
    return outer - capsule.fuel_outer_radius_mm


def level0_physics(
    configuration: DeviceConfiguration,
    capsule: CapsuleDeclaration,
    illumination: IlluminationDeclaration,
    shot: ShotDeclaration,
) -> Level0Physics:
    """Compose the level-0 physics record of one validated configuration.

    Parameters
    ----------
    configuration
        Validated beam-ICF configuration supplying the driver and the
        pellet's outer radius.
    capsule
        Declared capsule layering.
    illumination
        Declared beam arrangement.
    shot
        Declared shot outcome.

    Returns
    -------
    Level0Physics
        The composed record.

    Raises
    ------
    DeviceConfigurationError
        If a declared value leaves its documented interval or the
        layering does not fit the pellet; the refusals name the field.
    """
    outer = pellet_radius_mm(configuration)
    ablator = ablator_thickness_mm(configuration, capsule)
    per_beam = energy_per_beam_mj(
        configuration.driver.beam_energy_mj, illumination.beams_per_side
    )
    spot_area = elliptical_spot_area_mm2(
        illumination.major_semi_axis_mm, illumination.minor_semi_axis_mm
    )
    ablator_mass = shell_mass_mg(
        outer, capsule.fuel_outer_radius_mm, capsule.ablator_density_g_cm3
    )
    fuel_mass = shell_mass_mg(
        capsule.fuel_outer_radius_mm,
        capsule.fuel_inner_radius_mm,
        capsule.fuel_density_g_cm3,
    )
    vapour_mass = sphere_mass_mg(
        capsule.fuel_inner_radius_mm, capsule.vapour_density_g_cm3
    )
    inventory = fuel_mass + vapour_mass
    gain_of_capsule = capsule_gain(shot.yield_mj, shot.absorbed_energy_mj)
    gain_of_target = target_gain(shot.yield_mj, configuration.driver.beam_energy_mj)
    capsule_area = sphere_area_mm2(outer)
    return Level0Physics(
        configuration_digest_sha256=configuration.digest_sha256(),
        capsule=capsule,
        illumination=illumination,
        shot=shot,
        operating_point=OperatingPoint(
            beam_power_tw=configuration.driver.beam_power_tw(),
            total_beam_count=total_beam_count(illumination.beams_per_side),
            energy_per_beam_mj=per_beam,
            spot_area_mm2=spot_area,
            effective_spot_radius_mm=effective_spot_radius_mm(
                illumination.major_semi_axis_mm, illumination.minor_semi_axis_mm
            ),
            spot_fluence_mj_per_mm2=spot_fluence_mj_per_mm2(
                per_beam,
                illumination.major_semi_axis_mm,
                illumination.minor_semi_axis_mm,
            ),
            pellet_radius_mm=outer,
            ablator_thickness_mm=ablator,
            fuel_thickness_mm=capsule.fuel_thickness_mm(),
            fuel_areal_density_g_cm2=areal_density_g_cm2(
                capsule.fuel_thickness_mm(), capsule.fuel_density_g_cm3
            ),
            ablator_mass_mg=ablator_mass,
            fuel_mass_mg=fuel_mass,
            vapour_mass_mg=vapour_mass,
            fuel_inventory_mg=inventory,
            burnup_fraction=burnup_from_yield(shot.yield_mj, inventory),
            capsule_gain=gain_of_capsule,
            target_gain=gain_of_target,
            implied_conversion_efficiency=implied_conversion_efficiency(
                gain_of_target, gain_of_capsule, shot.coupling_efficiency
            ),
            capsule_area_mm2=capsule_area,
            enclosure_area_mm2=enclosure_area_mm2(
                capsule_area, shot.capsule_to_enclosure_area_ratio
            ),
            equivalent_enclosure_radius_mm=equivalent_enclosure_radius_mm(
                outer, shot.capsule_to_enclosure_area_ratio
            ),
        ),
    )
