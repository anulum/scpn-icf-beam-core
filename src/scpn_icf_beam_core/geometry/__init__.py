# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN ICF Beam Core — device geometry package

"""The two geometry tiers of the beam-driven ICF family.

**This package declares nothing.** A beam-ICF capsule is three
concentric bodies and all three of its radii already have homes: the
outermost in the configuration's target declaration, and the other two
in the level-0 capsule declaration, whose mass inventory is computed
from them. There is no fourth object to declare, because no filed source
prints a dimension of the radiation enclosure and inventing one would be
the only way to draw it.

So this package is two builders and the constants that identify what
they build. Design record: ADR 0006.
"""

from __future__ import annotations

from scpn_icf_beam_core.geometry.cad import (
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
from scpn_icf_beam_core.geometry.model import (
    BODY_ABLATOR_SHELL,
    BODY_FUEL_ICE_SHELL,
    BODY_FUEL_VAPOUR_CORE,
    BODY_NAMES_BY_IDENTIFIER,
    CAPSULE_BODY_NAMES,
    MATERIAL_BERYLLIUM_ABLATOR,
    MATERIAL_FUEL_VAPOUR,
    MATERIAL_SOLID_FUEL,
    MILLIMETRE_M,
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

__all__ = [
    "BODY_ABLATOR_SHELL",
    "BODY_FUEL_ICE_SHELL",
    "BODY_FUEL_VAPOUR_CORE",
    "BODY_NAMES_BY_IDENTIFIER",
    "CAD_MODEL_NON_CLAIMS",
    "CAD_MODEL_SCHEMA",
    "CAD_MODEL_SCHEMA_VERSION",
    "CAD_MODEL_UNITS",
    "CAPSULE_BODY_NAMES",
    "DEFAULT_ANGULAR_DEFLECTION_RAD",
    "DEFAULT_LINEAR_DEFLECTION_M",
    "DEFAULT_REFERENCE_MESH_SEGMENTS",
    "DEFAULT_SPHERE_RINGS",
    "MATERIAL_BERYLLIUM_ABLATOR",
    "MATERIAL_FUEL_VAPOUR",
    "MATERIAL_SOLID_FUEL",
    "MILLIMETRE_M",
    "MODEL_NON_CLAIMS",
    "MODEL_SCHEMA",
    "MODEL_SCHEMA_VERSION",
    "MODEL_UNITS",
    "ROLE_ABLATOR",
    "ROLE_FUEL",
    "DeviceModel3D",
    "DeviceModelCAD",
    "build_device_cad",
    "build_device_model",
    "capsule_radii_m",
]
