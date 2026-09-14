"""Typed Complete Tripartite Cosmology witness for TardiSHA.

Region C08 expands the early Rebis articulation without replacing it:

    ♾ = iω₀                         untouched, non-traversible source
    ⛎ = T_⛎(iω₀)                    deformable carrier / return hull
    ᳀ = (Law + Will)√(iω₀)          complex breach branch
        ∥ ⚛ GateBreach
        ∥ ❄₉₆₃ WRITE_PHYS

The Locus never becomes a route, Court, moving state, or digest input operator.
Q∞ and Q⛤ are Parliament offices and remain outside the dynamic Q0–Q3 domain.
The 110/144 body is carried as the exact Liquid connection governor, never
retyped as a probabilistic ratio or as the identity of an ordinary Q-state.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from decimal import Decimal
import json
from fractions import Fraction
from math import isfinite, sqrt
from typing import Final, Sequence

from .alqc_digest import alqc_hexdigest, validate_digest_hex
from .aeon_layers import court_layer, derive_court_motion, derive_domus_motion, normalize_source_domain
from .canon import FrequencyAnchor, LiquidConnectionGovernor, LIQUID_THRESHOLD, SATURATION_LIMIT, TOTAL_CAPACITY, court_active_connections, law
from .court_registry import court_record
from .manifestation import C_BIO_IMAGE, C_BIO_SQUARED, close_boundary
from .qstate_glyphs import Q_STATES
from .source_emission import BETA, SourceEmission, Q5Fraction, resolve_court_bearing, validate_court_bearing_lineage
from .mirror_math import derive_goetics
from .trig import ExactDomusFrequency, exact_domus_frequency_from_bearing

TRIPARTITE_CYCLE_DOMAIN: Final[bytes] = b"TARDISHA:COMPLETE-TRIPARTITE-COSMOLOGY\x00"
ROOT_FREQUENCY_BODY: Final[Fraction] = Fraction(1847, 100)
AXIOMYR_BRANCH_COMPONENT_SQUARED: Final[Fraction] = ROOT_FREQUENCY_BODY / 2
LOCUS_GLYPH: Final[str] = "♾"
SHADOW_LOCUS_GLYPH: Final[str] = "⛎"
AXIOMYR_GLYPH: Final[str] = "᳀"
AXIOMYR_SEAT_GLYPH: Final[str] = "♌"
GATE_BREACH_GLYPH: Final[str] = "⚛"
WRITE_PHYS_GLYPH: Final[str] = "❄"
Q_INFINITY: Final[str] = "Q∞"
Q_MAGIC_VECTOR: Final[str] = "Q⛤"
DYNAMIC_Q_STATES: Final[tuple[str, str, str, str]] = Q_STATES


@dataclass(frozen=True, slots=True)
class TripartiteComponentWitness:
    identifier: str
    component: str
    body_glyph: str
    parliament_seat_glyph: str | None
    q_vector: tuple[int, int, int, int]
    equation: str
    role: str
    non_computable: bool
    non_traversible: bool
    deformable: bool
    carries_imaginary_root_without_crossing: bool
    actuator: bool


@dataclass(frozen=True, slots=True)
class AxiomyrAxisWitness:
    index: int
    axis: str
    operator: str
    role: str
    frequency: FrequencyAnchor | None
    branch_component_squared: Fraction | None
    direct_locus_traversal: bool


@dataclass(frozen=True, slots=True)
class LiquidThresholdWitness:
    governor_active_connections: int
    governor_court_capacity: int
    governor_withheld_connections: int
    governor_expression: str
    energetic_body: LiquidConnectionGovernor
    phi_body: Q5Fraction
    c_local_connection_body: Fraction
    threshold_met: bool
    manifestation_state: str
    governing_threshold_not_ratio: bool


@dataclass(frozen=True, slots=True)
class EmissionWitness:
    celestial: str
    emission: str
    vector_office: str
    nature_office: str
    identity: str
    operation: str


@dataclass(frozen=True, slots=True)
class ParliamentSeedWitness:
    index: str
    glyph: str
    identity: str
    source_state: str
    target_state: str
    target_court: str
    target_frequency: FrequencyAnchor
    opcode: str
    bias_office: str
    vector_office: str
    energy_displacement: float


@dataclass(frozen=True, slots=True)
class InvariableStateWitness:
    symbol: str
    name: str
    replaces: str
    office: str
    dynamic_q_state: bool


@dataclass(frozen=True, slots=True)
class SpiritSoulGoldWitness:
    number: int
    spirit_hz: Decimal
    soul: str
    operator_identity: str
    gold: str


COMPONENTS: Final[tuple[TripartiteComponentWitness, ...]] = (
    TripartiteComponentWitness(
        "☽", "Locus", LOCUS_GLYPH, None, (0, 0, 1, 1), "♾ = iω₀",
        "Impossible Root / Scream / Throne at (0,0,0)", True, True, False, False, False,
    ),
    TripartiteComponentWitness(
        "☾", "Shadow Locus", SHADOW_LOCUS_GLYPH, None, (2, 2, 3, 3), "⛎ = T_⛎(iω₀)",
        "Translation Matrix / Throat / Hull", False, False, True, True, False,
    ),
    TripartiteComponentWitness(
        AXIOMYR_GLYPH, "Axiomyr", AXIOMYR_GLYPH, AXIOMYR_SEAT_GLYPH, (1, 1, 3, 3),
        "᳀ = (Law + Will)√(iω₀)", "Witch-Hand / Boundarywalker / Dynamic Will", False,
        False, False, True, True,
    ),
)

# Each Axiomyr branch component is carried by its exact squared body.
if AXIOMYR_BRANCH_COMPONENT_SQUARED != Fraction(1847, 200):
    raise RuntimeError("Axiomyr branch square escaped its exact root-frequency body")
AXIOMYR_AXES: Final[tuple[AxiomyrAxisWitness, ...]] = (
    AxiomyrAxisWitness(1, "Imagination", "√i18.47", "complex branch-state", None, AXIOMYR_BRANCH_COMPONENT_SQUARED, False),
    AxiomyrAxisWitness(2, "Gate Breach", GATE_BREACH_GLYPH, "threshold without Locus traversal", law(GATE_BREACH_GLYPH).frequency, None, False),
    AxiomyrAxisWitness(3, "Inscription", WRITE_PHYS_GLYPH, "WRITE_PHYS through Resonance Court", law(WRITE_PHYS_GLYPH).frequency, None, False),
)

EMISSIONS: Final[tuple[EmissionWitness, ...]] = (
    EmissionWitness("☿", "Ponder", "∞", "⛤", "Sakshi", "Q3 recursion and simulation logic"),
    EmissionWitness("♂", "Will", "∞", "⛤", "Vegvisir", "VECTORS_TO path"),
    EmissionWitness("♀", "Feel", "∞", "⛤", "Logos", "frequency synchronization"),
    EmissionWitness("♃", "Speak", "∞", "⛤", "Philosophia Perennis", "Axiomyr name/rule inscription"),
    EmissionWitness("♄", "Believe", "∞", "⛤", "Amidah", "seal true and invariance lock"),
    EmissionWitness("⛢", "Act", "∞", "⛤", "Shekhinah", "MATCH-SET manifold displacement"),
    EmissionWitness("♆", "Know", "∞", "⛤", "Hathor Akashic", "non-entropic archive return"),
    EmissionWitness("♇", "Ascend", "∞", "⛤", "Janus", "route friction and manage M.Gap"),
    EmissionWitness("☽☉☾", "Regia", "∞", "⛤", "Asīm Serenitatis", "proclaim Ex-Nihilo identity"),
)

_PARLIAMENT_ROWS: Final[tuple[tuple[str, str, str, str, str, str], ...]] = (
    ("P13-D1", "♈", "Akasha", "Lived", "Eternal", "⬡", "WRITE_ONLY"),
    ("P13-D2", "♉", "Caduceus", "Law", "Residue", "⧗", "AUTH_CHECK"),
    ("P13-D3", "♊", "Veritas", "Mask", "Bone", "❂", "DECRYPT"),
    ("P13-D4", "♋", "Phren", "Void", "Vector", "⌬", "VECTOR_TO"),
    ("P13-D5", "♑", "Daimon", "Stasis", "Pulse", "⏣", "ENTROPY_0"),
    ("P13-D6", "♍", "Aikyam", "Chaos", "Phase", "⚝", "SUPERPOS"),
    ("P13-D7", "♎", "Melos", "Static", "Fluid", "❈", "SIGNAL_IO"),
    ("P13-D8", "♏", "Da'ath", "Noise", "Null", "⊛", "SINK_STATE"),
    ("P13-D9", "♐", "Akaven", "State", "Trans", "⚛", "GUARD_NET"),
    ("P13-D10", "♌", "Axiomyr", "Will", "Law", "❄", "WRITE_PHYS"),
    ("P13-D11", "♒", "Nyx", "Time", "Motion", "✡", "NEXT_FRAME"),
    ("P13-D12", "♓", "Zaine", "Here", "There", "ꙮ", "BRIDGE"),
)
PARLIAMENT: Final[tuple[ParliamentSeedWitness, ...]] = tuple(
    ParliamentSeedWitness(
        index, glyph, identity, source, target, court, law(court).frequency, opcode,
        Q_INFINITY, Q_MAGIC_VECTOR, 0.0,
    )
    for index, glyph, identity, source, target, court, opcode in _PARLIAMENT_ROWS
)

INVARIABLE_STATES: Final[tuple[InvariableStateWitness, ...]] = (
    InvariableStateWitness(
        Q_INFINITY, "Isotropic Constant", "standard Bias",
        "equally infinite in every direction; anchors Parliament stillness", False,
    ),
    InvariableStateWitness(
        Q_MAGIC_VECTOR, "Magic Vector", "standard Vector",
        "always directed toward the Central Locus ♾", False,
    ),
)

SPIRIT_SOUL_GOLD: Final[tuple[SpiritSoulGoldWitness, ...]] = (
    SpiritSoulGoldWitness(1, Decimal("174"), "The Anaesthetic", "Melos", "Removes Pain → Foundation"),
    SpiritSoulGoldWitness(2, Decimal("285"), "The Weaver", "Caduceus", "Heals Tissue → Restoration"),
    SpiritSoulGoldWitness(3, Decimal("396"), "The Liberator", "Nyx", "Burns Fear → Propulsion (Q2)"),
    SpiritSoulGoldWitness(4, Decimal("417"), "The Shifter", "Akaven", "Undoes Trauma → Change"),
    SpiritSoulGoldWitness(5, Decimal("432"), "The Veritās", "Veritas", "Aligns Geometry → Natural Order"),
    SpiritSoulGoldWitness(6, Decimal("528"), "The Repairman", "Aikyam", "Repairs DNA → Miracle"),
    SpiritSoulGoldWitness(7, Decimal("639"), "The Connector", "Akasha", "Heals Relationships → Unity"),
    SpiritSoulGoldWitness(8, Decimal("741"), "The Solver", SHADOW_LOCUS_GLYPH, "Cleans Toxins → Expression"),
    SpiritSoulGoldWitness(9, Decimal("852"), "The Awakener", LOCUS_GLYPH, "Awakens Intuition → Return to Order"),
    SpiritSoulGoldWitness(10, Decimal("963"), "The Numinous", "Zaine", "Connects to Source → Light (Q1)"),
    SpiritSoulGoldWitness(11, Decimal("110"), "The Liquid State", "Liquid", "Induces Trance → Plasticity"),
    SpiritSoulGoldWitness(12, Decimal("111"), "The Bridge", "Bridge", "Cell Rejuvenation → Beta-Endorphins"),
    SpiritSoulGoldWitness(13, Decimal("7.83"), "The Ground", "YHMH", "Earth Resonance → Stability"),
    SpiritSoulGoldWitness(14, Decimal("144"), "The Grid", "Cubic Lattice", "Structure"),
    SpiritSoulGoldWitness(15, Decimal("0"), "The Void", "Da'ath", "Null State → Potential"),
)


@dataclass(frozen=True, slots=True)
class TripartiteWitness:
    carrier_frequency_hz: Fraction
    carrier_expression: str
    components: tuple[TripartiteComponentWitness, ...]
    axiomyr_branch_component_squared: Fraction
    axiomyr_branch_angle_degrees: int
    axiomyr_axes: tuple[AxiomyrAxisWitness, ...]
    emissions: tuple[EmissionWitness, ...]
    parliament: tuple[ParliamentSeedWitness, ...]
    invariable_states: tuple[InvariableStateWitness, ...]
    dynamic_q_states: tuple[str, str, str, str]
    spirit_soul_gold: tuple[SpiritSoulGoldWitness, ...]

    source_digest: str
    source_size: int
    source_domain: str
    nonce: int
    governing_court_address: int
    alternating_court_address: int
    governing_court_phase_digest: str
    alternating_court_bearing: tuple[int, ...]
    domus_frequency: ExactDomusFrequency
    domus_body_commitment: str
    trig_cycle_digest: str

    liquid_threshold: LiquidThresholdWitness
    c_bio: float
    c_bio_squared: Fraction
    q3_recursion_gain: float
    final_shadow_parity: str
    returned_through_shadow_locus: bool
    shadow_carrier_witnessed: bool
    gate_breach_witnessed: bool
    write_phys_witnessed: bool
    q2_to_q3_propulsion_witnessed: bool
    court_rooted: bool
    derives_through_courts_only: bool
    direct_locus_traversal: bool
    locus_unchanged: bool
    invariable_states_outside_dynamic_q_domain: bool
    axiomyr_actuator: bool
    axiomyr_constitutive_revivocus: bool
    derivation: str
    cycle_digest: str

    @property
    def locus(self) -> str:
        return LOCUS_GLYPH

    @property
    def shadow_locus(self) -> str:
        return SHADOW_LOCUS_GLYPH

    @property
    def axiomyr(self) -> str:
        return AXIOMYR_GLYPH

    @property
    def shared_root_frequency(self) -> Fraction:
        return self.carrier_frequency_hz

    @property
    def axiomyr_branch(self) -> complex:
        component = sqrt(float(self.axiomyr_branch_component_squared))
        return complex(component, component)

    @property
    def locus_non_traversable(self) -> bool:
        return self.locus_unchanged and not self.direct_locus_traversal

    @property
    def shadow_locus_deformable(self) -> bool:
        return COMPONENTS[1].deformable

    @property
    def shadow_locus_return_path(self) -> bool:
        return self.shadow_carrier_witnessed

    def as_dict(self) -> dict[str, object]:
        return _display(asdict(self))


def _canonical(value: object) -> object:
    if isinstance(value, Fraction):
        return {"fraction": [value.numerator, value.denominator]}
    if isinstance(value, Decimal):
        return {"decimal": str(value)}
    if isinstance(value, complex):
        return {"real": value.real.hex(), "imag": value.imag.hex()}
    if isinstance(value, float):
        return {"float": value.hex()}
    if isinstance(value, tuple):
        return [_canonical(item) for item in value]
    if isinstance(value, list):
        return [_canonical(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _canonical(item) for key, item in value.items()}
    return value


def _display(value: object) -> object:
    if isinstance(value, Fraction):
        return f"{value.numerator}/{value.denominator}"
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, complex):
        return str(value)
    if isinstance(value, tuple):
        return [_display(item) for item in value]
    if isinstance(value, list):
        return [_display(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _display(item) for key, item in value.items()}
    return value


def _payload(witness: TripartiteWitness) -> bytes:
    body = asdict(witness)
    body.pop("cycle_digest", None)
    return json.dumps(
        _canonical(body), ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def _digest(value: str, field: str) -> str:
    return validate_digest_hex(value, field=field)


def derive_liquid_threshold(
    *, active_connections: int, court_capacity: int, withheld_connections: int
) -> LiquidThresholdWitness:
    for field, value in (
        ("active_connections", active_connections),
        ("court_capacity", court_capacity),
        ("withheld_connections", withheld_connections),
    ):
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise ValueError(f"{field} must be a non-negative integer")
    if court_capacity != TOTAL_CAPACITY:
        raise ValueError("Liquid threshold is defined on the 144-Court capacity")
    if active_connections + withheld_connections != court_capacity:
        raise ValueError("active and withheld connections must partition the Court capacity")
    connection_body = Fraction(active_connections, court_capacity)
    if active_connections == TOTAL_CAPACITY:
        state = "WHITEOUT"
        threshold_met = False
    elif active_connections == SATURATION_LIMIT and withheld_connections == TOTAL_CAPACITY - SATURATION_LIMIT:
        state = "EVENT"
        threshold_met = True
    elif active_connections < SATURATION_LIMIT:
        state = "Potential"
        threshold_met = False
    else:
        state = "TRANSITION_BAND"
        threshold_met = False
    return LiquidThresholdWitness(
        governor_active_connections=active_connections,
        governor_court_capacity=court_capacity,
        governor_withheld_connections=withheld_connections,
        governor_expression=f"{active_connections}/{court_capacity}",
        energetic_body=LIQUID_THRESHOLD,
        phi_body=Q5Fraction(BETA.a, BETA.b, 1),
        c_local_connection_body=connection_body,
        threshold_met=threshold_met,
        manifestation_state=state,
        governing_threshold_not_ratio=True,
    )


def derive_tripartite_witness(
    *,
    source_digest: str,
    source_size: int,
    source_domain: str | bytes,
    nonce: int,
    governing_court_address: int,
    alternating_court_address: int,
    governing_court_phase_digest: str,
    alternating_court_bearing: Sequence[int],
    domus_frequency: complex,
    domus_body_commitment: str,
    trig_cycle_digest: str,
    active_connections: int,
    court_capacity: int,
    withheld_connections: int,
    c_bio: float,
    c_bio_squared: Fraction = C_BIO_SQUARED,
    q3_recursion_gain: float,
    final_shadow_parity: str,
    returned_through_shadow_locus: bool,
    gate_breach_witnessed: bool,
    write_phys_witnessed: bool,
    derives_through_courts_only: bool,
) -> TripartiteWitness:
    """Derive C08 from exact source, Court, Liquid, and return bodies."""
    digest = _digest(source_digest, "source_digest")
    governing_phase = _digest(governing_court_phase_digest, "governing_court_phase_digest")
    bearing_lineage = validate_court_bearing_lineage(alternating_court_bearing)
    domus_commitment = _digest(domus_body_commitment, "domus_body_commitment")
    trig_digest = _digest(trig_cycle_digest, "trig_cycle_digest")
    domain = normalize_source_domain(source_domain).decode("ascii").rstrip("\x00")

    if isinstance(source_size, bool) or not isinstance(source_size, int) or source_size < 0:
        raise ValueError("source_size must be a non-negative integer")
    if isinstance(nonce, bool) or not isinstance(nonce, int) or not 0 <= nonce < 2**64:
        raise ValueError("nonce must be an integer in [0,2^64)")
    for field, address in (("governing_court_address", governing_court_address), ("alternating_court_address", alternating_court_address)):
        if isinstance(address, bool) or not isinstance(address, int) or not 0 <= address < TOTAL_CAPACITY:
            raise ValueError(f"{field} must be an exact integer in [0,143]")
    if bearing_lineage[0] != alternating_court_address:
        raise ValueError("alternating Court bearing address does not match Court D")
    for field, value in (
        ("returned_through_shadow_locus", returned_through_shadow_locus),
        ("gate_breach_witnessed", gate_breach_witnessed),
        ("write_phys_witnessed", write_phys_witnessed),
        ("derives_through_courts_only", derives_through_courts_only),
    ):
        if type(value) is not bool:
            raise TypeError(f"{field} must be one exact Boolean witness")
    if type(final_shadow_parity) is not str:
        raise TypeError("final_shadow_parity must be one exact string")
    if type(domus_frequency) is not complex:
        raise TypeError("domus_frequency must be the exact complex image supplied by Domus")
    exact_frequency = exact_domus_frequency_from_bearing(alternating_court_address, bearing_lineage)
    if domus_frequency != exact_frequency.image:
        raise ValueError("domus_frequency image does not return from its exact Court anchor and Q(√5) breath")
    if type(c_bio) is not float or type(q3_recursion_gain) is not float:
        raise TypeError("c_bio and q3_recursion_gain must be exact float images")
    if not isfinite(c_bio) or c_bio <= 0.0 or not isfinite(q3_recursion_gain) or q3_recursion_gain < 0.0:
        raise ValueError("c_bio must be positive and Q3 gain must be finite and non-negative")
    if type(c_bio_squared) is not Fraction or c_bio_squared != C_BIO_SQUARED:
        raise ValueError("Tripartite C_bio squared must be the exact Fraction 61009/44")
    if c_bio.hex() != C_BIO_IMAGE.hex():
        raise ValueError("Tripartite C_bio image does not match its exact squared body")

    gate = law(GATE_BREACH_GLYPH)
    resonance = law(WRITE_PHYS_GLYPH)
    if gate.frequency != AXIOMYR_AXES[1].frequency or resonance.frequency != AXIOMYR_AXES[2].frequency:
        raise RuntimeError("Axiomyr breach/inscription Court laws have changed")
    if (active_connections, court_capacity, withheld_connections) != (SATURATION_LIMIT, TOTAL_CAPACITY, TOTAL_CAPACITY - SATURATION_LIMIT):
        raise ValueError("TardiSHA Domus must preserve exact 110 active / 34 withheld / 144 capacity")
    threshold = derive_liquid_threshold(
        active_connections=active_connections,
        court_capacity=court_capacity,
        withheld_connections=withheld_connections,
    )
    court_rooted = derives_through_courts_only
    shadow_carrier = returned_through_shadow_locus and court_rooted
    gate_witness = gate_breach_witnessed and gate.frequency == AXIOMYR_AXES[1].frequency
    write_witness = write_phys_witnessed and resonance.frequency == AXIOMYR_AXES[2].frequency
    propulsion = final_shadow_parity == "Q3" and q3_recursion_gain > 0.0 and shadow_carrier
    invariable_separate = (
        all(not state.dynamic_q_state for state in INVARIABLE_STATES)
        and all(state.symbol not in DYNAMIC_Q_STATES for state in INVARIABLE_STATES)
    )
    derivation = (
        "♾=iω₀ remains non-traversible; ⛎=T_⛎(iω₀) carries the impossible root; "
        "᳀=(Law+Will)√(iω₀) ∥ ⚛ GateBreach ∥ ❄ WRITE_PHYS; "
        f"Λ_Liquid=110/144 yields {threshold.manifestation_state}; "
        "Q∞ and Q⛤ remain Parliament offices outside Q0–Q3."
    )

    provisional = TripartiteWitness(
        carrier_frequency_hz=ROOT_FREQUENCY_BODY,
        carrier_expression="ω₀ = 18.47 Hz",
        components=COMPONENTS,
        axiomyr_branch_component_squared=AXIOMYR_BRANCH_COMPONENT_SQUARED,
        axiomyr_branch_angle_degrees=45,
        axiomyr_axes=AXIOMYR_AXES,
        emissions=EMISSIONS,
        parliament=PARLIAMENT,
        invariable_states=INVARIABLE_STATES,
        dynamic_q_states=DYNAMIC_Q_STATES,
        spirit_soul_gold=SPIRIT_SOUL_GOLD,
        source_digest=digest,
        source_size=source_size,
        source_domain=domain,
        nonce=nonce,
        governing_court_address=governing_court_address,
        alternating_court_address=alternating_court_address,
        governing_court_phase_digest=governing_phase,
        alternating_court_bearing=bearing_lineage,
        domus_frequency=exact_frequency,
        domus_body_commitment=domus_commitment,
        trig_cycle_digest=trig_digest,
        liquid_threshold=threshold,
        c_bio=c_bio,
        c_bio_squared=c_bio_squared,
        q3_recursion_gain=q3_recursion_gain,
        final_shadow_parity=final_shadow_parity,
        returned_through_shadow_locus=returned_through_shadow_locus,
        shadow_carrier_witnessed=shadow_carrier,
        gate_breach_witnessed=gate_witness,
        write_phys_witnessed=write_witness,
        q2_to_q3_propulsion_witnessed=propulsion,
        court_rooted=court_rooted,
        derives_through_courts_only=derives_through_courts_only,
        direct_locus_traversal=False,
        locus_unchanged=True,
        invariable_states_outside_dynamic_q_domain=invariable_separate,
        axiomyr_actuator=True,
        axiomyr_constitutive_revivocus=True,
        derivation=derivation,
        cycle_digest="0" * 64,
    )
    return replace(provisional, cycle_digest=alqc_hexdigest(_payload(provisional), domain=TRIPARTITE_CYCLE_DOMAIN))


def verify_tripartite_witness(witness: TripartiteWitness, emission: SourceEmission) -> bool:
    """Rederive C08 from the complete source emission and exact Court bodies."""
    try:
        if not isinstance(emission, SourceEmission):
            return False
        domain = normalize_source_domain(emission.source_domain).decode("ascii").rstrip("\x00")
        if (
            witness.source_digest != emission.source_digest
            or witness.source_size != emission.source_size
            or witness.source_domain != domain
        ):
            return False
        source_derivation = derive_goetics(emission)
        governing = court_record(source_derivation.court_address)
        alternating_bearing = resolve_court_bearing(emission)
        alternating = alternating_bearing.court
        if (
            witness.governing_court_address != governing.address
            or witness.alternating_court_address != alternating.address
        ):
            return False
        governing_layer = court_layer(governing)
        alternating_layer = court_layer(alternating)
        governing_motion = derive_court_motion(
            governing,
            source_digest=emission.source_digest,
            source_size=emission.source_size,
            source_domain=emission.source_domain,
            nonce=witness.nonce,
        )
        domus_motion = derive_domus_motion(
            governing_layer, alternating_layer, bearing=alternating_bearing
        )
        manifestation = close_boundary(
            governing_layer.governing_goetic.q_vector,
            alternating_layer.governing_goetic.q_vector,
            court=governing.address,
        )
        active = len(court_active_connections(governing.address))
        expected = derive_tripartite_witness(
            source_digest=emission.source_digest,
            source_size=emission.source_size,
            source_domain=emission.source_domain,
            nonce=witness.nonce,
            governing_court_address=governing.address,
            alternating_court_address=alternating.address,
            governing_court_phase_digest=governing_motion.phase.digest,
            alternating_court_bearing=alternating_bearing.lineage,
            domus_frequency=domus_motion.current_frequency,
            domus_body_commitment=witness.domus_body_commitment,
            trig_cycle_digest=witness.trig_cycle_digest,
            active_connections=active,
            court_capacity=TOTAL_CAPACITY,
            withheld_connections=TOTAL_CAPACITY - active,
            c_bio=C_BIO_IMAGE,
            c_bio_squared=C_BIO_SQUARED,
            q3_recursion_gain=manifestation.dcomp.q3_recursion_gain,
            final_shadow_parity=manifestation.ennead.final_parity,
            returned_through_shadow_locus=True,
            gate_breach_witnessed=(law(GATE_BREACH_GLYPH).frequency == AXIOMYR_AXES[1].frequency),
            write_phys_witnessed=(
                law(WRITE_PHYS_GLYPH).frequency == AXIOMYR_AXES[2].frequency
                and manifestation.ennead.strikes[-1].phase_locked
            ),
            derives_through_courts_only=domus_motion.derives_through_courts_only,
        )
    except (AttributeError, IndexError, TypeError, ValueError, RuntimeError):
        return False
    return witness == expected
