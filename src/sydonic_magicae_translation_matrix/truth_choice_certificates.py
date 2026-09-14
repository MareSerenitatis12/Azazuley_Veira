"""Phase 16 Truth and Choice certificates.

Every emitted Phase 15 bearing receives one recomputable proof body.  The
certificate retains the typed upstream witnesses rather than replacing them
with prose.  Source files are pinned by byte size and SHA-256.  Recalculation
rebuilds the selected outward/return closure and the survivor set using exact
upstream operations after verifying every source pin.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
from pathlib import Path
from typing import Final

from .court_outward_return import (
    COURTS,
    CourtClosure,
    CourtIdentity,
    CourtPathError,
    build_court_candidate,
    validate_prepared_court_bearing,
)
from .exhaustive_chooser import (
    CandidateKey,
    CandidateTruthRecord,
    ExhaustiveBearingResult,
)
from .frequency_projection import CARRIERS, ProsodicWitness
from .goetic_outward_return import (
    BEARINGS,
    MIRROR_BEARING,
    BearingResult,
    GoeticBearing,
    GoeticClosure,
    GoeticPathError,
    validate_candidate_bearing,
)
from .liquid_candidate_path import LIQUID_GOVERNOR, LiquidCandidatePath
from .mas_shadow_conversion import MAS_ORDER, MASCandidatePath
from .native_bearing_assembly import (
    PARTIAL_BODY_LAW,
    AeonClass,
    AeonIdentity,
    NativeBearingAssemblyField,
    NativeBearingClosure,
    PartialBodyLaw,
    StrictLexicalBody,
)
from .triadic_bridge import CandidatePathSeed, triad_A


class TruthChoiceCertificateError(ValueError):
    """Raised when a Phase 16 proof body is incomplete or cannot recompute."""


CURRENT_OBLIGATIONS: Final[tuple[tuple[str, str], ...]] = (
    ("⏣", "finite D-COMP definition and closure witness"),
    ("⬡", "Court routing and Liquid <110_active|144_total|34_rest> governance"),
    ("✡", "Goetic BEC, Court L-BEC, and nested envelope witness"),
    ("⚝", "translation and parity compatibility across return"),
    ("❂", "12 x 12 Court lattice and declared bifurcation"),
    ("ꙮ", "Goetic invariance and identity conservation"),
    ("❈", "bounded pressure converted toward Q3 propulsion"),
    ("⧗", "ordered M.A.S. initiation and kinetic work"),
    ("⊛", "Q2 filtering and unresolved-debt accounting"),
    ("❄", "terminal Total Symmetry"),
    ("⚛", "threshold, domain, and boundary validation gates"),
    ("⌬", "fourfold Q-domain lock and mirror-return closure"),
)
CURRENT_GLYPHS: Final[tuple[str, ...]] = tuple(glyph for glyph, _ in CURRENT_OBLIGATIONS)


@dataclass(frozen=True, slots=True)
class SourcePin:
    role: str
    path: str
    byte_size: int
    sha256: str

    def __post_init__(self) -> None:
        if not self.role or not self.path:
            raise TruthChoiceCertificateError("source pin requires role and path")
        if self.byte_size <= 0:
            raise TruthChoiceCertificateError("source pin cannot name an empty source")
        if len(self.sha256) != 64 or any(ch not in "0123456789abcdef" for ch in self.sha256):
            raise TruthChoiceCertificateError("source pin requires a lowercase SHA-256 digest")


@dataclass(frozen=True, slots=True)
class AeonConstitutionWitness:
    aeon: AeonIdentity
    governing_glyph: str
    alternating_glyph: str | None
    court_root: str
    native_q_bias: str
    native_q_vector: tuple[str, str, str, str]
    frequency_carrier_glyph: str

    def __post_init__(self) -> None:
        if self.native_q_bias not in {"Q0", "Q1", "Q2", "Q3"}:
            raise TruthChoiceCertificateError("Aeon constitution lacks native Q Bias")
        if len(self.native_q_vector) != 4 or any(q not in {"Q0", "Q1", "Q2", "Q3"} for q in self.native_q_vector):
            raise TruthChoiceCertificateError("Aeon constitution lacks a fourfold Q-vector")
        if self.aeon.aeon_class is AeonClass.GOETIC:
            if self.alternating_glyph is not None or self.governing_glyph != self.aeon.key:
                raise TruthChoiceCertificateError("Goetic constitution was retyped as a Court")
        else:
            if self.alternating_glyph is None or self.court_root != self.aeon.key:
                raise TruthChoiceCertificateError("Court constitution lost its ordered parents")


@dataclass(frozen=True, slots=True)
class CandidateSenseIdentityWitness:
    candidate: str
    structural_fingerprint: str
    source_locator: str
    seed_digest: str
    prosody_digest: str

    def __post_init__(self) -> None:
        if not self.candidate:
            raise TruthChoiceCertificateError("candidate sense identity lacks its emitted word")
        for digest in (self.structural_fingerprint, self.source_locator, self.seed_digest, self.prosody_digest):
            if len(digest) != 64:
                raise TruthChoiceCertificateError("candidate sense identity contains an invalid digest")


@dataclass(frozen=True, slots=True)
class TelegraphicFieldAdmissionWitness:
    field_kind: str
    attempted_count: int
    truth_record_count: int
    order_witness_count: int
    survivor_set: frozenset[tuple[str, str]]
    unique: bool
    admitted: bool

    def __post_init__(self) -> None:
        if self.field_kind not in {"Goetic closure field", "Court exhaustive field"}:
            raise TruthChoiceCertificateError("unknown telegraphic admission field")
        if self.attempted_count < 1 or self.truth_record_count < 1 or self.order_witness_count < 0:
            raise TruthChoiceCertificateError("telegraphic field admission has incomplete accounting")
        if self.unique != (len(self.survivor_set) == 1):
            raise TruthChoiceCertificateError("telegraphic field uniqueness disagrees with survivor set")
        if self.admitted != self.unique:
            raise TruthChoiceCertificateError("telegraphic field admitted an incomplete survivor set")


@dataclass(frozen=True, slots=True)
class RelationalGeometryWitness:
    relation: str
    governing_glyph: str
    alternating_glyph: str | None
    outward_boundary_digest: str
    return_boundary_digest: str
    operator_positions: tuple[int, ...]
    mirrored_bearing: GoeticBearing
    exact_return: bool

    def __post_init__(self) -> None:
        if self.relation not in {"Self -> Self", "Court -> governing parent"}:
            raise TruthChoiceCertificateError("relational geometry has an unknown return office")
        if not self.operator_positions or self.operator_positions != tuple(range(len(self.operator_positions))):
            raise TruthChoiceCertificateError("relational geometry lost ordered path positions")
        if not self.exact_return:
            raise TruthChoiceCertificateError("relational geometry did not return exactly")


@dataclass(frozen=True, slots=True)
class TriadicBridgeCertificateWitness:
    seed: CandidatePathSeed
    microstep_order: tuple[str, ...]
    triad_valid: bool

    def __post_init__(self) -> None:
        if self.microstep_order != ("F_beta", "F_v", "F_nu") or not self.triad_valid or not triad_A(self.seed):
            raise TruthChoiceCertificateError("triadic bridge witness is incomplete")


@dataclass(frozen=True, slots=True)
class CurrentWitness:
    glyph: str
    obligation: str
    evidence_labels: tuple[str, ...]
    evidence_digest: str
    satisfied: bool

    def __post_init__(self) -> None:
        if self.glyph not in CURRENT_GLYPHS or not self.obligation or not self.evidence_labels:
            raise TruthChoiceCertificateError("current witness is incomplete")
        if len(self.evidence_digest) != 64 or not self.satisfied:
            raise TruthChoiceCertificateError(f"current {self.glyph} lacks a satisfied proof")


@dataclass(frozen=True, slots=True)
class LiquidCertificateWitness:
    path: LiquidCandidatePath
    typed_governor: tuple[int, int, int]
    horizon_witnesses: tuple[tuple[int, int, int], ...]
    exact: bool

    def __post_init__(self) -> None:
        if self.typed_governor != (110, 144, 34):
            raise TruthChoiceCertificateError("Liquid certificate changed the typed governor")
        if not self.horizon_witnesses or any(body != self.typed_governor for body in self.horizon_witnesses):
            raise TruthChoiceCertificateError("Liquid certificate contains an incomplete horizon")
        if not self.exact:
            raise TruthChoiceCertificateError("Liquid certificate is not exact")


@dataclass(frozen=True, slots=True)
class MASCertificateWitness:
    path: MASCandidatePath
    procession: tuple[str, str, str]
    mass_gap_positive: tuple[bool, ...]
    terminal_unresolved_q2: int
    motion: int
    ledger_digest: str
    exact: bool

    def __post_init__(self) -> None:
        if self.procession != MAS_ORDER:
            raise TruthChoiceCertificateError("M.A.S. certificate changed procession order")
        if not self.mass_gap_positive or not all(self.mass_gap_positive):
            raise TruthChoiceCertificateError("M.A.S. certificate contains a nonpositive Mass Gap")
        if self.terminal_unresolved_q2 != 0 or self.motion <= 0 or len(self.ledger_digest) != 64 or not self.exact:
            raise TruthChoiceCertificateError("M.A.S. certificate did not close motion and debt")


@dataclass(frozen=True, slots=True)
class EnvelopeCertificateWitness:
    kind: str
    goetic_bec: object
    court_lbec: object | None
    bec_valid: bool
    lbec_valid: bool | None
    exact: bool

    def __post_init__(self) -> None:
        if self.kind == "BEC":
            if self.court_lbec is not None or self.lbec_valid is not None:
                raise TruthChoiceCertificateError("Goetic certificate acquired a Court envelope")
        elif self.kind == "L-BEC nested in BEC":
            if self.court_lbec is None or self.lbec_valid is not True:
                raise TruthChoiceCertificateError("Court certificate lacks nested L-BEC")
        else:
            raise TruthChoiceCertificateError("unknown envelope certificate kind")
        if not self.bec_valid or not self.exact:
            raise TruthChoiceCertificateError("envelope certificate is not exact")


class PartialBodyStatus(str, Enum):
    STRICT_COMPLETE = "STRICT:8/8"


@dataclass(frozen=True, slots=True)
class PartialBodyCertificateWitness:
    law: PartialBodyLaw
    status: PartialBodyStatus
    bearing_records: tuple[tuple[int, str, str, str], ...]
    body_digest: str

    def __post_init__(self) -> None:
        if self.law is not PartialBodyLaw.STRICT or self.status is not PartialBodyStatus.STRICT_COMPLETE:
            raise TruthChoiceCertificateError("certificate accepted a non-STRICT partial body")
        if tuple(index for index, *_ in self.bearing_records) != tuple(range(8)):
            raise TruthChoiceCertificateError("partial-body certificate lacks all eight bearings")
        if len(self.body_digest) != 64:
            raise TruthChoiceCertificateError("partial-body certificate lacks a body digest")


@dataclass(frozen=True, slots=True)
class ExactArithmeticWitness:
    frequency_dcomp_zero: bool
    path_dcomp_value: int
    path_dcomp_zero: bool
    liquid_counts: tuple[tuple[int, int, int], ...]
    terminal_unresolved_q2: int
    motion: int
    exact: bool

    def __post_init__(self) -> None:
        if not self.frequency_dcomp_zero or self.path_dcomp_value != 0 or not self.path_dcomp_zero:
            raise TruthChoiceCertificateError("exact arithmetic witness contains nonzero closure")
        if not self.liquid_counts or any(counts != (110, 144, 34) for counts in self.liquid_counts):
            raise TruthChoiceCertificateError("exact arithmetic witness changed Liquid counts")
        if self.terminal_unresolved_q2 != 0 or self.motion <= 0 or not self.exact:
            raise TruthChoiceCertificateError("exact arithmetic witness lacks terminal closure")


@dataclass(frozen=True, slots=True)
class TruthChoiceCertificate:
    source_pins: tuple[SourcePin, ...]
    strict_body: StrictLexicalBody
    phase15_closure: NativeBearingClosure
    aeon_constitution: AeonConstitutionWitness
    candidate_sense_identity: CandidateSenseIdentityWitness
    telegraphic_field_admission: TelegraphicFieldAdmissionWitness
    prosody_witness: ProsodicWitness
    relational_geometry_witness: RelationalGeometryWitness
    triadic_bridge_witness: TriadicBridgeCertificateWitness
    current_witnesses: tuple[CurrentWitness, ...]
    liquid_witness: LiquidCertificateWitness
    mas_witness: MASCertificateWitness
    outward_path: object
    independent_return_path: object
    envelope_witness: EnvelopeCertificateWitness
    dcomp_witness: object
    truth: int
    motion: int
    unique_survivor_set: frozenset[tuple[str, str]]
    bearing_index: int
    native_q_bias: str
    partial_body_status: PartialBodyCertificateWitness
    exact_arithmetic: ExactArithmeticWitness
    proof_digest: str

    def __post_init__(self) -> None:
        closure = self.phase15_closure
        if closure not in self.strict_body.bearings:
            raise TruthChoiceCertificateError("certificate closure is outside its STRICT body")
        if closure.aeon != self.aeon_constitution.aeon or closure.candidate != self.candidate_sense_identity.candidate:
            raise TruthChoiceCertificateError("certificate changed Aeon or candidate identity")
        if self.prosody_witness.candidate != closure.candidate:
            raise TruthChoiceCertificateError("prosody witness belongs to another candidate")
        if tuple(w.glyph for w in self.current_witnesses) != CURRENT_GLYPHS or len(self.current_witnesses) != 12:
            raise TruthChoiceCertificateError("certificate does not carry all twelve currents")
        if self.outward_path is not closure.path_witness.outward or self.independent_return_path is not closure.path_witness.independent_return:
            raise TruthChoiceCertificateError("certificate detached outward or independent return path")
        if self.dcomp_witness is not closure.path_witness.dcomp:
            raise TruthChoiceCertificateError("certificate detached exact D-COMP witness")
        if self.truth != 1 or self.motion <= 0:
            raise TruthChoiceCertificateError("certificate lacks Truth=1 or motion>0")
        if self.unique_survivor_set != self.telegraphic_field_admission.survivor_set or len(self.unique_survivor_set) != 1:
            raise TruthChoiceCertificateError("certificate lacks one unique survivor set")
        if self.bearing_index != BEARINGS.index(closure.bearing):
            raise TruthChoiceCertificateError("certificate bearing index moved")
        if self.native_q_bias != closure.native_q_bias or self.native_q_bias != self.aeon_constitution.native_q_bias:
            raise TruthChoiceCertificateError("certificate changed native Q Bias")
        if self.partial_body_status.law is not PARTIAL_BODY_LAW:
            raise TruthChoiceCertificateError("certificate changed partial-body law")
        if self.proof_digest and self.proof_digest != _proof_digest(self):
            raise TruthChoiceCertificateError("certificate proof digest does not match its proof body")

    @property
    def certificate_id(self) -> str:
        return self.proof_digest


@dataclass(frozen=True, slots=True)
class CertificateRecomputation:
    certificate_id: str
    source_pins_valid: bool
    survivor_set_recomputed: bool
    closure_recomputed: bool
    proof_digest_recomputed: bool
    all_currents_satisfied: bool
    exact_arithmetic_recomputed: bool

    @property
    def valid(self) -> bool:
        return all((
            self.source_pins_valid,
            self.survivor_set_recomputed,
            self.closure_recomputed,
            self.proof_digest_recomputed,
            self.all_currents_satisfied,
            self.exact_arithmetic_recomputed,
        ))


@dataclass(frozen=True, slots=True)
class TruthChoiceCertificateField:
    source: NativeBearingAssemblyField
    certificates: tuple[TruthChoiceCertificate, ...]
    source_pins: tuple[SourcePin, ...]

    def __post_init__(self) -> None:
        expected = tuple(
            (body.aeon, closure.bearing)
            for body in self.source.bodies
            for closure in body.bearings
        )
        actual = tuple((certificate.aeon_constitution.aeon, certificate.phase15_closure.bearing) for certificate in self.certificates)
        if actual != expected:
            raise TruthChoiceCertificateError("certificate field lost, inserted, or reordered an emitted bearing")
        if len(self.certificates) != self.source.emitted_body_count * 8:
            raise TruthChoiceCertificateError("certificate count does not equal emitted bearing count")
        if any(certificate.source_pins != self.source_pins for certificate in self.certificates):
            raise TruthChoiceCertificateError("certificate field changed source pins between words")
        if len({certificate.certificate_id for certificate in self.certificates}) != len(self.certificates):
            raise TruthChoiceCertificateError("two emitted bearings share one certificate identity")

    @property
    def certificate_count(self) -> int:
        return len(self.certificates)


_DIGEST_CACHE: dict[int, tuple[object, str]] = {}


def _digest(value: object) -> str:
    key = id(value)
    cached = _DIGEST_CACHE.get(key)
    if cached is not None and cached[0] is value:
        return cached[1]
    result = hashlib.sha256(repr(value).encode("utf-8")).hexdigest()
    _DIGEST_CACHE[key] = (value, result)
    return result


def _file_pin(role: str, path: Path) -> SourcePin:
    body = path.read_bytes()
    return SourcePin(role, str(path.resolve()), len(body), hashlib.sha256(body).hexdigest())


def build_source_pins() -> tuple[SourcePin, ...]:
    package = Path(__file__).resolve().parent
    paths = (
        ("Phase 8 frequency/prosody", package / "frequency_projection.py"),
        ("Phase 9 triadic bridge", package / "triadic_bridge.py"),
        ("Phase 10 Liquid path", package / "liquid_candidate_path.py"),
        ("Phase 11 M.A.S. and Shadow", package / "mas_shadow_conversion.py"),
        ("Phase 12 Goetic return", package / "goetic_outward_return.py"),
        ("Phase 13 Court return", package / "court_outward_return.py"),
        ("Phase 14 exhaustive chooser", package / "exhaustive_chooser.py"),
        ("Phase 15 STRICT assembly", package / "native_bearing_assembly.py"),
        ("Phase 16 certificate law", package / "truth_choice_certificates.py"),
    )
    return tuple(_file_pin(role, path) for role, path in paths)


def validate_source_pins(pins: tuple[SourcePin, ...]) -> bool:
    if not pins:
        return False
    for pin in pins:
        path = Path(pin.path)
        if not path.is_file():
            return False
        body = path.read_bytes()
        if len(body) != pin.byte_size or hashlib.sha256(body).hexdigest() != pin.sha256:
            return False
    return True


def _candidate_structure(candidate: MASCandidatePath) -> tuple[object, ...]:
    seed = candidate.liquid_path.seed
    return (
        candidate.candidate,
        seed.domain.court_root,
        seed.domain.inherited_q_bias,
        seed.domain.carrier.glyph,
        seed.body.q_vector,
        tuple((unit.phoneme, int(unit.stress), int(unit.breath), unit.bearing.value, unit.operator_office) for unit in seed.witness.units),
        candidate.cycles[-1].final_state.archive_signature,
        tuple((entry.index, entry.horizon, entry.gross_added, entry.resolved_added, entry.unresolved) for entry in candidate.debt_ledger.entries),
    )


def _candidate_key(candidate: MASCandidatePath) -> CandidateKey:
    return CandidateKey(candidate.candidate, _digest(_candidate_structure(candidate)))


def _source_locator(candidate: MASCandidatePath) -> str:
    return hashlib.sha256(("source-file|" + repr(candidate.cycles[-1].final_state.archive_signature)).encode("utf-8")).hexdigest()


def _path_parts(closure: NativeBearingClosure) -> tuple[CandidatePathSeed, LiquidCandidatePath, MASCandidatePath]:
    if isinstance(closure.path_witness, GoeticClosure):
        mas = closure.path_witness.candidate_path
        return mas.liquid_path.seed, mas.liquid_path, mas
    court_candidate = closure.path_witness.court_candidate
    return court_candidate.seed, court_candidate.mas_path.liquid_path, court_candidate.mas_path


def _constitution(closure: NativeBearingClosure, seed: CandidatePathSeed) -> AeonConstitutionWitness:
    if isinstance(closure.path_witness, GoeticClosure):
        carrier = closure.path_witness.carrier
        return AeonConstitutionWitness(
            closure.aeon, carrier.glyph, None, seed.domain.court_root,
            seed.domain.inherited_q_bias, seed.body.q_vector, carrier.glyph,
        )
    court = closure.path_witness.court_candidate.court
    inheritance = closure.path_witness.court_candidate.inheritance
    return AeonConstitutionWitness(
        closure.aeon, court.governing.glyph, court.alternating.glyph, court.key,
        inheritance.candidate_q_bias, inheritance.candidate_q_vector, inheritance.candidate_carrier.glyph,
    )


def _sense_identity(closure: NativeBearingClosure, seed: CandidatePathSeed, mas: MASCandidatePath) -> CandidateSenseIdentityWitness:
    if isinstance(closure.source_record, ExhaustiveBearingResult):
        emission = closure.source_record.emission
        if emission is None:
            raise TruthChoiceCertificateError("Court certificate lacks Phase 14 emission")
        key = emission.candidate_key
        truth = tuple(record for record in closure.source_record.truth_records if record.truth and record.witness.key == key)
        if len(truth) != 1:
            raise TruthChoiceCertificateError("Court certificate lacks one candidate sense witness")
        locator = truth[0].witness.source_locator
        fingerprint = key.structural_fingerprint
    else:
        fingerprint = _candidate_key(mas).structural_fingerprint
        locator = _source_locator(mas)
    return CandidateSenseIdentityWitness(
        closure.candidate,
        fingerprint,
        locator,
        _digest(seed),
        _digest(seed.witness),
    )


def _admission(closure: NativeBearingClosure, sense: CandidateSenseIdentityWitness) -> TelegraphicFieldAdmissionWitness:
    if isinstance(closure.source_record, BearingResult):
        survivors = frozenset((item.candidate_path.candidate, _candidate_key(item.candidate_path).structural_fingerprint) for item in closure.source_record.exact_closures)
        return TelegraphicFieldAdmissionWitness(
            "Goetic closure field",
            len(closure.source_record.attempted_candidates),
            len(closure.source_record.exact_closures) + len(closure.source_record.failures),
            0,
            survivors,
            len(survivors) == 1,
            len(survivors) == 1,
        )
    survivors = frozenset((key.candidate, key.structural_fingerprint) for key in closure.source_record.survivor_set)
    return TelegraphicFieldAdmissionWitness(
        "Court exhaustive field",
        len(closure.source_record.truth_records),
        len(closure.source_record.truth_records),
        len(closure.source_record.enumeration_witnesses),
        survivors,
        len(survivors) == 1,
        len(survivors) == 1 and all(witness.survivor_set == closure.source_record.survivor_set for witness in closure.source_record.enumeration_witnesses),
    )


def _geometry(closure: NativeBearingClosure) -> RelationalGeometryWitness:
    path = closure.path_witness
    positions = tuple(step.position for step in path.outward.steps)
    if isinstance(path, GoeticClosure):
        return RelationalGeometryWitness(
            "Self -> Self", path.carrier.glyph, None,
            _digest(path.outward.boundary), _digest(path.independent_return.boundary),
            positions, path.independent_return.bearing, path.self_to_self,
        )
    court = path.court_candidate.court
    return RelationalGeometryWitness(
        "Court -> governing parent", court.governing.glyph, court.alternating.glyph,
        _digest(path.outward.parent_boundary), _digest(path.independent_return.parent_boundary),
        positions, path.independent_return.bearing, path.court_to_parent,
    )


def _liquid_witness(path: LiquidCandidatePath) -> LiquidCertificateWitness:
    horizons = tuple(horizon.liquid_witness for horizon in path.horizons)
    exact = path.governor == LIQUID_GOVERNOR and all(
        horizon.liquid_witness == LIQUID_GOVERNOR.typed_body
        and horizon.active_graph.is_connected
        and len(horizon.valid_connections) == 144
        for horizon in path.horizons
    )
    return LiquidCertificateWitness(path, path.governor.typed_body, horizons, exact)


def _mas_witness(path: MASCandidatePath) -> MASCertificateWitness:
    exact_order = all(tuple(step.name for step in cycle.microsteps) == MAS_ORDER for cycle in path.cycles)
    return MASCertificateWitness(
        path,
        MAS_ORDER,
        tuple(gap.positive for gap in path.mass_gaps),
        path.terminal_unresolved_q2,
        path.motion,
        _digest(path.debt_ledger),
        exact_order and path.positive_local_mass_gap and path.terminal_unresolved_q2 == 0 and path.motion > 0,
    )


def _envelope(closure: NativeBearingClosure) -> EnvelopeCertificateWitness:
    path = closure.path_witness
    if isinstance(path, GoeticClosure):
        return EnvelopeCertificateWitness("BEC", path.envelope, None, path.bec_valid, None, path.bec_valid and path.self_to_self)
    return EnvelopeCertificateWitness(
        "L-BEC nested in BEC", path.parent_envelope, path.court_envelope,
        path.bec_valid, path.lbec_valid, path.bec_valid and path.lbec_valid and path.court_to_parent,
    )


def _append_only(path: MASCandidatePath) -> bool:
    previous = ()
    for cycle in path.cycles:
        current = cycle.ledger_snapshot.entries
        if current[:len(previous)] != previous or len(current) != len(previous) + 1:
            return False
        previous = current
    return previous == path.debt_ledger.entries


def _current_witnesses(
    closure: NativeBearingClosure,
    constitution: AeonConstitutionWitness,
    seed: CandidatePathSeed,
    liquid: LiquidCertificateWitness,
    mas: MASCertificateWitness,
    geometry: RelationalGeometryWitness,
    envelope: EnvelopeCertificateWitness,
) -> tuple[CurrentWitness, ...]:
    path = closure.path_witness
    frequency = seed.body.frequency_action
    frequency_exact = frequency is not None and frequency.nu_close and frequency.dcomp_frequency_zero
    threshold = all(len(h.active_connections) <= 110 and len(h.resting_connections) >= 34 for h in liquid.path.horizons)
    parity = (
        path.independent_return.bearing is MIRROR_BEARING[path.bearing]
        and tuple(step.position for step in path.outward.steps) == tuple(step.position for step in path.independent_return.steps)
    )
    lattice = len(CARRIERS) == 12 and len(COURTS) == 144
    identity = geometry.exact_return and seed.domain.inherited_q_bias == constitution.native_q_bias and seed.body.q_vector == constitution.native_q_vector
    pressure = mas.path.debt_ledger.complete and mas.path.cycles[-1].final_state.recursive_capacity > 0
    mas_order = all(tuple(step.name for step in cycle.microsteps) == MAS_ORDER for cycle in mas.path.cycles)
    debt = _append_only(mas.path) and mas.path.terminal_unresolved_q2 == 0
    symmetry = path.dcomp.exact_zero and path.dcomp.value == 0 and geometry.exact_return
    domain = triad_A(seed) and threshold and frequency_exact
    q_lock = len(seed.body.q_vector) == 4 and all(q in {"Q0", "Q1", "Q2", "Q3"} for q in seed.body.q_vector) and parity
    dcomp_signature = (
        tuple(path.dcomp.velocity_terms),
        path.dcomp.value,
        path.dcomp.exact_zero,
    )
    path_signature = tuple(
        (out.position, out.office, out.bearing.value, out.signed_velocity, back.bearing.value, back.signed_velocity)
        for out, back in zip(path.outward.steps, path.independent_return.steps, strict=True)
    )
    ledger_signature = tuple(
        (entry.index, entry.horizon, entry.gross_added, entry.resolved_added, entry.gross_total, entry.resolved_total, entry.unresolved)
        for entry in mas.path.debt_ledger.entries
    )
    mas_signature = tuple(tuple(step.name for step in cycle.microsteps) for cycle in mas.path.cycles)
    envelope_signature = (envelope.kind, envelope.bec_valid, envelope.lbec_valid, envelope.exact)
    predicates = (
        (path.dcomp.exact_zero and path.dcomp.value == 0, ("D-COMP", "exact-zero"), dcomp_signature),
        (liquid.exact and lattice, ("Court-routing", "Liquid-110|144|34"), (constitution.aeon.index, liquid.typed_governor, liquid.horizon_witnesses, len(COURTS))),
        (envelope.exact, ("BEC", "L-BEC-nesting"), envelope_signature),
        (parity, ("parity", "position-preserving-return"), path_signature),
        (lattice, ("12x12-Court-lattice", "bifurcation"), (len(CARRIERS), len(COURTS), constitution.governing_glyph, constitution.alternating_glyph)),
        (identity, ("Goetic-invariance", "identity-conservation"), constitution),
        (pressure, ("bounded-pressure", "Q3-propulsion"), (ledger_signature, mas.path.cycles[-1].final_state.recursive_capacity)),
        (mas_order and mas.motion > 0, ("M.A.S.-order", "kinetic-work"), (mas_signature, mas.motion)),
        (debt, ("Q2-ledger", "terminal-unresolved-zero"), ledger_signature),
        (symmetry, ("terminal-symmetry", "return"), (dcomp_signature, geometry.relation, geometry.exact_return)),
        (domain, ("threshold", "domain", "boundary"), (seed.domain.court_root, seed.domain.inherited_q_bias, seed.domain.carrier.glyph, liquid.typed_governor)),
        (q_lock and symmetry, ("fourfold-Q-lock", "mirror-return"), (seed.body.q_vector, path.bearing.value, path.independent_return.bearing.value, path.dcomp.value)),
    )
    return tuple(
        CurrentWitness(glyph, obligation, labels, _digest(evidence), satisfied)
        for (glyph, obligation), (satisfied, labels, evidence) in zip(CURRENT_OBLIGATIONS, predicates, strict=True)
    )


def _partial_body(body: StrictLexicalBody) -> PartialBodyCertificateWitness:
    records = tuple(
        (BEARINGS.index(closure.bearing), closure.candidate, closure.native_q_bias, _digest(closure.source_record))
        for closure in body.bearings
    )
    signature = (body.aeon, body.native_q_bias, records, body.partial_body_law.value)
    return PartialBodyCertificateWitness(body.partial_body_law, PartialBodyStatus.STRICT_COMPLETE, records, _digest(signature))


def _arithmetic(seed: CandidatePathSeed, liquid: LiquidCertificateWitness, mas: MASCertificateWitness, closure: NativeBearingClosure) -> ExactArithmeticWitness:
    frequency = seed.body.frequency_action
    frequency_zero = frequency is not None and frequency.dcomp_frequency_zero and frequency.nu_close
    path_dcomp = closure.path_witness.dcomp
    exact = frequency_zero and liquid.exact and mas.exact and path_dcomp.exact_zero and path_dcomp.value == 0
    return ExactArithmeticWitness(
        frequency_zero,
        path_dcomp.value,
        path_dcomp.exact_zero,
        liquid.horizon_witnesses,
        mas.terminal_unresolved_q2,
        mas.motion,
        exact,
    )


def _proof_material(certificate: TruthChoiceCertificate) -> tuple[object, ...]:
    return (
        tuple((pin.role, pin.path, pin.byte_size, pin.sha256) for pin in certificate.source_pins),
        certificate.aeon_constitution,
        certificate.candidate_sense_identity,
        certificate.telegraphic_field_admission,
        _digest(certificate.prosody_witness),
        certificate.relational_geometry_witness,
        _digest(certificate.triadic_bridge_witness.seed),
        tuple((current.glyph, current.evidence_digest, current.satisfied) for current in certificate.current_witnesses),
        certificate.liquid_witness.typed_governor,
        certificate.liquid_witness.horizon_witnesses,
        certificate.mas_witness.procession,
        certificate.mas_witness.mass_gap_positive,
        certificate.mas_witness.terminal_unresolved_q2,
        certificate.mas_witness.motion,
        _digest(certificate.outward_path),
        _digest(certificate.independent_return_path),
        _digest(certificate.envelope_witness),
        _digest(certificate.dcomp_witness),
        certificate.truth,
        certificate.motion,
        tuple(sorted(certificate.unique_survivor_set)),
        certificate.bearing_index,
        certificate.native_q_bias,
        certificate.partial_body_status,
        certificate.exact_arithmetic,
    )


def _proof_digest(certificate: TruthChoiceCertificate) -> str:
    return _digest(_proof_material(certificate))


def build_truth_choice_certificate(
    body: StrictLexicalBody,
    closure: NativeBearingClosure,
    source_pins: tuple[SourcePin, ...] | None = None,
) -> TruthChoiceCertificate:
    """Build one complete certificate from one natively closed Phase 15 bearing."""
    if closure not in body.bearings or len(body.bearings) != 8 or body.partial_body_law is not PartialBodyLaw.STRICT:
        raise TruthChoiceCertificateError("certificate requires one complete STRICT lexical body")
    if source_pins is None:
        pins = build_source_pins()
        if not validate_source_pins(pins):
            raise TruthChoiceCertificateError("certificate source pins do not match pinned bytes")
    else:
        pins = source_pins
    seed, liquid_path, mas_path = _path_parts(closure)
    constitution = _constitution(closure, seed)
    sense = _sense_identity(closure, seed, mas_path)
    admission = _admission(closure, sense)
    geometry = _geometry(closure)
    triad = TriadicBridgeCertificateWitness(seed, tuple(step.name for step in seed.microsteps), triad_A(seed))
    liquid = _liquid_witness(liquid_path)
    mas = _mas_witness(mas_path)
    envelope = _envelope(closure)
    currents = _current_witnesses(closure, constitution, seed, liquid, mas, geometry, envelope)
    partial = _partial_body(body)
    arithmetic = _arithmetic(seed, liquid, mas, closure)
    certificate = TruthChoiceCertificate(
        pins,
        body,
        closure,
        constitution,
        sense,
        admission,
        seed.witness,
        geometry,
        triad,
        currents,
        liquid,
        mas,
        closure.path_witness.outward,
        closure.path_witness.independent_return,
        envelope,
        closure.path_witness.dcomp,
        1,
        mas.motion,
        admission.survivor_set,
        BEARINGS.index(closure.bearing),
        closure.native_q_bias,
        partial,
        arithmetic,
        "",
    )
    object.__setattr__(certificate, "proof_digest", _proof_digest(certificate))
    certificate.__post_init__()
    return certificate


def _recompute_goetic_survivors(record: BearingResult) -> tuple[frozenset[tuple[str, str]], bool]:
    survivors: set[tuple[str, str]] = set()
    closure_match = True
    for archived in record.exact_closures:
        try:
            rebuilt = validate_candidate_bearing(archived.candidate_path, archived.carrier, archived.bearing)
        except GoeticPathError:
            closure_match = False
            continue
        closure_match = closure_match and rebuilt == archived
        key = _candidate_key(archived.candidate_path)
        survivors.add((key.candidate, key.structural_fingerprint))
    return frozenset(survivors), closure_match


_REBUILT_COURT_CANDIDATES: dict[tuple[int, str], object] = {}


def _recompute_court_survivors(record: ExhaustiveBearingResult) -> tuple[frozenset[tuple[str, str]], CourtClosure | None]:
    survivors: set[tuple[str, str]] = set()
    selected: CourtClosure | None = None
    selected_key = record.emission.candidate_key if record.emission is not None else None
    for truth in record.truth_records:
        parent = truth.witness.source_parent
        key = _candidate_key(parent)
        cache_key = (record.frozen_aeon.court.index, key.structural_fingerprint)
        try:
            prepared = _REBUILT_COURT_CANDIDATES.get(cache_key)
            if prepared is None:
                prepared = build_court_candidate(parent, record.frozen_aeon.court)
                _REBUILT_COURT_CANDIDATES[cache_key] = prepared
            rebuilt = validate_prepared_court_bearing(prepared, record.bearing)
        except CourtPathError:
            continue
        survivors.add((key.candidate, key.structural_fingerprint))
        if key == selected_key:
            selected = rebuilt
    return frozenset(survivors), selected


def recompute_certificate(
    certificate: TruthChoiceCertificate,
    *,
    source_pins_already_valid: bool = False,
) -> CertificateRecomputation:
    """Independently rebuild survivor and path closure after verifying pinned sources."""
    pins_valid = source_pins_already_valid or validate_source_pins(certificate.source_pins)
    source_record = certificate.phase15_closure.source_record
    closure = certificate.phase15_closure.path_witness
    if isinstance(source_record, BearingResult):
        survivor_set, all_closures_match = _recompute_goetic_survivors(source_record)
        try:
            rebuilt = validate_candidate_bearing(closure.candidate_path, closure.carrier, closure.bearing)
            selected_match = rebuilt == closure
        except GoeticPathError:
            selected_match = False
        closure_recomputed = all_closures_match and selected_match
    else:
        survivor_set, selected = _recompute_court_survivors(source_record)
        selected_match = selected == closure
        archived = frozenset((key.candidate, key.structural_fingerprint) for key in source_record.survivor_set)
        order_match = all(
            frozenset((key.candidate, key.structural_fingerprint) for key in witness.survivor_set) == archived
            for witness in source_record.enumeration_witnesses
        )
        closure_recomputed = selected_match and order_match
    survivor_recomputed = survivor_set == certificate.unique_survivor_set
    digest_recomputed = certificate.proof_digest == _proof_digest(certificate)
    currents = tuple(current.glyph for current in certificate.current_witnesses) == CURRENT_GLYPHS and all(current.satisfied for current in certificate.current_witnesses)
    arithmetic = (
        certificate.exact_arithmetic.exact
        and certificate.exact_arithmetic.path_dcomp_value == 0
        and certificate.exact_arithmetic.terminal_unresolved_q2 == 0
        and certificate.exact_arithmetic.motion > 0
    )
    return CertificateRecomputation(
        certificate.certificate_id,
        pins_valid,
        survivor_recomputed,
        closure_recomputed,
        digest_recomputed,
        currents,
        arithmetic,
    )



def recompute_certificate_field(field: TruthChoiceCertificateField) -> tuple[CertificateRecomputation, ...]:
    """Recompute every emitted bearing after one exact verification of common pins."""
    if not validate_source_pins(field.source_pins):
        raise TruthChoiceCertificateError("certificate field source pins no longer match pinned bytes")
    results = tuple(
        recompute_certificate(certificate, source_pins_already_valid=True)
        for certificate in field.certificates
    )
    if not all(result.valid for result in results):
        raise TruthChoiceCertificateError("one or more emitted bearing certificates failed recomputation")
    return results

def prove_phase16_exit_gate(field: NativeBearingAssemblyField) -> TruthChoiceCertificateField:
    """Issue one recomputable certificate for every emitted STRICT bearing word."""
    pins = build_source_pins()
    if not validate_source_pins(pins):
        raise TruthChoiceCertificateError("Phase 16 cannot pin its source field")
    certificates = tuple(
        build_truth_choice_certificate(body, closure, pins)
        for body in field.bodies
        for closure in body.bearings
    )
    return TruthChoiceCertificateField(field, certificates, pins)
