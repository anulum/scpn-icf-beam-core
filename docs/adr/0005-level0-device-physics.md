<!--
SPDX-License-Identifier: AGPL-3.0-or-later
Commercial license available
© Concepts 1996–2026 Miroslav Šotek. All rights reserved.
© Code 2020–2026 Miroslav Šotek. All rights reserved.
ORCID: 0009-0009-3560-0851
Contact: www.anulum.li | protoscience@anulum.li
SCPN Icf Beam Core — ADR 0005
-->

# ADR 0005 — Level-0 device physics as illumination, inventory and a coupling chain

Status: accepted (2026-09-04). Builds on ADR 0002 (device configuration
model), whose `BeamDriver` and `TargetDeclaration` already carry the
beam energy, the pulse duration, the per-particle energy and the
pellet's outer radius.

## Context

A beam-driven inertial-fusion shot is a radiation-hydrodynamics problem
and this repository performs none of it. What it can carry is the set of
closed-form definitions that a published design is quoted by, evaluated
on declarations, with every number traceable to a filed source or
labelled as declared.

**The cited work is unobtainable.** Bangerter, Faltens & Seidl, *Rev.
Accel. Sci. Technol.* **6** (2013) 85, is behind a World Scientific
subscription and its companion is blocked by a publisher gateway. Step 0
of the group's rollout goal asks, in that case, for a free and legally
accessible source that prints what the model carries. Two were found and
filed, both United States Department of Energy laboratory preprints
marked for unlimited distribution:

- Ho, Harte & Tabak, UCRL-JC-118161 (1994) — the capsule and the
  coupling chain;
- Callahan-Miller & Tabak, UCRL-JC-131974 (1998) — the beam arrangement
  and four driver-energy-and-yield cases.

Both describe **heavy-ion** drivers. This repository owns an
electron-beam configuration as well, and nothing free was found that
prints geometry for it.

## Decision

**Three surfaces, split by what they are about rather than by what they
compute.** `beam` is what the driver puts on the target; `capsule` is
what the target is made of and what its fuel can release; `coupling` is
the chain of efficiencies between the two. A fourth module composes them
into one record with a canonical serialisation and a digest.

**The chain is a factorisation and nothing more.**

    G_target = eta_c * eta_e * G_capsule

None of the four quantities is calculated here. Calculating any of them
is radiation hydrodynamics, and stating the identity that relates them
is the whole content of the module.

**Two relations run backwards, because the sources force it.** They
print a yield and never a burn-up fraction, so the fraction is obtained
from the yield and the inventory. They plot a conversion efficiency
against converter radius and never print a number, so the efficiency is
obtained from the two gains and the coupling efficiency. Both are
reported as implied, both are named for it in the record, and neither is
validated as a fraction — a result above one is a meaningful answer that
says the declarations do not describe one design, and refusing it would
hide the finding.

**The ion range is data, not a law.** The illumination review prints
three range-and-energy pairs and states no relation between them. The
module exposes the exponent joining any two of them rather than fitting
a power law, because the exponent is not the same for every pair.

**Areas here are areas of ideal spheres.** That is correct in physics
and would be wrong in the geometry package, where every body is an
inscribed polyhedron and its own profile is its reference. A ratio of
published areas is not a measurement of a built body.

## What is printed, what is implied, what is declared

Printed and reproduced:

- the capsule's three radii and three densities, and every mass that
  follows from them;
- the beams' two focal semi-axes, their counts per side, and the
  effective radius `sqrt(a b)` — reproduced at the precision each of the
  review's two answers is printed at, one decimal and two;
- the capsule gain, exactly, from the printed yield and absorbed energy;
- three of the illumination review's four printed gains.

Implied by printed values, and labelled:

- the burn-up fraction, measured at 0.3286 of the inventory;
- the conversion efficiency, measured at 0.8859.

Reconstructed, and named for it:

- the driver energy of the capsule review's design, which neither source
  prints. It is the printed yield over the printed system gain, so
  recovering that gain from it is a round trip and the test that does so
  says as much.

Declared, with no source claimed:

- the pulse duration.

## Measured, rather than assumed

- **Neither layer thickness comes back exactly.** The printed radii are
  decimals in millimetres, so their differences carry rounding: the
  ablator returns 0.21999999999999975 and the fuel layer
  0.32000000000000006. This is the opposite of the sibling laser family,
  whose printed radii are whole micrometres and whose layer arithmetic
  is exact. Both were measured before an equality was written, and both
  tests are bounds.
- **The illumination review truncates its gains.** 370/6.35 is 58.2677
  and it prints 58; 413/7.4 is 55.8108 and it prints 55; 436/3.3 is
  132.1212 and it prints 132. All three are floors, and the middle one
  is not the rounded value. A test asserting rounding would have failed
  on it.
- **No single power law joins the three printed range pairs.** The
  exponents are 1.1200, 1.2544 and 1.1926, and the test asserts that
  they disagree rather than hiding the spread in a tolerance.
- **The two families' enclosure ratios are different quantities.** This
  family's source prints capsule-to-enclosure 0.075, whose reciprocal is
  13.33; the laser family's precursor prints enclosure-to-capsule 15 to
  25. Neither is used to check the other, and the test says so.

## Consequences

- One capability is declared, `level0_device_physics`, at
  `computational_prototype` maturity.
- The record's non-claims carry the electron-beam boundary explicitly,
  and a guard refuses an ion-stated relation applied to an electron
  driver. The composition itself does not refuse an electron-beam
  configuration: masses, gains and fluences do not know what the beam is
  made of, and it is the **evidence** that is ion-only, not the
  arithmetic.
- The pellet's outer radius stays in the configuration and the capsule's
  two inner radii live in the declaration. The ablator's thickness
  exists in neither and is built from both, which is why a fuel layer
  reaching the pellet's surface is refused rather than reported.
- 100 % statement and branch coverage of the new package.
