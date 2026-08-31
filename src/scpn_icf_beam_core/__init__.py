# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN ICF Beam Core — device configuration model package

"""Device configuration model of the SCPN beam-ICF device family.

Public surface of the ``device_configuration_model`` capability at
``computational_prototype`` maturity: validated parameter objects,
documented consistency estimates, canonical serialisation with SHA-256
digests, and a data-only pin to the SPO reactor registry. No claim about
any real machine is made anywhere in this package.
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
from scpn_icf_beam_core.errors import DeviceConfigurationError
from scpn_icf_beam_core.parameters import (
    BEAM_SPECIES,
    BeamDriver,
    TargetDeclaration,
)

__version__: Final = "0.1.0.dev0"

__all__ = [
    "BEAM_SPECIES",
    "HEAVY_ION_ENERGY_WINDOW_GEV",
    "OWNED_CONFIGURATIONS",
    "SPECIES_BY_IDENTIFIER",
    "BeamDriver",
    "ConsistencyFinding",
    "DeviceConfiguration",
    "DeviceConfigurationError",
    "RegistryBinding",
    "TargetDeclaration",
    "__version__",
    "configuration_from_bytes",
    "configuration_from_record",
]
