<!--
SPDX-License-Identifier: AGPL-3.0-or-later
Commercial license available
© Concepts 1996–2026 Miroslav Šotek. All rights reserved.
© Code 2020–2026 Miroslav Šotek. All rights reserved.
ORCID: 0009-0009-3560-0851
Contact: www.anulum.li | protoscience@anulum.li
SCPN Icf Beam Core — ADR 0006
-->

# ADR 0006 — Device 3D and CAD models of a beam-driven capsule

Status: accepted (2026-09-04). Builds on ADR 0002 (device configuration
model), which owns the pellet's outer radius, and ADR 0005 (level-0
device physics), which owns the fuel layer's two radii.

## Context

A beam-driven ICF target is a capsule inside a radiation enclosure. The
capsule is fully printed by a filed source. The enclosure is not printed
at all. Everything below follows from that asymmetry.

**The capsule is completely determined.** Fig. 1 of the filed capsule
review gives three radii — 2.34 mm, 2.12 mm and 1.8 mm — and three
densities. Two of those radii already live in the level-0 capsule
declaration, because the mass inventory is computed from them, and the
outermost lives in the configuration's target declaration. So the
geometry package has nothing of its own to declare.

**The enclosure is not determined at all.** Both filed sources describe
a hohlraum and neither prints a dimension of it. The running text gives
a converter opening radius of 0.15 cm and a 0.7 cm shell radius used for
a wall-motion calculation; neither is a case radius, a wall thickness or
a length. The one schematic that shows the enclosure is drawn on
labelled axes with no dimension callouts, so nothing can be read off it
by measurement.

**The level-0 record does carry an enclosure number, and it is a trap.**
`equivalent_enclosure_radius_mm` is the radius of the *sphere whose area
equals the enclosure's*, obtained from a printed capsule-to-enclosure
area ratio of 0.075. It is an area statement. Building a cylinder on it
would produce a case with a plausible size and no source, which is
exactly the failure mode this group's anchoring discipline exists to
prevent.

## Decision

**The geometry package declares nothing.** No envelope object, no
constants of its own beyond the identity of what it builds. Its sibling
laser-ICF family declares one thing, an enclosure; here there is no
second home for any dimension, so there is no declaration module at all.
The package is two builders.

**Three bodies, and no enclosure.** The ablator shell, the fuel layer
and the vapour the fuel layer encloses. The absence of a case is
recorded in the non-claims of both tiers, so that a consumer who knows
the design has a hohlraum can find out from the record why the model
does not draw one, rather than concluding the model is incomplete.

**The body set does not follow the identifier**, and that is a statement
about sources rather than about machines. The laser family draws a
fourth body for exactly one of its three identifiers because a related
precursor prints dimensionless enclosure geometry it can anchor a
declared case against. This family has no such precursor for either of
its identifiers, and the `pulsed_electron_beam_icf` class has no filed
source whatsoever. Both owned configurations therefore draw the same
three bodies, and the identifier-to-body-set map is kept — rather than
collapsed to a constant — because the group's contract is that a body
set is a property of an identifier, and a family where the two agree
should say so explicitly.

**The vapour is drawn, although it is a gas**, for the same reason as in
the laser family: the source prints its density and it belongs to the
fuel inventory. The beam-target family draws nothing inside its bore
because nothing is declared to be there.

**The ablator's material token is `beryllium_ablator`**, not the laser
family's plastic. The source prints a beryllium ablator at 1.85 g/cm³.

## What the sources print, and what is anchored

Every radius the geometry uses is printed, and all three are recovered
from the built bodies as exact equalities rather than read back out of
the declaration.

**The layer thicknesses do not come back exactly, and the cause is the
opposite of the laser family's.** Measured: the ablator returns
0.2199999999999997 against a printed 0.22, and the fuel layer
0.3200000000000002 against 0.32. There the source prints integer
micrometres, the layer arithmetic is exact, and the conversion to metres
introduces the rounding. Here the source prints millimetres to two
decimals and 2.34, 2.12 and 1.8 are already inexact in binary before any
conversion happens — 2.34 − 2.12 is 0.21999999999999975 in millimetres
alone. Both families end up with a bound instead of an equality, by
different routes, and each says which.

## What was measured on this family's own bodies

**The ring count is bounded by the back-end, and the bound is not a
simple ceiling.** Scanning every count from 30 to 75:

| ring counts | behaviour |
|---|---|
| 30 to 41 | every count exact, to floating-point noise |
| 42 to 65 | mixed: every even count refuses, every odd count is exact |
| 66 and above | every count refuses |

The first refusal is at 42 rings, where the fuel shell and the vapour
core both depart — the shell by 8.2e-5 against a 1e-9 tolerance.

**An even ring count places exactly one profile sample on the equator,
at exactly `(0, R)`, and an odd count places none.** The refusals inside
the mixed band fall exactly on the even counts. That correlation is
measured; whether the equatorial sample is what the revolve fails on is
**not** established here. The mechanism belongs to the back-end.

**The default is the top of the first regime, not the highest count that
builds.** Odd counts to 65 build. Choosing one would mean sitting a
single step from a refusal on the strength of a parity whose cause is
unknown.

**The count is 41 here and 39 in the laser family**, whose cavity is
1.503 mm against this one's 1.8 mm. Where the band starts moves with the
body's radius — measured on solid spheres, the first refusal is at 34
rings for 1.0 mm, 40 at 1.503 mm, 42 at 1.8 mm, 46 at 2.34 mm, 50 at
3.0 mm and 58 at 5.0 mm, with nothing failing at 10 mm and above up to
120 rings. That is why a family may not inherit a sibling's count, and
why the laser family's record was corrected on 2026-09-04 after this
measurement contradicted it.

**The linear deflection changes nothing about the model.** Measured
across 5e-7, 3e-7, 2.5e-7, 2e-7, 1.5e-7 and 1.2e-7 metres, the faceted
volume deficit of every body is the same number to five significant
figures; what moves is the declared bound `2 d / r`. A test asserts that
directly, by building at two deflections and comparing.

**So the threshold is exact rather than a rung on a ladder.** The bound
is violated when `2 d / r` falls below the measured deficit, so the
smallest deflection the worst body clears is `deficit · r / 2` =
**1.1326e-7 m**. The declared 2e-7 m sits above it deliberately, putting
the vapour core at 0.57 of its bound: a stated margin against back-end
drift rather than the strongest claim available. A test computes the
threshold from the built model and asserts it lies between the refused
1e-7 m and the declared value, which is what makes the choice
falsifiable.

**The angular deflection does not bind.** Between 0.5 and 0.1 radians
every body's deficit is identical to four significant figures.

**The radius handed to the deficit bound is each body's outer radius.**
A sphere's circles run from zero at the poles to the outer radius at the
equator, so there is no single smallest circle to name and the poles
would make the bound unbounded. The outer radius is the tightest bound
the body admits.

## Consequences

- Two capabilities are declared, `device_3d_model` and
  `device_cad_model`, both at `computational_prototype` maturity.
- This repository gains its first dependency: the shared kernel library,
  pinned by commit, with the CAD back-end as an optional extra naming
  the same commit. Three workflows gain an install step and one of them
  also installs the system library the mesher links against.
- The manifest gains a `kernel_library` pin naming **eleven** kernels,
  one fewer than the laser family: no body here is a cylinder or a tube,
  so the primitives kernel is not consumed. The manifest validator does
  not inspect that field — a fleet-wide finding this repository joins
  rather than resolves, because resolving it changes the shared standard
  and that is an owner-authorised change. A repository contract test
  holds the pin, the dependency and the workflows to one commit in the
  meantime.
- A consumer must not compare any volume here to `4/3 π r³`. Every body
  is an inscribed polyhedron of revolution, and its own profile is its
  reference. The library states the same rule in its ADR 0013.
- Nothing here is evidence about the `pulsed_electron_beam_icf` class.
  It builds from whatever is declared for it, and both filed sources are
  heavy-ion.
