# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN ICF Beam Core — device configuration container

"""Device configuration container bound to the SPO reactor registry.

A :class:`DeviceConfiguration` composes a validated beam driver and
target declaration under exactly one of the two registry identifiers
this repository owns. The species class invariant is hard (ion for
`ion_beam_icf`, electron for `pulsed_electron_beam_icf`); an ion-class
per-particle energy outside the documented heavy-ion driver window is
flagged (Bangerter, Faltens & Seidl, RAST 6 (2013) 85). Serialisation
is canonical (sorted keys, no NaN or infinity accepted anywhere) and
the SHA-256 digest of those bytes identifies the exact parameter set.
The registry binding is a data pin only — this package never imports
SCPN Phase Orchestrator code.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from typing import Any, Final

from scpn_icf_beam_core.errors import DeviceConfigurationError
from scpn_icf_beam_core.parameters import BeamDriver, TargetDeclaration

OWNED_CONFIGURATIONS: Final = ("ion_beam_icf", "pulsed_electron_beam_icf")
SPECIES_BY_IDENTIFIER: Final = {
    "ion_beam_icf": "ion",
    "pulsed_electron_beam_icf": "electron",
}
HEAVY_ION_ENERGY_WINDOW_GEV: Final = (1.0, 10.0)
HEX_DIGEST: Final = re.compile(r"^[0-9a-f]{64}$")


@dataclass(frozen=True, slots=True)
class RegistryBinding:
    """Pin to one SPO reactor registry release.

    Parameters
    ----------
    version
        Registry release version; non-empty.
    digest_sha256
        Registry digest as 64 lowercase hexadecimal characters.

    Raises
    ------
    DeviceConfigurationError
        If either pin component is malformed.
    """

    version: str
    digest_sha256: str

    def __post_init__(self) -> None:
        """Validate the registry pin.

        Raises
        ------
        DeviceConfigurationError
            If either pin component is malformed.
        """
        if not self.version:
            raise DeviceConfigurationError("registry.version: must be non-empty")
        if HEX_DIGEST.fullmatch(self.digest_sha256) is None:
            raise DeviceConfigurationError(
                "registry.digest_sha256: must be 64 lowercase hexadecimal "
                f"characters, got {self.digest_sha256!r}"
            )


@dataclass(frozen=True, slots=True)
class ConsistencyFinding:
    """One internal-consistency finding on a device configuration.

    Parameters
    ----------
    field
        Dotted field path the finding refers to.
    message
        Human-readable statement of the inconsistency.
    """

    field: str
    message: str


@dataclass(frozen=True, slots=True)
class DeviceConfiguration:
    """Validated beam-ICF device configuration.

    Parameters
    ----------
    identifier
        SPO registry configuration identifier; one of ``ion_beam_icf``
        or ``pulsed_electron_beam_icf``.
    driver
        Validated beam driver.
    target
        Validated target declaration.
    registry
        Pin to the SPO reactor registry release the identifier belongs
        to.

    Raises
    ------
    DeviceConfigurationError
        If the identifier is not owned by this repository or the driver
        species contradicts it.
    """

    identifier: str
    driver: BeamDriver
    target: TargetDeclaration
    registry: RegistryBinding

    def __post_init__(self) -> None:
        """Validate identifier ownership and the species invariant.

        Raises
        ------
        DeviceConfigurationError
            If the identifier is not owned by this repository or the
            driver species contradicts it.
        """
        if self.identifier not in OWNED_CONFIGURATIONS:
            raise DeviceConfigurationError(
                f"identifier: {self.identifier!r} is not owned by "
                f"SCPN-ICF-BEAM-CORE; owned: {OWNED_CONFIGURATIONS!r}"
            )
        expected = SPECIES_BY_IDENTIFIER[self.identifier]
        if self.driver.species != expected:
            raise DeviceConfigurationError(
                f"driver.species: {self.identifier} requires the "
                f"{expected!r} species, got {self.driver.species!r}"
            )

    def consistency_report(self) -> tuple[ConsistencyFinding, ...]:
        """Report physics-consistency findings without failing.

        Returns
        -------
        tuple of ConsistencyFinding
            Advisory findings from the documented estimates; empty when
            an ion-class per-particle energy sits in the documented
            heavy-ion driver window, and always empty for the electron
            class. Findings are advisory instruments, not machine
            claims.
        """
        findings: list[ConsistencyFinding] = []
        if self.driver.species == "ion":
            low, high = HEAVY_ION_ENERGY_WINDOW_GEV
            energy = self.driver.particle_energy_gev
            if not low <= energy <= high:
                findings.append(
                    ConsistencyFinding(
                        field="driver.particle_energy_gev",
                        message=(
                            f"per-particle energy {energy:.3g} GeV is "
                            f"outside the documented heavy-ion driver "
                            f"window [{low:.0f}, {high:.0f}] GeV"
                        ),
                    )
                )
        return tuple(findings)

    def to_record(self) -> dict[str, Any]:
        """Project the configuration to a JSON-serialisable record.

        Returns
        -------
        dict[str, Any]
            Nested record with every declared parameter.
        """
        return {
            "identifier": self.identifier,
            "driver": {
                "species": self.driver.species,
                "beam_energy_mj": self.driver.beam_energy_mj,
                "pulse_duration_ns": self.driver.pulse_duration_ns,
                "particle_energy_gev": self.driver.particle_energy_gev,
            },
            "target": {
                "pellet_radius_um": self.target.pellet_radius_um,
            },
            "registry": {
                "version": self.registry.version,
                "digest_sha256": self.registry.digest_sha256,
            },
        }

    def canonical_bytes(self) -> bytes:
        """Serialise the configuration canonically.

        Returns
        -------
        bytes
            UTF-8 JSON with sorted keys, minimal separators, and a
            trailing newline; NaN and infinity are never emitted.
        """
        text = json.dumps(
            self.to_record(),
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        return (text + "\n").encode("utf-8")

    def digest_sha256(self) -> str:
        """Identify the exact parameter set.

        Returns
        -------
        str
            SHA-256 digest of :meth:`canonical_bytes` as lowercase hex.
        """
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


def _require_mapping(record: dict[str, Any], field: str) -> dict[str, Any]:
    """Return one required mapping field of a record.

    Parameters
    ----------
    record
        Parent mapping under inspection.
    field
        Key that must hold a mapping.

    Returns
    -------
    dict[str, Any]
        The nested mapping.

    Raises
    ------
    DeviceConfigurationError
        If the field is missing or not a mapping.
    """
    value = record.get(field)
    if not isinstance(value, dict):
        raise DeviceConfigurationError(f"{field}: must be an object")
    return value


def _number(record: dict[str, Any], field: str) -> float:
    """Return one required real-number field of a record.

    Parameters
    ----------
    record
        Mapping under inspection.
    field
        Key that must hold a real number.

    Returns
    -------
    float
        The numeric value; booleans are rejected.

    Raises
    ------
    DeviceConfigurationError
        If the field is missing or not a real number.
    """
    value = record.get(field)
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise DeviceConfigurationError(f"{field}: must be a number, got {value!r}")
    return float(value)


def _string(record: dict[str, Any], field: str) -> str:
    """Return one required string field of a record.

    Parameters
    ----------
    record
        Mapping under inspection.
    field
        Key that must hold a string.

    Returns
    -------
    str
        The string value.

    Raises
    ------
    DeviceConfigurationError
        If the field is missing or not a string.
    """
    value = record.get(field)
    if not isinstance(value, str):
        raise DeviceConfigurationError(f"{field}: must be a string, got {value!r}")
    return value


def configuration_from_record(record: Any) -> DeviceConfiguration:
    """Build a validated configuration from a decoded record.

    Parameters
    ----------
    record
        Decoded JSON object in the shape produced by
        :meth:`DeviceConfiguration.to_record`.

    Returns
    -------
    DeviceConfiguration
        The fully validated configuration.

    Raises
    ------
    DeviceConfigurationError
        If the record shape or any value violates the model.
    """
    if not isinstance(record, dict):
        raise DeviceConfigurationError("record: must be an object")
    known = {"identifier", "driver", "target", "registry"}
    unknown = sorted(set(record) - known)
    if unknown:
        raise DeviceConfigurationError(f"record: unknown fields {unknown!r}")
    driver = _require_mapping(record, "driver")
    target = _require_mapping(record, "target")
    registry = _require_mapping(record, "registry")
    return DeviceConfiguration(
        identifier=_string(record, "identifier"),
        driver=BeamDriver(
            species=_string(driver, "species"),
            beam_energy_mj=_number(driver, "beam_energy_mj"),
            pulse_duration_ns=_number(driver, "pulse_duration_ns"),
            particle_energy_gev=_number(driver, "particle_energy_gev"),
        ),
        target=TargetDeclaration(
            pellet_radius_um=_number(target, "pellet_radius_um"),
        ),
        registry=RegistryBinding(
            version=_string(registry, "version"),
            digest_sha256=_string(registry, "digest_sha256"),
        ),
    )


def configuration_from_bytes(data: bytes) -> DeviceConfiguration:
    """Build a validated configuration from canonical JSON bytes.

    Parameters
    ----------
    data
        UTF-8 JSON document; NaN and infinity literals are rejected.

    Returns
    -------
    DeviceConfiguration
        The fully validated configuration.

    Raises
    ------
    DeviceConfigurationError
        If the document is not valid strict JSON or violates the model.
    """

    def _reject_constant(literal: str) -> float:
        raise DeviceConfigurationError(
            f"record: non-finite JSON literal {literal!r} is rejected"
        )

    try:
        record = json.loads(data.decode("utf-8"), parse_constant=_reject_constant)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise DeviceConfigurationError(f"record: invalid JSON document: {exc}") from exc
    return configuration_from_record(record)
