<!--
SPDX-License-Identifier: AGPL-3.0-or-later
Commercial license available
© Concepts 1996–2026 Miroslav Šotek. All rights reserved.
© Code 2020–2026 Miroslav Šotek. All rights reserved.
ORCID: 0009-0009-3560-0851
Contact: www.anulum.li | protoscience@anulum.li
SCPN ICF Beam Core — VALIDATION
-->

# Validation

Every gate currently active in this repository, with its exact scope,
followed by the evidence record of each implemented capability.

## Local gates

| Gate | Command | Scope |
|---|---|---|
| Lint | `ruff check .` | all Python under `src/`, `tools/`, and `tests/` |
| Format | `ruff format --check .` | same scope |
| Typing | `mypy --strict src tools tests` | zero errors, strict mode |
| Tests + coverage | `pytest -q --cov=src --cov=tools --cov-branch --cov-fail-under=100` | 100 % statement and branch coverage of `src/` and `tools/` |
| Domain manifest | `python3 tools/validate_reactor_domain.py reactor-domain.json` | schema, registry version/digest, exact configuration set, capability inventory shape and ceiling rule, safety boundary |
| Studio descriptor | `python3 tools/derive_studio_descriptor.py --check` | committed descriptor byte-identical to a fresh derivation |
| Capability inventory | `python3 tools/generate_capability_inventory.py --check` | committed inventory byte-identical to a fresh generation |
| Licensing | `reuse lint` | REUSE 3.x compliance of the full tree |
| Workflow lint | `actionlint` | all files under `.github/workflows/` |
| Workflow modularity | `python3 tools/audit_workflows.py` | distributed workflow inventory: single ownership per job, coordinator/gate contract, action pinning, size ceilings |
| Documentation | `python3 tools/preflight.py --only docs` | UTF-8 readability and relative-link integrity of every Markdown file |
| Orchestrated | `python3 tools/preflight.py` | fail-closed run of all gates above |

## Workflow gates

Definitions are present in-repository; they run on the hosted platform
only once a remote exists under separate owner authority.

The hosted surface is modular: `ci.yml` is a coordinator that carries
only trigger policy, two reusable-workflow calls, and one stable
fail-closed `gate` job aggregating every category (failure,
cancellation, and unexpected skips all fail the gate). Every job is
declared and owned exactly once in the versioned inventory
`.github/workflow-inventory.json`, which the workflow-modularity guard
verifies locally and in hosted CI.

| Workflow | Purpose |
|---|---|
| `ci.yml` | coordinator and stable required gate |
| `reusable-static-policy.yml` | lint, format, typing, domain policy, workflow guard |
| `reusable-tests.yml` | tests with complete statement and branch coverage |
| `pre-commit.yml` | exact pre-commit parity |
| `codeql.yml` | Python code scanning |
| `security-audit.yml` | secrets, dependency, licence, and workflow policy |
| `docs.yml` | strict documentation and link validation, no deployment |
| `sbom.yml` | reproducible dependency inventory, no release |
| `scorecard.yml` | read-only supply-chain analysis |

## Shared ecosystem gate

From the monorepo root:

```bash
python3 agentic-shared/scripts/repository_tier0_scaffold_audit.py \
  03_CODE/SCPN-ICF-BEAM-CORE --json
```

proves the Tier-0 local-scaffold machine profile (required and forbidden
paths, Git/remote boundary, workflow pins and permissions, badge non-claims,
JSON integrity, defensive ignore rules).

## Device configuration model

Evidence record of the `device_configuration_model` capability
(`computational_prototype`; design record: `docs/adr/0002-device-configuration-model.md`).

What is exercised, all under the 100 % statement-and-branch coverage gate:

- Validated frozen parameter objects (`BeamDriver`, `TargetDeclaration`,
  `DeviceConfiguration`) rejecting non-finite values, non-positive
  extents, unknown species, and the hard species class invariant (ion
  for `ion_beam_icf`, electron for `pulsed_electron_beam_icf`) — every
  rejection branch is tested.
- The beam-power relation `P = E / tau` as a documented derived
  quantity, with an advisory finding for ion-class per-particle energies
  outside the documented heavy-ion driver window `[1, 10] GeV`
  (Bangerter, Faltens & Seidl, Rev. Accel. Sci. Technol. 6 (2013) 85;
  not applied to the electron class), reported and never clamped.
- Canonical serialisation (sorted keys, NaN/infinity rejected on both
  emit and parse), SHA-256 digest identity, and a strict round-trip
  parser that refuses unknown fields.
- A data-only pin equality check binding the model to the SPO reactor
  registry version and digest declared in `reactor-domain.json`.

Bounded claims — what is NOT claimed:

- No parameter set describes, approximates, or validates any real
  machine; every exercised parameter set is a synthetic test fixture.
- The estimates are advisory regime checks, not deposition, implosion,
  or yield results; no benchmark, dataset, solver, controller, or
  experimental correlation exists in this repository.

## Diagnostic and clock semantics

Evidence record of the `diagnostic_clock_semantics` capability
(`computational_prototype`; design record: `docs/adr/0003-diagnostic-clock-semantics.md`).

What is exercised, all under the 100 % statement-and-branch coverage gate:

- Validated frozen declaration objects (`ClockModel`,
  `DiagnosticChannelPlan`, `DeferredCandidate`, `DiagnosticPlan`)
  rejecting catalogue misalignment: inapplicable candidates,
  inadmissible carriers, evidence-vocabulary mismatches, incompatible
  clock kinds, Nyquist violations, unresolvable event-timing bounds,
  and incomplete candidate coverage — every rejection branch is tested.
- A data-only pin (`ObservabilityBinding`) to the SPO
  observability-profile catalogue release `1.0.0`
  (`d70c0de696534e5a77066ef8420cf7ca17bc4d7321984b0ac83523dbc1dce609`),
  bound in turn to reactor registry `1.0.0`; a plan pinned to any other
  release is rejected.
- A reference plan mirroring canonical practice with synthetic
  declarations: bunch-timing train, trajectory radiography, asymmetry mode set, shot-outcome set, synthetic oscillator, each bound to its clock domain.
- Documented advisory band and timing checks with their sources stated
  in the code: implosion-asymmetry bands of 1 MHz–10 GHz and sub-ns bunch timing (Bangerter 2013); findings are reported, never clamped.
- Canonical serialisation (sorted keys, NaN/infinity rejected on both
  emit and parse), SHA-256 digest identity, and a strict round-trip
  parser that refuses unknown fields.

Bounded claims — what is NOT claimed:

- No channel describes a real diagnostic, measurement, or facility;
  every plan is a synthetic declaration of HOW evidence slots would be
  bound, marked `synthetic=True` by hard invariant.
- No SPO semantic-profile ingress is declared; the profile registry
  `ingress_state` for this device family remains `not_declared`, and
  no adapter, producer, or handoff exists in this repository.

### Portable plan envelope

The `diagnostic_clock_semantics` capability additionally exercises a
producer-owned portable envelope
(`src/scpn_icf_beam_core/plan_envelope.py`,
`scpn.reactor-diagnostic-plan-envelope.v1` version `1.0.0`): one
canonically serialised object carrying the exact project identity and
owned configurations, the capability and its maturity, the
synthetic/review-only/non-actuating statements, both SPO registry pins,
the SHA-256 digest of the inner canonical plan, the producer revision,
and fixed no-observation/no-control non-claims. The committed immutable
fixture (`tests/data/plan_envelope_fixture.json`, byte hash pinned in
the tests) is verified together with positive, tamper, wrong-project,
wrong-configuration, registry-drift, duplicate-member, and non-finite
rejection paths, all under the 100 % coverage gate. The envelope claims
nothing beyond the enveloped synthetic declaration.

### Typed frames, clock relations, and acquisition geometry

The deepened model adds typed reference frames (per-repository allowed
`FrameKind` subset; every noncyclic `coordinate_frame` binding must
reference a declared frame), clock synchronisation relations
(synthetic offset/uncertainty BOUNDS between declared non-simulation
clocks with an explicit method statement — no correlation evidence is
claimed and no clock is mapped to physical wall time), and per-channel
acquisition windows and element counts with device-cited advisory
scales. Both decoders are hardened per the SPO intake architecture:
recursive exact-key refusal in every nested entry, duplicate-member
refusal, and byte-canonical refusal (a document that is not exactly
canonical bytes is rejected). The envelope is `1.1.0`, adding
`manifest_sha256` — the SHA-256 of the committed canonical
`reactor-domain.json` — verified in tests against the committed file.
All declarations remain synthetic; nothing here observes or controls
anything.

### Signal inventories, frame transformations, and clock topology

The depth slice (envelope `1.2.0`; a `1.1.0` document is refused by the
`1.2.0` codec and vice versa — no defaults, no cross-version coercion;
`1.1.0` remains historical custody at the consumer) adds three typed
declaration surfaces, every branch under the 100 % statement-and-branch
gate:

- A per-channel **signal inventory** (`SignalDeclaration`: identifier,
  quantity, unit, role, description). Hard rules: non-empty, unique and
  sorted; exactly one `carrier`; a `timing_marker` in `"s"` exactly for
  event-relative channels and forbidden otherwise; numerical-only
  channels declare a single `phase`/`rad` carrier. Quantity and unit are
  declared tokens — no SI or UCUM validation is performed or claimed —
  and no declaration creates or overrides a candidate, carrier,
  observation, or phase: the candidate profile stays authoritative. An
  advisory flags a multi-element cyclic array without an amplitude
  signal.
- **Frame transformations** (`FrameTransformation`) between declared
  frames: kind admissibility fixed by frame-kind pair (`flux_mapping`
  for machine↔flux, flux↔Boozer, field-line↔machine; `projection` for
  blanket↔machine; `rigid` for chamber↔beamline), `equilibrium_dependent`
  exactly for flux mappings, at most one transformation per frame pair,
  sorted by source then target, and — with two or more frames — a
  connected transformation graph. Methods are declarations;
  `evidence_claimed` is always `False`.
- A **clock topology** (`ClockDomain`, `ClockTopology`): every physical
  clock in exactly one domain, the simulation clock in none; a domain
  holding a facility clock is rooted there, otherwise at its shot-event
  epoch; every non-root member declares a relation to its root; every
  non-reference root declares a relation to the reference root (star);
  relations must not form a cycle. The reference plan declares one
  domain (`clk_facility` root, `clk_shot` member); multi-domain rules
  are exercised by test-constructed plans. Scopes are declarations;
  `mapping_state` stays `unmapped`.

## Level-0 device physics

Evidence record of the `level0_device_physics` capability
(`computational_prototype`; design record:
`docs/adr/0005-level0-device-physics.md`).

The work this repository cites for its driver window is behind a
subscription and is not on file. Two United States Department of Energy
laboratory preprints are, both marked for unlimited distribution, and
every anchor below is read from one of them. **Both describe heavy-ion
drivers**, and nothing here is evidence about the electron-beam
configuration this repository also owns.

What is exercised, all under the 100 % statement-and-branch coverage gate:

- The illumination geometry of a multibeam arrangement: the elliptical
  focal spot, its area, its effective radius, the equal split of driver
  energy across both cones, and the spot-averaged fluence.
- The mass inventory of a three-layer capsule from radii and densities,
  and the energy its fuel can release, with the deuterium-tritium
  specific energy built from the two nuclear masses and the released
  energy per reaction rather than carried as a rounded constant.
- The factorisation `G_target = eta_c eta_e G_capsule`, in both
  directions, and the enclosure area a capsule-to-enclosure ratio
  implies.
- A composed record that builds the ablator's thickness from the
  configuration's pellet radius and the declaration's fuel radius, and
  refuses a fuel layer that reaches or passes the pellet's surface.
- Every declared quantity validated where it is declared as well as
  inside the relation that consumes it.
- Canonical serialisation (sorted keys, NaN/infinity rejected) and
  SHA-256 digest identity of the record.

Anchors — printed values reproduced, and nothing further:

- The capsule's three radii and three densities, and every mass that
  follows: 25.45 mg of ablator against 3.87 mg of solid fuel and
  0.0073 mg of vapour.
- The effective radius `sqrt(a b)` of both printed focal spots,
  reproduced at the precision each printed answer carries: 2.7331 for a
  review that prints 2.7, and 1.6673 for one that prints 1.67.
- The printed beam counts of eight and sixteen per side doubling into
  the printed totals of sixteen and thirty-two.
- The capsule gain, exactly 430 from a printed 430 MJ and a printed
  1 MJ.

Implied by printed values, and labelled as implied rather than
reproduced:

- The burn-up fraction, 0.3286 of the inventory. The source prints a
  yield and never a fraction, so this is the only available direction.
- The conversion efficiency, 0.8859. The source plots it against
  converter radius and never prints a number; this is what its own four
  printed quantities require of the fifth.

Reconstructed, and named for it in the fixtures:

- The driver energy of the capsule design, which neither source prints.
  It is the printed yield over the printed system gain, so recovering
  that gain from it is a round trip; the test that does so states that
  it proves arithmetic and not a property of the design.

Measured, rather than assumed:

- **Neither layer thickness returns exactly.** The printed radii are
  decimals in millimetres, so their differences carry rounding: the
  ablator gives 0.21999999999999975 and the fuel layer
  0.32000000000000006. The sibling laser family's printed radii are
  whole micrometres and its layer arithmetic is exact; this one's is
  not, and both tests are bounds with the reason written down.
- **The illumination review truncates its gains rather than rounding
  them.** 370/6.35 is 58.2677 and it prints 58; 413/7.4 is 55.8108 and
  it prints 55; 436/3.3 is 132.1212 and it prints 132. All three are
  floors and the middle one is not the rounded value.
- **No single power law joins the three printed range-and-energy
  pairs.** The exponents are 1.1200, 1.2544 and 1.1926. The module
  exposes the exponent between two pairs and never fits a range law, and
  the test asserts that the exponents disagree.
- **The two families' enclosure ratios are different quantities.** This
  family's source prints capsule-to-enclosure 0.075, whose reciprocal is
  13.33; the laser family's precursor prints enclosure-to-capsule 15 to
  25. Neither checks the other.

Boundaries:

- The pulse duration used by the fixtures is declared and no source is
  claimed for it.
- The beams are split equally and the fluence is averaged over the whole
  ellipse; the sources' beams are Gaussian, so no value here is a peak.
- An implied burn-up fraction or conversion efficiency above one is
  returned rather than refused, because it is the finding that the
  declarations do not describe one design.
- No value describes, approximates or validates any real machine or
  shot; an anchor reproduces a number a filed source prints and nothing
  further.

## Device 3D model

Evidence record of the `device_3d_model` capability
(`computational_prototype`; design record:
`docs/adr/0006-device-3d-and-cad-models.md`; consumer contract:
`docs/DEVICE_3D_MODEL_CONTRACT.md`).

What is exercised, all under the 100 % statement-and-branch coverage gate:

- The body set of each owned configuration, in its fixed order: the same
  three concentric capsule bodies for both, and the map covering exactly
  the configurations this repository owns.
- The single conversion from the millimetres the level-0 declaration
  carries to the metres the bodies are built in, with the
  configuration's own micrometres converted by the level-0 relation that
  owns them rather than a second time here.
- A fuel layer that leaves no ablator inside the pellet refused by the
  level-0 relation itself, from both directions — a layering too large
  for its pellet, and a pellet too small for its layering — so this tier
  cannot draw a capsule the physics record would have rejected.
- The two resolutions asserted not to be interchangeable, in two tests:
  one recording that at the anchor counts the multiple-of-eight rule
  happens to catch the swap, and one showing that where both counts are
  legal nothing objects.
- Canonical serialisation and SHA-256 digest identity of the model
  record, including the digests of the configuration and the capsule
  declaration it was built from, and that a configuration change leaves
  the capsule digest where it was.

Anchors — printed values reproduced, and nothing further:

- All three printed radii — 2.34 mm, 2.12 mm and 1.8 mm — read off the
  built bodies as exact equalities. The sphere profile places a vertex
  at exactly the centre plus the radius and the capsule is centred on
  the origin.
- Every radius is printed. The cavity is anchored rather than derived,
  which is the difference from the laser-ICF family, whose review prints
  an outer radius and two thicknesses.

Measured, rather than assumed:

- The printed layer thicknesses do **not** return exactly: the ablator
  comes back as 0.2199999999999997 and the fuel layer as
  0.3200000000000002, at 1.4e-15 and 5.2e-16 relative. The cause is the
  opposite of the laser family's — there the source prints integer
  micrometres and the conversion to metres introduces the rounding,
  while here the printed millimetres are already inexact in binary,
  2.34 − 2.12 being 0.21999999999999975 before any conversion. The test
  carries a measured bound and asserts the inequality explicitly.

Boundaries:

- **No radiation enclosure is drawn.** Both filed sources describe one
  and neither prints a case radius, wall thickness or length; the one
  schematic showing it carries no dimension callouts. The level-0
  `equivalent_enclosure_radius_mm` is the radius of a sphere of equal
  *area*, derived from a printed area ratio, and is not a case
  dimension. The absence is stated in the non-claims of both tiers and a
  test asserts that it is.
- **Nothing here is evidence about `pulsed_electron_beam_icf`.** Both
  filed sources are heavy-ion. That configuration builds from whatever
  is declared for it; a test asserts that its record differs from the
  ion-class one and that the non-claims say so.
- Every body is an inscribed polyhedron of revolution. Comparing any
  volume here to `4/3 pi r^3` compares two different solids.

## Device CAD model

Evidence record of the `device_cad_model` capability
(`computational_prototype`; design record:
`docs/adr/0006-device-3d-and-cad-models.md`). The tier is behind the
optional `cad` extra; two CI jobs install it.

What is exercised, all under the same coverage gate:

- The same body set and the same order as tier G1.
- The library's fail-closed evidence on every body: the back-end's
  volume and area against the analytic closed forms, the faceted volume
  against the declared chord-deficit bound, and the faceted volume
  against the tier-G1 mesh of the same body.
- The assembly manifest, the normalised STEP bytes and their digest, and
  the pinned back-end versions.
- Refusals: an unknown identifier, a manifest of the wrong schema, a
  manifest counting the wrong number of bodies, a body set in the wrong
  order, and an invalid deflection arriving as this package's own error
  type.

Measured on this family's own bodies, and recorded because none of it
transfers from a sibling:

- **The ring count is bounded, and the bound is not a simple ceiling.**
  Scanning every count from 30 to 75: to 41 every count is exact; from
  42 to 65 every even count refuses and every odd count is exact; from
  66 upward every count refuses. The first refusal is at 42, where the
  fuel shell departs by 8.2e-5 against a 1e-9 tolerance.
- **The parity is measured; its cause is not claimed.** An even ring
  count places exactly one profile sample on the equator, at exactly
  `(0, R)`, and an odd count places none; the refusals in the mixed band
  fall exactly on the even counts. Whether that is what the revolve
  fails on is not established here.
- **The default is the top of the first regime, not the highest count
  that builds.** Odd counts to 65 build and are not used: their margin
  is one step, on a parity whose cause is unknown.
- **The count is 41 here and 39 in the laser family.** Where the band
  starts moves with the body's radius: measured on solid spheres, the
  first refusal is at 34 rings for 1.0 mm, 40 at 1.503 mm, 42 at 1.8 mm,
  46 at 2.34 mm, 50 at 3.0 mm and 58 at 5.0 mm, with nothing failing at
  10 mm and above up to 120 rings. No family may inherit a sibling's
  count.
- **The linear deflection does not change the model at all.** Across
  5e-7, 3e-7, 2.5e-7, 2e-7, 1.5e-7 and 1.2e-7 metres the faceted volume
  deficit of every body is the same number to five significant figures;
  what moves is the declared bound `2 d / r`. A test asserts this
  directly by building at two deflections and comparing both the
  deficits and the ratio of the bounds.
- **The threshold is therefore exact, not a rung on a ladder.** The
  smallest deflection the worst body clears is `deficit * r / 2` =
  1.1326e-7 m, computed from the built model by a test that asserts it
  lies between the refused 1e-7 m and the declared 2e-7 m. The declared
  value leaves the vapour core at 0.57 of its bound, which is a stated
  margin against back-end drift rather than the strongest claim
  available.
- **The angular deflection does not bind.** Between 0.5 and 0.1 radians
  every body's deficit is identical to four significant figures.
- The deficit bound of each body uses that body's **outer** radius,
  which is the tightest bound a body of revolution admits; a sphere's
  circles run to zero at the poles and would make the bound unbounded.

Boundaries:

- Determinism of the STEP bytes is claimed within one pinned back-end
  environment only, never across back-end versions.
- No body is an engineering model and no fabrication tolerance is
  carried.
