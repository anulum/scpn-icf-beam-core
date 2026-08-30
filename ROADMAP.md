<!--
SPDX-License-Identifier: AGPL-3.0-or-later
Commercial license available
© Concepts 1996–2026 Miroslav Šotek. All rights reserved.
© Code 2020–2026 Miroslav Šotek. All rights reserved.
ORCID: 0009-0009-3560-0851
Contact: www.anulum.li | protoscience@anulum.li
SCPN ICF Beam Core — ROADMAP
-->

# Roadmap

Planned work and implemented capability are kept strictly separate. Anything
listed under "Planned" carries no implementation, no code, and no claim in
this repository until it appears in the capability inventory with evidence.

## Implemented (repository infrastructure, not reactor capability)

- Domain manifest (`reactor-domain.json`) with validator.
- Derived Studio portfolio descriptor (`not_federated`) with drift check.
- Generated capability inventory (truthfully empty) with drift check.
- CONTROL adapter specification (contract only, no implementation).
- Local and workflow gate definitions (lint, typing, tests, coverage,
  REUSE, security audit, SBOM, documentation checks).

## Planned (no implementation exists; ordering is not a commitment)

1. **Device configuration model** — typed configuration policy for the
   beam-ICF family (driver-chain classes, deposition-profile envelopes,
   target contracts), with evidence-maturity target
   `computational_prototype`.
2. **Diagnostic and clock semantics** — declared driver and burn channels
   with the bang-time anchor and nanosecond clock identities, aligned with
   the SCPN Phase Orchestrator semantic profile.
3. **Safety-envelope declaration** — machine-readable operational envelope
   (beam, magnet, diode, activation bounds) consumed by the CONTROL
   adapter contract.
4. **CONTROL adapter implementation** — device-owned adapter against the
   published specification, with replay fixtures and HIL evidence,
   targeting `control_research_ready` only after replay and HIL
   acceptance.
5. **Solver seam consumption** — versioned consumption of exact
   `SCPN-FUSION-CORE` seams for deposition and implosion surfaces,
   strictly after the family migration gate proves exact replacement; no
   solver code is copied.
6. **Facility-data correlation** — preregistered acceptance contracts
   against identified facility or published experimental data, targeting
   `experiment_correlated` per capability.

## Not planned in this repository

Laser-driven ICF, projectile/impact ICF, non-imploding beam-target
systems, magnetic-confinement devices, generic controller mathematics,
machine-protection logic, and any direct actuation path.
