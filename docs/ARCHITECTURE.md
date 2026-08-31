<!--
SPDX-License-Identifier: AGPL-3.0-or-later
Commercial license available
© Concepts 1996–2026 Miroslav Šotek. All rights reserved.
© Code 2020–2026 Miroslav Šotek. All rights reserved.
ORCID: 0009-0009-3560-0851
Contact: www.anulum.li | protoscience@anulum.li
SCPN ICF Beam Core — Architecture
-->

# Architecture

## Purpose and evidence state

`SCPN-ICF-BEAM-CORE` is the device-family owner for particle-beam-driven
inertial confinement fusion systems in the SCPN Reactor Systems Research
Group portfolio. The
repository owns one implemented capability — the device configuration model
at `computational_prototype` (`src/scpn_icf_beam_core/`, design record ADR 0002,
evidence record `VALIDATION.md#device-configuration-model`). Every other
section below describes boundaries and contracts. The claim inventory is
empty; capability and claim inventories are generated and drift-checked.

## The five-surface boundary

1. **Governing confinement physics** — inertial confinement of an imploded
   target (`inertial` registry family) with intense particle beams as the
   driver. The two owned configurations share driver-class physics:
   `ion_beam_icf` (heavy- or light-ion beams whose classical stopping
   deposits energy volumetrically in the absorber with a Bragg-peak
   profile) and `pulsed_electron_beam_icf` (high-current relativistic
   electron beams from pulsed diodes, with scattering-dominated deposition
   and beam-transport physics of its own). Both replace laser-plasma
   coupling with accelerator/diode transport, final focusing, and
   charged-particle energy deposition, and both share the implosion
   hydrodynamics downstream of deposition. Laser-driven schemes,
   projectile impact, and non-imploding beam-target systems fail this
   sharing test and are excluded.
2. **Primary driver and energy delivery** — accelerator chains
   (induction or RF linacs, storage/compression rings, final-focus
   magnets) for ion drivers; Marx-bank-driven high-current diodes for
   pulsed electron drivers; beam pointing, bunching, and pulse-shaping
   systems as configuration facets.
3. **Plant and shot lifecycle** — discrete shot-cycle lifecycle: target
   metrology acceptance, target insertion and alignment, driver charge and
   beam preparation, shot with implosion and burn window, and post-shot
   recovery. Device-level hazard semantics cover beam mis-steer, final-
   focus faults, diode flashover, and target-chamber activation
   constraints.
4. **Diagnostic, reference-frame, and clock model** — target-chamber and
   beamline coordinate conventions, driver diagnostics (delivered current,
   emittance and spot-size proxies, deposition symmetry), burn diagnostics
   (yield, bang time as timing anchor), and nanosecond-class shot-relative
   clock identities.
5. **Solver, evidence, and control-contract boundary** — versioned seams
   towards `SCPN-FUSION-CORE`, review-only semantics towards
   `SCPN-PHASE-ORCHESTRATOR`, and the device-owned CONTROL adapter
   specification towards `SCPN-CONTROL`.

## Position in the SCPN ecosystem

```text
SCPN-ICF-BEAM-CORE (device truth: driver/deposition policy, shot-cycle
                    lifecycle, beamline diagnostics, safety envelope,
                    adapter spec)
   │  optional versioned solver seams (none active)
   ├──────────────► SCPN-FUSION-CORE      (solver mathematics, evidence)
   │  typed review-only semantics
   ├──────────────► SCPN-PHASE-ORCHESTRATOR (semantics, comparability)
   │  device-owned adapter (specification only; no implementation)
   ├──────────────► SCPN-CONTROL          (admission; sole ControlAction author)
   │  derived portfolio descriptor (not_federated)
   └──────────────► SCPN-STUDIO           (catalogue, evidence UI, gating)

SCPN-CONTROL ──admitted ControlAction──► independent machine protection
                                          (final veto) ─► plant actuators
```

## Repository layout

| Path | Role |
|---|---|
| `reactor-domain.json` | portable source of project identity and contracts |
| `studio/portfolio-descriptor.json` | derived Studio descriptor, `not_federated` |
| `capability-inventory.json` | generated, truthfully empty inventory |
| `docs/CONTROL_ADAPTER_SPECIFICATION.md` | device-owned adapter contract |
| `docs/THREAT_MODEL.md` | assets, trust boundaries, misuse paths |
| `docs/adr/0001-repository-boundary.md` | boundary decision record |
| `tools/` | validators, derivation tools, preflight orchestrator |
| `tests/` | statement- and branch-complete tests for `tools/` |
| `.github/workflows/` | read-only CI definitions (no publication) |

## Contract surfaces and versioning

- `reactor-domain.json` follows schema `scpn.reactor-domain.v1`; unknown
  schemas are rejected by consumers.
- The Studio descriptor is derived deterministically and embeds the
  manifest's SHA-256; manual edits are detected as drift.
- The CONTROL adapter contract is specification-only at `0.1.0-spec`.
- SPO binding is fixed to reactor registry `1.0.0`, digest
  `786d9542ce76c56dd7748fa948b17efed6c073525e527ce90e6d5e29a2d00090`.

## What would change this architecture

Acceptance of a FUSION solver seam through the family migration gate,
ratification of an SPO `ControlIntent`-class contract, or Studio federation
after a real capability passes producer and consumer gates — each recorded
as a versioned contract change in a new ADR.
