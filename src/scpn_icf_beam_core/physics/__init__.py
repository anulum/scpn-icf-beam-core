# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN ICF Beam Core — level-0 device physics package

"""Closed-form level-0 physics of a beam-driven inertial-fusion target.

Three surfaces: the illumination geometry a particle-beam driver puts on
the target, the mass inventory of a layered capsule and the energy its
fuel can release, and the chain of efficiencies between the beam and
that energy. Nothing here integrates anything in time. Design record:
ADR 0005.
"""

from __future__ import annotations

from scpn_icf_beam_core.physics.beam import (
    ILLUMINATION_SIDES,
    MIN_BEAMS_PER_SIDE,
    effective_spot_radius_mm,
    elliptical_spot_area_mm2,
    energy_per_beam_mj,
    range_energy_exponent,
    require_beam_count,
    spot_fluence_mj_per_mm2,
    total_beam_count,
)
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
from scpn_icf_beam_core.physics.coupling import (
    absorbed_energy_mj,
    capsule_gain,
    enclosure_area_mm2,
    equivalent_enclosure_radius_mm,
    implied_conversion_efficiency,
    require_species,
    sphere_area_mm2,
    target_gain,
)
from scpn_icf_beam_core.physics.level0 import (
    LEVEL0_NON_CLAIMS,
    LEVEL0_SCHEMA,
    LEVEL0_SCHEMA_VERSION,
    MICROMETRES_PER_MILLIMETRE,
    CapsuleDeclaration,
    IlluminationDeclaration,
    Level0Physics,
    OperatingPoint,
    ShotDeclaration,
    ablator_thickness_mm,
    level0_physics,
    pellet_radius_mm,
)

__all__ = [
    "DT_FUSION_ENERGY_MEV",
    "ILLUMINATION_SIDES",
    "LEVEL0_NON_CLAIMS",
    "LEVEL0_SCHEMA",
    "LEVEL0_SCHEMA_VERSION",
    "MICROMETRES_PER_MILLIMETRE",
    "MIN_BEAMS_PER_SIDE",
    "CapsuleDeclaration",
    "IlluminationDeclaration",
    "Level0Physics",
    "OperatingPoint",
    "ShotDeclaration",
    "ablator_thickness_mm",
    "absorbed_energy_mj",
    "areal_density_g_cm2",
    "burnup_from_yield",
    "capsule_gain",
    "dt_specific_energy_j_per_g",
    "effective_spot_radius_mm",
    "elliptical_spot_area_mm2",
    "enclosure_area_mm2",
    "energy_per_beam_mj",
    "equivalent_enclosure_radius_mm",
    "fusion_yield_mj",
    "implied_conversion_efficiency",
    "level0_physics",
    "pellet_radius_mm",
    "range_energy_exponent",
    "require_beam_count",
    "require_fraction",
    "require_species",
    "shell_mass_mg",
    "sphere_area_mm2",
    "sphere_mass_mg",
    "spot_fluence_mj_per_mm2",
    "target_gain",
    "total_beam_count",
]
