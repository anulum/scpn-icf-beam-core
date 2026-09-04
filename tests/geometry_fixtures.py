# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN ICF Beam Core — device geometry anchors

"""Anchors shared by the two geometry tiers' tests.

Reproducing a printed value is an anchor, never a claim about that
machine.

**Nothing new is anchored here.** Every radius this family's geometry
uses is printed by the source the level-0 record already anchors on, and
they live in :mod:`physics_fixtures`. This module imports them and
converts them once, because a second copy would be a second place for
them to drift.

That is the whole of it, and the shortness is the point. The sibling
laser-ICF family's geometry fixtures carry four constants of their own,
for an enclosure whose dimensions no source of theirs prints either;
they get away with it because a related precursor prints two
*dimensionless* enclosure quantities they can anchor a declared case
against. This family has no such precursor. Both of its filed sources
describe a radiation enclosure and neither prints a case radius, a wall
thickness or a length, so no enclosure is drawn and no constant is
declared for one.

The tessellation resolutions below were measured on this family's own
bodies. They are not the sibling's, and the sibling's are not
transferable — see ADR 0006.
"""

from __future__ import annotations

from typing import Final

from physics_fixtures import (
    PRINTED_HO_FUEL_INNER_RADIUS_MM,
    PRINTED_HO_FUEL_OUTER_RADIUS_MM,
    PRINTED_HO_PELLET_RADIUS_MM,
    anchor_capsule,
    anchor_configuration,
)
from scpn_icf_beam_core.geometry import MILLIMETRE_M

# --- Tessellation resolutions the tests build at ---
# Independent knobs: the segments set what the revolution keeps of the
# profile, the rings set the profile itself. The ring count is the top of
# this family's own exact regime, measured; both tiers share it.
ANCHOR_SEGMENTS: Final = 8
ANCHOR_RINGS: Final = 41

# --- Derived from the printed radii above, never typed ---
ANCHOR_PELLET_RADIUS_M: Final = PRINTED_HO_PELLET_RADIUS_MM * MILLIMETRE_M
ANCHOR_FUEL_OUTER_RADIUS_M: Final = PRINTED_HO_FUEL_OUTER_RADIUS_MM * MILLIMETRE_M
ANCHOR_CAVITY_RADIUS_M: Final = PRINTED_HO_FUEL_INNER_RADIUS_MM * MILLIMETRE_M

__all__ = [
    "ANCHOR_CAVITY_RADIUS_M",
    "ANCHOR_FUEL_OUTER_RADIUS_M",
    "ANCHOR_PELLET_RADIUS_M",
    "ANCHOR_RINGS",
    "ANCHOR_SEGMENTS",
    "PRINTED_HO_FUEL_INNER_RADIUS_MM",
    "PRINTED_HO_FUEL_OUTER_RADIUS_MM",
    "PRINTED_HO_PELLET_RADIUS_MM",
    "anchor_capsule",
    "anchor_configuration",
]
