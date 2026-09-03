# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN ICF Beam Core — shared diagnostic and clock test fixtures

"""Shared fixtures for the diagnostic plan and clock semantics tests.

The catalogue bindings, signal inventories, clocks, frames, relations and
channel builders used by more than one surface live here so that each test
module states only what is particular to its own surface.

All plans in this module are synthetic fixtures; none describes any real
diagnostic, measurement, or facility.
"""

from __future__ import annotations

from typing import Any

from scpn_icf_beam_core.observability import (
    CATALOGUE_BINDING,
    ClockDomain,
    ClockKind,
    ClockModel,
    ClockRelation,
    ClockTopology,
    DiagnosticChannelPlan,
    DiagnosticPlan,
    FrameKind,
    FrameTransformation,
    ReferenceFrame,
    SemanticCarrier,
    SignalDeclaration,
    SignalRole,
    TransformationKind,
)

DERIVED_BINDINGS = {
    "calibration": "synthetic coil transfer functions",
    "clock_epoch": "clk_facility",
    "mode_identity": "declared spherical-harmonic mode labels",
    "observability_threshold": "declared amplitude floor",
    "observation_operator": "synthetic coil-array projection operator",
    "operator_validation": "operator exercised on synthetic fields",
    "provenance": "synthetic fixture",
    "quality": "synthetic quality flags",
    "reference_signal": "synthetic reference oscillator",
    "uncertainty": "declared amplitude and phase bounds",
    "validity": "synthetic validity window",
}


EVENT_BINDINGS = {
    "clock_epoch": "clk_shot",
    "event_reference": "synthetic bunch fiducial marker",
    "provenance": "synthetic fixture",
    "repetition_evidence": "synthetic repeated cycle labels",
    "timing_uncertainty": "declared bound",
    "validity": "synthetic validity window",
}


NONCYCLIC_BINDINGS = {
    "calibration": "synthetic calibration set",
    "clock_epoch": "clk_shot",
    "coordinate_frame": "frm_chamber",
    "provenance": "synthetic fixture",
    "quality": "synthetic quality flags",
    "uncertainty": "declared bounds",
    "units": "SI units declared per field",
    "validity": "synthetic validity window",
}


NUMERICAL_BINDINGS = {
    "initial_condition": "synthetic initial state",
    "model_revision": "model revision identifier",
    "provenance": "synthetic fixture",
    "simulation_clock": "clk_sim",
    "solver_validity": "declared solver validity envelope",
}


REFERENCE_FRAMES = (
    ReferenceFrame(
        identifier="frm_beamline",
        kind=FrameKind.BEAMLINE,
        description="accelerator beamline frame to target chamber centre",
    ),
    ReferenceFrame(
        identifier="frm_chamber",
        kind=FrameKind.CHAMBER_CARTESIAN,
        description="target-chamber Cartesian frame at chamber centre",
    ),
)


CLOCK_RELATIONS = (
    ClockRelation(
        child_identifier="clk_shot",
        parent_identifier="clk_facility",
        max_offset_s=1.0e-6,
        uncertainty_s=1.0e-7,
        method=(
            "synthetic declaration: trigger timestamped against the "
            "facility oscillator; no correlation evidence claimed"
        ),
        mapping_state="unmapped",
        evidence_claimed=False,
    ),
)


SIGNALS_CH_ASYMMETRY_MODE_SET = (
    SignalDeclaration(
        identifier="sig_asymmetry_amplitude",
        quantity="normalised_amplitude",
        unit="1",
        role=SignalRole.AMPLITUDE,
        description="synthetic asymmetry-mode amplitude",
    ),
    SignalDeclaration(
        identifier="sig_mode_number",
        quantity="mode_number",
        unit="1",
        role=SignalRole.AUXILIARY,
        description="declared toroidal or azimuthal mode label",
    ),
    SignalDeclaration(
        identifier="sig_mode_phase",
        quantity="phase",
        unit="rad",
        role=SignalRole.CARRIER,
        description="synthetic mode phase",
    ),
)


SIGNALS_CH_BUNCH_TIMING_TRAIN = (
    SignalDeclaration(
        identifier="sig_bunch_charge",
        quantity="charge",
        unit="C",
        role=SignalRole.AMPLITUDE,
        description="synthetic bunch charge",
    ),
    SignalDeclaration(
        identifier="sig_bunch_cycle",
        quantity="cycle_index",
        unit="1",
        role=SignalRole.CARRIER,
        description="synthetic repeated-cycle label per event",
    ),
    SignalDeclaration(
        identifier="sig_bunch_duration",
        quantity="time",
        unit="s",
        role=SignalRole.AUXILIARY,
        description="synthetic event duration",
    ),
    SignalDeclaration(
        identifier="sig_bunch_onset",
        quantity="time",
        unit="s",
        role=SignalRole.TIMING_MARKER,
        description="synthetic event onset marker",
    ),
)


SIGNALS_CH_SHOT_OUTCOME_SET = (
    SignalDeclaration(
        identifier="sig_burn_duration",
        quantity="time",
        unit="s",
        role=SignalRole.AUXILIARY,
        description="synthetic burn duration",
    ),
    SignalDeclaration(
        identifier="sig_neutron_yield",
        quantity="count",
        unit="1",
        role=SignalRole.CARRIER,
        description="synthetic neutron yield",
    ),
)


SIGNALS_CH_SYNTHETIC_OSCILLATOR = (
    SignalDeclaration(
        identifier="sig_phase",
        quantity="phase",
        unit="rad",
        role=SignalRole.CARRIER,
        description="model-owned synthetic oscillator phase",
    ),
)


SIGNALS_CH_TRAJECTORY_RADIOGRAPHY = (
    SignalDeclaration(
        identifier="sig_implosion_velocity",
        quantity="velocity",
        unit="m/s",
        role=SignalRole.AUXILIARY,
        description="synthetic implosion velocity",
    ),
    SignalDeclaration(
        identifier="sig_shell_radius",
        quantity="length",
        unit="m",
        role=SignalRole.CARRIER,
        description="synthetic shell radius trajectory",
    ),
)


REFERENCE_TRANSFORMATIONS: tuple[FrameTransformation, ...] = (
    FrameTransformation(
        source_identifier="frm_beamline",
        target_identifier="frm_chamber",
        kind=TransformationKind.RIGID,
        equilibrium_dependent=False,
        method=(
            "synthetic declaration: mapping between the declared frames; "
            "no mapping evidence claimed"
        ),
        evidence_claimed=False,
    ),
)


CLOCK_TOPOLOGY = ClockTopology(
    domains=(
        ClockDomain(
            identifier="dom_facility",
            root_clock_identifier="clk_facility",
            member_clock_identifiers=("clk_facility", "clk_shot"),
            scope="facility master timing and the shot trigger bound to it",
        ),
    ),
    reference_domain_identifier="dom_facility",
)


def clock_facility() -> ClockModel:
    """Build the synthetic facility master clock."""
    return ClockModel(
        identifier="clk_facility",
        kind=ClockKind.FACILITY_MONOTONIC,
        epoch="facility master oscillator zero",
        resolution_s=1.0e-12,
        uncertainty_s=1.0e-12,
    )


def clock_shot() -> ClockModel:
    """Build the synthetic shot-fiducial epoch clock."""
    return ClockModel(
        identifier="clk_shot",
        kind=ClockKind.SHOT_EVENT_EPOCH,
        epoch="shot fiducial t0",
        resolution_s=1.0e-11,
        uncertainty_s=1.0e-11,
    )


def clock_simulation() -> ClockModel:
    """Build the synthetic simulation clock."""
    return ClockModel(
        identifier="clk_sim",
        kind=ClockKind.SIMULATION,
        epoch="solver step zero",
        resolution_s=1.0e-9,
        uncertainty_s=0.0,
    )


def channel_event_train() -> DiagnosticChannelPlan:
    """Build the synthetic bunch-arrival event channel."""
    return DiagnosticChannelPlan(
        identifier="ch_bunch_timing_train",
        candidate_id="inertial.driver_timing",
        carrier=SemanticCarrier.EVENT_CYCLE,
        clock_identifier="clk_shot",
        sample_rate_hz=1.0e10,
        max_signal_frequency_hz=0.0,
        timing_uncertainty_s=5.0e-10,
        acquisition_start_s=0.0,
        acquisition_duration_s=1e-07,
        element_count=1,
        evidence_bindings=dict(EVENT_BINDINGS),
        signals=SIGNALS_CH_BUNCH_TIMING_TRAIN,
        synthetic=True,
    )


def channel_noncyclic_one() -> DiagnosticChannelPlan:
    """Build the synthetic streaked-radiography trajectory channel."""
    return DiagnosticChannelPlan(
        identifier="ch_trajectory_radiography",
        candidate_id="inertial.implosion_trajectory",
        carrier=SemanticCarrier.BOUNDED_FEATURE,
        clock_identifier="clk_shot",
        sample_rate_hz=1.0e09,
        max_signal_frequency_hz=0.0,
        timing_uncertainty_s=None,
        acquisition_start_s=0.0,
        acquisition_duration_s=1e-07,
        element_count=1,
        evidence_bindings=dict(NONCYCLIC_BINDINGS),
        signals=SIGNALS_CH_TRAJECTORY_RADIOGRAPHY,
        synthetic=True,
    )


def channel_noncyclic_two() -> DiagnosticChannelPlan:
    """Build the synthetic shot-outcome channel."""
    return DiagnosticChannelPlan(
        identifier="ch_shot_outcome_set",
        candidate_id="inertial.shot_outcome",
        carrier=SemanticCarrier.BOUNDED_FEATURE,
        clock_identifier="clk_shot",
        sample_rate_hz=1.0e00,
        max_signal_frequency_hz=0.0,
        timing_uncertainty_s=None,
        acquisition_start_s=0.0,
        acquisition_duration_s=1e-06,
        element_count=1,
        evidence_bindings=dict(NONCYCLIC_BINDINGS),
        signals=SIGNALS_CH_SHOT_OUTCOME_SET,
        synthetic=True,
    )


def channel_derived() -> DiagnosticChannelPlan:
    """Build the synthetic implosion-asymmetry mode channel."""
    return DiagnosticChannelPlan(
        identifier="ch_asymmetry_mode_set",
        candidate_id="inertial.resolved_asymmetry_mode",
        carrier=SemanticCarrier.COMPLEX_MODE,
        clock_identifier="clk_facility",
        sample_rate_hz=4.0e09,
        max_signal_frequency_hz=1.0e09,
        timing_uncertainty_s=None,
        acquisition_start_s=0.0,
        acquisition_duration_s=1e-07,
        element_count=8,
        evidence_bindings=dict(DERIVED_BINDINGS),
        signals=SIGNALS_CH_ASYMMETRY_MODE_SET,
        synthetic=True,
    )


def channel_oscillator() -> DiagnosticChannelPlan:
    """Build the synthetic model-oscillator channel."""
    return DiagnosticChannelPlan(
        identifier="ch_synthetic_oscillator",
        candidate_id="model.synthetic_oscillator_coordinate",
        carrier=SemanticCarrier.NUMERICAL_PHASE,
        clock_identifier="clk_sim",
        sample_rate_hz=1.0e4,
        max_signal_frequency_hz=0.0,
        timing_uncertainty_s=None,
        acquisition_start_s=0.0,
        acquisition_duration_s=1e-08,
        element_count=1,
        evidence_bindings=dict(NUMERICAL_BINDINGS),
        signals=SIGNALS_CH_SYNTHETIC_OSCILLATOR,
        synthetic=True,
    )


def synthetic_plan() -> DiagnosticPlan:
    """Build a fully valid synthetic diagnostic plan."""
    return DiagnosticPlan(
        identifier="icf_beam_reference_plan",
        binding=CATALOGUE_BINDING,
        clocks=(clock_facility(), clock_shot(), clock_simulation()),
        frames=REFERENCE_FRAMES,
        clock_relations=CLOCK_RELATIONS,
        frame_transformations=REFERENCE_TRANSFORMATIONS,
        clock_topology=CLOCK_TOPOLOGY,
        channels=(
            channel_derived(),
            channel_event_train(),
            channel_noncyclic_two(),
            channel_oscillator(),
            channel_noncyclic_one(),
        ),
        deferrals=(),
    )


def derived_channel(**overrides: Any) -> DiagnosticChannelPlan:
    """Build the Mirnov channel with keyword overrides applied."""
    values: dict[str, Any] = {
        "identifier": "ch_asymmetry_mode_set",
        "candidate_id": "inertial.resolved_asymmetry_mode",
        "carrier": SemanticCarrier.COMPLEX_MODE,
        "clock_identifier": "clk_facility",
        "sample_rate_hz": 4.0e09,
        "max_signal_frequency_hz": 1.0e09,
        "timing_uncertainty_s": None,
        "acquisition_start_s": 0.0,
        "acquisition_duration_s": 1e-07,
        "element_count": 8,
        "evidence_bindings": dict(DERIVED_BINDINGS),
        "signals": SIGNALS_CH_ASYMMETRY_MODE_SET,
        "synthetic": True,
    }
    values.update(overrides)
    return DiagnosticChannelPlan(**values)


def plan_with(**overrides: Any) -> DiagnosticPlan:
    """Rebuild the synthetic plan with keyword overrides applied."""
    plan = synthetic_plan()
    values: dict[str, Any] = {
        "identifier": plan.identifier,
        "binding": plan.binding,
        "clocks": plan.clocks,
        "frames": plan.frames,
        "clock_relations": plan.clock_relations,
        "frame_transformations": plan.frame_transformations,
        "clock_topology": plan.clock_topology,
        "channels": plan.channels,
        "deferrals": plan.deferrals,
    }
    values.update(overrides)
    return DiagnosticPlan(**values)


def signal_declaration(**overrides: Any) -> SignalDeclaration:
    """Build an auxiliary signal with keyword overrides applied."""
    values: dict[str, Any] = {
        "identifier": "sig_zz_extra",
        "quantity": "current",
        "unit": "A",
        "role": SignalRole.AUXILIARY,
        "description": "synthetic auxiliary signal",
    }
    values.update(overrides)
    return SignalDeclaration(**values)
