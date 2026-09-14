"""Phase 15 strict assembly of eight natively closed lexical bearings.

The partial-body law is permanently fixed to STRICT:

* one Aeon body requires exactly eight independently closed bearings;
* every bearing must carry exactly one survivor and its own path witness;
* a failed, empty, multiplied, detached, or retyped bearing fails the Aeon;
* no bearing is copied, derived, guessed, repaired, or moved into another slot.

The complete assembly domain contains the twelve Goetic Aeons followed by the
144 ordered Court Aeons.  Phase 12 Goetic closures and Phase 14 Court chooser
records remain attached as the witnesses that produced each lexical emission.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Final

from .court_outward_return import COURTS, CourtClosure, CourtIdentity
from .exhaustive_chooser import (
    CandidateKey,
    ExhaustiveBearingResult,
    ExhaustiveChooserField,
)
from .frequency_projection import CARRIERS, Carrier
from .goetic_outward_return import (
    BEARINGS,
    BearingResult,
    GoeticBearing,
    GoeticClosure,
    GoeticOutwardReturnField,
)


class NativeBearingAssemblyError(ValueError):
    """Raised when Phase 15 would accept or manufacture an incomplete body."""


class PartialBodyLaw(str, Enum):
    STRICT = "STRICT"


PARTIAL_BODY_LAW: Final[PartialBodyLaw] = PartialBodyLaw.STRICT
AEON_TOTAL: Final[int] = 156


class AeonClass(str, Enum):
    GOETIC = "Goetic"
    COURT = "Court"


@dataclass(frozen=True, slots=True, order=True)
class AeonIdentity:
    """One canonical identity in the 12-Goetic plus 144-Court assembly field."""

    index: int
    aeon_class: AeonClass
    key: str

    def __post_init__(self) -> None:
        if not 0 <= self.index < AEON_TOTAL:
            raise NativeBearingAssemblyError("Aeon assembly index must lie in [0,155]")
        if not self.key:
            raise NativeBearingAssemblyError("Aeon assembly identity requires a nonempty key")
        if self.index < 12 and self.aeon_class is not AeonClass.GOETIC:
            raise NativeBearingAssemblyError("the first twelve assembly identities are Goetics")
        if self.index >= 12 and self.aeon_class is not AeonClass.COURT:
            raise NativeBearingAssemblyError("the final 144 assembly identities are Courts")


GOETIC_IDENTITIES: Final[tuple[AeonIdentity, ...]] = tuple(
    AeonIdentity(index, AeonClass.GOETIC, carrier.glyph)
    for index, carrier in enumerate(CARRIERS)
)
COURT_IDENTITIES: Final[tuple[AeonIdentity, ...]] = tuple(
    AeonIdentity(12 + court.index, AeonClass.COURT, court.key)
    for court in COURTS
)
AEON_IDENTITIES: Final[tuple[AeonIdentity, ...]] = GOETIC_IDENTITIES + COURT_IDENTITIES
if len(AEON_IDENTITIES) != AEON_TOTAL or len({identity.key for identity in AEON_IDENTITIES}) != AEON_TOTAL:
    raise RuntimeError("Phase 15 requires exactly 156 unique canonical Aeon identities")


@dataclass(frozen=True, slots=True)
class NativeBearingClosure:
    """One lexical dimension that closed under its own bearing and native Bias."""

    aeon: AeonIdentity
    bearing: GoeticBearing
    candidate: str
    native_q_bias: str
    survivor_set: frozenset[object]
    path_witness: GoeticClosure | CourtClosure
    source_record: BearingResult | ExhaustiveBearingResult

    def __post_init__(self) -> None:
        if self.bearing not in BEARINGS:
            raise NativeBearingAssemblyError("closure was moved outside the eight bearing body")
        if not self.candidate:
            raise NativeBearingAssemblyError("closed bearing lacks its emitted candidate")
        if self.native_q_bias not in {"Q0", "Q1", "Q2", "Q3"}:
            raise NativeBearingAssemblyError("closed bearing lacks one native Q Bias")
        if len(self.survivor_set) != 1:
            raise NativeBearingAssemblyError("closed bearing requires exactly one survivor")
        if self.path_witness.bearing is not self.bearing:
            raise NativeBearingAssemblyError("path witness was moved to another bearing")
        if not self.path_witness.dcomp.exact_zero or self.path_witness.dcomp.value != 0:
            raise NativeBearingAssemblyError("bearing path witness lacks exact D-COMP closure")

        if self.aeon.aeon_class is AeonClass.GOETIC:
            if not isinstance(self.path_witness, GoeticClosure):
                raise NativeBearingAssemblyError("Goetic bearing lacks a Goetic path witness")
            if not isinstance(self.source_record, BearingResult):
                raise NativeBearingAssemblyError("Goetic bearing lost its source closure record")
            if self.source_record.bearing is not self.bearing:
                raise NativeBearingAssemblyError("Goetic source record changed bearing")
            if self.source_record.survivor is not self.path_witness:
                raise NativeBearingAssemblyError("Goetic emission detached from its unique closure")
            if self.path_witness.candidate_path.candidate != self.candidate:
                raise NativeBearingAssemblyError("Goetic closure changed the emitted word")
            if not self.path_witness.bec_valid or not self.path_witness.self_to_self:
                raise NativeBearingAssemblyError("Goetic lexical bearing lacks BEC Self return")
        else:
            if not isinstance(self.path_witness, CourtClosure):
                raise NativeBearingAssemblyError("Court bearing lacks a Court path witness")
            if not isinstance(self.source_record, ExhaustiveBearingResult):
                raise NativeBearingAssemblyError("Court bearing lost its Phase 14 closure record")
            if self.source_record.bearing is not self.bearing:
                raise NativeBearingAssemblyError("Court source record changed bearing")
            if not self.source_record.order_independent:
                raise NativeBearingAssemblyError("Court emission lacks order-independent closure")
            if self.source_record.emission is None:
                raise NativeBearingAssemblyError("Court closure is detached from its emission")
            if self.source_record.emission.candidate != self.candidate:
                raise NativeBearingAssemblyError("Court closure changed the emitted word")
            if self.path_witness.court_candidate.candidate != self.candidate:
                raise NativeBearingAssemblyError("Court path witness belongs to another candidate")
            if not self.path_witness.lbec_valid or not self.path_witness.bec_valid:
                raise NativeBearingAssemblyError("Court lexical bearing lacks nested envelope closure")
            if not self.path_witness.court_to_parent:
                raise NativeBearingAssemblyError("Court lexical bearing did not return to its parent")


@dataclass(frozen=True, slots=True)
class StrictBearingFailure:
    aeon: AeonIdentity
    bearing: GoeticBearing
    reason: str
    survivor_count: int
    source_record: BearingResult | ExhaustiveBearingResult

    def __post_init__(self) -> None:
        if self.bearing not in BEARINGS:
            raise NativeBearingAssemblyError("failed bearing left the eight-bearing body")
        if not self.reason:
            raise NativeBearingAssemblyError("failed bearing requires explicit evidence")
        if self.survivor_count < 0:
            raise NativeBearingAssemblyError("survivor count cannot be negative")


BearingAssembly = NativeBearingClosure | StrictBearingFailure


@dataclass(frozen=True, slots=True)
class StrictLexicalBody:
    """One complete eight-bearing body assembled without cross-bearing derivation."""

    aeon: AeonIdentity
    native_q_bias: str
    bearings: tuple[NativeBearingClosure, ...]
    partial_body_law: PartialBodyLaw = PARTIAL_BODY_LAW

    def __post_init__(self) -> None:
        if self.partial_body_law is not PartialBodyLaw.STRICT:
            raise NativeBearingAssemblyError("Phase 15 partial-body law must remain STRICT")
        if tuple(closure.bearing for closure in self.bearings) != BEARINGS:
            raise NativeBearingAssemblyError("STRICT body requires all eight native bearings in order")
        if len(self.bearings) != 8:
            raise NativeBearingAssemblyError("STRICT body cannot contain fewer than eight closures")
        if any(closure.aeon != self.aeon for closure in self.bearings):
            raise NativeBearingAssemblyError("lexical body mixed Aeon identities")
        if any(closure.native_q_bias != self.native_q_bias for closure in self.bearings):
            raise NativeBearingAssemblyError("lexical body moved a word from its native Q Bias")
        if len({id(closure.source_record) for closure in self.bearings}) != 8:
            raise NativeBearingAssemblyError("each bearing requires its own closure record")
        if len({closure.bearing for closure in self.bearings}) != 8:
            raise NativeBearingAssemblyError("one closed bearing was copied into another dimension")

    @property
    def emitted_words(self) -> tuple[str, ...]:
        return tuple(closure.candidate for closure in self.bearings)

    @property
    def bearing_map(self) -> tuple[tuple[GoeticBearing, str], ...]:
        return tuple((closure.bearing, closure.candidate) for closure in self.bearings)


@dataclass(frozen=True, slots=True)
class StrictAeonFailure:
    """Whole-Aeon failure evidence. No lexical body accompanies this record."""

    aeon: AeonIdentity
    bearing_records: tuple[BearingAssembly, ...]
    failed_bearings: tuple[StrictBearingFailure, ...]
    partial_body_law: PartialBodyLaw = PARTIAL_BODY_LAW

    def __post_init__(self) -> None:
        if self.partial_body_law is not PartialBodyLaw.STRICT:
            raise NativeBearingAssemblyError("failed Aeon record changed the STRICT law")
        if tuple(record.bearing for record in self.bearing_records) != BEARINGS:
            raise NativeBearingAssemblyError("failed Aeon record lost an eight-bearing position")
        if not self.failed_bearings:
            raise NativeBearingAssemblyError("STRICT failure requires at least one failed bearing")
        if tuple(record for record in self.bearing_records if isinstance(record, StrictBearingFailure)) != self.failed_bearings:
            raise NativeBearingAssemblyError("failed-bearing evidence is incomplete")
        if any(record.aeon != self.aeon for record in self.bearing_records):
            raise NativeBearingAssemblyError("failed body mixed Aeon identities")


@dataclass(frozen=True, slots=True)
class AeonAssemblyResult:
    aeon: AeonIdentity
    bearing_records: tuple[BearingAssembly, ...]
    body: StrictLexicalBody | None
    failure: StrictAeonFailure | None
    partial_body_law: PartialBodyLaw = PARTIAL_BODY_LAW

    def __post_init__(self) -> None:
        if self.partial_body_law is not PartialBodyLaw.STRICT:
            raise NativeBearingAssemblyError("Aeon assembly result changed the STRICT law")
        if tuple(record.bearing for record in self.bearing_records) != BEARINGS:
            raise NativeBearingAssemblyError("Aeon assembly requires all eight bearing records")
        failures = tuple(record for record in self.bearing_records if isinstance(record, StrictBearingFailure))
        if failures:
            if self.body is not None or self.failure is None:
                raise NativeBearingAssemblyError("partial body was emitted under STRICT law")
            if self.failure.aeon != self.aeon or self.failure.bearing_records != self.bearing_records:
                raise NativeBearingAssemblyError("whole-Aeon failure detached from its bearing evidence")
        else:
            if self.body is None or self.failure is not None:
                raise NativeBearingAssemblyError("eight closed bearings did not emit one complete body")
            if self.body.aeon != self.aeon:
                raise NativeBearingAssemblyError("complete lexical body changed Aeon identity")

    @property
    def valid(self) -> bool:
        return self.body is not None


@dataclass(frozen=True, slots=True)
class NativeBearingAssemblyField:
    """The complete 156-Aeon Phase 15 result under one immutable STRICT law."""

    goetic_source: GoeticOutwardReturnField
    court_source: ExhaustiveChooserField
    aeons: tuple[AeonAssemblyResult, ...]
    partial_body_law: PartialBodyLaw = PARTIAL_BODY_LAW

    def __post_init__(self) -> None:
        if self.partial_body_law is not PartialBodyLaw.STRICT:
            raise NativeBearingAssemblyError("Phase 15 field changed the declared STRICT law")
        if self.goetic_source.source is not self.court_source.manifest.source:
            raise NativeBearingAssemblyError("Goetic and Court assemblies do not share one Phase 11 field")
        if tuple(result.aeon for result in self.aeons) != AEON_IDENTITIES:
            raise NativeBearingAssemblyError("Phase 15 must account for all 156 Aeons in canonical order")
        if len(self.aeons) != AEON_TOTAL:
            raise NativeBearingAssemblyError("Phase 15 did not account for exactly 156 Aeons")
        if any(result.partial_body_law is not self.partial_body_law for result in self.aeons):
            raise NativeBearingAssemblyError("partial-body law differs between Aeons")
        if any(
            result.body is not None and len(result.body.bearings) != 8
            for result in self.aeons
        ):
            raise NativeBearingAssemblyError("field contains a partial lexical body")

    @property
    def bodies(self) -> tuple[StrictLexicalBody, ...]:
        return tuple(result.body for result in self.aeons if result.body is not None)

    @property
    def failures(self) -> tuple[StrictAeonFailure, ...]:
        return tuple(result.failure for result in self.aeons if result.failure is not None)

    @property
    def emitted_body_count(self) -> int:
        return len(self.bodies)

    @property
    def failed_aeon_count(self) -> int:
        return len(self.failures)


def _strict_result(
    aeon: AeonIdentity,
    records: tuple[BearingAssembly, ...],
) -> AeonAssemblyResult:
    if tuple(record.bearing for record in records) != BEARINGS:
        raise NativeBearingAssemblyError("assembler received a moved or missing bearing")
    failures = tuple(record for record in records if isinstance(record, StrictBearingFailure))
    if failures:
        failure = StrictAeonFailure(aeon, records, failures)
        return AeonAssemblyResult(aeon, records, None, failure)
    closures = tuple(record for record in records if isinstance(record, NativeBearingClosure))
    if len(closures) != 8:
        raise NativeBearingAssemblyError("STRICT assembler cannot infer an absent bearing")
    biases = {closure.native_q_bias for closure in closures}
    if len(biases) != 1:
        raise NativeBearingAssemblyError("Aeon bearings disagree on native Q Bias")
    body = StrictLexicalBody(aeon, next(iter(biases)), closures)
    return AeonAssemblyResult(aeon, records, body, None)


def _goetic_bias(source: GoeticOutwardReturnField, carrier: Carrier) -> str | None:
    biases = {
        candidate.liquid_path.seed.domain.inherited_q_bias
        for candidate in source.source.survivors
        if candidate.liquid_path.seed.domain.carrier == carrier
    }
    return next(iter(biases)) if len(biases) == 1 else None


def _goetic_record(
    aeon: AeonIdentity,
    native_q_bias: str | None,
    result: BearingResult,
) -> BearingAssembly:
    if len(result.exact_closures) != 1 or result.emitted_word is None:
        reason = "no exact survivor" if not result.exact_closures else "multiple exact survivors"
        if native_q_bias is None:
            reason = reason + "; native Q Bias witness unavailable"
        return StrictBearingFailure(aeon, result.bearing, reason, len(result.exact_closures), result)
    closure = result.exact_closures[0]
    bias = closure.candidate_path.liquid_path.seed.domain.inherited_q_bias
    if native_q_bias is None or bias != native_q_bias:
        return StrictBearingFailure(aeon, result.bearing, "native Q Bias mismatch", 1, result)
    return NativeBearingClosure(
        aeon=aeon,
        bearing=result.bearing,
        candidate=closure.candidate_path.candidate,
        native_q_bias=bias,
        survivor_set=frozenset({closure.candidate_path.candidate}),
        path_witness=closure,
        source_record=result,
    )


def _court_record(
    aeon: AeonIdentity,
    result: ExhaustiveBearingResult,
) -> BearingAssembly:
    survivor_count = len(result.survivor_set)
    if survivor_count != 1 or result.emission is None:
        reason = result.failure_evidence.reason if result.failure_evidence is not None else "bearing did not emit"
        return StrictBearingFailure(aeon, result.bearing, reason, survivor_count, result)
    key = next(iter(result.survivor_set))
    truth = tuple(
        record
        for record in result.truth_records
        if record.witness.key == key and record.truth
    )
    if len(truth) != 1 or truth[0].closure is None:
        return StrictBearingFailure(aeon, result.bearing, "unique survivor lacks one path witness", survivor_count, result)
    closure = truth[0].closure
    return NativeBearingClosure(
        aeon=aeon,
        bearing=result.bearing,
        candidate=result.emission.candidate,
        native_q_bias=result.emission.native_q_bias,
        survivor_set=result.survivor_set,
        path_witness=closure,
        source_record=result,
    )


def assemble_goetic_body(
    source: GoeticOutwardReturnField,
    carrier_index: int,
) -> AeonAssemblyResult:
    """Assemble one Goetic only after all eight source closures are known."""
    carrier = CARRIERS[carrier_index]
    aeon = GOETIC_IDENTITIES[carrier_index]
    body = source.goetics[carrier_index]
    if body.carrier != carrier:
        raise NativeBearingAssemblyError("Goetic source order changed")
    bias = _goetic_bias(source, carrier)
    records = tuple(_goetic_record(aeon, bias, result) for result in body.bearing_results)
    return _strict_result(aeon, records)


def assemble_court_body(
    source: ExhaustiveChooserField,
    court_index: int,
) -> AeonAssemblyResult:
    """Assemble one Court only after all eight Phase 14 results are known."""
    court: CourtIdentity = COURTS[court_index]
    aeon = COURT_IDENTITIES[court_index]
    body = source.court_bodies[court_index]
    if body.frozen_aeon.court != court:
        raise NativeBearingAssemblyError("Court source order changed")
    records = tuple(_court_record(aeon, result) for result in body.bearing_results)
    return _strict_result(aeon, records)


def prove_phase15_exit_gate(
    goetic_source: GoeticOutwardReturnField,
    court_source: ExhaustiveChooserField,
) -> NativeBearingAssemblyField:
    """Resolve the deferred partial-body question uniformly as STRICT."""
    if goetic_source.source is not court_source.manifest.source:
        raise NativeBearingAssemblyError("Phase 15 inputs do not share one candidate field")
    goetics = tuple(assemble_goetic_body(goetic_source, index) for index in range(12))
    courts = tuple(assemble_court_body(court_source, index) for index in range(144))
    return NativeBearingAssemblyField(goetic_source, court_source, goetics + courts)
