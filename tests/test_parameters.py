# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN ICF Beam Core — parameter model tests

"""Every validation branch of the beam-ICF parameter model.

All parameter sets in this module are synthetic fixtures; none describes
any real machine.
"""

from __future__ import annotations

import math
from typing import Any

import pytest

from scpn_icf_beam_core.errors import DeviceConfigurationError
from scpn_icf_beam_core.parameters import (
    BeamDriver,
    TargetDeclaration,
    require_finite,
    require_positive,
)


def synthetic_driver(**overrides: Any) -> BeamDriver:
    """Build a valid synthetic beam driver with optional overrides."""
    values: dict[str, Any] = {
        "species": "ion",
        "beam_energy_mj": 4.0,
        "pulse_duration_ns": 10.0,
        "particle_energy_gev": 5.0,
    }
    values.update(overrides)
    return BeamDriver(**values)


def test_require_finite_accepts_and_rejects() -> None:
    """The finite guard returns the value and rejects NaN and infinity."""
    assert require_finite("x", 1.5) == 1.5
    for bad in (math.nan, math.inf, -math.inf):
        with pytest.raises(DeviceConfigurationError, match="x: must be finite"):
            require_finite("x", bad)


def test_require_positive_accepts_and_rejects() -> None:
    """The positive guard returns the value and rejects zero and below."""
    assert require_positive("x", 0.1) == 0.1
    for bad in (0.0, -2.0):
        with pytest.raises(DeviceConfigurationError, match="strictly positive"):
            require_positive("x", bad)
    with pytest.raises(DeviceConfigurationError, match="must be finite"):
        require_positive("x", math.nan)


def test_beam_power_formula() -> None:
    """The beam power follows ``E / tau`` exactly."""
    assert synthetic_driver().beam_power_tw() == pytest.approx(4.0e6 / 10.0e-9 / 1.0e12)


@pytest.mark.parametrize(
    ("overrides", "fragment"),
    [
        ({"species": "muon"}, "species"),
        ({"beam_energy_mj": 0.0}, "beam_energy_mj"),
        ({"pulse_duration_ns": -1.0}, "pulse_duration_ns"),
        ({"particle_energy_gev": 0.0}, "particle_energy_gev"),
        ({"beam_energy_mj": math.nan}, "beam_energy_mj"),
    ],
)
def test_invalid_driver_is_rejected(overrides: dict[str, Any], fragment: str) -> None:
    """Each driver violation is rejected with its field name."""
    with pytest.raises(DeviceConfigurationError, match=fragment):
        synthetic_driver(**overrides)


def test_electron_species_constructs() -> None:
    """The electron species class constructs."""
    assert synthetic_driver(species="electron").species == "electron"


def test_invalid_target_is_rejected() -> None:
    """Non-positive pellet radii are rejected."""
    with pytest.raises(DeviceConfigurationError, match="pellet_radius_um"):
        TargetDeclaration(pellet_radius_um=0.0)
    with pytest.raises(DeviceConfigurationError, match="pellet_radius_um"):
        TargetDeclaration(pellet_radius_um=math.inf)
