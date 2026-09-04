# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN ICF Beam Core — tier-G1 device model

"""Tier-G1 tessellated model of a beam-driven ICF target.

The capsule is three concentric bodies about the origin: the ablator
shell, the solid fuel layer inside it, and the vapour the fuel layer
encloses. The vapour carries a body although it is a gas, because the
filed source prints its density and it belongs to the fuel inventory.

**Every radius of this capsule is printed, and none of them is derived.**
The filed source's Fig. 1 gives the ablator's outer radius, the fuel
layer's outer radius and the fuel layer's inner boundary, so the cavity
is anchored rather than obtained by subtracting declared thicknesses.
That is the opposite of the laser-ICF family, whose review prints an
outer radius and two thicknesses; the two families reach the same three
surfaces from different directions and neither arrangement is a model
choice, only a record of what each source prints.

**No enclosure is drawn, and the absence is the decision.** Both filed
sources describe a radiation enclosure, and neither prints one
dimension of it: the running text gives a converter opening radius and
a shell radius used for a wall-motion calculation, neither of which is a
case radius, wall thickness or length, and the one schematic that shows
the enclosure carries axes but no dimension callouts. The level-0 record
does carry an ``equivalent_enclosure_radius_mm``, and it is **not** a
case radius — it is the radius of the sphere whose *area* matches the
enclosure's, obtained from a printed area ratio. A cylinder built on it
would be a fabrication wearing an anchor's clothes.

**The body set therefore does not follow the identifier**, and that too
is a statement about the sources rather than about the machines. The
laser-ICF family draws a fourth body for exactly one of its three
identifiers because its precursor prints dimensionless enclosure
geometry. Here neither owned configuration has an enclosure to draw, and
the electron-beam class has no filed source at all.

The bodies are spheres and spherical shells, both of which the shared
kernel library already builds, so this tier adds no primitive.

**The bodies are inscribed polyhedra of revolution, not ideal spheres.**
A consumer comparing a volume here to ``4/3 pi r^3`` would be comparing
two different solids; the profile volume of the body actually built is
the reference, and the library states the same rule in its own design
record. Design record: ADR 0006.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Final

from scpn_reactor_kernels.errors import GeometryError
from scpn_reactor_kernels.geometry import (
    TriangleMesh,
    require_rings,
    require_segments,
    sphere_solid,
    spherical_shell,
)

from scpn_icf_beam_core.configuration import DeviceConfiguration
from scpn_icf_beam_core.errors import DeviceGeometryError
from scpn_icf_beam_core.physics.level0 import (
    CapsuleDeclaration,
    ablator_thickness_mm,
    pellet_radius_mm,
)

MODEL_SCHEMA: Final = "scpn.beam-icf-3d-model.v1"
MODEL_SCHEMA_VERSION: Final = "1.0.0"
MODEL_UNITS: Final = {
    "length": "metre",
    "handedness": "right",
    "axis": "z along the illumination axis; the capsule is centred on the origin",
    "origin": "the centre of the capsule",
}
MODEL_NON_CLAIMS: Final = (
    "analytic surfaces tessellated from a declared configuration and capsule",
    (
        "every body is an inscribed polyhedron of revolution, never an ideal "
        "sphere; the profile volume of the body built is its own reference"
    ),
    (
        "the capsule is three uniform concentric layers; no fill tube, no "
        "mounting stalk, no surface roughness and no layer non-uniformity is "
        "modelled, and those are the quantities an implosion is sensitive to"
    ),
    (
        "no radiation enclosure is drawn: the filed sources print no case "
        "radius, wall thickness or length, and the level-0 equivalent "
        "enclosure radius is the radius of a sphere of equal area rather than "
        "a dimension of any case"
    ),
    (
        "no beam, focal spot, final-focus magnet or converter is drawn; the "
        "illumination is a declaration of the level-0 record and not a solid"
    ),
    (
        "no body describes the target during a shot: these are the "
        "dimensions before the drive begins, and an implosion changes all "
        "of them"
    ),
    (
        "both filed sources describe heavy-ion drivers; no body here is "
        "evidence about an electron-beam driver"
    ),
    "no body is a CAD solid or an engineering model",
    "no material property, load, field, dose or activation quantity is carried",
    "no value describes or validates any real machine or shot",
)

#: One millimetre in metres. The level-0 relations carry millimetres and
#: every body is built in metres; this is the only place the two meet.
#: The configuration's own micrometres are converted by the level-0
#: relation that owns them, never a second time here.
MILLIMETRE_M: Final = 1.0e-3

ROLE_ABLATOR: Final = "ablator"
ROLE_FUEL: Final = "fuel"
MATERIAL_BERYLLIUM_ABLATOR: Final = "beryllium_ablator"
MATERIAL_SOLID_FUEL: Final = "solid_fuel_ice"
MATERIAL_FUEL_VAPOUR: Final = "fuel_vapour"

BODY_ABLATOR_SHELL: Final = "ablator_shell"
BODY_FUEL_ICE_SHELL: Final = "fuel_ice_shell"
BODY_FUEL_VAPOUR_CORE: Final = "fuel_vapour_core"

CAPSULE_BODY_NAMES: Final = (
    BODY_ABLATOR_SHELL,
    BODY_FUEL_ICE_SHELL,
    BODY_FUEL_VAPOUR_CORE,
)
BODY_NAMES_BY_IDENTIFIER: Final = {
    "ion_beam_icf": CAPSULE_BODY_NAMES,
    "pulsed_electron_beam_icf": CAPSULE_BODY_NAMES,
}
"""The body set of each owned configuration. Both draw the same three
bodies: neither has an enclosure whose dimensions any filed source
prints, and the electron-beam class has no filed source at all. The map
exists rather than a bare constant because the group's contract is that
a body set is a property of an identifier, and a family in which the two
agree should say so rather than leave it to be inferred."""


def _declaration_digest(record: dict[str, Any]) -> str:
    """Identify a declaration by the canonical bytes of its record.

    Parameters
    ----------
    record
        The declaration's JSON-serialisable record.

    Returns
    -------
    str
        SHA-256 of the canonical bytes as lowercase hex. The bytes are
        formed the way every other record in this repository is formed:
        sorted keys, minimal separators, one trailing newline, and no
        NaN or infinity anywhere.
    """
    text = json.dumps(record, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256((text + "\n").encode("utf-8")).hexdigest()


def capsule_radii_m(
    configuration: DeviceConfiguration, capsule: CapsuleDeclaration
) -> tuple[float, float, float]:
    """Return the three capsule radii in metres, outermost first.

    Parameters
    ----------
    configuration
        Validated beam-ICF configuration carrying the pellet's outer
        radius.
    capsule
        Declared layering carrying the fuel layer's two radii.

    Returns
    -------
    (outer, fuel_outer, cavity)
        The pellet's outer radius, the outer radius of the fuel layer,
        and the radius of the vapour cavity, all in metres.

    Raises
    ------
    DeviceConfigurationError
        If the fuel layer does not fit inside the pellet. The refusal
        comes from the level-0 relation rather than from a copy of it,
        so the geometry cannot admit a layering the physics would have
        refused. The relation's return value is discarded here: what is
        wanted from it is the refusal, and the thickness it computes is
        already the difference of two radii this function returns.
    """
    ablator_thickness_mm(configuration, capsule)
    return (
        pellet_radius_mm(configuration) * MILLIMETRE_M,
        capsule.fuel_outer_radius_mm * MILLIMETRE_M,
        capsule.fuel_inner_radius_mm * MILLIMETRE_M,
    )


@dataclass(frozen=True, slots=True)
class DeviceModel3D:
    """The tessellated device model of one configuration and capsule.

    Parameters
    ----------
    identifier
        Configuration identifier the body set belongs to.
    configuration_digest_sha256
        Digest of the configuration the model was built from.
    capsule_digest_sha256
        Digest of the declared capsule layering.
    segments
        Circumferential segment count every body was tessellated at.
    rings
        Polar step count the bodies were sampled at.
    meshes
        The bodies, in the fixed order for that identifier.

    Raises
    ------
    DeviceGeometryError
        If the identifier is unknown, or the body names or their order
        differ from the set that identifier owns.
    """

    identifier: str
    configuration_digest_sha256: str
    capsule_digest_sha256: str
    segments: int
    rings: int
    meshes: tuple[TriangleMesh, ...]

    def __post_init__(self) -> None:
        """Validate the body set and its order against the identifier.

        Raises
        ------
        DeviceGeometryError
            If the identifier is unknown, or the body names or their
            order differ from the set that identifier owns.
        """
        expected = BODY_NAMES_BY_IDENTIFIER.get(self.identifier)
        if expected is None:
            raise DeviceGeometryError(
                f"identifier: must be one of "
                f"{tuple(BODY_NAMES_BY_IDENTIFIER)!r}, got {self.identifier!r}"
            )
        names = tuple(mesh.name for mesh in self.meshes)
        if names != expected:
            raise DeviceGeometryError(
                f"meshes: bodies of {self.identifier!r} must be exactly "
                f"{expected!r} in order, got {names!r}"
            )

    def to_record(self) -> dict[str, Any]:
        """Project the model to a JSON-serialisable record.

        Returns
        -------
        dict[str, Any]
            The schema-tagged record with one entry per body.
        """
        return {
            "schema": MODEL_SCHEMA,
            "schema_version": MODEL_SCHEMA_VERSION,
            "units": dict(MODEL_UNITS),
            "non_claims": list(MODEL_NON_CLAIMS),
            "identifier": self.identifier,
            "configuration_digest_sha256": self.configuration_digest_sha256,
            "capsule_digest_sha256": self.capsule_digest_sha256,
            "segments": self.segments,
            "rings": self.rings,
            "bodies": [
                {
                    "name": mesh.name,
                    "role": mesh.role,
                    "material_identifier": mesh.material_identifier,
                    "vertex_count": mesh.vertex_count,
                    "face_count": mesh.face_count,
                    "volume_m3": mesh.signed_volume_m3(),
                    "surface_area_m2": mesh.surface_area_m2(),
                }
                for mesh in self.meshes
            ],
        }

    def canonical_bytes(self) -> bytes:
        """Serialise the model record canonically.

        Returns
        -------
        bytes
            UTF-8 JSON with sorted keys, minimal separators and a
            trailing newline; NaN and infinity are never emitted.
        """
        text = json.dumps(
            self.to_record(), sort_keys=True, separators=(",", ":"), allow_nan=False
        )
        return (text + "\n").encode("utf-8")

    def digest_sha256(self) -> str:
        """Identify the exact model record.

        Returns
        -------
        str
            SHA-256 of :meth:`canonical_bytes` as lowercase hex.
        """
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


def build_device_model(
    configuration: DeviceConfiguration,
    capsule: CapsuleDeclaration,
    segments: int,
    rings: int,
) -> DeviceModel3D:
    """Tessellate the bodies of a validated design.

    Parameters
    ----------
    configuration
        Validated beam-ICF configuration; its identifier selects the
        body set and its pellet radius sets the outermost body.
    capsule
        Declared capsule layering supplying the two inner radii.
    segments
        Circumferential segments for every body; at least 8, multiple
        of 8.
    rings
        Polar steps from pole to pole; at least the library's minimum.
        It is independent of ``segments``: this one sets the profile,
        the other sets what the revolution keeps of it.

    Returns
    -------
    DeviceModel3D
        The composed model.

    Raises
    ------
    DeviceGeometryError
        If a count is invalid; the library's refusals are re-raised
        under the device error type with their messages.
    DeviceConfigurationError
        If the declared layering does not fit inside the pellet.
    """
    try:
        require_segments(segments)
        require_rings(rings)
    except GeometryError as exc:
        raise DeviceGeometryError(str(exc)) from exc
    outer, fuel_outer, cavity = capsule_radii_m(configuration, capsule)
    bodies = (
        (
            BODY_ABLATOR_SHELL,
            ROLE_ABLATOR,
            MATERIAL_BERYLLIUM_ABLATOR,
            spherical_shell(fuel_outer, outer, 0.0, segments, rings),
        ),
        (
            BODY_FUEL_ICE_SHELL,
            ROLE_FUEL,
            MATERIAL_SOLID_FUEL,
            spherical_shell(cavity, fuel_outer, 0.0, segments, rings),
        ),
        (
            BODY_FUEL_VAPOUR_CORE,
            ROLE_FUEL,
            MATERIAL_FUEL_VAPOUR,
            sphere_solid(cavity, 0.0, segments, rings),
        ),
    )
    meshes = tuple(
        TriangleMesh(
            name=name,
            role=role,
            material_identifier=material,
            vertices=vertices,
            faces=faces,
        )
        for name, role, material, (vertices, faces) in bodies
    )
    return DeviceModel3D(
        identifier=configuration.identifier,
        configuration_digest_sha256=configuration.digest_sha256(),
        capsule_digest_sha256=_declaration_digest(capsule.to_record()),
        segments=segments,
        rings=rings,
        meshes=meshes,
    )
