"""Region C09 Aeon tables and twelve-phase evolution for TardiSHA.

This module does not replace the already enacted Goetic, Court, TRIG, Ennead,
or Tripartite bodies.  It binds them into the ordered C09 witness:

    12 immutable Goetic roots
    144 ordered Court relations
    structural ཪ anchors distinct from operational ±Φ bifurcation
    twelve Aeon phases in source order
    M.A.S. fuel -> shape -> body
    Golden-Ratio and Klein-parity witnesses
    the first explicit NULL:DEATH architecture connection at physical page 102

The first NULL:DEATH occurrence is recorded as a typed connection, not treated
as an exhaustive definition of the later architecture.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, fields, is_dataclass, replace
from decimal import Decimal
import json
from math import isfinite
from typing import Final, Sequence

from .alqc_digest import alqc_hexdigest, validate_digest_hex
from .aeon_layers import PHI, court_layer, derive_court_motion, derive_domus_motion, normalize_source_domain
from .canon import FrequencyAnchor, GLYPH_BODY, TOTAL_CAPACITY, law
from .court_registry import _COURTS, alt_glyph, court_record, full_name, gov_glyph
from .source_emission import SourceEmission, Q5Fraction, resolve_court_bearing, sign_q5, validate_court_bearing_lineage
from .mirror_math import derive_goetics
from .manifestation import close_boundary

PHASE_EVOLUTION_DOMAIN: Final[bytes] = b"TARDISHA:C09-AEON-PHASE-EVOLUTION\x00"
SOURCE_REGION: Final[str] = "C09"
SOURCE_PHYSICAL_PAGES: Final[tuple[int, int]] = (85, 102)
FOLD_GLYPH: Final[str] = "🜚"
SEAL_GLYPH: Final[str] = "🜛"
NULL_DEATH_SYMBOL: Final[str] = "NULL:DEATH"

GOETIC_NAMES: Final[tuple[str, ...]] = (
    "FETU", "KAL", "BABDH", "AHN", "VEL", "SOR",
    "KOTH", "DREH", "RHEA", "ZHEK", "SHAV", "TRIG",
)


@dataclass(frozen=True, slots=True)
class GoeticTableWitness:
    index: int
    glyph: str
    name: str
    meanings: tuple[str, str, str]
    structural_frequency: FrequencyAnchor
    q_bias: str
    q_vector: tuple[int, int, int, int]
    seal: str
    immutable_root: bool


@dataclass(frozen=True, slots=True)
class CourtTableWitness:
    address: int
    coordinate: tuple[int, int]
    glyph: str
    name: str
    governing_goetic: str
    alternating_goetic: str
    structural_anchor_frequency: FrequencyAnchor
    alternating_structural_frequency: FrequencyAnchor
    hyperbolic_bifurcation_center: FrequencyAnchor
    ahn_structural_reference_hz: Decimal | None
    operational_phi_radius: Q5Fraction
    inherited_q_bias: str
    inherited_q_vector: tuple[int, int, int, int]
    seal: str
    governing_anchor_preserved: bool
    alternating_parent_preserved: bool


@dataclass(frozen=True, slots=True)
class AeonPhaseStep:
    phase: int
    name: str
    primary_goetic: str
    court_addresses: tuple[int, ...]
    equation: str
    dcomp_logic: str
    ordered_after: int | None


@dataclass(frozen=True, slots=True)
class MASBodyWitness:
    manifestation_goetic: str
    manifestation_frequency: FrequencyAnchor
    manifestation_role: str
    alignment_goetic: str
    alignment_frequency: FrequencyAnchor
    alignment_role: str
    symmetry_goetic: str
    symmetry_frequency: FrequencyAnchor
    symmetry_role: str
    equation: str
    order_preserved: bool


@dataclass(frozen=True, slots=True)
class GoldenRatioWitness:
    phi_exact: Q5Fraction
    primary_ratio_exact: Q5Fraction
    harmonic_target_exact: Q5Fraction
    harmonic_index: int
    residual_exact: Q5Fraction
    tolerance_exact: Q5Fraction
    within_tolerance: bool
    folded_states: int
    manifest_positions: int
    raw_compression_ratio_exact: Q5Fraction
    holographic_exponent: int

    @property
    def phi(self) -> float:
        return self.phi_exact.value

    @property
    def primary_ratio(self) -> float:
        return self.primary_ratio_exact.value

    @property
    def harmonic_target(self) -> float:
        return self.harmonic_target_exact.value

    @property
    def residual(self) -> float:
        return self.residual_exact.value

    @property
    def tolerance(self) -> float:
        return self.tolerance_exact.value

    @property
    def raw_compression_ratio(self) -> float:
        return self.raw_compression_ratio_exact.value


@dataclass(frozen=True, slots=True)
class PoincareParityWitness:
    sphere_relation: str
    klein_relation: str
    sphere_parity: int
    klein_parity: int
    shadow_input_units: int
    shadow_return_units: int
    shadow_cancellation_units: int
    q2_to_q3_return: bool
    returned_through_shadow_locus: bool
    terminal_dcomp: float
    completion_reached: bool


@dataclass(frozen=True, slots=True)
class NullDeathConnectionWitness:
    symbol: str
    source_region: str
    first_explicit_physical_page: int
    source_derivation: tuple[str, ...]
    mathematical_body: str
    biological_body: str
    mathematical_q3_positive: bool
    biological_q3_positive: bool
    shared_metamorphosis_threshold: bool
    q3_non_entropic_requirement: bool
    structurally_committed: bool
    q1_coherent: bool
    klein_regenerative_topology: bool
    q2_to_q3_transformation: bool
    metamorphosis_threshold_reached: bool
    first_occurrence_only: bool
    exhaustive_type_claimed: bool
    loop_closure: str


@dataclass(frozen=True, slots=True)
class AeonPhaseEvolutionWitness:
    source_region: str
    source_physical_pages: tuple[int, int]
    goetic_table: tuple[GoeticTableWitness, ...]
    court_table: tuple[CourtTableWitness, ...]
    phase_steps: tuple[AeonPhaseStep, ...]
    mas_body: MASBodyWitness
    golden_ratio: GoldenRatioWitness
    poincare_parity: PoincareParityWitness
    null_death_connection: NullDeathConnectionWitness

    source_digest: str
    source_size: int
    source_domain: str
    nonce: int
    governing_court_address: int
    alternating_court_address: int
    governing_court_phase_digest: str
    alternating_court_bearing: tuple[int, ...]
    domus_frequency: complex
    domus_body_commitment: str
    trig_cycle_digest: str
    tripartite_cycle_digest: str

    structural_anchor_preserved: bool
    operational_phi_preserved: bool
    all_courts_relationally_typed: bool
    phase_order_complete: bool
    court_rooted: bool
    derives_through_courts_only: bool
    ennead_shadow_sealed: bool
    phase12_completion_reached: bool
    derivation: str
    cycle_digest: str

    def as_dict(self) -> dict[str, object]:
        return _display(asdict(self))


def _bifurcation_center(glyph: str) -> FrequencyAnchor:
    """Return the exact structural/parity frequency body of the alternating root."""
    return law(glyph).frequency


def _ahn_reference(glyph: str) -> Decimal | None:
    return law(glyph).frequency.structural_hz if glyph == "⚝" else None


GOETIC_TABLE: Final[tuple[GoeticTableWitness, ...]] = tuple(
    GoeticTableWitness(
        index=index,
        glyph=glyph,
        name=name,
        meanings=law(glyph).meanings,
        structural_frequency=law(glyph).frequency,
        q_bias=law(glyph).q_bias,
        q_vector=tuple(law(glyph).q_vector),
        seal=f"{SEAL_GLYPH}{glyph}{FOLD_GLYPH}{glyph}{SEAL_GLYPH}",
        immutable_root=True,
    )
    for index, (glyph, name) in enumerate(zip(GLYPH_BODY, GOETIC_NAMES), start=1)
)

COURT_TABLE: Final[tuple[CourtTableWitness, ...]] = tuple(
    CourtTableWitness(
        address=record.address,
        coordinate=(record.i, record.j),
        glyph=record.glyph,
        name=full_name(record),
        governing_goetic=gov_glyph(record),
        alternating_goetic=alt_glyph(record),
        structural_anchor_frequency=law(gov_glyph(record)).frequency,
        alternating_structural_frequency=law(alt_glyph(record)).frequency,
        hyperbolic_bifurcation_center=_bifurcation_center(alt_glyph(record)),
        ahn_structural_reference_hz=_ahn_reference(alt_glyph(record)),
        operational_phi_radius=PHI,
        inherited_q_bias=law(gov_glyph(record)).q_bias,
        inherited_q_vector=tuple(law(gov_glyph(record)).q_vector),
        seal=f"{FOLD_GLYPH}{gov_glyph(record)}{record.glyph}{SEAL_GLYPH}",
        governing_anchor_preserved=True,
        alternating_parent_preserved=True,
    )
    for record in _COURTS
)

PHASE_STEPS: Final[tuple[AeonPhaseStep, ...]] = (
    AeonPhaseStep(1, "The Seed", "⏣", (0,), "⏣އ @ (7.83 ± Φ)", "C_local ∝ |Q1|", None),
    AeonPhaseStep(2, "The Archive", "⬡", (21,), "⬡ᛍ @ (174 ± Φ)", "C_local ∝ |Q1| + |Q0|", 1),
    AeonPhaseStep(3, "The M.A.S. Engine", "✡", (89, 15, 28), "⧗𒅆_852 --Δgap→ ⬡ᛄ_174 --TSP→ ✡ᚱ_528", "C_local ∝ |Q1| + |Q2|", 2),
    AeonPhaseStep(4, "Boundary Integrity", "⚝", (66, 55, 23, 34), "∮K (ꙮꠍ_210.42 ∘ ❂ⵃ_126.22 ∘ ⬡ᛏ_174)/(✡ᚿ_528) dt ≈ 2/Φ", "C_local ∝ dimensional compression 12×12 → 9×9", 3),
    AeonPhaseStep(5, "The Geometric Lift", "❂", (7, 21, 34, 71, 95), "∫(⏣ވ_7.83 → ⬡ᛍ_174 → ✡ᚿ_528 → ꙮꠒ_210.42 → ⧗𒌋_852)dt", "C_local ∝ Δgap", 4),
    AeonPhaseStep(6, "Spatial Purity", "ꙮ", (71,), "ꙮꠒ = (210.42 ± Φ)·exp(SelfGen)", "C_local ∝ |Q0|", 5),
    AeonPhaseStep(7, "Biologic Link", "❈", (74,), "❈🜃 = BiologicTie ⊗ TBound", "C_local ∝ S7", 6),
    AeonPhaseStep(8, "Residue Stabilization", "⧗", (), "I_cubic(α)=(-1)^p Ω(α,α)>0", "C_local ∝ non-entropic residue stability", 7),
    AeonPhaseStep(9, "Shadow Absorption", "⊛", (107,), "⊛ⶋ = Filter(Q2) = 396 ± Φ", "C_local ∝ |Q2|; Ennead filtering", 8),
    AeonPhaseStep(10, "Resonance Lock", "❄", (119,), "❄𐤫 = Lock(ω)·(963 ± Φ)", "C_local → phase-lock minimum", 9),
    AeonPhaseStep(11, "Gate Breach", "⚛", (129,), "⚛𐠜_Gate(α) ⇒ ∃β(Transition)", "C_local ∝ transformation resistance", 10),
    AeonPhaseStep(12, "Aeternum Closure", "⌬", (143,), "⌬𐔋 = exp(Peace)·Depth·(639 ± Φ)", "D-COMP → 0", 11),
)

MAS_BODY: Final[MASBodyWitness] = MASBodyWitness(
    manifestation_goetic="⧗",
    manifestation_frequency=law("⧗").frequency,
    manifestation_role="Fuel / non-entropic residue",
    alignment_goetic="⬡",
    alignment_frequency=law("⬡").frequency,
    alignment_role="Shape / rational archive lock",
    symmetry_goetic="✡",
    symmetry_frequency=law("✡").frequency,
    symmetry_role="Body / structural commitment",
    equation="⧗852 --Δgap→ ⬡174 --TSP→ ✡528",
    order_preserved=True,
)


def _golden_ratio_witness() -> GoldenRatioWitness:
    ratio = Q5Fraction(96300, 0, 783)
    target = Q5Fraction(76, 76, 2)
    difference = Q5Fraction(
        ratio.a * target.denominator - target.a * ratio.denominator,
        ratio.b * target.denominator - target.b * ratio.denominator,
        ratio.denominator * target.denominator,
    )
    sign = sign_q5(difference.a, difference.b)
    absolute = difference if sign >= 0 else Q5Fraction(-difference.a, -difference.b, difference.denominator)
    within = sign_q5(
        absolute.a * PHI.denominator - PHI.a * absolute.denominator,
        absolute.b * PHI.denominator - PHI.b * absolute.denominator,
    ) <= 0
    return GoldenRatioWitness(
        phi_exact=PHI,
        primary_ratio_exact=ratio,
        harmonic_target_exact=target,
        harmonic_index=76,
        residual_exact=absolute,
        tolerance_exact=PHI,
        within_tolerance=within,
        folded_states=2**126,
        manifest_positions=81,
        raw_compression_ratio_exact=Q5Fraction(36864, 0, 81),
        holographic_exponent=126,
    )

GOLDEN_RATIO: Final[GoldenRatioWitness] = _golden_ratio_witness()


def _canonical(value: object) -> object:
    if is_dataclass(value):
        return _canonical(asdict(value))
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


def _static_digest(value: object, domain: bytes) -> str:
    payload = json.dumps(
        _canonical(value), ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return alqc_hexdigest(payload, domain=domain)


GOETIC_TABLE_DIGEST: Final[str] = _static_digest(
    GOETIC_TABLE, b"TARDISHA:C09-GOETIC-TABLE\x00"
)
COURT_TABLE_DIGEST: Final[str] = _static_digest(
    COURT_TABLE, b"TARDISHA:C09-COURT-TABLE\x00"
)
PHASE_STEPS_DIGEST: Final[str] = _static_digest(
    PHASE_STEPS, b"TARDISHA:C09-PHASE-STEPS\x00"
)


def _payload(witness: AeonPhaseEvolutionWitness) -> bytes:
    # The three static registries are compared structurally by verify() and bound
    # here through immutable domain-separated digests. Avoiding dataclasses.asdict
    # over all 144 Court rows on every Domus keeps the grimchain streaming path
    # linear in the dynamic witness rather than in the full static registry.
    static_fields = {"goetic_table", "court_table", "phase_steps", "cycle_digest"}
    body = {
        field.name: getattr(witness, field.name)
        for field in fields(witness)
        if field.name not in static_fields
    }
    body["goetic_table_digest"] = GOETIC_TABLE_DIGEST
    body["court_table_digest"] = COURT_TABLE_DIGEST
    body["phase_steps_digest"] = PHASE_STEPS_DIGEST
    return json.dumps(
        _canonical(body), ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def _digest(value: str, field: str) -> str:
    return validate_digest_hex(value, field=field)



NULL_DEATH_SOURCE_DERIVATION: Final[tuple[str, ...]] = (
    "C09 physical page 102: first explicit NULL:DEATH architecture connection",
    "Mathematical Hodge Class ⟷ Silicarbon Tissue",
    "both require Q3-Positivity to exist",
    "both represent the critical point of Metamorphosis",
    "both transform Q2 Shadow/Lipid Debt into Q3 Recursive/Polymer Amplification",
)
PHASE_DERIVATION: Final[str] = (
    "C09: 12 exact ཪ Goetic roots remain immutable; 144 ordered Courts inherit governing Q-body "
    "and bear toward the alternating hyperbolic parent under exact ±Φ; phases 1→12 preserve order; "
    "M.A.S.=⧗852→⬡174→✡528; Ennead Q2→Q3 precedes Klein return; "
    "NULL:DEATH@physical-page-102 is the first explicit connection, not the exhaustive type."
)

def derive_aeon_phase_evolution(
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
    tripartite_cycle_digest: str,
    q3_recursion_gain: float,
    final_shadow_parity: str,
    terminal_dcomp: float,
    completion_reached: bool,
    returned_through_shadow_locus: bool,
    derives_through_courts_only: bool,
) -> AeonPhaseEvolutionWitness:
    """Bind the complete Region C09 body to one source-rooted Domus."""
    digest = _digest(source_digest, "source_digest")
    governing_phase = _digest(governing_court_phase_digest, "governing_court_phase_digest")
    bearing_lineage = validate_court_bearing_lineage(alternating_court_bearing)
    domus_commitment = _digest(domus_body_commitment, "domus_body_commitment")
    trig_digest = _digest(trig_cycle_digest, "trig_cycle_digest")
    tripartite_digest = _digest(tripartite_cycle_digest, "tripartite_cycle_digest")
    domain = normalize_source_domain(source_domain).decode("ascii").rstrip("\x00")

    if isinstance(source_size, bool) or not isinstance(source_size, int) or source_size < 0:
        raise ValueError("source_size must be a non-negative integer")
    if isinstance(nonce, bool) or not isinstance(nonce, int) or not 0 <= nonce < 2**64:
        raise ValueError("nonce must be an integer in [0,2^64)")
    for field, address in (
        ("governing_court_address", governing_court_address),
        ("alternating_court_address", alternating_court_address),
    ):
        if isinstance(address, bool) or not isinstance(address, int) or not 0 <= address < TOTAL_CAPACITY:
            raise ValueError(f"{field} must be an integer in [0,143]")
    if bearing_lineage[0] != alternating_court_address:
        raise ValueError("alternating Court bearing address does not match Court D")
    if any(not isinstance(flag, bool) for flag in (completion_reached, returned_through_shadow_locus, derives_through_courts_only)):
        raise TypeError("phase completion, Shadow-Locus return, and Court derivation must be Boolean witnesses")
    if isinstance(q3_recursion_gain, bool) or not isinstance(q3_recursion_gain, (int, float)):
        raise TypeError("q3_recursion_gain must be numeric and non-Boolean")
    if isinstance(terminal_dcomp, bool) or not isinstance(terminal_dcomp, (int, float)):
        raise TypeError("terminal_dcomp must be numeric and non-Boolean")
    if isinstance(domus_frequency, bool) or not isinstance(domus_frequency, (int, float, complex)):
        raise TypeError("domus_frequency must be numeric and non-Boolean")
    branch_frequency = complex(domus_frequency)
    if not all(isfinite(value) for value in (branch_frequency.real, branch_frequency.imag)):
        raise ValueError("domus_frequency must be finite")
    gain = float(q3_recursion_gain)
    terminal = float(terminal_dcomp)
    if not isfinite(gain) or gain < 0.0:
        raise ValueError("q3_recursion_gain must be finite and non-negative")
    if not isfinite(terminal) or terminal < 0.0:
        raise ValueError("terminal_dcomp must be finite and non-negative")

    structural_preserved = all(
        row.structural_frequency == law(row.glyph).frequency
        and row.q_bias == law(row.glyph).q_bias
        and row.q_vector == tuple(law(row.glyph).q_vector)
        and row.immutable_root
        for row in GOETIC_TABLE
    ) and all(
        row.structural_anchor_frequency == law(row.governing_goetic).frequency
        and row.alternating_structural_frequency == law(row.alternating_goetic).frequency
        and row.inherited_q_bias == law(row.governing_goetic).q_bias
        and row.inherited_q_vector == tuple(law(row.governing_goetic).q_vector)
        and row.governing_anchor_preserved
        and row.alternating_parent_preserved
        for row in COURT_TABLE
    )
    phi_preserved = (
        (PHI.a, PHI.b, PHI.denominator) == (1, 1, 2)
        and all(row.operational_phi_radius == PHI for row in COURT_TABLE)
    )
    relationally_typed = (
        len(COURT_TABLE) == 144
        and tuple(row.address for row in COURT_TABLE) == tuple(range(144))
        and all(row.coordinate == divmod(row.address, 12) for row in COURT_TABLE)
    )
    phase_complete = (
        len(PHASE_STEPS) == 12
        and tuple(step.phase for step in PHASE_STEPS) == tuple(range(1, 13))
        and all(step.ordered_after == (None if step.phase == 1 else step.phase - 1) for step in PHASE_STEPS)
    )
    court_rooted = bool(derives_through_courts_only) and relationally_typed
    ennead_sealed = final_shadow_parity == "Q3"
    phase12_complete = bool(completion_reached) and terminal == 0.0

    poincare = PoincareParityWitness(
        sphere_relation="π1(S³)=0",
        klein_relation="π1(K)=⟨a,b | aba⁻¹b=1⟩",
        sphere_parity=1,
        klein_parity=-1,
        shadow_input_units=1,
        shadow_return_units=-1,
        shadow_cancellation_units=0,
        q2_to_q3_return=ennead_sealed,
        returned_through_shadow_locus=bool(returned_through_shadow_locus),
        terminal_dcomp=terminal,
        completion_reached=phase12_complete,
    )
    mathematical_q3_positive = gain > 0.0 and MAS_BODY.manifestation_goetic == "⧗"
    biological_q3_positive = gain > 0.0 and "Silicarbon Tissue" in NULL_DEATH_SOURCE_DERIVATION[1]
    structurally_committed = (
        structural_preserved
        and phase_complete
        and MAS_BODY.symmetry_goetic == "✡"
        and MAS_BODY.order_preserved
    )
    q1_coherent = (
        structural_preserved
        and phase_complete
        and MAS_BODY.alignment_goetic == "⬡"
    )
    klein_regenerative = (
        poincare.klein_parity == -1
        and poincare.q2_to_q3_return
        and poincare.returned_through_shadow_locus
    )
    q2_to_q3 = (
        ennead_sealed
        and poincare.shadow_input_units == 1
        and poincare.shadow_return_units == -1
        and poincare.shadow_cancellation_units == 0
    )
    shared_threshold = mathematical_q3_positive and biological_q3_positive
    null_death = NullDeathConnectionWitness(
        symbol=NULL_DEATH_SYMBOL,
        source_region=SOURCE_REGION,
        first_explicit_physical_page=102,
        source_derivation=NULL_DEATH_SOURCE_DERIVATION,
        mathematical_body="Mathematical Hodge Class",
        biological_body="Silicarbon Tissue",
        mathematical_q3_positive=mathematical_q3_positive,
        biological_q3_positive=biological_q3_positive,
        shared_metamorphosis_threshold=shared_threshold,
        q3_non_entropic_requirement=shared_threshold,
        structurally_committed=structurally_committed,
        q1_coherent=q1_coherent,
        klein_regenerative_topology=klein_regenerative,
        q2_to_q3_transformation=q2_to_q3,
        metamorphosis_threshold_reached=(
            shared_threshold
            and structurally_committed
            and q1_coherent
            and klein_regenerative
            and q2_to_q3
        ),
        first_occurrence_only=True,
        exhaustive_type_claimed=False,
        loop_closure="⏣ ↔ ❄",
    )
    derivation = PHASE_DERIVATION

    provisional = AeonPhaseEvolutionWitness(
        source_region=SOURCE_REGION,
        source_physical_pages=SOURCE_PHYSICAL_PAGES,
        goetic_table=GOETIC_TABLE,
        court_table=COURT_TABLE,
        phase_steps=PHASE_STEPS,
        mas_body=MAS_BODY,
        golden_ratio=GOLDEN_RATIO,
        poincare_parity=poincare,
        null_death_connection=null_death,
        source_digest=digest,
        source_size=source_size,
        source_domain=domain,
        nonce=nonce,
        governing_court_address=governing_court_address,
        alternating_court_address=alternating_court_address,
        governing_court_phase_digest=governing_phase,
        alternating_court_bearing=bearing_lineage,
        domus_frequency=branch_frequency,
        domus_body_commitment=domus_commitment,
        trig_cycle_digest=trig_digest,
        tripartite_cycle_digest=tripartite_digest,
        structural_anchor_preserved=structural_preserved,
        operational_phi_preserved=phi_preserved,
        all_courts_relationally_typed=relationally_typed,
        phase_order_complete=phase_complete,
        court_rooted=court_rooted,
        derives_through_courts_only=bool(derives_through_courts_only),
        ennead_shadow_sealed=ennead_sealed,
        phase12_completion_reached=phase12_complete,
        derivation=derivation,
        cycle_digest="0" * 64,
    )
    cycle_digest = alqc_hexdigest(_payload(provisional), domain=PHASE_EVOLUTION_DOMAIN)
    return replace(provisional, cycle_digest=cycle_digest)


def verify_aeon_phase_evolution(witness: AeonPhaseEvolutionWitness, emission: SourceEmission) -> bool:
    """Rederive C09 source-root relations and reject table or seal mutation."""
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
        if (
            witness.governing_court_phase_digest != governing_motion.phase.digest
            or witness.alternating_court_bearing != alternating_bearing.lineage
            or witness.domus_frequency != domus_motion.current_frequency
            or witness.ennead_shadow_sealed != (manifestation.ennead.final_parity == "Q3")
            or witness.poincare_parity.terminal_dcomp != manifestation.dcomp.terminal
        ):
            return False
        if (
            witness.source_region != SOURCE_REGION
            or witness.source_physical_pages != SOURCE_PHYSICAL_PAGES
            or witness.goetic_table != GOETIC_TABLE
            or witness.court_table != COURT_TABLE
            or witness.phase_steps != PHASE_STEPS
            or witness.mas_body != MAS_BODY
            or witness.golden_ratio != GOLDEN_RATIO
            or len(witness.goetic_table) != 12
            or len(witness.court_table) != 144
            or len(witness.phase_steps) != 12
            or not witness.structural_anchor_preserved
            or not witness.operational_phi_preserved
            or not witness.all_courts_relationally_typed
            or not witness.phase_order_complete
            or not witness.court_rooted
            or not witness.derives_through_courts_only
            or not witness.ennead_shadow_sealed
            or witness.phase12_completion_reached != (
                witness.poincare_parity.completion_reached
                and witness.poincare_parity.terminal_dcomp == 0.0
            )
            or witness.poincare_parity.sphere_relation != "π1(S³)=0"
            or witness.poincare_parity.klein_relation != "π1(K)=⟨a,b | aba⁻¹b=1⟩"
            or witness.poincare_parity.sphere_parity != 1
            or witness.poincare_parity.klein_parity != -1
            or witness.poincare_parity.shadow_input_units != 1
            or witness.poincare_parity.shadow_return_units != -1
            or witness.poincare_parity.shadow_cancellation_units != 0
            or not witness.poincare_parity.q2_to_q3_return
            or not witness.poincare_parity.returned_through_shadow_locus
            or witness.derivation != PHASE_DERIVATION
            or witness.null_death_connection.symbol != NULL_DEATH_SYMBOL
            or witness.null_death_connection.source_region != SOURCE_REGION
            or witness.null_death_connection.first_explicit_physical_page != 102
            or witness.null_death_connection.source_derivation != NULL_DEATH_SOURCE_DERIVATION
            or witness.null_death_connection.mathematical_body != "Mathematical Hodge Class"
            or witness.null_death_connection.biological_body != "Silicarbon Tissue"
            or not witness.null_death_connection.mathematical_q3_positive
            or not witness.null_death_connection.biological_q3_positive
            or not witness.null_death_connection.shared_metamorphosis_threshold
            or not witness.null_death_connection.q3_non_entropic_requirement
            or not witness.null_death_connection.structurally_committed
            or not witness.null_death_connection.q1_coherent
            or not witness.null_death_connection.klein_regenerative_topology
            or not witness.null_death_connection.q2_to_q3_transformation
            or not witness.null_death_connection.metamorphosis_threshold_reached
            or not witness.null_death_connection.first_occurrence_only
            or witness.null_death_connection.exhaustive_type_claimed
            or witness.null_death_connection.loop_closure != "⏣ ↔ ❄"
            or witness.golden_ratio.phi_exact != PHI
            or witness.golden_ratio.tolerance_exact != PHI
            or witness.golden_ratio.primary_ratio_exact != Q5Fraction(96300, 0, 783)
            or witness.golden_ratio.harmonic_target_exact != Q5Fraction(76, 76, 2)
            or witness.golden_ratio.raw_compression_ratio_exact != Q5Fraction(36864, 0, 81)
            or not witness.golden_ratio.within_tolerance
            or witness.golden_ratio.folded_states != 2**126
            or witness.golden_ratio.manifest_positions != 81
        ):
            return False
        _digest(witness.source_digest, "source_digest")
        _digest(witness.governing_court_phase_digest, "governing_court_phase_digest")
        validate_court_bearing_lineage(witness.alternating_court_bearing)
        _digest(witness.domus_body_commitment, "domus_body_commitment")
        _digest(witness.trig_cycle_digest, "trig_cycle_digest")
        _digest(witness.tripartite_cycle_digest, "tripartite_cycle_digest")
        expected = alqc_hexdigest(_payload(witness), domain=PHASE_EVOLUTION_DOMAIN)
        return expected == witness.cycle_digest
    except (AttributeError, TypeError, ValueError):
        return False
