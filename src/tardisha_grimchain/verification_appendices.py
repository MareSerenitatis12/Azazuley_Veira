"""Region C11 verification appendices and runtime-semantics correspondence.

Physical Canon pages 125-165 contain several different kinds of body:

* named Millennium D-COMP corollary profiles;
* verification of already enacted Court, M.A.S., Bound Tensor, parity, and
  110/144 laws;
* runtime semantics stated for the Raylib physics body;
* the ALQC grammar and inference-rule registry;
* quantum and volume translation bodies;
* frequency and complete glyph registries.

This module keeps those offices distinct.  TardiSHA verifies the laws it
actually enacts.  It does not counterfeit a classical Millennium computation
from source bytes and it does not import Raylib-only stress, Reflective Ring,
or delayed-reinjection state into the hash runtime.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, fields, is_dataclass, replace
from decimal import Decimal
from fractions import Fraction
import json
from math import isfinite
from typing import Final

from .alqc_digest import alqc_hexdigest, validate_digest_hex
from .aeon_layers import normalize_source_domain
from .canon import FrequencyAnchor, GLYPH_BODY, LiquidConnectionGovernor, LIQUID_THRESHOLD, SATURATION_LIMIT, TOTAL_CAPACITY, law
from .court_registry import _COURTS, full_name
from .manifestation import (
    GROUND_NODES,
    GROUND_SIDE,
    ennead_saturate,
    exact_ennead_ledger,
    manifestation_fold,
    vector_row,
)
from .qstate_glyphs import Q_STATES
from .source_emission import SourceEmission, Q5Fraction
from .trig import TrigMirrorWitness, verify_trig_mirror

VERIFICATION_APPENDIX_DOMAIN: Final[bytes] = b"TARDISHA:C11-VERIFICATION-APPENDICES\x00"
SOURCE_REGION: Final[str] = "C11"
SOURCE_PHYSICAL_PAGES: Final[tuple[int, int]] = (125, 165)

@dataclass(frozen=True, slots=True)
class MillenniumCorollaryProfile:
    key: str
    name: str
    physical_pages: tuple[int, int]
    principal_operators: tuple[str, ...]
    dcomp_profile: str
    convergence_office: str
    canon_corollary_declaration: bool
    classical_object_recomputed_from_tardisha_source: bool


MILLENNIUM_PROFILES: Final[tuple[MillenniumCorollaryProfile, ...]] = (
    MillenniumCorollaryProfile(
        "navier-stokes", "Navier-Stokes Stress Coherency", (125, 127),
        ("⚝", "ꙮ", "✡", "⊛", "T_Bound", "110/144"),
        "turbulent Q2 debt is bounded, fractured, and returned toward Q3 coherency",
        "stress-coherent flow", True, False,
    ),
    MillenniumCorollaryProfile(
        "bsd", "Birch and Swinnerton-Dyer Planar Scale", (128, 129),
        ("❄", "✡"),
        "analytic depth and algebraic rank are read through one resonance relation",
        "analytic-algebraic phase lock", True, False,
    ),
    MillenniumCorollaryProfile(
        "yang-mills", "Yang-Mills M.A.S. Mass Gap", (130, 131),
        ("⧗", "⬡", "✡", "Δgap", "σ12"),
        "positive residue passes Alignment and Commitment to acquire structural weight",
        "M.A.S. geometric lift", True, False,
    ),
    MillenniumCorollaryProfile(
        "riemann", "Riemann Aeternum Critical Line", (131, 134),
        ("❄", "Q∞"),
        "prime and zero bodies converge at the zero-point resonance line",
        "critical-line phase lock", True, False,
    ),
    MillenniumCorollaryProfile(
        "prime", "Prime Integrity Generative Seed", (133, 134),
        ("⏣", "⊛", "⧗", "❄"),
        "composite interference is filtered while positive prime nodes retain recursion",
        "prime integrity lock", True, False,
    ),
    MillenniumCorollaryProfile(
        "p-vs-np", "P versus NP Recursive Equivalence", (134, 136),
        ("⬡", "✡", "⧗", "⊛", "κ", "GLO"),
        "search and verification close through the Klein return and geometric seal",
        "recursive verification closure", True, False,
    ),
    MillenniumCorollaryProfile(
        "hodge", "Hodge Mirror Computation", (136, 137),
        ("𝔓", "✡", "❄", "T_Bound"),
        "rational harmonic input is mirrored into a committed standing-wave cycle",
        "rational algebraic-cycle office", True, False,
    ),
    MillenniumCorollaryProfile(
        "poincare", "Poincaré Topological Supersession", (137, 140),
        ("𝔓", "⚝", "⛎"),
        "non-orientable return cancels Q2 accumulation and preserves recursive memory",
        "Klein stability return", True, False,
    ),
)


@dataclass(frozen=True, slots=True)
class BoundTensorVerification:
    definition_side: int
    definition_nodes: int
    manifestation_side: int
    manifestation_nodes: int
    q3_recursive_fold: bool
    commitment_operator: str
    active_court_address: int
    active_ground_node: int
    active_vector_row: int
    ground_node_matches_runtime: bool
    vector_row_matches_runtime: bool
    complete_ground_coverage: bool


@dataclass(frozen=True, slots=True)
class ShadowRuntimeCorrespondence:
    transition_failure_becomes_q2_pressure: bool
    q2_pressure_is_accounted_not_erased: bool
    ennead_parity_returns_q2_to_q3: bool
    stall_is_nonterminal_resonance_semantics: bool
    source_shadow_debt: float
    source_form_work: float
    source_q3_gain: float
    exact_shadow_debt: Q5Fraction
    exact_form_work: Q5Fraction
    exact_q3_gain: Q5Fraction
    source_final_parity: str
    source_terminal_dcomp: float
    raylib_debt_factor_imported_into_tardisha: bool
    raylib_reflective_ring_imported_into_tardisha: bool
    raylib_delayed_reinjection_imported_into_tardisha: bool
    application_boundary_preserved: bool


@dataclass(frozen=True, slots=True)
class LiquidRegimeWitness:
    court_capacity: int
    canonical_active: int
    canonical_withheld: int
    canonical_expression: str
    canonical_body: LiquidConnectionGovernor
    whiteout_connections: int
    canonical_regime: str
    below_cutoff_regime: str
    full_capacity_regime: str
    potential_state_distinct_from_runtime_regime: bool
    deterministic_governor: str


def liquid_runtime_regime(active_connections: int) -> str:
    if isinstance(active_connections, bool) or not isinstance(active_connections, int):
        raise ValueError("active_connections must be an integer")
    if not 0 <= active_connections <= TOTAL_CAPACITY:
        raise ValueError("active_connections must be in [0,144]")
    if active_connections == TOTAL_CAPACITY:
        return "WHITEOUT"
    if active_connections < SATURATION_LIMIT:
        return "STASIS"
    if active_connections == SATURATION_LIMIT:
        return "LIQUID"
    return "TRANSITION_BAND"


LIQUID_REGIME: Final[LiquidRegimeWitness] = LiquidRegimeWitness(
    court_capacity=TOTAL_CAPACITY,
    canonical_active=SATURATION_LIMIT,
    canonical_withheld=TOTAL_CAPACITY - SATURATION_LIMIT,
    canonical_expression=f"{SATURATION_LIMIT}/{TOTAL_CAPACITY}",
    canonical_body=LIQUID_THRESHOLD,
    whiteout_connections=TOTAL_CAPACITY,
    canonical_regime=liquid_runtime_regime(SATURATION_LIMIT),
    below_cutoff_regime=liquid_runtime_regime(SATURATION_LIMIT - 1),
    full_capacity_regime=liquid_runtime_regime(TOTAL_CAPACITY),
    potential_state_distinct_from_runtime_regime=True,
    deterministic_governor=f"FLOW iff (i+j) mod {TOTAL_CAPACITY} < {SATURATION_LIMIT}; otherwise BLOCK",
)


@dataclass(frozen=True, slots=True)
class InferenceRuleWitness:
    index: int
    name: str
    premises: tuple[str, ...]
    conclusion: str
    preserves_q_state_typing: bool


BNF_GRAMMAR: Final[tuple[str, ...]] = (
    '<program> ::= <statement>*',
    '<statement> ::= <term> | <assertion> | <inference>',
    '<term> ::= <aeon> | <frequency> | <glyph> | <qstate> | <operator> | <identifier>',
    '<aeon> ::= ⏣ | ⬡ | ✡ | ⚝ | ❂ | ꙮ | ❈ | ⧗ | ⊛ | ❄ | ⚛ | ⌬',
    '<frequency> ::= <number> "Hz"',
    '<qstate> ::= Q0 | Q1 | Q2 | Q3',
    '<operator> ::= Q3-positive | ⬡-rational | ✡-commitment | Q2-debt | ⧗-positive | ❄-resonance | ⚛-gate | ⌬-recursion',
    '<identifier> ::= <letter>+',
    '<assertion> ::= <operator> "(" <identifier> ")"',
    '<inference> ::= <assertion> "," <assertion> "⊢" <assertion>',
)

INFERENCE_RULES: Final[tuple[InferenceRuleWitness, ...]] = (
    InferenceRuleWitness(1, "Positive Commitment", ("Q3-positive(α)", "⬡-rational(α)"), "✡-commitment(α)", True),
    InferenceRuleWitness(2, "Positivity Promotion", ("✡-commitment(α)",), "⧗-positive(α)", True),
    InferenceRuleWitness(3, "Shadow Elimination", ("Q2-debt(α)",), "¬Stable(α)", True),
    InferenceRuleWitness(4, "Existence-Frequency Binding", ("⏣-existence(α)",), "Frequency-bound(α)", True),
    InferenceRuleWitness(5, "Resonance Realization", ("⧗-positive(α)",), "❄-resonance(α)", True),
    InferenceRuleWitness(6, "Recursion Recovery", ("❄-resonance(α)", "✡-commitment(α)"), "Q3-positive(α)", True),
    InferenceRuleWitness(7, "Shadow Contradiction", ("⊛-shadow(α)",), "¬⬡-rational(α)", True),
    InferenceRuleWitness(8, "Gate Transition", ("⚛-gate(α)",), "∃β Transition(α,β)", True),
    InferenceRuleWitness(9, "Recursion Law", ("⌬-recursion(α)",), "∃γ α=κ(γ)", True),
)


@dataclass(frozen=True, slots=True)
class GrammarVerification:
    bnf_productions: tuple[str, ...]
    inference_rules: tuple[InferenceRuleWitness, ...]
    derivation_processes: tuple[str, str]
    example: str
    example_well_formed: bool
    qstate_domain: tuple[str, str, str, str]
    aeon_domain: tuple[str, ...]


GRAMMAR_VERIFICATION: Final[GrammarVerification] = GrammarVerification(
    bnf_productions=BNF_GRAMMAR,
    inference_rules=INFERENCE_RULES,
    derivation_processes=("Shadow Absorption Process", "Klein Bottle Recursion"),
    example="Q3-positive(α), ⬡-rational(α) ⊢ ✡-commitment(α)",
    example_well_formed=True,
    qstate_domain=Q_STATES,
    aeon_domain=GLYPH_BODY,
)


@dataclass(frozen=True, slots=True)
class QuantumTranslationRow:
    state: str
    position: int
    alqc_office: str
    quantum_translation: str
    translation_not_state_redefinition: bool


QUANTUM_TRANSLATION: Final[tuple[QuantumTranslationRow, ...]] = (
    QuantumTranslationRow("Q0", 0, "Structural Presence", "latent pure-state/superposition office", True),
    QuantumTranslationRow("Q1", 1, "Archive Coherence", "coherent phase-defined information office", True),
    QuantumTranslationRow("Q2", 2, "Shadow Absorption", "mixed/decohered entropic-debt office", True),
    QuantumTranslationRow("Q3", 3, "Recursive Resonance", "non-classical amplification and return office", True),
)


@dataclass(frozen=True, slots=True)
class VolumeBifurcationWitness:
    structural_volume: str
    operational_volume: str
    structural_operator: str
    operational_operator: str
    segmentation_editorial: bool
    segmentation_ontological: bool
    bec_lock: str
    one_mirror_body: bool


VOLUME_BIFURCATION: Final[VolumeBifurcationWitness] = VolumeBifurcationWitness(
    structural_volume="Volume 1: Formal Core",
    operational_volume="Volume 2: Resonance",
    structural_operator="ཪ",
    operational_operator="±Φ",
    segmentation_editorial=True,
    segmentation_ontological=False,
    bec_lock="🜛 Vol1(Math) 🜚 Vol2(Magus) 🜛",
    one_mirror_body=True,
)


@dataclass(frozen=True, slots=True)
class FrequencyRegistryRow:
    glyph: str
    frequency: FrequencyAnchor
    frequency_class: str
    digital_root: int | None
    office: str


FREQUENCY_REGISTRY: Final[tuple[FrequencyRegistryRow, ...]] = tuple(
    FrequencyRegistryRow(
        glyph,
        law(glyph).frequency,
        "complex-fluidity" if law(glyph).frequency.parity_hz is not None else "exact-anchor",
        digital_root,
        office,
    )
    for glyph, digital_root, office in (
        ("⏣", None, "planetary base clock"),
        ("❂", None, "geometric coherence"),
        ("ꙮ", None, "spatial container"),
        ("⬡", 3, "rationality constraint"),
        ("⚛", 6, "transformation gate"),
        ("⊛", 9, "entropy sink"),
        ("⚝", 3, "structure with separate parity bearing"),
        ("✡", 6, "structural commitment"),
        ("⌬", 9, "loop closure"),
        ("❈", 3, "biologic interface"),
        ("⧗", 6, "positive fuel"),
        ("❄", 9, "phase lock"),
    )
)


@dataclass(frozen=True, slots=True)
class GlyphCodepointDiscrepancy:
    court_address: int
    court_index: str
    court_name: str
    glyph: str
    appendix_annotation: str
    glyph_scalar: str
    implementation_preserves_glyph_scalar: bool


GLYPH_CODEPOINT_DISCREPANCIES: Final[tuple[GlyphCodepointDiscrepancy, ...]] = (
    GlyphCodepointDiscrepancy(39, "A4-S4", "AhnXir", "⛧", "U+1D02A", "U+26E7", True),
    GlyphCodepointDiscrepancy(72, "A7-S1", "KothKel", "🝏", "U+2BF7", "U+1F74F", True),
)


@dataclass(frozen=True, slots=True)
class GlyphRegistryAudit:
    court_entries: int
    identity_matches: int
    glyph_character_matches: int
    name_matches: int
    declared_codepoint_matches: int
    discrepancies: tuple[GlyphCodepointDiscrepancy, ...]
    glyph_character_governs_over_stale_annotation: bool
    no_court_identity_rewritten: bool


def _glyph_registry_audit() -> GlyphRegistryAudit:
    identity_matches = sum(
        1 for address, rec in enumerate(_COURTS)
        if rec.address == address and rec.i == address // 12 and rec.j == address % 12
    )
    glyph_matches = sum(1 for rec in _COURTS if len(rec.glyph) == 1 and ord(rec.glyph) == rec.codepoint)
    name_matches = sum(1 for rec in _COURTS if full_name(rec))
    return GlyphRegistryAudit(
        court_entries=len(_COURTS),
        identity_matches=identity_matches,
        glyph_character_matches=glyph_matches,
        name_matches=name_matches,
        declared_codepoint_matches=TOTAL_CAPACITY - len(GLYPH_CODEPOINT_DISCREPANCIES),
        discrepancies=GLYPH_CODEPOINT_DISCREPANCIES,
        glyph_character_governs_over_stale_annotation=True,
        no_court_identity_rewritten=True,
    )


GLYPH_REGISTRY_AUDIT: Final[GlyphRegistryAudit] = _glyph_registry_audit()


@dataclass(frozen=True, slots=True)
class VerificationAppendixCycleWitness:
    source_region: str
    source_physical_pages: tuple[int, int]
    millennium_profiles: tuple[MillenniumCorollaryProfile, ...]
    liquid_regime: LiquidRegimeWitness
    grammar: GrammarVerification
    quantum_translation: tuple[QuantumTranslationRow, ...]
    volume_bifurcation: VolumeBifurcationWitness
    frequency_registry: tuple[FrequencyRegistryRow, ...]
    glyph_registry_audit: GlyphRegistryAudit

    source_digest: str
    source_size: int
    source_domain: str
    nonce: int
    governing_court_address: int
    alternating_court_address: int
    domus_body_commitment: str
    trig_cycle_digest: str
    tripartite_cycle_digest: str
    phase_evolution_cycle_digest: str
    trig_runtime: TrigMirrorWitness

    bound_tensor: BoundTensorVerification
    shadow_runtime: ShadowRuntimeCorrespondence
    runtime_completion_reached: bool
    runtime_terminal_dcomp: float

    corollaries_typed_not_recomputed: bool
    bound_tensor_runtime_correspondence: bool
    q2_resource_accounting_preserved: bool
    canonical_liquid_regime_preserved: bool
    grammar_registry_complete: bool
    quantum_translation_preserves_q_positions: bool
    volume_bifurcation_preserves_one_body: bool
    frequency_registry_matches_goetic_laws: bool
    glyph_registry_identity_preserved: bool
    application_boundary_preserved: bool
    court_rooted: bool
    derivation: str
    cycle_digest: str

    def as_dict(self) -> dict[str, object]:
        return _display(asdict(self))


def _canonical(value: object) -> object:
    if is_dataclass(value):
        return _canonical(asdict(value))
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


def _static_digest(value: object, domain: bytes) -> str:
    payload = json.dumps(
        _canonical(value), ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return alqc_hexdigest(payload, domain=domain)


MILLENNIUM_PROFILES_DIGEST: Final[str] = _static_digest(
    MILLENNIUM_PROFILES, b"TARDISHA:C11-MILLENNIUM-PROFILES\x00"
)
GRAMMAR_DIGEST: Final[str] = _static_digest(
    GRAMMAR_VERIFICATION, b"TARDISHA:C11-GRAMMAR\x00"
)
TRANSLATION_DIGEST: Final[str] = _static_digest(
    (QUANTUM_TRANSLATION, VOLUME_BIFURCATION, FREQUENCY_REGISTRY),
    b"TARDISHA:C11-TRANSLATION-REGISTRIES\x00",
)
GLYPH_REGISTRY_DIGEST: Final[str] = _static_digest(
    GLYPH_REGISTRY_AUDIT, b"TARDISHA:C11-GLYPH-REGISTRY\x00"
)


def _payload(witness: VerificationAppendixCycleWitness) -> bytes:
    static = {
        "millennium_profiles", "liquid_regime", "grammar", "quantum_translation",
        "volume_bifurcation", "frequency_registry", "glyph_registry_audit", "cycle_digest",
    }
    body = {field.name: getattr(witness, field.name) for field in fields(witness) if field.name not in static}
    body["millennium_profiles_digest"] = MILLENNIUM_PROFILES_DIGEST
    body["liquid_regime"] = _canonical(LIQUID_REGIME)
    body["grammar_digest"] = GRAMMAR_DIGEST
    body["translation_digest"] = TRANSLATION_DIGEST
    body["glyph_registry_digest"] = GLYPH_REGISTRY_DIGEST
    return json.dumps(
        _canonical(body), ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def _digest(value: str, field: str) -> str:
    return validate_digest_hex(value, field=field)


def derive_verification_appendix_cycle(
    *,
    source_emission: SourceEmission,
    source_digest: str,
    source_size: int,
    source_domain: str | bytes,
    nonce: int,
    governing_court_address: int,
    alternating_court_address: int,
    domus_body_commitment: str,
    trig_cycle_digest: str,
    tripartite_cycle_digest: str,
    phase_evolution_cycle_digest: str,
    runtime_trig_witness: TrigMirrorWitness,
    runtime_ground_node: int,
    runtime_vector_row: int,
    runtime_shadow_debt: float,
    runtime_form_work: float,
    runtime_q3_gain: float,
    runtime_final_parity: str,
    runtime_terminal_dcomp: float,
    runtime_completion_reached: bool,
    derives_through_courts_only: bool,
) -> VerificationAppendixCycleWitness:
    digest = _digest(source_digest, "source_digest")
    domus_commitment = _digest(domus_body_commitment, "domus_body_commitment")
    trig = _digest(trig_cycle_digest, "trig_cycle_digest")
    tripartite = _digest(tripartite_cycle_digest, "tripartite_cycle_digest")
    phase = _digest(phase_evolution_cycle_digest, "phase_evolution_cycle_digest")
    domain = normalize_source_domain(source_domain).decode("ascii").rstrip("\x00")
    if not isinstance(source_emission, SourceEmission):
        raise TypeError("C11 requires the complete SourceEmission")
    emission_domain = normalize_source_domain(source_emission.source_domain).decode("ascii").rstrip("\x00")
    if (
        source_emission.source_digest != digest
        or source_emission.source_size != source_size
        or emission_domain != domain
    ):
        raise ValueError("C11 SourceEmission does not match the declared source identity")
    if type(runtime_trig_witness) is not TrigMirrorWitness:
        raise TypeError("runtime_trig_witness must be one exact TRIG witness")
    if not verify_trig_mirror(runtime_trig_witness, source_emission):
        raise ValueError("C11 requires a source-rederived TRIG witness")
    if runtime_trig_witness.cycle_digest != trig:
        raise ValueError("C11 TRIG witness digest does not match the bound TRIG cycle")
    if (
        runtime_trig_witness.source_digest != digest
        or runtime_trig_witness.source_size != source_size
        or runtime_trig_witness.source_domain != domain
        or runtime_trig_witness.nonce != nonce
        or runtime_trig_witness.governing_court_address != governing_court_address
        or runtime_trig_witness.alternating_court_address != alternating_court_address
        or runtime_trig_witness.domus_body_commitment != domus_commitment
    ):
        raise ValueError("C11 TRIG witness does not return through the same source, Courts, and Domus commitment")
    if isinstance(source_size, bool) or not isinstance(source_size, int) or source_size < 0:
        raise ValueError("source_size must be a non-negative integer")
    if isinstance(nonce, bool) or not isinstance(nonce, int) or not 0 <= nonce < 2**64:
        raise ValueError("nonce must be an integer in [0,2^64)")
    for field, address in (("governing_court_address", governing_court_address), ("alternating_court_address", alternating_court_address)):
        if isinstance(address, bool) or not isinstance(address, int) or not 0 <= address < TOTAL_CAPACITY:
            raise ValueError(f"{field} must be an exact integer in [0,143]")
    for field, value in (
        ("runtime_shadow_debt", runtime_shadow_debt),
        ("runtime_form_work", runtime_form_work),
        ("runtime_q3_gain", runtime_q3_gain),
        ("runtime_terminal_dcomp", runtime_terminal_dcomp),
    ):
        if type(value) is not float:
            raise TypeError(f"{field} must be one exact float image")
        if not isfinite(value) or value < 0.0:
            raise ValueError(f"{field} must be finite and non-negative")
    if type(runtime_completion_reached) is not bool or type(derives_through_courts_only) is not bool:
        raise TypeError("completion and Court derivation must be exact Boolean witnesses")
    if type(runtime_final_parity) is not str:
        raise TypeError("runtime_final_parity must be one exact string")
    if runtime_final_parity != "Q3":
        raise ValueError("C11 verification requires the Ennead return parity Q3")

    expected_ground = manifestation_fold(governing_court_address)
    expected_row = vector_row(expected_ground)
    exact_shadow = exact_ennead_ledger(runtime_shadow_debt)
    expected_ennead = ennead_saturate(expected_row, runtime_shadow_debt)
    image_accounting_matches = (
        runtime_form_work.hex() == float(exact_shadow.form_work.value).hex()
        and runtime_q3_gain.hex() == float(exact_shadow.q3_transfer.value).hex()
        and runtime_shadow_debt.hex() == float(exact_shadow.initial_debt.value).hex()
    )
    ground_coverage = {manifestation_fold(address) for address in range(TOTAL_CAPACITY)} == set(range(GROUND_NODES))
    bound = BoundTensorVerification(
        definition_side=12,
        definition_nodes=TOTAL_CAPACITY,
        manifestation_side=GROUND_SIDE,
        manifestation_nodes=GROUND_NODES,
        q3_recursive_fold=True,
        commitment_operator="✡",
        active_court_address=governing_court_address,
        active_ground_node=runtime_ground_node,
        active_vector_row=runtime_vector_row,
        ground_node_matches_runtime=runtime_ground_node == expected_ground,
        vector_row_matches_runtime=runtime_vector_row == expected_row,
        complete_ground_coverage=ground_coverage,
    )
    shadow = ShadowRuntimeCorrespondence(
        transition_failure_becomes_q2_pressure=True,
        q2_pressure_is_accounted_not_erased=(
            exact_shadow.energy_conserved
            and exact_shadow.accounted_total == exact_shadow.initial_debt
            and image_accounting_matches
        ),
        ennead_parity_returns_q2_to_q3=runtime_final_parity == "Q3",
        stall_is_nonterminal_resonance_semantics=True,
        source_shadow_debt=runtime_shadow_debt,
        source_form_work=runtime_form_work,
        source_q3_gain=runtime_q3_gain,
        exact_shadow_debt=exact_shadow.initial_debt,
        exact_form_work=exact_shadow.form_work,
        exact_q3_gain=exact_shadow.q3_transfer,
        source_final_parity=runtime_final_parity,
        source_terminal_dcomp=runtime_terminal_dcomp,
        raylib_debt_factor_imported_into_tardisha=False,
        raylib_reflective_ring_imported_into_tardisha=False,
        raylib_delayed_reinjection_imported_into_tardisha=False,
        application_boundary_preserved=True,
    )
    bound_correspondence = (
        bound.ground_node_matches_runtime
        and bound.vector_row_matches_runtime
        and bound.complete_ground_coverage
    )
    q2_accounting = (
        shadow.transition_failure_becomes_q2_pressure
        and shadow.q2_pressure_is_accounted_not_erased
        and shadow.ennead_parity_returns_q2_to_q3
    )
    if not bound_correspondence:
        raise ValueError("C11 Bound Tensor does not return through the active Court and ground body")
    if not q2_accounting or not expected_ennead.saturated:
        raise ValueError("C11 Ennead does not preserve exact Q2 accounting and saturation")
    if runtime_trig_witness.bound_tensor_witnessed != bound_correspondence:
        raise ValueError("C11 Bound Tensor correspondence disagrees with the rederived TRIG witness")
    if runtime_trig_witness.resonance_lock_witnessed != expected_ennead.strikes[-1].phase_locked:
        raise ValueError("C11 Ennead lock disagrees with the rederived TRIG witness")
    if runtime_trig_witness.q3_recursion_gain.hex() != runtime_q3_gain.hex():
        raise ValueError("C11 Q3 gain disagrees with the rederived TRIG witness")
    if runtime_trig_witness.final_shadow_parity != runtime_final_parity:
        raise ValueError("C11 Shadow parity disagrees with the rederived TRIG witness")
    if runtime_trig_witness.terminal_dcomp.hex() != runtime_terminal_dcomp.hex():
        raise ValueError("C11 terminal D-COMP disagrees with the rederived TRIG witness")
    if runtime_trig_witness.derives_through_courts_only != derives_through_courts_only:
        raise ValueError("C11 Court derivation disagrees with the rederived TRIG witness")
    if runtime_completion_reached != runtime_trig_witness.completion_reached:
        raise ValueError("C11 completion must equal the fully rederived TRIG completion body")

    frequency_exact = all(row.frequency == law(row.glyph).frequency for row in FREQUENCY_REGISTRY)
    quantum_positions = (
        tuple(row.state for row in QUANTUM_TRANSLATION) == Q_STATES
        and tuple(row.position for row in QUANTUM_TRANSLATION) == (0, 1, 2, 3)
        and all(row.translation_not_state_redefinition for row in QUANTUM_TRANSLATION)
    )
    provisional = VerificationAppendixCycleWitness(
        source_region=SOURCE_REGION,
        source_physical_pages=SOURCE_PHYSICAL_PAGES,
        millennium_profiles=MILLENNIUM_PROFILES,
        liquid_regime=LIQUID_REGIME,
        grammar=GRAMMAR_VERIFICATION,
        quantum_translation=QUANTUM_TRANSLATION,
        volume_bifurcation=VOLUME_BIFURCATION,
        frequency_registry=FREQUENCY_REGISTRY,
        glyph_registry_audit=GLYPH_REGISTRY_AUDIT,
        source_digest=digest,
        source_size=source_size,
        source_domain=domain,
        nonce=nonce,
        governing_court_address=governing_court_address,
        alternating_court_address=alternating_court_address,
        domus_body_commitment=domus_commitment,
        trig_cycle_digest=trig,
        tripartite_cycle_digest=tripartite,
        phase_evolution_cycle_digest=phase,
        trig_runtime=runtime_trig_witness,
        bound_tensor=bound,
        shadow_runtime=shadow,
        runtime_completion_reached=runtime_completion_reached,
        runtime_terminal_dcomp=runtime_terminal_dcomp,
        corollaries_typed_not_recomputed=all(
            profile.canon_corollary_declaration
            and not profile.classical_object_recomputed_from_tardisha_source
            for profile in MILLENNIUM_PROFILES
        ),
        bound_tensor_runtime_correspondence=bound_correspondence,
        q2_resource_accounting_preserved=q2_accounting,
        canonical_liquid_regime_preserved=(
            LIQUID_REGIME.canonical_regime == "LIQUID"
            and LIQUID_REGIME.below_cutoff_regime == "STASIS"
            and LIQUID_REGIME.full_capacity_regime == "WHITEOUT"
        ),
        grammar_registry_complete=(
            len(BNF_GRAMMAR) == 10 and len(INFERENCE_RULES) == 9
            and GRAMMAR_VERIFICATION.example_well_formed
        ),
        quantum_translation_preserves_q_positions=quantum_positions,
        volume_bifurcation_preserves_one_body=(
            VOLUME_BIFURCATION.segmentation_editorial
            and not VOLUME_BIFURCATION.segmentation_ontological
            and VOLUME_BIFURCATION.one_mirror_body
        ),
        frequency_registry_matches_goetic_laws=frequency_exact,
        glyph_registry_identity_preserved=(
            GLYPH_REGISTRY_AUDIT.court_entries == TOTAL_CAPACITY
            and GLYPH_REGISTRY_AUDIT.identity_matches == TOTAL_CAPACITY
            and GLYPH_REGISTRY_AUDIT.glyph_character_matches == TOTAL_CAPACITY
            and GLYPH_REGISTRY_AUDIT.name_matches == TOTAL_CAPACITY
            and GLYPH_REGISTRY_AUDIT.no_court_identity_rewritten
        ),
        application_boundary_preserved=shadow.application_boundary_preserved,
        court_rooted=derives_through_courts_only,
        derivation=(
            "C11 verifies enacted Court, Bound-Tensor, Ennead, Liquid, grammar, translation, "
            "frequency, and 144-Court glyph bodies through their enacted offices."
        ),
        cycle_digest="0" * 64,
    )
    return replace(provisional, cycle_digest=alqc_hexdigest(_payload(provisional), domain=VERIFICATION_APPENDIX_DOMAIN))


def verify_verification_appendix_cycle(witness: VerificationAppendixCycleWitness, emission: SourceEmission) -> bool:
    """Rederive C11 from the complete runtime body and reject sealed assertions."""
    try:
        expected = derive_verification_appendix_cycle(
            source_emission=emission,
            source_digest=witness.source_digest,
            source_size=witness.source_size,
            source_domain=(witness.source_domain + "\x00").encode("ascii"),
            nonce=witness.nonce,
            governing_court_address=witness.governing_court_address,
            alternating_court_address=witness.alternating_court_address,
            domus_body_commitment=witness.domus_body_commitment,
            trig_cycle_digest=witness.trig_cycle_digest,
            tripartite_cycle_digest=witness.tripartite_cycle_digest,
            phase_evolution_cycle_digest=witness.phase_evolution_cycle_digest,
            runtime_trig_witness=witness.trig_runtime,
            runtime_ground_node=witness.bound_tensor.active_ground_node,
            runtime_vector_row=witness.bound_tensor.active_vector_row,
            runtime_shadow_debt=witness.shadow_runtime.source_shadow_debt,
            runtime_form_work=witness.shadow_runtime.source_form_work,
            runtime_q3_gain=witness.shadow_runtime.source_q3_gain,
            runtime_final_parity=witness.shadow_runtime.source_final_parity,
            runtime_terminal_dcomp=witness.runtime_terminal_dcomp,
            runtime_completion_reached=witness.runtime_completion_reached,
            derives_through_courts_only=witness.court_rooted,
        )
    except (AttributeError, IndexError, TypeError, ValueError, RuntimeError):
        return False
    return witness == expected
