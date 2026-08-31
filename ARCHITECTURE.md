<!--
SPDX-License-Identifier: AGPL-3.0-or-later
Commercial license available
© Concepts 1996–2026 Miroslav Šotek. All rights reserved.
© Code 2020–2026 Miroslav Šotek. All rights reserved.
ORCID: 0009-0009-3560-0851
Contact: www.anulum.li | protoscience@anulum.li
SCPN ICF Beam Core — Architecture summary
-->

# Architecture summary

`SCPN-ICF-BEAM-CORE` is the device-family owner for particle-beam-driven
inertial confinement fusion systems (ion-beam and pulsed-electron-beam
drivers) inside the SCPN Reactor Systems Research Group. The repository holds one implemented
capability — the device configuration model at `computational_prototype`
(`src/scpn_icf_beam_core/`, ADR 0002) — alongside the device boundary, its
ecosystem contracts, and the validation tooling that enforces both.

The authoritative architecture record is
[`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md). The ownership decision and
its consequences are fixed in
[`docs/adr/0001-repository-boundary.md`](docs/adr/0001-repository-boundary.md).

Boundary in one paragraph: this repository owns beam-ICF plant and
experiment truth — configuration policy for capsule implosions driven by
intense ion beams (accelerator chains, final focus, Bragg-peak deposition)
or pulsed relativistic electron beams (high-current diodes), shot-cycle
lifecycle semantics with mis-steer and flashover hazard records, beamline
and burn diagnostic and clock declarations anchored on bang time,
actuator-response boundaries limited to shot-to-shot campaign programming,
safety-envelope declarations, and the device-owned CONTROL adapter
specification. Laser-driven ICF stays with `SCPN-ICF-LASER-CORE`;
non-imploding beam-target systems with `SCPN-BEAM-TARGET-CORE`; solver
mathematics in `SCPN-FUSION-CORE`; typed semantics in
`SCPN-PHASE-ORCHESTRATOR` (review-only); admitted control actions are
formed only by `SCPN-CONTROL`; independent machine protection keeps the
final veto; portfolio presentation belongs to `SCPN-STUDIO`, towards which
this project is `not_federated`.
