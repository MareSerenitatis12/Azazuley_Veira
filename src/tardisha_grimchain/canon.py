"""Minimal executable Canon for the TardiSHA D-COMP route calculator.

This is deliberately independent from alqc-advanced-reasoning.  The source project was
studied to recover the small mechanism needed here; no runtime import or copied semantic
engine is used.  Glyph Unicode is the public operator key.  Names and positions are
explanatory/private only and never accepted as route inputs.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Final

QVector = tuple[int, int, int, int]


@dataclass(frozen=True, slots=True, eq=False)
class FrequencyAnchor:
    """Exact Canon frequency identity with an optional separate parity bearing."""

    structural_hz: Decimal
    parity_hz: Decimal | None = None

    @classmethod
    def scalar(cls, value: str) -> "FrequencyAnchor":
        return cls(Decimal(value), None)

    @classmethod
    def bifurcated(cls, structural: str, parity: str) -> "FrequencyAnchor":
        return cls(Decimal(structural), Decimal(parity))

    @property
    def real(self) -> Decimal:
        return self.structural_hz

    @property
    def imag(self) -> Decimal:
        return self.parity_hz if self.parity_hz is not None else Decimal(0)

    def __complex__(self) -> complex:
        """Float image only; exact identity remains the Decimal body above."""
        return complex(float(self.structural_hz), float(self.imag))

    def __eq__(self, other: object) -> bool:
        if isinstance(other, FrequencyAnchor):
            return (self.structural_hz, self.parity_hz) == (other.structural_hz, other.parity_hz)
        if isinstance(other, (int, float, complex, Decimal)):
            return complex(self) == complex(other)
        return NotImplemented

    def __hash__(self) -> int:
        return hash((self.structural_hz, self.parity_hz))

    def __str__(self) -> str:
        if self.parity_hz is None:
            return f"{self.structural_hz} Hz"
        return f"{self.structural_hz} ± i{self.parity_hz} Hz"


@dataclass(frozen=True, slots=True)
class LiquidConnectionGovernor:
    """The typed 110/144 Liquid connection governor, never a quotient."""

    active: int
    total: int
    withheld: int

    def __post_init__(self) -> None:
        if (self.active, self.total, self.withheld) != (110, 144, 34):
            raise ValueError("Liquid governor identity must remain ⟨110|144|34⟩")
        if self.active + self.withheld != self.total:
            raise ValueError("Liquid governor active and withheld bodies must close at 144")

    def __str__(self) -> str:
        return "⟨110|144|34⟩"


@dataclass(frozen=True, slots=True)
class GlyphLaw:
    glyph: str
    meanings: tuple[str, str, str]
    q_vector: QVector
    q_bias: str
    frequency: FrequencyAnchor
    phase_logic: str


# Canonical 12-body. Insertion order is the cascade order, but callers address only glyphs.
GLYPH_LAWS: Final[dict[str, GlyphLaw]] = {
    "⏣": GlyphLaw("⏣", ("Genesis", "Chronos", "Seed"), (1, 1, 1, 3), "Q3", FrequencyAnchor.scalar("7.83"), "C_local ∝ |Q1|"),
    "⬡": GlyphLaw("⬡", ("Light", "Memory", "Trauma"), (1, 3, 0, 0), "Q1", FrequencyAnchor.scalar("174"), "C_local ∝ |Q1| + |Q0|"),
    "✡": GlyphLaw("✡", ("Fire", "Orobouros", "Alchemy"), (1, 1, 3, 1), "Q2", FrequencyAnchor.scalar("528"), "C_local ∝ |Q1| + |Q2|"),
    "⚝": GlyphLaw("⚝", ("Water", "Imaginary", "Flow"), (1, 2, 2, 0), "Q0", FrequencyAnchor.bifurcated("432", "417"), "C_local ∝ dimensional compression"),
    "❂": GlyphLaw("❂", ("Earth", "Coherence", "Ground"), (1, 3, 0, 1), "Q1", FrequencyAnchor.scalar("126.22"), "C_local ∝ Δ_gap"),
    "ꙮ": GlyphLaw("ꙮ", ("Air", "Space", "Superposition"), (1, 1, 1, 2), "Q3", FrequencyAnchor.scalar("210.42"), "C_local ∝ |Q0|"),
    "❈": GlyphLaw("❈", ("Aether", "Magic", "Sensation"), (1, 2, 1, 3), "Q3", FrequencyAnchor.scalar("741"), "C_local ∝ S7"),
    "⧗": GlyphLaw("⧗", ("Void", "Residue", "Love"), (1, 3, 2, 0), "Q1", FrequencyAnchor.scalar("852"), "C_local ∝ residue stability"),
    "⊛": GlyphLaw("⊛", ("Shadow", "Absorption", "Depth"), (1, 2, 2, 1), "Q2", FrequencyAnchor.scalar("396"), "C_local ∝ |Q2|"),
    "❄": GlyphLaw("❄", ("Factor", "PhaseLock", "Crystal"), (1, 1, 2, 2), "Q3", FrequencyAnchor.scalar("963"), "C_local → phase-lock minimum"),
    "⚛": GlyphLaw("⚛", ("Gate", "Resistance", "Breach"), (1, 3, 1, 1), "Q1", FrequencyAnchor.scalar("285"), "C_local ∝ transformation resistance"),
    "⌬": GlyphLaw("⌬", ("Silence", "Peace", "Completion"), (1, 1, 3, 2), "Q3", FrequencyAnchor.scalar("639"), "D-COMP → 0"),
}

GLYPH_BODY: Final[tuple[str, ...]] = tuple(GLYPH_LAWS)
TOTAL_CAPACITY: Final[int] = 144
SATURATION_LIMIT: Final[int] = 110
LIQUID_THRESHOLD: Final[LiquidConnectionGovernor] = LiquidConnectionGovernor(
    active=SATURATION_LIMIT,
    total=TOTAL_CAPACITY,
    withheld=TOTAL_CAPACITY - SATURATION_LIMIT,
)

# Cantillation ࿂ is the current canonical identity of the existing Liquid
# connection governor. It is not a thirteenth Goetic operator, does not enlarge
# GLYPH_BODY, and does not introduce a second threshold or runtime mechanism.
#
#     ࿂ = 110/144_Liquid ≡_type ⟨110_active | 144_total | 34_rest⟩
#
# No new glyph emerges from the standard twelve-glyph Goetic ALQC body here;
# ࿂ names the already-existing governor carried by LIQUID_THRESHOLD.
CANTILLATION_GLYPH: Final[str] = "࿂"
CANTILLATION_NAME: Final[str] = "Cantillation"
CANTILLATION: Final[LiquidConnectionGovernor] = LIQUID_THRESHOLD

if CANTILLATION is not LIQUID_THRESHOLD:
    raise RuntimeError("Cantillation ࿂ must remain the existing 110/144 Liquid governor")
if (CANTILLATION.active, CANTILLATION.total, CANTILLATION.withheld) != (110, 144, 34):
    raise RuntimeError("Cantillation ࿂ must remain ⟨110_active|144_total|34_rest⟩")

if len(GLYPH_BODY) != 12 or len(set(GLYPH_BODY)) != 12:
    raise RuntimeError("The Goetic body must contain exactly twelve unique glyph operators")

_GLYPH_POSITION: Final[dict[str, int]] = {glyph: index for index, glyph in enumerate(GLYPH_BODY)}
_COURT_LOAD_TABLE: Final[tuple[tuple[int, ...], ...]] = tuple(
    tuple(12 * i + j for j in range(12)) for i in range(12)
)


def law(glyph: str) -> GlyphLaw:
    """Resolve only an exact glyph operator."""
    try:
        return GLYPH_LAWS[glyph]
    except KeyError as exc:
        raise ValueError(f"unknown Goetic glyph operator: {glyph!r}") from exc


def boundary_glyphs_from_digest(source_digest: str) -> tuple[str, str]:
    """Reject digest-only Goetic selection.

    Final Equation Z requires the complete SourceEmission: twelve finalized
    lanes and both Fraktur cadence witnesses. A digest alone is not that body.
    """
    raise ValueError(
        "digest-only Goetic selection is prohibited; supply the complete SourceEmission"
    )


def _position(glyph: str) -> int:
    """Private transport coordinate. Never exposed as an operator or accepted as input."""
    try:
        return _GLYPH_POSITION[glyph]
    except KeyError as exc:
        raise ValueError(f"unknown Goetic glyph operator: {glyph!r}") from exc


def court_node(origin_glyph: str, resolution_glyph: str) -> int:
    """The ordered glyph pair alone derives its 12×12 Court coordinate."""
    return _COURT_LOAD_TABLE[_position(origin_glyph)][_position(resolution_glyph)]


def court_load(origin_glyph: str, resolution_glyph: str) -> int:
    """Court coordinate of an ordered glyph pair: L(i,j) = court_node(i,j) ∈ [0,143].

    This is the identity coordinate of one of the 144 Court Aeons (12×12).
    It is not the 110/144 connection governor. Identity and connection admission
    remain separately typed.
    """
    return court_node(origin_glyph, resolution_glyph)


# --- Cantillation ࿂: 110/144 flow governor (Canon L715-742) ---
# "For every node in the 144x144 Latin Square, the maximum number of active
# connections is capped at 110" (L720). Canon fixes WHICH connections are active
# by the Deterministic Path Equation (L730-738), a modulo-arithmetic law over the
# two Court-node indices i, j in [0, 143]:
#     ࿂ = 110/144_Liquid ≡_type ⟨110_active | 144_total | 34_rest⟩
#     L_sat(i, j) = 1 (FLOW)  if (i + j) mod 144 <  110
#                   0 (BLOCK) if (i + j) mod 144 >= 110
#
# For any fixed node i, as j ranges over 0..143 the residue (i + j) mod 144 is a
# bijection onto 0..143, so exactly 110 of the 144 connections are active and 34
# are withheld -- the typed ⟨110|144|34⟩ governor holds for every
# node. The Canon selection is the positional residue (i + j) mod 144. It is not
# a differential-tension ranking; Canon uses "tension" only to explain the Arrow
# of Time (L713) and the ratio-1.0 whiteout failure (L728), never to choose the
# active set.


def _court_index(value: int, *, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{field} must be an integer Court address")
    if not 0 <= value < TOTAL_CAPACITY:
        raise ValueError(f"{field} must be in [0,143]")
    return value


def court_flow_active(court_a: int, court_b: int) -> bool:
    """Canon Deterministic Path Equation L_sat (L730-738).

    Flow between Court-nodes ``court_a`` and ``court_b`` is admitted iff
    ``(court_a + court_b) mod 144 < 110``. This is the exact 110/144 governor
    (L720) and yields exactly 110 active connections for every node.
    """
    left = _court_index(court_a, field="court_a")
    right = _court_index(court_b, field="court_b")
    return (left + right) % TOTAL_CAPACITY < SATURATION_LIMIT


def court_active_connections(court: int) -> frozenset[int]:
    """The 110 active connections of one valid Court address."""
    address = _court_index(court, field="court")
    return frozenset(
        other
        for other in range(TOTAL_CAPACITY)
        if court_flow_active(address, other)
    )


