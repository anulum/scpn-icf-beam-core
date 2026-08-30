<!--
SPDX-License-Identifier: AGPL-3.0-or-later
Commercial license available
© Concepts 1996–2026 Miroslav Šotek. All rights reserved.
© Code 2020–2026 Miroslav Šotek. All rights reserved.
ORCID: 0009-0009-3560-0851
Contact: www.anulum.li | protoscience@anulum.li
SCPN ICF Beam Core — ADR 0001: repository boundary
-->

# ADR 0001 — Repository boundary and ownership

**Status:** accepted (2026-08-30)

**Deciders:** project owner; SCPN Reactor Systems Research Group standard

## Context

The SCPN reactor portfolio assigns every built-in configuration of the SCPN
Phase Orchestrator reactor registry (version `1.0.0`, 32 configurations) to
exactly one device-family repository. Beam-driven implosion borders both
laser ICF (shared implosion physics) and non-imploding beam-target fusion
(shared accelerator heritage); a boundary decision was needed on both
edges.

## Decision

1. `SCPN-ICF-BEAM-CORE` owns exactly two registry configurations:
   `ion_beam_icf` and `pulsed_electron_beam_icf`. Both drive an implosion
   with intense particle beams; accelerator/diode transport, final
   focusing, and charged-particle deposition define one shared driver
   surface, and the downstream implosion lifecycle and diagnostics are
   common. The driver species is the configuration parameter.
2. The repository owns device-level truth only: driver and deposition
   configuration policy, shot-cycle lifecycle semantics, beamline and burn
   diagnostic and clock declarations, actuator-response model boundaries,
   the safety-envelope declaration, and the device-owned CONTROL adapter
   specification.
3. Solver mathematics remains in `SCPN-FUSION-CORE` until an exact surface
   passes the family migration gate. No solver code is copied here.
4. Typed semantics remain in `SCPN-PHASE-ORCHESTRATOR` (review-only).
   Admission and `ControlAction` formation remain exclusively in
   `SCPN-CONTROL`. Machine protection remains independent with the final
   veto. Presentation remains in `SCPN-STUDIO`; this project is
   `not_federated`.
5. The repository starts, and remains until evidenced otherwise, at
   `architecture_only` with empty capability and claim inventories.

## Alternatives considered

- **Folding beam-driven ICF into the laser-ICF repository** (shared
  implosion physics): rejected — the driver surface differs
  fundamentally: accelerator transport, final focusing, and
  charged-particle stopping replace laser optics and laser-plasma
  interaction, changing lifecycle stages, diagnostics, and hazards
  (surfaces 2–4).
- **Grouping with non-imploding beam-target fusion** (shared accelerator
  heritage): rejected — the confinement principle differs (inertial
  implosion versus direct beam-target kinematics without implosion); the
  portfolio map separates the owners.
- **Separate repositories per beam species**: rejected — the two
  configurations share the driver-class surface and every downstream
  surface; the split would duplicate contracts for a species parameter.
- **Absorbing solver code at scaffold time**: rejected — violates the
  migration gate.

## Consequences

- Downstream consumers get one stable identity per beam-ICF configuration
  and a manifest to bind against.
- The validator fails on any capability or claim entry while maturity is
  `architecture_only`.
- Boundary changes require a portfolio-level map change first; a future
  ADR records any such change here.
