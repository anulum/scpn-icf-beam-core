<!--
SPDX-License-Identifier: AGPL-3.0-or-later
Commercial license available
© Concepts 1996–2026 Miroslav Šotek. All rights reserved.
© Code 2020–2026 Miroslav Šotek. All rights reserved.
ORCID: 0009-0009-3560-0851
Contact: www.anulum.li | protoscience@anulum.li
SCPN Icf Beam Core — device model contract
-->

# Device model contract

What a consumer of this repository's geometry receives, and what it may
not conclude from it.

## The two things to read first

**Every body here is an inscribed polyhedron of revolution**, not a
sphere. Its own profile — the frustum stack the body was built from — is
its analytic reference. Comparing a volume in these records to
`4/3 π r³`, or an area to `4 π r²`, compares two different solids and
will show a deficit that is a property of the comparison, not of the
model.

**No radiation enclosure is drawn, and that is deliberate.** The design
this family anchors on has one. Neither filed source prints a case
radius, a wall thickness or a length, and the only schematic of the
enclosure carries no dimension callouts. The level-0 record's
`equivalent_enclosure_radius_mm` is **not** a case radius: it is the
radius of a sphere whose *area* matches the enclosure's, derived from a
printed area ratio. A model built on it would carry a case with a
plausible size and no source. A consumer needing enclosure geometry must
obtain it elsewhere and must not infer it from anything here.

## The two tiers

| Tier | Schema | Built by |
|---|---|---|
| G1, tessellated | `scpn.beam-icf-3d-model.v1` | `build_device_model` |
| G2, B-rep | `scpn.beam-icf-cad-model.v1` | `build_device_cad` |

Both schemas are at version `1.0.0`. Tier G2 requires the optional
`cad` extra; every other capability of this package works without it.

## Units and frame

| | |
|---|---|
| length | metre |
| handedness | right |
| axis | `z` along the illumination axis |
| origin | the centre of the capsule |

The configuration carries **micrometres** and the level-0 capsule
declaration carries **millimetres**. The configuration's micrometres are
converted by the level-0 relation that owns them; the geometry converts
millimetres to metres once, in `capsule_radii_m`, and nowhere else.

## The bodies

| Identifier | Bodies, in order |
|---|---|
| `ion_beam_icf` | `ablator_shell`, `fuel_ice_shell`, `fuel_vapour_core` |
| `pulsed_electron_beam_icf` | the same three |

| Body | Role | Material token | Shape |
|---|---|---|---|
| `ablator_shell` | `ablator` | `beryllium_ablator` | spherical shell |
| `fuel_ice_shell` | `fuel` | `solid_fuel_ice` | spherical shell |
| `fuel_vapour_core` | `fuel` | `fuel_vapour` | sphere |

The order is part of the contract and is validated at construction.

Both owned configurations draw the same set. The map is kept rather than
collapsed to a constant because a body set is a property of an
identifier throughout this group, and a family where the two agree
should say so rather than leave it to be inferred.

## Where each dimension comes from

| Dimension | Home |
|---|---|
| pellet outer radius | `TargetDeclaration.pellet_radius_um` |
| fuel layer outer radius | `CapsuleDeclaration.fuel_outer_radius_mm` |
| fuel cavity radius | `CapsuleDeclaration.fuel_inner_radius_mm` |

Nothing in that table appears twice, and the geometry package declares
none of it. All three radii are printed by the filed source, so the
cavity is anchored rather than derived — unlike the laser-ICF family,
where it is a subtraction of two declared thicknesses.

A fuel layer that leaves no ablator inside the pellet is refused by the
level-0 relation itself, so this tier cannot draw a capsule the physics
record would have rejected.

## Resolutions

`segments` sets what the revolution keeps of the profile; `rings` sets
the profile. They are independent, and passing one where the other
belongs builds a valid body of the wrong shape that no gate downstream
would notice.

Defaults for tier G2: 8 reference segments, 41 rings, a linear
deflection of 2e-7 m and an angular deflection of 0.1 rad.

## Exports and identity

Both tiers serialise canonically — sorted keys, minimal separators, one
trailing newline, no NaN or infinity — and carry the SHA-256 of those
bytes. Tier G2 additionally carries normalised STEP bytes and their
digest, the library's assembly manifest, and the back-end versions that
produced the solids.

Each record names the digests of the inputs it was built from: the
configuration and the capsule declaration.

## Declared limits

- **41 rings is the top of this family's exact regime, not a
  preference.** At 42 the back-end's own volume measure departs from the
  analytic form by four orders of magnitude beyond the library's
  tolerance and the evidence kernel refuses. Above 42 the behaviour is
  mixed rather than uniformly wrong: every even count refuses and every
  odd count is exact, up to 65, above which every count refuses. Odd
  counts in that band are not used, because their margin is one step and
  the parity's cause is not established. Where the band starts is a
  function of the body's radius — measured, the first refusal is at 34
  rings for 1.0 mm and 58 for 5.0 mm — so it transfers to no other
  family. A consumer building at a different radius must measure its
  own.
- **The linear deflection does not change the model, only the claim.**
  The faceted volume deficit is identical across every deflection
  measured; what moves is the bound `2 d / r`. The exact threshold below
  which the worst body violates its bound is `deficit · r / 2` =
  1.1326e-7 m. The declared 2e-7 m carries a stated margin over it,
  leaving the vapour core at 0.57 of its bound.
- The faceting deficit bound of each body is `2 d / r` at that body's
  **outer** radius, which is the tightest bound a body of revolution
  admits.
- Determinism of the STEP bytes is claimed **within one pinned back-end
  environment**, never across back-end versions.

## Non-claims

- No dimension describes the target during a shot. These are the
  dimensions before the drive begins, and an implosion changes all of
  them.
- The capsule is three uniform concentric layers. No fill tube, no
  mounting stalk, no surface roughness and no layer non-uniformity is
  modelled — and those are precisely the quantities an implosion is
  sensitive to.
- No enclosure, beam, focal spot, final-focus magnet or converter is
  drawn. The illumination is a declaration of the level-0 record, not a
  solid.
- **Nothing here is evidence about `pulsed_electron_beam_icf`.** Both
  filed sources describe heavy-ion drivers. That configuration builds
  from whatever is declared for it, and the identical body set must not
  be read as identical evidence.
- No body is an engineering model, and no material property, load,
  field, dose, activation quantity or fabrication tolerance is carried.
- No value here describes or validates any real machine or shot.
  Reproducing a printed value is an anchor, never a claim about that
  machine.
