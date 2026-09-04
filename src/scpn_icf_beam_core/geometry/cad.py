# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN ICF Beam Core — tier-G2 device model

"""Tier-G2 B-rep model of a beam-driven ICF target.

The same three bodies as tier G1, built as exact solids through the
shared library's ``cad`` group instead of tessellated, checked
fail-closed by the library's evidence kernel against its analytic closed
forms and against its tier-G1 twin, and exported as normalised STEP
bytes with a digest.

**Every number below was measured on this family's own bodies.** A
sibling family measured its own and got different answers, which is the
whole reason each family measures rather than inherits.

The ring count is bounded by the back-end, and the bound is not a simple
ceiling. Scanning every count from thirty to seventy-five gives three
regimes: to forty-one every count is exact, agreeing with the analytic
frustum stack to floating-point noise; from forty-two to sixty-five the
behaviour alternates, with every even count refusing and every odd count
exact; from sixty-six upward every count refuses. The first refusal is
at forty-two, where the fuel shell reports 8.2e-5 against a 1e-9
tolerance.

**An even ring count places exactly one profile sample on the equator,
at exactly ``(0, R)``, and an odd count places none; the refusals inside
the mixed band fall exactly on the even counts.** That correlation is
measured. Whether the equatorial sample is what the revolve fails on is
**not** established here — the mechanism belongs to the back-end.

The default is the top of the first regime and not the highest count
that happens to build. Odd counts to sixty-five do build, and choosing
one would mean sitting a single step from a refusal on the strength of a
parity whose cause is unknown.

The deflections behave as follows, and the first of the two is the
interesting one.

**The linear deflection does not change the model at all — it changes
only what the model is checked against.** Measured across 5e-7, 3e-7,
2.5e-7, 2e-7, 1.5e-7 and 1.2e-7 metres, the faceted volume deficit of
the vapour core is 1.2585e-4 at every one of them, to five significant
figures. What moves is the declared bound, which is ``2 d / r``. So the
deflection is not an accuracy knob at this scale; it is the strength of
the claim being made.

**That makes the threshold exact rather than a rung on a ladder.** The
bound is violated when ``2 d / r`` falls below the measured deficit, so
the smallest deflection this family's worst body clears is
``deficit * r / 2`` = **1.1326e-7 m**. The declared value of 2e-7 m is
above it deliberately: it puts the worst body at 0.566 of its bound,
which is a stated margin against back-end drift rather than the
strongest claim available. A test asserts that 1e-7 m — below the
threshold — is refused.

**The angular deflection does not bind.** Between 0.5 and 0.1 radians
every body's deficit is identical to four significant figures.

**The radius handed to the deficit bound is the outer radius of each
body, and that is deliberate.** The bound ``2 d / r`` is written for a
circular profile of one radius; a sphere's circles run from zero at the
poles to the outer radius at the equator, so there is no single smallest
circle to name and the poles would make the bound unbounded. The outer
radius gives the **tightest** bound the body admits, and every body is
measured to clear it. Design record: ADR 0006.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Final

from scpn_reactor_kernels.cad import (
    MANIFEST_SCHEMA,
    BodyEvidence,
    BrepAssembly,
    assembly_evidence,
    backend_versions,
    facet_assembly,
    sphere_brep,
    spherical_shell_brep,
    step_bytes,
    step_sha256,
)
from scpn_reactor_kernels.errors import CadError, GeometryError
from scpn_reactor_kernels.geometry import TriangleMesh

from scpn_icf_beam_core.configuration import DeviceConfiguration
from scpn_icf_beam_core.errors import DeviceGeometryError
from scpn_icf_beam_core.geometry.model import (
    BODY_ABLATOR_SHELL,
    BODY_FUEL_ICE_SHELL,
    BODY_FUEL_VAPOUR_CORE,
    BODY_NAMES_BY_IDENTIFIER,
    MATERIAL_BERYLLIUM_ABLATOR,
    MATERIAL_FUEL_VAPOUR,
    MATERIAL_SOLID_FUEL,
    ROLE_ABLATOR,
    ROLE_FUEL,
    build_device_model,
    capsule_radii_m,
)
from scpn_icf_beam_core.physics.level0 import CapsuleDeclaration

CAD_MODEL_SCHEMA: Final = "scpn.beam-icf-cad-model.v1"
CAD_MODEL_SCHEMA_VERSION: Final = "1.0.0"
CAD_MODEL_UNITS: Final = {
    "length": "metre",
    "handedness": "right",
    "axis": "z along the illumination axis; the capsule is centred on the origin",
    "origin": "the centre of the capsule",
}
CAD_MODEL_NON_CLAIMS: Final = (
    "exact solids of revolution of a declared configuration and capsule",
    (
        "every body is a polyhedron of revolution, never an ideal sphere; the "
        "frustum stack of the profile built is its own analytic reference"
    ),
    (
        "the capsule is three uniform concentric layers; no fill tube, no "
        "mounting stalk, no surface roughness and no layer non-uniformity is "
        "modelled"
    ),
    (
        "no radiation enclosure, beam, focal spot or converter is drawn; the "
        "filed sources print no dimension of any of them"
    ),
    (
        "determinism of the STEP bytes is claimed within one pinned back-end "
        "environment only, never across back-end versions"
    ),
    (
        "both filed sources describe heavy-ion drivers; no solid here is "
        "evidence about an electron-beam driver"
    ),
    "no body is an engineering model and no fabrication tolerance is carried",
    "no value describes or validates any real machine or shot",
)

#: Reference tessellation the B-rep bodies are checked against.
DEFAULT_REFERENCE_MESH_SEGMENTS: Final = 8
#: Polar steps of the spherical profiles: the largest count below the
#: back-end's first refusal on this family's own bodies, which is the top
#: of the regime where every count is exact. Higher odd counts build and
#: are still not used; see the module docstring. The sibling laser family
#: measured 39 for the same reason at its own radii, which is why this is
#: measured here rather than inherited.
DEFAULT_SPHERE_RINGS: Final = 41
#: Mesher deflections, both measured on this family's own bodies. The
#: linear value carries a stated margin over the exact threshold of
#: 1.1326e-7 m rather than sitting on it.
DEFAULT_LINEAR_DEFLECTION_M: Final = 2.0e-7
DEFAULT_ANGULAR_DEFLECTION_RAD: Final = 0.1


@dataclass(frozen=True, slots=True)
class DeviceModelCAD:
    """The B-rep device model of one configuration and capsule.

    Parameters
    ----------
    identifier
        Configuration identifier the body set belongs to.
    configuration_digest_sha256, capsule_digest_sha256
        Digests of the inputs the model was built from.
    reference_mesh_segments, rings
        Tier-G1 reference the bodies were checked against, and the polar
        step count both tiers share.
    linear_deflection_m, angular_deflection_rad
        Mesher deflections of the faceting comparison.
    backend_versions
        Versions of the pinned back-ends that produced the solids.
    assembly_manifest
        The library's assembly manifest of the bodies.
    step_sha256
        Digest of the normalised STEP bytes.
    bodies
        Checked evidence of each body, in the fixed order.
    step_data
        The normalised STEP bytes themselves.
    faceted_meshes
        The faceted meshes the evidence was computed from.

    Raises
    ------
    DeviceGeometryError
        If the identifier is unknown, or the manifest schema, the body
        count or the body order is wrong.
    """

    identifier: str
    configuration_digest_sha256: str
    capsule_digest_sha256: str
    reference_mesh_segments: int
    rings: int
    linear_deflection_m: float
    angular_deflection_rad: float
    backend_versions: dict[str, str]
    assembly_manifest: dict[str, Any]
    step_sha256: str
    bodies: tuple[BodyEvidence, ...]
    step_data: bytes
    faceted_meshes: tuple[TriangleMesh, ...]

    def __post_init__(self) -> None:
        """Validate the manifest and the body set against the identifier.

        Raises
        ------
        DeviceGeometryError
            If the identifier is unknown, or the manifest schema, the
            body count or the body order is wrong.
        """
        expected = BODY_NAMES_BY_IDENTIFIER.get(self.identifier)
        if expected is None:
            raise DeviceGeometryError(
                f"identifier: must be one of "
                f"{tuple(BODY_NAMES_BY_IDENTIFIER)!r}, got {self.identifier!r}"
            )
        if self.assembly_manifest.get("schema") != MANIFEST_SCHEMA:
            raise DeviceGeometryError(
                f"assembly_manifest.schema: must be {MANIFEST_SCHEMA!r}"
            )
        if self.assembly_manifest.get("body_count") != len(expected):
            raise DeviceGeometryError(
                f"assembly_manifest.body_count: must be {len(expected)}, got "
                f"{self.assembly_manifest.get('body_count')!r}"
            )
        names = tuple(body.name for body in self.bodies)
        if names != expected:
            raise DeviceGeometryError(
                f"bodies: of {self.identifier!r} must be exactly {expected!r} "
                f"in order, got {names!r}"
            )

    def to_record(self) -> dict[str, Any]:
        """Project the model to a JSON-serialisable record.

        Returns
        -------
        dict[str, Any]
            The schema-tagged record with one entry per body.
        """
        return {
            "schema": CAD_MODEL_SCHEMA,
            "schema_version": CAD_MODEL_SCHEMA_VERSION,
            "units": dict(CAD_MODEL_UNITS),
            "non_claims": list(CAD_MODEL_NON_CLAIMS),
            "identifier": self.identifier,
            "configuration_digest_sha256": self.configuration_digest_sha256,
            "capsule_digest_sha256": self.capsule_digest_sha256,
            "reference_mesh_segments": self.reference_mesh_segments,
            "rings": self.rings,
            "linear_deflection_m": self.linear_deflection_m,
            "angular_deflection_rad": self.angular_deflection_rad,
            "backend_versions": dict(self.backend_versions),
            "assembly_manifest": self.assembly_manifest,
            "step_sha256": self.step_sha256,
            "bodies": [body.to_record() for body in self.bodies],
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


def build_device_cad(
    configuration: DeviceConfiguration,
    capsule: CapsuleDeclaration,
    segments: int = DEFAULT_REFERENCE_MESH_SEGMENTS,
    rings: int = DEFAULT_SPHERE_RINGS,
    linear_deflection_m: float = DEFAULT_LINEAR_DEFLECTION_M,
    angular_deflection_rad: float = DEFAULT_ANGULAR_DEFLECTION_RAD,
) -> DeviceModelCAD:
    """Build the B-rep device model of a validated design.

    Parameters
    ----------
    configuration
        Validated beam-ICF configuration.
    capsule
        Declared capsule layering.
    segments
        Segment count of the tier-G1 reference mesh of the comparison.
    rings
        Polar steps of the spherical profiles, shared by both tiers.
    linear_deflection_m, angular_deflection_rad
        Mesher deflections of the faceting comparison.

    Returns
    -------
    DeviceModelCAD
        The composed, fail-closed checked model with its STEP export.

    Raises
    ------
    DeviceGeometryError
        If a count or a deflection is invalid, or a body violates a
        declared evidence bound; the library's refusals are re-raised
        under the device error type with their messages.
        :class:`~scpn_reactor_kernels.errors.CadUnavailableError` if the
        optional CAD back-end is absent.
    DeviceConfigurationError
        If the declared layering does not fit inside the pellet.
    """
    reference = build_device_model(configuration, capsule, segments, rings)
    outer, fuel_outer, cavity = capsule_radii_m(configuration, capsule)
    try:
        solids = (
            spherical_shell_brep(
                fuel_outer,
                outer,
                0.0,
                rings,
                BODY_ABLATOR_SHELL,
                ROLE_ABLATOR,
                MATERIAL_BERYLLIUM_ABLATOR,
            ),
            spherical_shell_brep(
                cavity,
                fuel_outer,
                0.0,
                rings,
                BODY_FUEL_ICE_SHELL,
                ROLE_FUEL,
                MATERIAL_SOLID_FUEL,
            ),
            sphere_brep(
                cavity,
                0.0,
                rings,
                BODY_FUEL_VAPOUR_CORE,
                ROLE_FUEL,
                MATERIAL_FUEL_VAPOUR,
            ),
        )
        brep = BrepAssembly(solids)
        faceted = facet_assembly(brep, linear_deflection_m, angular_deflection_rad)
        bodies = assembly_evidence(
            brep.bodies,
            (outer, fuel_outer, cavity),
            faceted,
            reference.meshes,
            linear_deflection_m,
            segments,
        )
    except (CadError, GeometryError) as exc:
        raise DeviceGeometryError(str(exc)) from exc
    manifest = brep.manifest()
    extras = {
        "schema": CAD_MODEL_SCHEMA,
        "schema_version": CAD_MODEL_SCHEMA_VERSION,
        "identifier": configuration.identifier,
        "configuration_digest_sha256": configuration.digest_sha256(),
        "capsule_digest_sha256": reference.capsule_digest_sha256,
        "assembly_manifest_sha256": brep.manifest_sha256(),
        "units": dict(CAD_MODEL_UNITS),
        "non_claims": list(CAD_MODEL_NON_CLAIMS),
        "backend_versions": backend_versions(),
    }
    step_data = step_bytes(brep, extras)
    return DeviceModelCAD(
        identifier=configuration.identifier,
        configuration_digest_sha256=configuration.digest_sha256(),
        capsule_digest_sha256=reference.capsule_digest_sha256,
        reference_mesh_segments=segments,
        rings=rings,
        linear_deflection_m=linear_deflection_m,
        angular_deflection_rad=angular_deflection_rad,
        backend_versions=backend_versions(),
        assembly_manifest=manifest,
        step_sha256=step_sha256(step_data),
        bodies=bodies,
        step_data=step_data,
        faceted_meshes=faceted,
    )
