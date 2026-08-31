# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN ICF Beam Core — beam-ICF parameter model

"""Validated parameter objects of a beam-driven ICF configuration.

The derived quantity implements one standard estimate and nothing more:
the beam power ``P = E / tau``. It is a rough consistency instrument
with documented applicability bounds (heavy-ion driver window;
R. O. Bangerter, A. Faltens, P. A. Seidl, Rev. Accel. Sci. Technol. 6
(2013) 85); no claim about any real machine follows from it.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Final

from scpn_icf_beam_core.errors import DeviceConfigurationError

BEAM_SPECIES: Final = ("electron", "ion")


def require_finite(name: str, value: float) -> float:
    """Return ``value`` when finite, otherwise fail closed.

    Parameters
    ----------
    name
        Field name reported in the rejection message.
    value
        Value under validation.

    Returns
    -------
    float
        The validated value.

    Raises
    ------
    DeviceConfigurationError
        If ``value`` is NaN or infinite; non-finite input is rejected,
        never clamped.
    """
    if not math.isfinite(value):
        raise DeviceConfigurationError(f"{name}: must be finite, got {value!r}")
    return value


def require_positive(name: str, value: float) -> float:
    """Return ``value`` when finite and strictly positive.

    Parameters
    ----------
    name
        Field name reported in the rejection message.
    value
        Value under validation.

    Returns
    -------
    float
        The validated value.

    Raises
    ------
    DeviceConfigurationError
        If ``value`` is non-finite or not strictly positive.
    """
    require_finite(name, value)
    if value <= 0.0:
        raise DeviceConfigurationError(
            f"{name}: must be strictly positive, got {value!r}"
        )
    return value


@dataclass(frozen=True, slots=True)
class BeamDriver:
    """Particle-beam driver of a beam-ICF configuration.

    Parameters
    ----------
    species
        Beam species class: ``ion`` or ``electron``.
    beam_energy_mj
        Total delivered beam energy in megajoules; strictly positive.
    pulse_duration_ns
        Pulse duration in nanoseconds; strictly positive.
    particle_energy_gev
        Kinetic energy per particle in gigaelectronvolts; strictly
        positive.

    Raises
    ------
    DeviceConfigurationError
        If the species is unknown or a parameter violates its bound.
    """

    species: str
    beam_energy_mj: float
    pulse_duration_ns: float
    particle_energy_gev: float

    def __post_init__(self) -> None:
        """Validate the beam-driver invariants.

        Raises
        ------
        DeviceConfigurationError
            If the species is unknown or a parameter violates its
            bound.
        """
        if self.species not in BEAM_SPECIES:
            raise DeviceConfigurationError(
                f"species: must be one of {BEAM_SPECIES!r}, got {self.species!r}"
            )
        require_positive("beam_energy_mj", self.beam_energy_mj)
        require_positive("pulse_duration_ns", self.pulse_duration_ns)
        require_positive("particle_energy_gev", self.particle_energy_gev)

    def beam_power_tw(self) -> float:
        """Beam power of the validated driver.

        Returns
        -------
        float
            ``P = E / tau`` in terawatts.
        """
        energy_j = self.beam_energy_mj * 1.0e6
        duration_s = self.pulse_duration_ns * 1.0e-9
        return energy_j / duration_s / 1.0e12


@dataclass(frozen=True, slots=True)
class TargetDeclaration:
    """Target declaration of a beam-ICF configuration.

    Parameters
    ----------
    pellet_radius_um
        Pellet outer radius in micrometres; strictly positive.

    Raises
    ------
    DeviceConfigurationError
        If the radius is non-finite or not strictly positive.
    """

    pellet_radius_um: float

    def __post_init__(self) -> None:
        """Validate the target invariants.

        Raises
        ------
        DeviceConfigurationError
            If the radius is non-finite or not strictly positive.
        """
        require_positive("pellet_radius_um", self.pellet_radius_um)
