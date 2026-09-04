# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN ICF Beam Core — capsule inventory and released energy

"""Mass inventory of a layered capsule, and the energy its fuel can release.

The capsule of a beam-driven target is a stack of concentric layers,
each declared by an outer radius and a density. This module turns that
declaration into masses and turns a mass into an energy. It performs no
hydrodynamics: what fraction of the fuel actually burns is an input
here, never a result.

**Two things are computed rather than typed.** The specific energy of a
deuterium-tritium reaction is built from the two nuclear masses and the
released energy per reaction, not carried as a rounded constant; and the
burn-up fraction of a filed design is obtained by dividing its printed
yield by the inventory this module computes, because the filed source
prints the yield and never the fraction.

Lengths are millimetres and densities grams per cubic centimetre,
because that is what the filed sources print. Masses are milligrams.

Design record: ADR 0005.
"""

from __future__ import annotations

import math
from typing import Final

from scpn_icf_beam_core.errors import DeviceConfigurationError
from scpn_icf_beam_core.parameters import require_positive

#: Atomic mass unit in kilograms (CODATA 2022).
ATOMIC_MASS_UNIT_KG: Final = 1.66053906892e-27
#: One megaelectronvolt in joules (exact, from the 2019 SI definition of
#: the elementary charge).
MEGAELECTRONVOLT_J: Final = 1.602176634e-13
#: Deuteron and triton masses in atomic mass units.
DEUTERON_MASS_U: Final = 2.013553212745
TRITON_MASS_U: Final = 3.01550941034
#: Energy released by one D + T -> alpha + n reaction, in MeV.
DT_FUSION_ENERGY_MEV: Final = 17.59
#: Cubic centimetres in a cubic millimetre.
CUBIC_MM_PER_CUBIC_CM: Final = 1.0e-3
#: Milligrams in a gram.
MILLIGRAMS_PER_GRAM: Final = 1.0e3
#: Millimetres in a centimetre.
MILLIMETRES_PER_CENTIMETRE: Final = 10.0


def dt_specific_energy_j_per_g() -> float:
    """Return the energy a gram of equimolar DT releases on full burn.

    The reacting pair is one deuteron and one triton, so a gram of
    equimolar fuel contains one pair per combined nuclear mass.

    Returns
    -------
    float
        Joules per gram of fuel consumed.
    """
    pair_mass_g = (
        (DEUTERON_MASS_U + TRITON_MASS_U) * ATOMIC_MASS_UNIT_KG * MILLIGRAMS_PER_GRAM
    )
    return DT_FUSION_ENERGY_MEV * MEGAELECTRONVOLT_J / pair_mass_g


def sphere_mass_mg(radius_mm: float, density_g_cm3: float) -> float:
    """Return the mass of a uniform sphere.

    Parameters
    ----------
    radius_mm
        Sphere radius in millimetres; strictly positive.
    density_g_cm3
        Uniform density in grams per cubic centimetre; strictly
        positive.

    Returns
    -------
    float
        Mass in milligrams.

    Raises
    ------
    DeviceConfigurationError
        If either value is non-finite or not strictly positive.
    """
    require_positive("radius_mm", radius_mm)
    require_positive("density_g_cm3", density_g_cm3)
    volume_cm3 = 4.0 / 3.0 * math.pi * radius_mm**3 * CUBIC_MM_PER_CUBIC_CM
    return volume_cm3 * density_g_cm3 * MILLIGRAMS_PER_GRAM


def shell_mass_mg(
    outer_radius_mm: float, inner_radius_mm: float, density_g_cm3: float
) -> float:
    """Return the mass of a uniform spherical shell.

    Parameters
    ----------
    outer_radius_mm, inner_radius_mm
        Shell boundaries in millimetres; both strictly positive with the
        outer strictly greater.
    density_g_cm3
        Uniform density in grams per cubic centimetre; strictly
        positive.

    Returns
    -------
    float
        Mass in milligrams.

    Raises
    ------
    DeviceConfigurationError
        If a value is non-finite or not strictly positive, or the outer
        radius does not exceed the inner one. A shell of zero or
        negative thickness is refused rather than returned as a zero or
        negative mass.
    """
    require_positive("outer_radius_mm", outer_radius_mm)
    require_positive("inner_radius_mm", inner_radius_mm)
    require_positive("density_g_cm3", density_g_cm3)
    if outer_radius_mm <= inner_radius_mm:
        raise DeviceConfigurationError(
            "outer_radius_mm: must exceed inner_radius_mm, got "
            f"outer={outer_radius_mm!r} inner={inner_radius_mm!r}"
        )
    volume_cm3 = (
        4.0
        / 3.0
        * math.pi
        * (outer_radius_mm**3 - inner_radius_mm**3)
        * CUBIC_MM_PER_CUBIC_CM
    )
    return volume_cm3 * density_g_cm3 * MILLIGRAMS_PER_GRAM


def require_fraction(name: str, value: float) -> float:
    """Return a fraction when it lies in ``(0, 1]``.

    Parameters
    ----------
    name
        Field name reported in the rejection message.
    value
        Value under validation.

    Returns
    -------
    float
        The validated fraction.

    Raises
    ------
    DeviceConfigurationError
        If the value is non-finite, not strictly positive, or above one.
        A fraction above one is refused rather than clamped: it is a
        statement that more was consumed than existed.
    """
    require_positive(name, value)
    if value > 1.0:
        raise DeviceConfigurationError(f"{name}: must not exceed 1.0, got {value!r}")
    return value


def fusion_yield_mj(fuel_mass_mg: float, burnup_fraction: float) -> float:
    """Return the energy released by burning part of a fuel inventory.

    Parameters
    ----------
    fuel_mass_mg
        Fuel inventory in milligrams; strictly positive.
    burnup_fraction
        Fraction of that inventory consumed, in ``(0, 1]``.

    Returns
    -------
    float
        Released energy in megajoules.

    Raises
    ------
    DeviceConfigurationError
        If the mass is not strictly positive or the fraction leaves its
        interval.
    """
    require_positive("fuel_mass_mg", fuel_mass_mg)
    require_fraction("burnup_fraction", burnup_fraction)
    grams = fuel_mass_mg / MILLIGRAMS_PER_GRAM
    return grams * burnup_fraction * dt_specific_energy_j_per_g() / 1.0e6


def burnup_from_yield(yield_mj: float, fuel_mass_mg: float) -> float:
    """Return the burn-up fraction a yield implies for an inventory.

    The inverse of :func:`fusion_yield_mj`, and the direction the filed
    sources force: they print the yield of a design and never the
    fraction of its fuel that burned.

    Parameters
    ----------
    yield_mj
        Released energy in megajoules; strictly positive.
    fuel_mass_mg
        Fuel inventory in milligrams; strictly positive.

    Returns
    -------
    float
        The implied fraction. It is **not** validated as a fraction:
        a value above one is a meaningful answer here, and it says the
        yield cannot come from that inventory. A caller that needs the
        refusal applies :func:`require_fraction` to the result.

    Raises
    ------
    DeviceConfigurationError
        If either value is non-finite or not strictly positive.
    """
    require_positive("yield_mj", yield_mj)
    require_positive("fuel_mass_mg", fuel_mass_mg)
    grams = fuel_mass_mg / MILLIGRAMS_PER_GRAM
    return yield_mj * 1.0e6 / (grams * dt_specific_energy_j_per_g())


def areal_density_g_cm2(path_length_mm: float, density_g_cm3: float) -> float:
    """Return the areal density along a path through uniform material.

    Parameters
    ----------
    path_length_mm
        Length of the path in millimetres; strictly positive. For a
        solid sphere that is its radius; for a shell it is its
        thickness, and the caller decides which it means.
    density_g_cm3
        Uniform density in grams per cubic centimetre; strictly
        positive.

    Returns
    -------
    float
        ``rho L`` in grams per square centimetre, which is the unit ion
        ranges and burn fractions are quoted in.

    Raises
    ------
    DeviceConfigurationError
        If either value is non-finite or not strictly positive.
    """
    require_positive("path_length_mm", path_length_mm)
    require_positive("density_g_cm3", density_g_cm3)
    return density_g_cm3 * path_length_mm / MILLIMETRES_PER_CENTIMETRE
