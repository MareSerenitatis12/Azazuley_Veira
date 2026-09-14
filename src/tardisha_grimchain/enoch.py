"""TardiSHA-local Enoch / Understanding classification.

This module reflects the authored Synodic Magicae offices locally without creating
any runtime dependency on the Sydonic Magicae implementation. It classifies the
eleven native Enoch glyphs already present in TardiSHA and records only the behavior
needed by GrimChain itself.

Phase 1 only classifies the generated Enochian Understandings. Generated coordinates
remain unchanged; boundary completion belongs to Sydonic causal execution.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from .qstate_glyphs import q_state_of


@dataclass(frozen=True, slots=True)
class EnochOffice:
    """One exact TardiSHA-local Enoch office."""

    glyph: str
    office: str
    reaches_backward: bool
    generated: bool = True
    positional_operation: str | None = None
    phantasmagoria: bool = False
    phantasm_state: str | None = None


_BACKWARD_ENOCHS: Final[frozenset[str]] = frozenset({"ཪ", "☍", "߷", "🜚", "🜛"})
_Q_ENOCHS: Final[frozenset[str]] = frozenset({"🜔", "🜕", "🜖", "🜗"})

ENOCH_OFFICES: Final[dict[str, EnochOffice]] = {
    "ཪ": EnochOffice("ཪ", "Anchor", True, phantasmagoria=True),
    "☍": EnochOffice("☍", "Adverbial Bearing", True),
    "⟠": EnochOffice("⟠", "Prosody", False, generated=False),
    "⚶": EnochOffice(
        "⚶",
        "Ouroboric Reversal",
        False,
        positional_operation="reverse_adjacent_pair; boundary completion belongs to Sydonic causal execution",
    ),
    "߷": EnochOffice("߷", "Adjective Bearing", True),
    "🜚": EnochOffice("🜚", "Action / Condition Recognition", True),
    "🜛": EnochOffice("🜛", "Item Recognition", True),
    "🜕": EnochOffice("🜕", "Truth", False, phantasm_state=q_state_of("🜕")),
    "🜗": EnochOffice("🜗", "Recursion", False, phantasm_state=q_state_of("🜗")),
    "🜔": EnochOffice("🜔", "Form", False, phantasm_state=q_state_of("🜔")),
    "🜖": EnochOffice("🜖", "Shadow", False, phantasm_state=q_state_of("🜖")),
}

GENERATED_ENOCH_GLYPHS: Final[tuple[str, ...]] = tuple(
    glyph for glyph, body in ENOCH_OFFICES.items() if body.generated
)
BACKWARD_REACHING_ENOCHS: Final[frozenset[str]] = _BACKWARD_ENOCHS


def enoch_office(glyph: str) -> EnochOffice:
    """Return the exact TardiSHA-local office for one Enoch glyph."""
    if not isinstance(glyph, str) or len(glyph) != 1:
        raise ValueError("Enoch lookup requires exactly one glyph code point")
    try:
        return ENOCH_OFFICES[glyph]
    except KeyError as exc:
        raise ValueError(f"not a TardiSHA Enoch glyph: {glyph!r}") from exc


def is_enoch(glyph: str) -> bool:
    """Return whether ``glyph`` is one of the eleven native Enoch glyphs."""
    return isinstance(glyph, str) and len(glyph) == 1 and glyph in ENOCH_OFFICES


def reaches_backward(glyph: str) -> bool:
    """Return True only for the five Enochs that deepen backward reach."""
    if not is_enoch(glyph):
        return False
    return ENOCH_OFFICES[glyph].reaches_backward


def is_generated_enoch(glyph: str) -> bool:
    """Return whether an Enoch may occur in the generated GrimChain middle."""
    return is_enoch(glyph) and ENOCH_OFFICES[glyph].generated


def is_ouroboric_reversal(glyph: str) -> bool:
    """Identify ⚶ without misclassifying it as a backward-reaching Enoch."""
    return glyph == "⚶"


if {glyph for glyph, body in ENOCH_OFFICES.items() if body.reaches_backward} != _BACKWARD_ENOCHS:
    raise RuntimeError("exactly ཪ ☍ ߷ 🜚 🜛 must reach backward")
if len(GENERATED_ENOCH_GLYPHS) != 10 or "⟠" in GENERATED_ENOCH_GLYPHS or "𝔓" in GENERATED_ENOCH_GLYPHS:
    raise RuntimeError("exactly ten Enochs are generated; ⟠ and 𝔓 remain non-generated")
if ENOCH_OFFICES["⚶"].reaches_backward:
    raise RuntimeError("⚶ is positional Ouroboric Reversal, not backward depth")
if not ENOCH_OFFICES["ཪ"].phantasmagoria:
    raise RuntimeError("ཪ must retain the Phantasmagoria Anchor office")
if {glyph: ENOCH_OFFICES[glyph].phantasm_state for glyph in _Q_ENOCHS} != {
    "🜔": "Q0",
    "🜕": "Q1",
    "🜖": "Q2",
    "🜗": "Q3",
}:
    raise RuntimeError("phantasm-state Enochs must preserve the Q0/Q1/Q2/Q3 seam")
