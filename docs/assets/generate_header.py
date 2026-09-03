# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN ICF Beam Core — repository header artwork generator

"""Generate the three README header images (1280x640) for this repository.

Every image is original generated artwork derived from this repository's
own domain surface — the two-sided accelerator drive on a target, the
ion-versus-electron species invariant, and the heavy-ion per-particle
energy window the configuration model checks. The right-hand text panel
states only facts backed by the repository itself.

Outputs (written next to this script):

- ``repo_header.png`` — the two-sided accelerator drive with focusing
  lattices and converging ion bunches (used by ``README.md``).
- ``repo_header_species_split.png`` — the ion class beside the pulsed
  electron class.
- ``repo_header_energy_window.png`` — the documented heavy-ion driver
  window with flagged outliers.

Generation-time tooling only: requires ``numpy`` and ``matplotlib``,
which are deliberately not part of the pinned development lock. Run as
``python3 docs/assets/generate_header.py`` from the repository root.
The output is deterministic (fixed geometry, no random input).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

OUT_DIR = Path(__file__).resolve().parent

BG = "#00050a"
CYAN = "#00ccff"
MAGENTA = "#ff00ff"
STEEL = "#334466"
PROBE = "#66aaff"
RED = "#ff3366"
GREEN = "#3ddc84"

WIDTH_IN, HEIGHT_IN, DPI = 12.8, 6.4, 100

TITLE_METRICS: list[tuple[str, str]] = [
    ("Device Configurations", "ion_beam · pulsed_electron_beam"),
    ("Species Invariant", "ion vs electron class, hard"),
    ("Ion Energy Window", "heavy-ion driver window flagged"),
    ("Reference", "Bangerter et al., RAST 6 (2013) 85"),
    ("Plan Envelope", "v1.1.0 · synthetic · review-only"),
    ("Quality Gates", "100% branch cov · mypy --strict"),
]


def _pyplot() -> Any:
    """Return pyplot configured for headless Agg rendering."""
    import matplotlib as mpl

    mpl.use("Agg")
    import matplotlib.pyplot as plt

    return plt


def _glow_cmap() -> Any:
    """Build the family glow colormap (deep navy to cyan)."""
    from matplotlib.colors import LinearSegmentedColormap

    return LinearSegmentedColormap.from_list(
        "scpn_glow",
        ["#00050a", "#001428", "#002d55", "#005588", "#0088bb", "#00ccff"],
    )


def _text_panel(fig: Any, subtitle: str) -> None:
    """Draw the family right-hand text panel onto ``fig``."""
    ax = fig.add_axes([0.62, 0.0, 0.38, 1.0], facecolor=BG)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.text(
        0.08,
        0.84,
        "SCPN",
        color="white",
        fontsize=36,
        fontweight="bold",
        fontfamily="monospace",
        alpha=0.95,
    )
    ax.text(
        0.08,
        0.745,
        "ICF BEAM",
        color="white",
        fontsize=28,
        fontweight="bold",
        fontfamily="monospace",
        alpha=0.95,
    )
    ax.text(
        0.08,
        0.695,
        "CORE",
        color="white",
        fontsize=28,
        fontweight="bold",
        fontfamily="monospace",
        alpha=0.95,
    )
    ax.text(
        0.08,
        0.635,
        subtitle,
        color=CYAN,
        fontsize=11,
        fontfamily="monospace",
        alpha=0.85,
    )
    ax.plot([0.08, 0.85], [0.595, 0.595], color=STEEL, lw=0.8, alpha=0.5)
    y = 0.535
    for label, value in TITLE_METRICS:
        ax.text(
            0.08,
            y,
            f"▸ {label}",
            color="#6688aa",
            fontsize=9,
            fontfamily="monospace",
            alpha=0.9,
        )
        ax.text(
            0.10,
            y - 0.030,
            value,
            color="#99bbdd",
            fontsize=8,
            fontfamily="monospace",
            alpha=0.7,
        )
        y -= 0.072
    ax.text(
        0.08,
        0.06,
        "© 1996–2026 Miroslav Šotek",
        color="#445566",
        fontsize=7,
        fontfamily="monospace",
        alpha=0.6,
    )
    ax.text(
        0.08,
        0.03,
        "anulum.li | AGPL-3.0",
        color="#445566",
        fontsize=7,
        fontfamily="monospace",
        alpha=0.5,
    )


def _art_axes(fig: Any) -> Any:
    """Return the borderless left-hand art axes of ``fig``."""
    ax = fig.add_axes([0.0, 0.0, 0.68, 1.0], facecolor=BG)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    return ax


def _save(fig: Any, plt: Any, name: str) -> None:
    """Save ``fig`` to ``name`` inside the assets directory and close it."""
    target = OUT_DIR / name
    fig.savefig(target, dpi=DPI, facecolor=BG, bbox_inches="tight", pad_inches=0)
    plt.close(fig)
    print(f"generated {target}")


def _target_glow(
    ax: Any,
    centre_x: float,
    centre_z: float,
    core_radius: float,
    halo_radius: float,
) -> None:
    """Draw a glowing spherical target."""
    grid_x = np.linspace(centre_x - halo_radius, centre_x + halo_radius, 140)
    grid_z = np.linspace(centre_z - halo_radius, centre_z + halo_radius, 140)
    mesh_x, mesh_z = np.meshgrid(grid_x, grid_z)
    rho = np.sqrt((mesh_x - centre_x) ** 2 + (mesh_z - centre_z) ** 2) / core_radius
    ax.contourf(
        mesh_x,
        mesh_z,
        np.exp(-rho * 1.8),
        levels=30,
        cmap=_glow_cmap(),
        alpha=0.95,
    )


def _beamline(
    ax: Any,
    x_start: float,
    x_end: float,
    y_centre: float,
    plt: Any,
    direction: int = 1,
    magnets: int = 4,
) -> None:
    """Draw an accelerator beamline with a converging ion bundle."""
    for magnet_x in np.linspace(x_start, x_end - direction * 0.9, magnets):
        ax.add_patch(
            plt.Rectangle(
                (magnet_x - 0.22, y_centre - 0.34),
                0.44,
                0.68,
                fill=False,
                ec=STEEL,
                lw=1.6,
                alpha=0.85,
            )
        )
    for offset in (-0.16, -0.08, 0.0, 0.08, 0.16):
        along = np.linspace(0, 1, 120)
        ax.plot(
            x_start + (x_end - x_start) * along,
            y_centre + offset * (1 - along * 0.92),
            color=GREEN,
            lw=1.0,
            alpha=0.75,
        )
    ax.annotate(
        "",
        xy=(x_end, y_centre),
        xytext=(x_end - direction * 0.35, y_centre),
        arrowprops={
            "arrowstyle": "-|>",
            "color": GREEN,
            "lw": 1.6,
            "alpha": 0.95,
            "mutation_scale": 11,
        },
    )


def generate_accelerator_drive() -> None:
    """Generate ``repo_header.png``: the two-sided accelerator drive."""
    plt = _pyplot()
    fig = plt.figure(figsize=(WIDTH_IN, HEIGHT_IN), dpi=DPI, facecolor=BG)
    ax = _art_axes(fig)
    ax.set_xlim(0, 10)
    ax.set_ylim(-2.6, 2.6)

    _target_glow(ax, 5.0, 0.0, 0.4, 1.1)
    theta = np.linspace(0.0, 2.0 * np.pi, 200)
    ax.plot(
        5.0 + 0.4 * np.cos(theta),
        0.4 * np.sin(theta),
        color=CYAN,
        lw=1.9,
        alpha=0.95,
    )

    _beamline(ax, 0.7, 4.45, 0.0, plt, direction=1, magnets=4)
    _beamline(ax, 9.3, 5.55, 0.0, plt, direction=-1, magnets=4)
    ax.text(
        2.4,
        0.72,
        "focusing lattice",
        color="#667799",
        fontsize=8,
        fontfamily="monospace",
        ha="center",
        alpha=0.9,
    )
    ax.text(
        2.4,
        -0.75,
        "heavy-ion bunch",
        color=GREEN,
        fontsize=8,
        fontfamily="monospace",
        ha="center",
        alpha=0.95,
    )

    ax.annotate(
        "volumetric energy deposition",
        xy=(5.28, 0.3),
        xytext=(7.3, 1.8),
        color="white",
        fontsize=8,
        fontfamily="monospace",
        ha="center",
        alpha=0.9,
        arrowprops={"arrowstyle": "->", "color": "white", "lw": 0.9, "alpha": 0.6},
    )

    ax.text(
        5.0,
        -2.35,
        "particle momentum, not light · two-sided accelerator drive",
        color="#445566",
        fontsize=8,
        fontfamily="monospace",
        ha="center",
    )
    _text_panel(fig, "Mass Instead Of Light")
    _save(fig, plt, "repo_header.png")


def generate_species_split() -> None:
    """Generate ``repo_header_species_split.png``: the class split."""
    plt = _pyplot()
    fig = plt.figure(figsize=(WIDTH_IN, HEIGHT_IN), dpi=DPI, facecolor=BG)
    ax = _art_axes(fig)
    ax.set_xlim(0, 10)
    ax.set_ylim(-3.2, 3.2)
    theta = np.linspace(0.0, 2.0 * np.pi, 200)

    _target_glow(ax, 3.35, 0.0, 0.28, 0.7)
    ax.plot(
        3.35 + 0.28 * np.cos(theta),
        0.28 * np.sin(theta),
        color=CYAN,
        lw=1.5,
        alpha=0.95,
    )
    _beamline(ax, 0.6, 2.85, 0.0, plt, direction=1, magnets=3)
    ax.text(
        2.25,
        2.0,
        "ion_beam_icf",
        color=GREEN,
        fontsize=9,
        fontfamily="monospace",
        ha="center",
        alpha=0.95,
    )
    ax.text(
        2.25,
        1.62,
        "heavy ions · stiff bunch",
        color="#99bbdd",
        fontsize=7.5,
        fontfamily="monospace",
        ha="center",
        alpha=0.9,
    )
    ax.text(
        2.25,
        -2.5,
        "per-particle energy window checked",
        color="#445566",
        fontsize=7.5,
        fontfamily="monospace",
        ha="center",
    )

    _target_glow(ax, 8.45, 0.0, 0.28, 0.7)
    ax.plot(
        8.45 + 0.28 * np.cos(theta),
        0.28 * np.sin(theta),
        color=CYAN,
        lw=1.5,
        alpha=0.95,
    )
    along = np.linspace(0, 1, 200)
    for offset in (-0.14, 0.0, 0.14):
        wiggle = offset * (1 - along) + 0.09 * np.sin(14 * np.pi * along) * (1 - along)
        ax.plot(
            5.7 + 2.45 * along,
            wiggle,
            color=MAGENTA,
            lw=1.0,
            alpha=0.8,
        )
    ax.annotate(
        "",
        xy=(8.17, 0.0),
        xytext=(7.9, 0.0),
        arrowprops={
            "arrowstyle": "-|>",
            "color": MAGENTA,
            "lw": 1.6,
            "alpha": 0.95,
            "mutation_scale": 11,
        },
    )
    ax.add_patch(
        plt.Rectangle(
            (5.45, -0.5),
            0.3,
            1.0,
            fill=False,
            ec=STEEL,
            lw=1.6,
            alpha=0.85,
        )
    )
    ax.text(
        7.55,
        2.0,
        "pulsed_electron_beam_icf",
        color=MAGENTA,
        fontsize=9,
        fontfamily="monospace",
        ha="center",
        alpha=0.95,
    )
    ax.text(
        7.55,
        1.62,
        "light electrons · pulsed diode",
        color="#99bbdd",
        fontsize=7.5,
        fontfamily="monospace",
        ha="center",
        alpha=0.9,
    )
    ax.text(
        7.55,
        -2.5,
        "species class is a hard invariant",
        color="#445566",
        fontsize=7.5,
        fontfamily="monospace",
        ha="center",
    )

    ax.plot([5.0, 5.0], [-2.2, 2.3], color=STEEL, lw=0.8, alpha=0.4)
    ax.text(
        5.0,
        -2.95,
        "an identifier contradicting its species is rejected",
        color=PROBE,
        fontsize=8,
        fontfamily="monospace",
        ha="center",
        alpha=0.85,
    )
    _text_panel(fig, "Two Species, Two Identifiers")
    _save(fig, plt, "repo_header_species_split.png")


def generate_energy_window() -> None:
    """Generate ``repo_header_energy_window.png``: the checked window."""
    plt = _pyplot()
    fig = plt.figure(figsize=(WIDTH_IN, HEIGHT_IN), dpi=DPI, facecolor=BG)
    ax = _art_axes(fig)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)

    ax.plot([1.0, 9.2], [1.7, 1.7], color=STEEL, lw=1.0, alpha=0.7)
    ax.plot([1.0, 1.0], [1.7, 9.1], color=STEEL, lw=1.0, alpha=0.7)
    ax.text(
        8.85,
        1.25,
        "ion mass",
        color="#8899bb",
        fontsize=9.5,
        fontfamily="monospace",
        ha="right",
    )
    ax.text(
        1.15,
        8.85,
        "per-particle energy",
        color="#8899bb",
        fontsize=9.5,
        fontfamily="monospace",
    )

    mass = np.linspace(0.0, 1.0, 200)
    centre_line = 3.2 + 3.4 * mass
    px = 1.0 + 8.0 * mass
    ax.plot(
        px,
        centre_line + 1.1,
        color=GREEN,
        lw=1.0,
        alpha=0.6,
        ls=(0, (5, 3)),
    )
    ax.plot(
        px,
        centre_line - 1.1,
        color=GREEN,
        lw=1.0,
        alpha=0.6,
        ls=(0, (5, 3)),
    )
    ax.fill_between(
        px,
        centre_line - 1.1,
        centre_line + 1.1,
        color=GREEN,
        alpha=0.08,
    )
    ax.text(
        4.9,
        5.15,
        "documented heavy-ion driver window",
        color=GREEN,
        fontsize=8.5,
        fontfamily="monospace",
        ha="center",
        va="center",
        alpha=0.95,
        rotation=13,
    )

    points = [
        (0.35, 4.4, True),
        (0.62, 5.4, True),
        (0.85, 6.1, True),
        (0.30, 7.6, False),
        (0.75, 2.6, False),
    ]
    for mass_frac, energy, inside in points:
        mark_x, mark_y = 1.0 + 8.0 * mass_frac, energy
        if inside:
            ax.plot(mark_x, mark_y, "o", color=CYAN, ms=6, alpha=0.9)
        else:
            ax.plot(
                mark_x,
                mark_y,
                "x",
                color=RED,
                ms=9,
                mew=2.2,
                alpha=0.95,
            )
    ax.text(
        3.4,
        8.05,
        "flagged",
        color=RED,
        fontsize=8,
        fontfamily="monospace",
        ha="center",
        alpha=0.9,
    )
    ax.text(
        7.0,
        2.2,
        "flagged",
        color=RED,
        fontsize=8,
        fontfamily="monospace",
        ha="center",
        alpha=0.9,
    )

    ax.text(
        5.0,
        0.75,
        "ion-class per-particle energy checked · Bangerter, Faltens, "
        "Seidl, RAST 6 (2013) 85",
        color="#445566",
        fontsize=8,
        fontfamily="monospace",
        ha="center",
    )
    _text_panel(fig, "An Energy Window, Not A Guess")
    _save(fig, plt, "repo_header_energy_window.png")


if __name__ == "__main__":
    generate_accelerator_drive()
    generate_species_split()
    generate_energy_window()
