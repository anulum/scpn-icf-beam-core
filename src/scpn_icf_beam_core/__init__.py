# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN ICF Beam Core — device capability package

"""Device capability models of the SCPN beam-ICF device family.

Public surface of the ``device_configuration_model``,
``diagnostic_clock_semantics``, ``level0_device_physics``,
``device_3d_model`` and ``device_cad_model`` capabilities at
``computational_prototype`` maturity: validated parameter objects,
synthetic diagnostic and clock declarations aligned with the pinned SPO
observability catalogue, the illumination geometry of a particle-beam
driver, the mass inventory of a layered capsule and the chain of
efficiencies between the beam and the energy its fuel releases, the
tessellated and B-rep models of that capsule on the shared kernel
library, documented consistency estimates, canonical serialisation with
SHA-256 digests, and data-only pins to the SPO registries. No claim
about any real machine or diagnostic is made anywhere in this package.
"""

from __future__ import annotations

from typing import Final

from scpn_icf_beam_core.configuration import (
    HEAVY_ION_ENERGY_WINDOW_GEV,
    OWNED_CONFIGURATIONS,
    SPECIES_BY_IDENTIFIER,
    ConsistencyFinding,
    DeviceConfiguration,
    RegistryBinding,
    configuration_from_bytes,
    configuration_from_record,
)
from scpn_icf_beam_core.errors import (
    DeviceConfigurationError,
    DeviceGeometryError,
    DiagnosticPlanError,
)
from scpn_icf_beam_core.geometry import (
    BODY_ABLATOR_SHELL,
    BODY_FUEL_ICE_SHELL,
    BODY_FUEL_VAPOUR_CORE,
    BODY_NAMES_BY_IDENTIFIER,
    CAD_MODEL_NON_CLAIMS,
    CAD_MODEL_SCHEMA,
    CAD_MODEL_SCHEMA_VERSION,
    MODEL_NON_CLAIMS,
    MODEL_SCHEMA,
    MODEL_SCHEMA_VERSION,
    DeviceModel3D,
    DeviceModelCAD,
    build_device_cad,
    build_device_model,
)
from scpn_icf_beam_core.observability import (
    APPLICABLE_CANDIDATES,
    CATALOGUE_BINDING,
    CandidateProfile,
    ClockKind,
    ClockModel,
    ClockRelation,
    DeferredCandidate,
    DiagnosticChannelPlan,
    DiagnosticPlan,
    FrameKind,
    ObservabilityBinding,
    ObservabilityClass,
    ReferenceFrame,
    SemanticCarrier,
    plan_from_bytes,
    plan_from_record,
)
from scpn_icf_beam_core.parameters import (
    BEAM_SPECIES,
    BeamDriver,
    TargetDeclaration,
)
from scpn_icf_beam_core.physics import (
    LEVEL0_NON_CLAIMS,
    LEVEL0_SCHEMA,
    LEVEL0_SCHEMA_VERSION,
    CapsuleDeclaration,
    IlluminationDeclaration,
    Level0Physics,
    OperatingPoint,
    ShotDeclaration,
    burnup_from_yield,
    capsule_gain,
    dt_specific_energy_j_per_g,
    effective_spot_radius_mm,
    implied_conversion_efficiency,
    level0_physics,
    target_gain,
)
from scpn_icf_beam_core.plan_envelope import (
    PlanEnvelope,
    envelope_for_plan,
    envelope_from_bytes,
    envelope_from_record,
    verify_envelope,
)

__version__: Final = "0.1.0.dev0"

__all__ = [
    "APPLICABLE_CANDIDATES",
    "BEAM_SPECIES",
    "BODY_ABLATOR_SHELL",
    "BODY_FUEL_ICE_SHELL",
    "BODY_FUEL_VAPOUR_CORE",
    "BODY_NAMES_BY_IDENTIFIER",
    "CAD_MODEL_NON_CLAIMS",
    "CAD_MODEL_SCHEMA",
    "CAD_MODEL_SCHEMA_VERSION",
    "CATALOGUE_BINDING",
    "HEAVY_ION_ENERGY_WINDOW_GEV",
    "LEVEL0_NON_CLAIMS",
    "LEVEL0_SCHEMA",
    "LEVEL0_SCHEMA_VERSION",
    "MODEL_NON_CLAIMS",
    "MODEL_SCHEMA",
    "MODEL_SCHEMA_VERSION",
    "OWNED_CONFIGURATIONS",
    "SPECIES_BY_IDENTIFIER",
    "BeamDriver",
    "CandidateProfile",
    "CapsuleDeclaration",
    "ClockKind",
    "ClockModel",
    "ClockRelation",
    "ConsistencyFinding",
    "DeferredCandidate",
    "DeviceConfiguration",
    "DeviceConfigurationError",
    "DeviceGeometryError",
    "DeviceModel3D",
    "DeviceModelCAD",
    "DiagnosticChannelPlan",
    "DiagnosticPlan",
    "DiagnosticPlanError",
    "FrameKind",
    "IlluminationDeclaration",
    "Level0Physics",
    "ObservabilityBinding",
    "ObservabilityClass",
    "OperatingPoint",
    "PlanEnvelope",
    "ReferenceFrame",
    "RegistryBinding",
    "SemanticCarrier",
    "ShotDeclaration",
    "TargetDeclaration",
    "__version__",
    "build_device_cad",
    "build_device_model",
    "burnup_from_yield",
    "capsule_gain",
    "configuration_from_bytes",
    "configuration_from_record",
    "dt_specific_energy_j_per_g",
    "effective_spot_radius_mm",
    "envelope_for_plan",
    "envelope_from_bytes",
    "envelope_from_record",
    "implied_conversion_efficiency",
    "level0_physics",
    "plan_from_bytes",
    "plan_from_record",
    "target_gain",
    "verify_envelope",
]
