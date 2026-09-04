# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN ICF Beam Core — level-0 physics anchors and builders

"""Anchors and builders shared by the level-0 physics tests.

Reproducing a printed value is an anchor, never a claim about that
machine.

The work this repository cites for its driver window — Bangerter,
Faltens & Seidl, *Rev. Accel. Sci. Technol.* **6** (2013) 85 — is behind
a subscription and is not on file. Two United States Department of
Energy laboratory preprints are, both marked for unlimited
distribution, and every constant below whose name begins ``PRINTED_``
is read from one of them:

- ``HO_`` — D. D.-M. Ho, J. A. Harte, M. Tabak, *Radiation-Driven
  Targets for Heavy-Ion Fusion*, UCRL-JC-118161 (1994). The capsule and
  the coupling chain.
- ``CALLAHAN_`` — D. A. Callahan-Miller, M. Tabak, *A Distributed
  Radiator, Heavy Ion Driven Inertial Confinement Fusion Target with
  Realistic, Multibeam Illumination Geometry*, UCRL-JC-131974 (1998).
  The beam arrangement and four driver-energy-and-yield pairs.

Both were read off rendered pages. In the Ho preprint that was
load-bearing: the running text names the ablator's outer radius and the
fuel layer's outer radius and stops there, and the **third** radius —
the fuel layer's inner boundary, which is what makes the cavity
determinate — appears only in its Fig. 1. Taking the text alone would
have forced that radius to be declared instead of anchored.

**Two of this family's quantities run backwards**, and the fixtures say
so in their names. The sources print a yield and never a burn-up
fraction, and they plot a conversion efficiency and never print one, so
both are obtained from other printed numbers rather than reproduced.

**The driver energy of the Ho design is not printed.** It is
reconstructed from the printed yield and the printed system gain, and
is named ``RECONSTRUCTED_`` for that reason. A test that recovered the
printed gain from it would be a round trip and is not written; what the
tests assert instead is what the chain requires to close.

Both filed sources describe heavy-ion drivers. Nothing here is evidence
about the ``pulsed_electron_beam_icf`` configuration, and the tests that
touch that class say so.
"""

from __future__ import annotations

from typing import Final

from scpn_icf_beam_core.configuration import DeviceConfiguration, RegistryBinding
from scpn_icf_beam_core.parameters import BeamDriver, TargetDeclaration
from scpn_icf_beam_core.physics.level0 import (
    CapsuleDeclaration,
    IlluminationDeclaration,
    ShotDeclaration,
)

# --- Ho et al. 1994, Fig. 1: the capsule, in millimetres and g/cm3 ---
PRINTED_HO_PELLET_RADIUS_MM: Final = 2.34
PRINTED_HO_FUEL_OUTER_RADIUS_MM: Final = 2.12
PRINTED_HO_FUEL_INNER_RADIUS_MM: Final = 1.8
PRINTED_HO_ABLATOR_DENSITY_G_CM3: Final = 1.85
PRINTED_HO_FUEL_DENSITY_G_CM3: Final = 0.25
PRINTED_HO_VAPOUR_DENSITY_G_CM3: Final = 0.3e-3

# --- Ho et al. 1994, abstract and sections 1-2: the coupling chain ---
PRINTED_HO_ABSORBED_ENERGY_MJ: Final = 1.0
PRINTED_HO_YIELD_MJ: Final = 430.0
PRINTED_HO_COUPLING_EFFICIENCY: Final = 0.21
PRINTED_HO_SYSTEM_GAIN: Final = 80.0
PRINTED_HO_AREA_RATIO: Final = 0.075
PRINTED_HO_PEAK_RADIATION_TEMPERATURE_EV: Final = 260.0
PRINTED_HO_CONVERTER_OPENING_RADIUS_CM: Final = 0.15
PRINTED_HO_ION_ENERGIES_GEV: Final = (5.0, 7.5, 10.0)

# --- Callahan-Miller & Tabak 1998: the beam arrangement ---
PRINTED_CALLAHAN_MAJOR_SEMI_AXIS_MM: Final = 4.15
PRINTED_CALLAHAN_MINOR_SEMI_AXIS_MM: Final = 1.8
PRINTED_CALLAHAN_EFFECTIVE_RADIUS_MM: Final = 2.7
PRINTED_CALLAHAN_CLOSE_MAJOR_SEMI_AXIS_MM: Final = 2.78
PRINTED_CALLAHAN_CLOSE_MINOR_SEMI_AXIS_MM: Final = 1.0
PRINTED_CALLAHAN_CLOSE_EFFECTIVE_RADIUS_MM: Final = 1.67
PRINTED_CALLAHAN_FOOT_BEAMS_PER_SIDE: Final = 8
PRINTED_CALLAHAN_MAIN_BEAMS_PER_SIDE: Final = 16
PRINTED_CALLAHAN_FOOT_ION_ENERGY_GEV: Final = 3.0
PRINTED_CALLAHAN_MAIN_ION_ENERGY_GEV: Final = 4.0

#: Driver energy, yield and the gain the review prints for each of its
#: four cases, in megajoules. The fourth case prints no gain.
PRINTED_CALLAHAN_CASES: Final = (
    (6.35, 370.0, 58.0),
    (7.4, 413.0, 55.0),
    (3.3, 436.0, 132.0),
    (5.9, 390.0, None),
)

#: Ion kinetic energy and the range the review states for it, in GeV and
#: grams per square centimetre.
PRINTED_CALLAHAN_RANGE_PAIRS: Final = (
    (4.0, 0.035),
    (5.5, 0.05),
    (8.0, 0.08),
)

# --- Not printed by either source; reconstructed and named for it ---
RECONSTRUCTED_HO_DRIVER_ENERGY_MJ: Final = PRINTED_HO_YIELD_MJ / PRINTED_HO_SYSTEM_GAIN

# --- Synthetic; pins nothing ---
SYNTHETIC_REGISTRY_VERSION: Final = "1.0.0"
SYNTHETIC_REGISTRY_DIGEST: Final = "0" * 64
# Not printed by either source. Declared so the driver has a duration
# and the beam power has an input; no value is attributed to a design.
DECLARED_PULSE_DURATION_NS: Final = 10.0


def registry_binding() -> RegistryBinding:
    """Build the synthetic registry pin the fixtures share.

    Returns
    -------
    RegistryBinding
        A well-formed pin; its digest is synthetic and pins nothing.
    """
    return RegistryBinding(
        version=SYNTHETIC_REGISTRY_VERSION,
        digest_sha256=SYNTHETIC_REGISTRY_DIGEST,
    )


def anchor_configuration(*, identifier: str = "ion_beam_icf") -> DeviceConfiguration:
    """Build the configuration the anchors are evaluated on.

    Parameters
    ----------
    identifier
        Which owned configuration to build; the default is the
        heavy-ion class both filed sources describe.

    Returns
    -------
    DeviceConfiguration
        A configuration carrying the reconstructed driver energy, the
        main-pulse ion energy the illumination review prints, and the
        pellet radius the capsule review prints.
    """
    species = "ion" if identifier == "ion_beam_icf" else "electron"
    return DeviceConfiguration(
        identifier=identifier,
        driver=BeamDriver(
            species=species,
            beam_energy_mj=RECONSTRUCTED_HO_DRIVER_ENERGY_MJ,
            pulse_duration_ns=DECLARED_PULSE_DURATION_NS,
            particle_energy_gev=PRINTED_CALLAHAN_MAIN_ION_ENERGY_GEV,
        ),
        target=TargetDeclaration(pellet_radius_um=PRINTED_HO_PELLET_RADIUS_MM * 1.0e3),
        registry=registry_binding(),
    )


def anchor_capsule() -> CapsuleDeclaration:
    """Build the capsule layering the capsule review prints.

    Returns
    -------
    CapsuleDeclaration
        The two inner radii and the three densities of its Fig. 1. The
        outermost radius is not here: it belongs to the configuration.
    """
    return CapsuleDeclaration(
        ablator_density_g_cm3=PRINTED_HO_ABLATOR_DENSITY_G_CM3,
        fuel_outer_radius_mm=PRINTED_HO_FUEL_OUTER_RADIUS_MM,
        fuel_inner_radius_mm=PRINTED_HO_FUEL_INNER_RADIUS_MM,
        fuel_density_g_cm3=PRINTED_HO_FUEL_DENSITY_G_CM3,
        vapour_density_g_cm3=PRINTED_HO_VAPOUR_DENSITY_G_CM3,
    )


def anchor_illumination(
    *, beams_per_side: int = PRINTED_CALLAHAN_MAIN_BEAMS_PER_SIDE
) -> IlluminationDeclaration:
    """Build the beam arrangement the illumination review prints.

    Parameters
    ----------
    beams_per_side
        Beams in one cone; the default is the main pulse's count.

    Returns
    -------
    IlluminationDeclaration
        The declared arrangement with the review's printed semi-axes.
    """
    return IlluminationDeclaration(
        beams_per_side=beams_per_side,
        major_semi_axis_mm=PRINTED_CALLAHAN_MAJOR_SEMI_AXIS_MM,
        minor_semi_axis_mm=PRINTED_CALLAHAN_MINOR_SEMI_AXIS_MM,
    )


def anchor_shot() -> ShotDeclaration:
    """Build the shot outcome the capsule review prints.

    Returns
    -------
    ShotDeclaration
        The printed absorbed energy, yield, coupling efficiency and
        capsule-to-enclosure area ratio.
    """
    return ShotDeclaration(
        absorbed_energy_mj=PRINTED_HO_ABSORBED_ENERGY_MJ,
        yield_mj=PRINTED_HO_YIELD_MJ,
        coupling_efficiency=PRINTED_HO_COUPLING_EFFICIENCY,
        capsule_to_enclosure_area_ratio=PRINTED_HO_AREA_RATIO,
    )
