"""Phase 14 exhaustive, order-independent Court chooser.

The chooser evaluates complete bearing sub-fields only after freezing the Court
Aeon's governing Bias, governing Q-vector, and alternating frequency carrier.
Candidate truth is a local immutable witness.  No candidate can emit while the
sub-field is still being traversed.

Selection is replayed under manifest order, reversed order, several fixed
permutations, a file-source shuffle, and a parallel-chunk completion order.  A
bearing may emit only when every replay returns the same survivor set and that
set contains exactly one structural candidate.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
from typing import Final, Mapping

from .court_outward_return import (
    COURTS,
    CourtCandidate,
    CourtClosure,
    CourtIdentity,
    CourtPathError,
    build_court_candidate,
    validate_prepared_court_bearing,
)
from .goetic_outward_return import BEARINGS, GoeticBearing
from .mas_shadow_conversion import MASCandidatePath, MASGlobalField


class ExhaustiveChooserError(ValueError):
    """Raised when Phase 14 cannot preserve one frozen mathematical field."""


class EnumerationOrder(str, Enum):
    MANIFEST = "complete-manifest-order"
    REVERSED = "reversed-manifest-order"
    ROTATE_ONE = "deterministic-rotate-one"
    EVEN_ODD = "deterministic-even-odd"
    STRIDE_THREE = "deterministic-stride-three"
    FILE_SHUFFLED = "file-shuffled-source-order"
    PARALLEL_CHUNK = "parallel-chunk-order"


ENUMERATION_ORDERS: Final[tuple[EnumerationOrder, ...]] = tuple(EnumerationOrder)
if len(ENUMERATION_ORDERS) != 7:
    raise RuntimeError("Phase 14 requires all declared enumeration-order proofs")


@dataclass(frozen=True, slots=True, order=True)
class CandidateKey:
    candidate: str
    structural_fingerprint: str


@dataclass(frozen=True, slots=True)
class FrozenCourtAeon:
    """One Court held fixed while only L_b changes across bearings."""

    court: CourtIdentity
    native_q_bias: str
    native_q_vector: tuple[str, str, str, str]
    frequency_carrier_glyph: str

    def __post_init__(self) -> None:
        if not self.native_q_bias:
            raise ExhaustiveChooserError("frozen Court lacks its governing Q Bias")
        if len(self.native_q_vector) != 4:
            raise ExhaustiveChooserError("frozen Court requires one four-coordinate parent vector")
        if self.frequency_carrier_glyph != self.court.alternating.glyph:
            raise ExhaustiveChooserError("frozen Court changed the alternating carrier")


@dataclass(frozen=True, slots=True)
class CandidateWitness:
    """Candidate-local structure used by Truth_A(w), never an enumeration index."""

    key: CandidateKey
    source_parent: MASCandidatePath
    frozen_aeon: FrozenCourtAeon
    source_locator: str

    def __post_init__(self) -> None:
        seed = self.source_parent.liquid_path.seed
        if seed.domain.carrier != self.frozen_aeon.court.governing:
            raise ExhaustiveChooserError("candidate witness entered through a foreign governing parent")
        if seed.domain.inherited_q_bias != self.frozen_aeon.native_q_bias:
            raise ExhaustiveChooserError("candidate witness changed frozen Q Bias")
        if seed.body.q_vector != self.frozen_aeon.native_q_vector:
            raise ExhaustiveChooserError("candidate witness changed frozen Q-vector")
        if not self.source_locator:
            raise ExhaustiveChooserError("candidate witness lacks a stable source locator")


@dataclass(frozen=True, slots=True)
class BearingSubfield:
    frozen_aeon: FrozenCourtAeon
    bearing: GoeticBearing
    candidates: tuple[MASCandidatePath, ...]

    def __post_init__(self) -> None:
        keys = tuple(_candidate_key(candidate) for candidate in self.candidates)
        if len(set(keys)) != len(keys):
            raise ExhaustiveChooserError("bearing sub-field duplicated one structural candidate")
        for candidate in self.candidates:
            seed = candidate.liquid_path.seed
            if seed.domain.carrier != self.frozen_aeon.court.governing:
                raise ExhaustiveChooserError("L_b contains a candidate from another governing parent")
            if seed.domain.inherited_q_bias != self.frozen_aeon.native_q_bias:
                raise ExhaustiveChooserError("L_b changed the frozen Aeon Q Bias")
            if seed.body.q_vector != self.frozen_aeon.native_q_vector:
                raise ExhaustiveChooserError("L_b changed the frozen Aeon Q-vector")


@dataclass(frozen=True, slots=True)
class CompleteSubfieldManifest:
    source: MASGlobalField
    subfields: tuple[BearingSubfield, ...]

    def __post_init__(self) -> None:
        expected = tuple((court, bearing) for court in COURTS for bearing in BEARINGS)
        actual = tuple((entry.frozen_aeon.court, entry.bearing) for entry in self.subfields)
        if actual != expected:
            raise ExhaustiveChooserError("complete manifest must contain all 144 x 8 Court bearings in order")
        source_ids = {id(candidate) for candidate in self.source.survivors}
        if any(id(candidate) not in source_ids for entry in self.subfields for candidate in entry.candidates):
            raise ExhaustiveChooserError("complete manifest contains a candidate outside its Phase 11 source")
        for offset in range(0, len(self.subfields), 8):
            group = self.subfields[offset:offset + 8]
            if any(entry.frozen_aeon != group[0].frozen_aeon for entry in group):
                raise ExhaustiveChooserError("Aeon was not frozen across all eight bearing runs")


@dataclass(frozen=True, slots=True)
class CandidateTruthRecord:
    witness: CandidateWitness
    court_candidate: CourtCandidate | None
    closure: CourtClosure | None
    failure_reason: str | None

    def __post_init__(self) -> None:
        if (self.closure is None) == (self.failure_reason is None):
            raise ExhaustiveChooserError("candidate truth record must contain closure xor failure")
        if self.closure is not None:
            if self.court_candidate is None or self.closure.court_candidate != self.court_candidate:
                raise ExhaustiveChooserError("truth closure is detached from its Court candidate")
            if not self.closure.dcomp.exact_zero:
                raise ExhaustiveChooserError("Truth_A(w)=1 requires exact D_T zero")

    @property
    def truth(self) -> bool:
        return self.closure is not None


@dataclass(frozen=True, slots=True)
class EnumerationWitness:
    order: EnumerationOrder
    candidate_order: tuple[CandidateKey, ...]
    survivor_set: frozenset[CandidateKey]


@dataclass(frozen=True, slots=True)
class ChooserEmission:
    court: CourtIdentity
    bearing: GoeticBearing
    candidate_key: CandidateKey
    candidate: str
    native_q_bias: str


@dataclass(frozen=True, slots=True)
class ChooserFailureEvidence:
    court: CourtIdentity
    bearing: GoeticBearing
    reason: str
    survivor_set: frozenset[CandidateKey]
    candidate_failures: tuple[tuple[CandidateKey, str], ...]


@dataclass(frozen=True, slots=True)
class ExhaustiveBearingResult:
    frozen_aeon: FrozenCourtAeon
    bearing: GoeticBearing
    truth_records: tuple[CandidateTruthRecord, ...]
    enumeration_witnesses: tuple[EnumerationWitness, ...]
    survivor_set: frozenset[CandidateKey]
    emission: ChooserEmission | None
    failure_evidence: ChooserFailureEvidence | None

    def __post_init__(self) -> None:
        if tuple(w.order for w in self.enumeration_witnesses) != ENUMERATION_ORDERS:
            raise ExhaustiveChooserError("bearing lacks the complete order-independence proof")
        if any(w.survivor_set != self.survivor_set for w in self.enumeration_witnesses):
            raise ExhaustiveChooserError("enumeration order changed the survivor set")
        if len(self.survivor_set) == 1:
            if self.emission is None or self.failure_evidence is not None:
                raise ExhaustiveChooserError("unique survivor did not emit exactly once")
            if self.emission.native_q_bias != self.frozen_aeon.native_q_bias:
                raise ExhaustiveChooserError("emission changed native Q Bias")
        else:
            if self.emission is not None or self.failure_evidence is None:
                raise ExhaustiveChooserError("failed bearing emitted or lost failure evidence")

    @property
    def order_independent(self) -> bool:
        return all(w.survivor_set == self.survivor_set for w in self.enumeration_witnesses)

    @property
    def emitted_word(self) -> str | None:
        return self.emission.candidate if self.emission is not None else None


@dataclass(frozen=True, slots=True)
class ExhaustiveCourtBody:
    frozen_aeon: FrozenCourtAeon
    bearing_results: tuple[ExhaustiveBearingResult, ...]
    partial_body_law_deferred: bool = True

    def __post_init__(self) -> None:
        if tuple(result.bearing for result in self.bearing_results) != BEARINGS:
            raise ExhaustiveChooserError("exhaustive Court body must contain all eight bearings")
        if any(result.frozen_aeon != self.frozen_aeon for result in self.bearing_results):
            raise ExhaustiveChooserError("Court was not frozen across its bearing body")
        if not self.partial_body_law_deferred:
            raise ExhaustiveChooserError("Phase 17 partial-body law must remain deferred")

    @property
    def emitted_bearing_count(self) -> int:
        return sum(result.emission is not None for result in self.bearing_results)


@dataclass(frozen=True, slots=True)
class ExhaustiveChooserField:
    manifest: CompleteSubfieldManifest
    court_bodies: tuple[ExhaustiveCourtBody, ...]
    partial_body_law_deferred: bool = True

    def __post_init__(self) -> None:
        if tuple(body.frozen_aeon.court for body in self.court_bodies) != COURTS:
            raise ExhaustiveChooserError("Phase 14 must resolve all 144 Courts in canonical order")
        if any(len(body.bearing_results) != 8 for body in self.court_bodies):
            raise ExhaustiveChooserError("Phase 14 lost one of the eight bearings")
        if not self.partial_body_law_deferred:
            raise ExhaustiveChooserError("Phase 14 cannot decide Phase 17 standing")
        if not all(result.order_independent for body in self.court_bodies for result in body.bearing_results):
            raise ExhaustiveChooserError("Phase 14 result depends upon enumeration order")

    @property
    def emitted_bearing_count(self) -> int:
        return sum(body.emitted_bearing_count for body in self.court_bodies)

    @property
    def mathematical_signature(self) -> tuple[tuple[int, str, frozenset[CandidateKey]], ...]:
        return tuple(
            (body.frozen_aeon.court.index, result.bearing.value, result.survivor_set)
            for body in self.court_bodies
            for result in body.bearing_results
        )


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


def _fingerprint(candidate: MASCandidatePath) -> str:
    return hashlib.sha256(repr(_candidate_structure(candidate)).encode("utf-8")).hexdigest()


def _candidate_key(candidate: MASCandidatePath) -> CandidateKey:
    return CandidateKey(candidate.candidate, _fingerprint(candidate))


def _candidate_witness(candidate: MASCandidatePath, frozen: FrozenCourtAeon) -> CandidateWitness:
    key = _candidate_key(candidate)
    locator = hashlib.sha256(("source-file|" + repr(candidate.cycles[-1].final_state.archive_signature)).encode("utf-8")).hexdigest()
    return CandidateWitness(key, candidate, frozen, locator)


def _freeze_court(court: CourtIdentity, candidates: tuple[MASCandidatePath, ...]) -> FrozenCourtAeon:
    if not candidates:
        raise ExhaustiveChooserError(f"cannot freeze {court.key}: no governing-parent mathematical witness")
    biases = {candidate.liquid_path.seed.domain.inherited_q_bias for candidate in candidates}
    vectors = {candidate.liquid_path.seed.body.q_vector for candidate in candidates}
    if len(biases) != 1 or len(vectors) != 1:
        raise ExhaustiveChooserError(f"cannot freeze {court.key}: governing candidates disagree on native beta or vector")
    return FrozenCourtAeon(court, next(iter(biases)), next(iter(vectors)), court.alternating.glyph)


def build_complete_subfield_manifest(
    field: MASGlobalField,
    overrides: Mapping[tuple[int, GoeticBearing], tuple[MASCandidatePath, ...]] | None = None,
) -> CompleteSubfieldManifest:
    """Build every L_b while preserving one frozen Court across its eight runs."""
    override_map = {} if overrides is None else dict(overrides)
    legal_keys = {(court.index, bearing) for court in COURTS for bearing in BEARINGS}
    if any(key not in legal_keys for key in override_map):
        raise ExhaustiveChooserError("sub-field override names an unknown Court bearing")
    entries: list[BearingSubfield] = []
    for court in COURTS:
        parent_candidates = tuple(
            candidate for candidate in field.survivors
            if candidate.liquid_path.seed.domain.carrier == court.governing
        )
        frozen = _freeze_court(court, parent_candidates)
        parent_ids = {id(candidate) for candidate in parent_candidates}
        for bearing in BEARINGS:
            candidates = override_map.get((court.index, bearing), parent_candidates)
            if any(id(candidate) not in parent_ids for candidate in candidates):
                raise ExhaustiveChooserError("L_b override inserted a candidate outside the frozen Aeon")
            entries.append(BearingSubfield(frozen, bearing, tuple(candidates)))
    return CompleteSubfieldManifest(field, tuple(entries))


def _rotate_one(records: tuple[CandidateTruthRecord, ...]) -> tuple[CandidateTruthRecord, ...]:
    return records[1:] + records[:1] if records else records


def _even_odd(records: tuple[CandidateTruthRecord, ...]) -> tuple[CandidateTruthRecord, ...]:
    return records[::2] + records[1::2]


def _stride_three(records: tuple[CandidateTruthRecord, ...]) -> tuple[CandidateTruthRecord, ...]:
    return records[::3] + records[1::3] + records[2::3]


def _file_shuffled(records: tuple[CandidateTruthRecord, ...]) -> tuple[CandidateTruthRecord, ...]:
    return tuple(sorted(records, key=lambda record: record.witness.source_locator))


def _parallel_chunk_order(records: tuple[CandidateTruthRecord, ...]) -> tuple[CandidateTruthRecord, ...]:
    if len(records) < 2:
        return records
    chunk_size = max(1, (len(records) + 2) // 3)
    chunks = tuple(records[index:index + chunk_size] for index in range(0, len(records), chunk_size))
    return tuple(record for chunk in reversed(chunks) for record in chunk)


def _enumeration_manifests(
    records: tuple[CandidateTruthRecord, ...],
) -> tuple[tuple[EnumerationOrder, tuple[CandidateTruthRecord, ...]], ...]:
    variants = (
        (EnumerationOrder.MANIFEST, records),
        (EnumerationOrder.REVERSED, tuple(reversed(records))),
        (EnumerationOrder.ROTATE_ONE, _rotate_one(records)),
        (EnumerationOrder.EVEN_ODD, _even_odd(records)),
        (EnumerationOrder.STRIDE_THREE, _stride_three(records)),
        (EnumerationOrder.FILE_SHUFFLED, _file_shuffled(records)),
        (EnumerationOrder.PARALLEL_CHUNK, _parallel_chunk_order(records)),
    )
    expected = frozenset(record.witness.key for record in records)
    if any(frozenset(record.witness.key for record in variant) != expected for _, variant in variants):
        raise ExhaustiveChooserError("enumeration proof lost or inserted a candidate")
    return variants


def _truth_record(
    witness: CandidateWitness,
    prepared: CourtCandidate | None,
    preparation_failure: str | None,
    bearing: GoeticBearing,
) -> CandidateTruthRecord:
    if prepared is None:
        return CandidateTruthRecord(witness, None, None, preparation_failure or "Court candidate preparation failed")
    try:
        closure = validate_prepared_court_bearing(prepared, bearing)
        return CandidateTruthRecord(witness, prepared, closure, None)
    except CourtPathError as exc:
        return CandidateTruthRecord(witness, prepared, None, str(exc))


def _evaluate_bearing(
    subfield: BearingSubfield,
    prepared_cache: Mapping[CandidateKey, CourtCandidate | None],
    failure_cache: Mapping[CandidateKey, str | None],
    witness_cache: Mapping[CandidateKey, CandidateWitness],
) -> ExhaustiveBearingResult:
    truth_records: list[CandidateTruthRecord] = []
    for candidate in subfield.candidates:
        key = _candidate_key(candidate)
        truth_records.append(_truth_record(
            witness_cache[key],
            prepared_cache[key],
            failure_cache[key],
            subfield.bearing,
        ))

    complete_records = tuple(truth_records)
    enumeration_witnesses: list[EnumerationWitness] = []
    for order, manifest in _enumeration_manifests(complete_records):
        survivors = frozenset(record.witness.key for record in manifest if record.truth)
        enumeration_witnesses.append(EnumerationWitness(
            order,
            tuple(record.witness.key for record in manifest),
            survivors,
        ))

    survivor_set = enumeration_witnesses[0].survivor_set
    if any(witness.survivor_set != survivor_set for witness in enumeration_witnesses):
        raise ExhaustiveChooserError("survivor set changed under enumeration replay")

    emission: ChooserEmission | None = None
    failure_evidence: ChooserFailureEvidence | None = None
    if len(survivor_set) == 1:
        key = next(iter(survivor_set))
        emission = ChooserEmission(
            subfield.frozen_aeon.court,
            subfield.bearing,
            key,
            key.candidate,
            subfield.frozen_aeon.native_q_bias,
        )
    else:
        reason = "no exact survivor" if not survivor_set else "multiple exact survivors"
        failure_evidence = ChooserFailureEvidence(
            subfield.frozen_aeon.court,
            subfield.bearing,
            reason,
            survivor_set,
            tuple(
                (record.witness.key, record.failure_reason)
                for record in complete_records
                if record.failure_reason is not None
            ),
        )

    return ExhaustiveBearingResult(
        subfield.frozen_aeon,
        subfield.bearing,
        complete_records,
        tuple(enumeration_witnesses),
        survivor_set,
        emission,
        failure_evidence,
    )


def _evaluate_court_body(subfields: tuple[BearingSubfield, ...]) -> ExhaustiveCourtBody:
    if len(subfields) != 8 or tuple(entry.bearing for entry in subfields) != BEARINGS:
        raise ExhaustiveChooserError("Court chooser requires exactly eight ordered sub-fields")
    frozen = subfields[0].frozen_aeon
    if any(entry.frozen_aeon != frozen for entry in subfields):
        raise ExhaustiveChooserError("Court changed while bearing sub-fields changed")

    union: list[MASCandidatePath] = []
    seen: set[CandidateKey] = set()
    for entry in subfields:
        for candidate in entry.candidates:
            key = _candidate_key(candidate)
            if key not in seen:
                union.append(candidate)
                seen.add(key)

    prepared_cache: dict[CandidateKey, CourtCandidate | None] = {}
    failure_cache: dict[CandidateKey, str | None] = {}
    witness_cache: dict[CandidateKey, CandidateWitness] = {}
    for candidate in union:
        witness = _candidate_witness(candidate, frozen)
        witness_cache[witness.key] = witness
        try:
            prepared_cache[witness.key] = build_court_candidate(candidate, frozen.court)
            failure_cache[witness.key] = None
        except CourtPathError as exc:
            prepared_cache[witness.key] = None
            failure_cache[witness.key] = str(exc)

    results = tuple(
        _evaluate_bearing(entry, prepared_cache, failure_cache, witness_cache)
        for entry in subfields
    )
    return ExhaustiveCourtBody(frozen, results, partial_body_law_deferred=True)


def prove_phase14_exit_gate(manifest: CompleteSubfieldManifest) -> ExhaustiveChooserField:
    """Evaluate the complete field without allowing enumeration order to choose."""
    bodies = tuple(
        _evaluate_court_body(manifest.subfields[offset:offset + 8])
        for offset in range(0, len(manifest.subfields), 8)
    )
    return ExhaustiveChooserField(manifest, bodies, partial_body_law_deferred=True)
