# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN ICF Beam Core — the energy chain from driver to yield

"""The chain of efficiencies between a beam and the energy a capsule releases.

An indirectly driven, beam-driven target spends its driver energy twice
before any of it reaches the fuel. The beams stop in converters and
their energy becomes radiation, at a conversion efficiency; the
radiation fills an enclosure and part of it is absorbed by the capsule,
at a coupling efficiency. Only then does the capsule's own gain apply.

So the target gain factorises:

    G_target = eta_c * eta_e * G_capsule

and every one of those four quantities is a ratio the filed sources
either print or make recoverable. **The factorisation is the whole
content of this module** — none of the four efficiencies is calculated
here, because calculating any of them is radiation hydrodynamics this
repository does not perform.

The enclosure enters through one printed number: the ratio of the
capsule's surface area to the enclosure's. That ratio is what sets how
much of the radiation the capsule can intercept, and the filed source
prints its minimum for adequate symmetry rather than deriving it.

**The areas here are areas of ideal spheres.** That is correct in this
module and would be wrong in the geometry package, where every body is
an inscribed polyhedron and its own profile is its reference. A ratio
of published areas is not a measurement of a built body.

Design record: ADR 0005.
"""

from __future__ import annotations

import math

from scpn_icf_beam_core.errors import DeviceConfigurationError
from scpn_icf_beam_core.parameters import require_positive
from scpn_icf_beam_core.physics.capsule import require_fraction


def sphere_area_mm2(radius_mm: float) -> float:
    """Return the surface area of an ideal sphere.

    Parameters
    ----------
    radius_mm
        Radius in millimetres; strictly positive.

    Returns
    -------
    float
        ``4 pi r^2`` in square millimetres.

    Raises
    ------
    DeviceConfigurationError
        If the radius is non-finite or not strictly positive.
    """
    require_positive("radius_mm", radius_mm)
    return 4.0 * math.pi * radius_mm**2


def capsule_gain(yield_mj: float, absorbed_energy_mj: float) -> float:
    """Return the gain of the capsule alone.

    Parameters
    ----------
    yield_mj
        Energy the capsule released, in megajoules; strictly positive.
    absorbed_energy_mj
        Energy the capsule absorbed, in megajoules; strictly positive.

    Returns
    -------
    float
        The ratio of the two. This is the capsule's own figure and says
        nothing about the driver that fed it.

    Raises
    ------
    DeviceConfigurationError
        If either value is non-finite or not strictly positive.
    """
    require_positive("yield_mj", yield_mj)
    require_positive("absorbed_energy_mj", absorbed_energy_mj)
    return yield_mj / absorbed_energy_mj


def target_gain(yield_mj: float, driver_energy_mj: float) -> float:
    """Return the gain of the whole target system.

    Parameters
    ----------
    yield_mj
        Energy released, in megajoules; strictly positive.
    driver_energy_mj
        Energy the driver delivered, in megajoules; strictly positive.

    Returns
    -------
    float
        The ratio of the two, against **delivered beam energy** and
        never against wall-plug energy.

    Raises
    ------
    DeviceConfigurationError
        If either value is non-finite or not strictly positive.
    """
    require_positive("yield_mj", yield_mj)
    require_positive("driver_energy_mj", driver_energy_mj)
    return yield_mj / driver_energy_mj


def absorbed_energy_mj(
    driver_energy_mj: float,
    conversion_efficiency: float,
    coupling_efficiency: float,
) -> float:
    """Return the energy a capsule absorbs from a driver.

    Parameters
    ----------
    driver_energy_mj
        Energy the driver delivered, in megajoules; strictly positive.
    conversion_efficiency
        Fraction of beam energy that becomes radiation, in ``(0, 1]``.
    coupling_efficiency
        Fraction of that radiation the capsule absorbs, in ``(0, 1]``.

    Returns
    -------
    float
        The product of the three, in megajoules.

    Raises
    ------
    DeviceConfigurationError
        If the energy is not strictly positive or either efficiency
        leaves its interval.
    """
    require_positive("driver_energy_mj", driver_energy_mj)
    require_fraction("conversion_efficiency", conversion_efficiency)
    require_fraction("coupling_efficiency", coupling_efficiency)
    return driver_energy_mj * conversion_efficiency * coupling_efficiency


def implied_conversion_efficiency(
    system_gain: float, capsule_gain_value: float, coupling_efficiency: float
) -> float:
    """Return the conversion efficiency a stated system gain requires.

    Inverting ``G_target = eta_c eta_e G_capsule``. This is the
    direction the filed source forces: it prints the system gain, the
    coupling efficiency and everything needed for the capsule gain, and
    plots the conversion efficiency in a figure rather than printing a
    number for it.

    Parameters
    ----------
    system_gain
        The target-system gain; strictly positive.
    capsule_gain_value
        The capsule's own gain; strictly positive.
    coupling_efficiency
        Fraction of radiation the capsule absorbs, in ``(0, 1]``.

    Returns
    -------
    float
        The implied conversion efficiency. It is **not** validated as a
        fraction: a value above one is a meaningful answer and says the
        three inputs cannot describe the same design. A caller that
        needs that refused applies
        :func:`~scpn_icf_beam_core.physics.capsule.require_fraction` to
        the result.

    Raises
    ------
    DeviceConfigurationError
        If a gain is not strictly positive or the coupling efficiency
        leaves its interval.
    """
    require_positive("system_gain", system_gain)
    require_positive("capsule_gain_value", capsule_gain_value)
    require_fraction("coupling_efficiency", coupling_efficiency)
    return system_gain / (capsule_gain_value * coupling_efficiency)


def enclosure_area_mm2(capsule_area_mm2: float, area_ratio: float) -> float:
    """Return the enclosure area a capsule-to-enclosure ratio implies.

    Parameters
    ----------
    capsule_area_mm2
        Surface area of the capsule, in square millimetres; strictly
        positive.
    area_ratio
        The capsule's area divided by the enclosure's, in ``(0, 1]``.

    Returns
    -------
    float
        The enclosure's area in square millimetres.

    Raises
    ------
    DeviceConfigurationError
        If the area is not strictly positive or the ratio leaves its
        interval. A ratio above one describes an enclosure smaller than
        the capsule inside it and is refused.
    """
    require_positive("capsule_area_mm2", capsule_area_mm2)
    require_fraction("area_ratio", area_ratio)
    return capsule_area_mm2 / area_ratio


def equivalent_enclosure_radius_mm(
    capsule_radius_mm: float, area_ratio: float
) -> float:
    """Return the radius of the sphere of the implied enclosure area.

    A real enclosure is a cylinder with converters and shields in it, so
    this is not its radius. It is the radius of the sphere of equal
    area, which is the only length a bare area ratio determines, and it
    is what makes the printed ratio comparable across designs.

    Parameters
    ----------
    capsule_radius_mm
        Capsule outer radius in millimetres; strictly positive.
    area_ratio
        The capsule's area divided by the enclosure's, in ``(0, 1]``.

    Returns
    -------
    float
        ``r / sqrt(ratio)`` in millimetres.

    Raises
    ------
    DeviceConfigurationError
        If the radius is not strictly positive or the ratio leaves its
        interval.
    """
    require_positive("capsule_radius_mm", capsule_radius_mm)
    require_fraction("area_ratio", area_ratio)
    return capsule_radius_mm / math.sqrt(area_ratio)


def require_species(species: str, expected: str) -> str:
    """Return a beam species when it is the one a relation was stated for.

    Parameters
    ----------
    species
        Species of the driver under evaluation.
    expected
        Species the relation's filed source describes.

    Returns
    -------
    str
        The species, unchanged.

    Raises
    ------
    DeviceConfigurationError
        If they differ. Both filed sources for this chain describe
        heavy-ion drivers; applying their efficiencies to an electron
        beam would carry a number across a boundary its source never
        crossed.
    """
    if species != expected:
        raise DeviceConfigurationError(
            f"species: this relation is stated for {expected!r} drivers, "
            f"got {species!r}"
        )
    return species
