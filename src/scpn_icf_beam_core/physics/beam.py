# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN ICF Beam Core — beam illumination geometry and ion range

"""What a particle-beam driver puts on the target, in closed form.

A beam-driven target is illuminated by many beams arriving in two cones,
and the filed source that describes that arrangement prints its
geometry: each beam is focused to an ellipse and the ellipses are
overlaid into an annulus on the end of the enclosure. The elliptical
shape is not decorative — an alternating-gradient focusing system
focuses in one plane and defocuses in the other, so an ellipse is what
such a system produces.

**The effective radius of an elliptical spot is the geometric mean of
its semi-axes**, which is the radius of the circle of the same area.
That is the relation the source states and this module implements; it
is reproduced from the source's own printed semi-axes to the precision
the source prints its answer at, and the tests say which precision.

The ion range is treated as **data, not as a law**. The source prints
three range-and-energy pairs. Fitting a power law through them and
calling it the range would be inventing a relation the source does not
state; instead this module exposes the exponent between any two printed
pairs, and the tests record that the exponent is not the same for
every pair.

Design record: ADR 0005.
"""

from __future__ import annotations

import math
from typing import Final

from scpn_icf_beam_core.errors import DeviceConfigurationError
from scpn_icf_beam_core.parameters import require_positive

#: Fewest beams a single illumination cone can carry. One beam per side
#: is the two-beam arrangement the filed source describes as the
#: original assumption before multibeam geometry was required.
MIN_BEAMS_PER_SIDE: Final = 1
#: Illumination cones. A beam-driven target is illuminated from both
#: ends of its enclosure; the source's arrangements are all two-sided.
ILLUMINATION_SIDES: Final = 2


def require_beam_count(beams_per_side: int) -> int:
    """Validate a per-side beam count.

    Parameters
    ----------
    beams_per_side
        Number of beams in one illumination cone.

    Returns
    -------
    int
        The validated count.

    Raises
    ------
    DeviceConfigurationError
        If the count is below :data:`MIN_BEAMS_PER_SIDE`. A cone with no
        beam in it does not illuminate anything.
    """
    if beams_per_side < MIN_BEAMS_PER_SIDE:
        raise DeviceConfigurationError(
            f"beams_per_side: must be at least {MIN_BEAMS_PER_SIDE}, "
            f"got {beams_per_side!r}"
        )
    return beams_per_side


def total_beam_count(beams_per_side: int) -> int:
    """Return the total number of beams of a two-sided arrangement.

    Parameters
    ----------
    beams_per_side
        Beams in one illumination cone.

    Returns
    -------
    int
        Twice that count.

    Raises
    ------
    DeviceConfigurationError
        If the per-side count is below the minimum.
    """
    return ILLUMINATION_SIDES * require_beam_count(beams_per_side)


def elliptical_spot_area_mm2(
    major_semi_axis_mm: float, minor_semi_axis_mm: float
) -> float:
    """Return the area of one elliptical focal spot.

    Parameters
    ----------
    major_semi_axis_mm, minor_semi_axis_mm
        Semi-axes in millimetres; both strictly positive.

    Returns
    -------
    float
        ``pi a b`` in square millimetres.

    Raises
    ------
    DeviceConfigurationError
        If either semi-axis is non-finite or not strictly positive. The
        two are **not** required to be ordered: which of them is the
        larger depends on the focusing plane, and refusing the swapped
        pair would refuse a legitimate description of the same spot.
    """
    require_positive("major_semi_axis_mm", major_semi_axis_mm)
    require_positive("minor_semi_axis_mm", minor_semi_axis_mm)
    return math.pi * major_semi_axis_mm * minor_semi_axis_mm


def effective_spot_radius_mm(
    major_semi_axis_mm: float, minor_semi_axis_mm: float
) -> float:
    """Return the radius of the circle of the same area as the spot.

    Parameters
    ----------
    major_semi_axis_mm, minor_semi_axis_mm
        Semi-axes in millimetres; both strictly positive.

    Returns
    -------
    float
        ``sqrt(a b)``, the geometric mean of the semi-axes.

    Raises
    ------
    DeviceConfigurationError
        If either semi-axis is non-finite or not strictly positive.
    """
    require_positive("major_semi_axis_mm", major_semi_axis_mm)
    require_positive("minor_semi_axis_mm", minor_semi_axis_mm)
    return math.sqrt(major_semi_axis_mm * minor_semi_axis_mm)


def energy_per_beam_mj(total_energy_mj: float, beams_per_side: int) -> float:
    """Return the energy each beam of an arrangement carries.

    Parameters
    ----------
    total_energy_mj
        Energy delivered by the whole arrangement, in megajoules;
        strictly positive.
    beams_per_side
        Beams in one illumination cone.

    Returns
    -------
    float
        The total divided equally among every beam. An equal split is a
        statement about this model, not about any accelerator: the
        filed source's arrangements are symmetric, and a design with
        unequal beams is outside what this relation describes.

    Raises
    ------
    DeviceConfigurationError
        If the energy is not strictly positive or the count is below the
        minimum.
    """
    require_positive("total_energy_mj", total_energy_mj)
    return total_energy_mj / total_beam_count(beams_per_side)


def spot_fluence_mj_per_mm2(
    energy_mj: float, major_semi_axis_mm: float, minor_semi_axis_mm: float
) -> float:
    """Return the energy density delivered onto one elliptical spot.

    Parameters
    ----------
    energy_mj
        Energy arriving on the spot, in megajoules; strictly positive.
    major_semi_axis_mm, minor_semi_axis_mm
        Semi-axes of the spot in millimetres; both strictly positive.

    Returns
    -------
    float
        Megajoules per square millimetre, taken over the ellipse's full
        area. The filed source's beams carry a Gaussian profile rather
        than a uniform one, so this is the spot-averaged value and never
        a peak.

    Raises
    ------
    DeviceConfigurationError
        If any value is non-finite or not strictly positive.
    """
    require_positive("energy_mj", energy_mj)
    return energy_mj / elliptical_spot_area_mm2(major_semi_axis_mm, minor_semi_axis_mm)


def range_energy_exponent(
    lower_energy_gev: float,
    lower_range_g_cm2: float,
    upper_energy_gev: float,
    upper_range_g_cm2: float,
) -> float:
    """Return the power-law exponent between two range-and-energy pairs.

    The exponent ``n`` for which ``R2 / R1 == (E2 / E1) ** n``.

    Parameters
    ----------
    lower_energy_gev, lower_range_g_cm2
        The first pair; both strictly positive.
    upper_energy_gev, upper_range_g_cm2
        The second pair; both strictly positive, with the energy
        strictly greater than the first.

    Returns
    -------
    float
        The exponent joining exactly those two pairs. It is a
        **measurement of two points**, never a fitted range law: the
        filed source prints pairs and states no relation between them,
        and the exponent this returns is not the same for every pair of
        points it prints.

    Raises
    ------
    DeviceConfigurationError
        If any value is non-finite or not strictly positive, or the two
        energies are not distinct and ordered. Equal energies are
        refused rather than returning an infinity.
    """
    require_positive("lower_energy_gev", lower_energy_gev)
    require_positive("lower_range_g_cm2", lower_range_g_cm2)
    require_positive("upper_energy_gev", upper_energy_gev)
    require_positive("upper_range_g_cm2", upper_range_g_cm2)
    if upper_energy_gev <= lower_energy_gev:
        raise DeviceConfigurationError(
            "upper_energy_gev: must exceed lower_energy_gev, got "
            f"{upper_energy_gev!r} <= {lower_energy_gev!r}"
        )
    return math.log(upper_range_g_cm2 / lower_range_g_cm2) / math.log(
        upper_energy_gev / lower_energy_gev
    )
