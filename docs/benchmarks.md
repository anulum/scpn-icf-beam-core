<!--
SPDX-License-Identifier: AGPL-3.0-or-later
Commercial license available
© Concepts 1996–2026 Miroslav Šotek. All rights reserved.
© Code 2020–2026 Miroslav Šotek. All rights reserved.
ORCID: 0009-0009-3560-0851
Contact: www.anulum.li | protoscience@anulum.li
SCPN ICF Beam Core — Benchmarks and computation contract
-->

# Benchmarks and computation contract

## Computation contract

The level-0 physics of this package is a set of closed forms evaluated in
IEEE-754 binary64 on the Python floor (lengths in mm, densities in g/cm³,
masses in mg, energies in MJ):

| Module | Kernels | Operations |
|---|---|---|
| `physics/beam.py` | beam counts, elliptical spot area and effective radius `sqrt(a b)`, energy per beam, spot fluence, range-energy exponent | integer arithmetic, `* /`, `sqrt`, **`log`** |
| `physics/capsule.py` | D-T specific energy from CODATA 2022 masses, sphere and shell masses `4/3 pi rho r^3`, yield and burn-up, areal density | `* / -`, `pi`, **`pow`** (cube) |
| `physics/coupling.py` | sphere area, capsule and target gain, absorbed energy, implied conversion efficiency, enclosure area and equivalent radius | `* /`, `pi`, `sqrt`, **`pow`** (square) |
| `physics/level0.py` | the composed record with canonical bytes and SHA-256 digest | composition, JSON serialisation |

Every input outside its domain is refused with the package error, never
clamped; counts are integers. The square root is correctly rounded by
IEEE-754; `pow` and `log` are the platform's, which the standard does not
require to be correctly rounded. A native backend that must agree bit for
bit would have to use one deterministic implementation of each on both
sides. The constants and their editions are documented in
`physics/capsule.py` and bound by tests.

**Backend status.** Python floor only. There is no native crate. Audit
plan Q01 asks for a native path on required numeric paths and allows a
scoped, owner-approved exception for trivial non-hot arithmetic; that
decision is the owner's and is recorded as open in the backlog. The
benchmark marks the native backend as unavailable instead of omitting it.

## Level-0 physics — local workstation (non-isolated)

Artefact: `benchmarks/results/level0_physics.local.json` (schema
`scpn-icf-beam-core.level0-physics-benchmark.v1`, generated 2026-10-31T03:45:46.847907+00:00, at commit
`890399a3b1c1` with the working tree of the landing commit).
Host: 11th Gen Intel(R) Core(TM) i5-11600K @ 3.90GHz, Linux-7.0.0-34-generic-x86_64-with-glibc2.39, Python 3.12.3; load average
at start 4.69 (other sessions were active on the host);
cores not isolated, so treat the numbers as a smoke timing, not a
performance measurement. Parameters: 20000 closed-form points and
2000 records, 3 warm-up passes, 20 timed passes.

### `closed_forms` (two capsule masses, spot radius, energy per beam, gain and enclosure radius per point)

| Backend | P50 µs/point | P95 µs/point | P99 µs/point | mean µs/point | throughput points/s | status |
|---|---|---|---|---|---|---|
| `python_floor` (public API) | 1.518 | 1.794 | 2.327 | 1.523 | 658966 | measured |
| `rust_native` | — | — | — | — | — | unavailable: no native crate |

### `level0_record` (composed record with canonical bytes per point)

| Backend | P50 µs/record | P95 µs/record | P99 µs/record | mean µs/record | throughput records/s | status |
|---|---|---|---|---|---|---|
| `python_floor` (public API) | 43.063 | 66.898 | 67.194 | 46.987 | 23222 | measured |
| `rust_native` | — | — | — | — | — | unavailable: no native crate |

## Regenerate

```bash
.venv/bin/python benchmarks/level0_physics.py --label local
```

The script writes `benchmarks/results/level0_physics.<label>.json` with the
provenance above. A number from a fixed CI runner or isolated cores would
replace the smoke timing here; none is claimed yet.
