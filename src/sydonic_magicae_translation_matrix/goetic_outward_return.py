"""Phase 12 Goetic outward and independently constructed return paths.

Every Phase 11 survivor is tested only under its declared Goetic carrier.  The
Goetic Bound Envelope Constraint is represented exactly as::

    BEC(A_i) = 🜛 o (A_i ->🜚 A_i^-1)

Eight bearings are preserved as the four authored Mirror-Math pairs:
``+ <-> -``, ``Manifest <-> Reflect``, ``Ascend <-> Descend``, and
``Utter <-> Receive``.  Mirroring changes bearing while preserving every M.A.S.
step position.  The independent return builder does not receive or inspect an
outward path.

A bearing emits one candidate identifier only when exactly one candidate closes
with Self -> Self, valid BEC, and exact ``D_T = 0``.  Zero survivors or multiple
survivors leave that bearing failed.  This module deliberately makes no decision
about whether a Goetic with fewer than eight closed bearings stands; that law is
deferred to Phase 17.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Final

from .frequency_projection import CARRIERS, Carrier
from .mas_shadow_conversion import MASGlobalField, MASCandidatePath, MAS_ORDER


class GoeticPathError(ValueError):
    """Raised when a Phase 12 path violates BEC or exact return law."""


class GoeticBearing(str, Enum):
    PLUS = "+"
    MINUS = "-"
    MANIFEST = "Manifest"
    REFLECT = "Reflect"
    ASCEND = "Ascend"
    DESCEND = "Descend"
    UTTER = "Utter"
    RECEIVE = "Receive"


BEARINGS: Final[tuple[GoeticBearing, ...]] = tuple(GoeticBearing)
MIRROR_BEARING: Final[dict[GoeticBearing, GoeticBearing]] = {
    GoeticBearing.PLUS: GoeticBearing.MINUS,
    GoeticBearing.MINUS: GoeticBearing.PLUS,
    GoeticBearing.MANIFEST: GoeticBearing.REFLECT,
    GoeticBearing.REFLECT: GoeticBearing.MANIFEST,
    GoeticBearing.ASCEND: GoeticBearing.DESCEND,
    GoeticBearing.DESCEND: GoeticBearing.ASCEND,
    GoeticBearing.UTTER: GoeticBearing.RECEIVE,
    GoeticBearing.RECEIVE: GoeticBearing.UTTER,
}
if len(BEARINGS) != 8 or any(MIRROR_BEARING[MIRROR_BEARING[bearing]] is not bearing for bearing in BEARINGS):
    raise RuntimeError("Phase 12 requires eight involutive Goetic bearings")


@dataclass(frozen=True, slots=True)
class GoeticEnvelopeWitness:
    """Exact Goetic self-recursion envelope ``🜛 o (A ->🜚 A^-1)``."""

    carrier: Carrier
    triquatra_seal: str = "🜛"
    goetic_identity: str = ""
    klein_seam: str = "🜚"
    inverse_identity: str = ""

    def __post_init__(self) -> None:
        if self.carrier not in CARRIERS:
            raise GoeticPathError("BEC requires one of the twelve canonical Goetics")
        expected_goetic = self.carrier.glyph
        expected_inverse = f"{self.carrier.glyph}^-1"
        if self.goetic_identity != expected_goetic:
            raise GoeticPathError("BEC changed the Goetic self identity")
        if self.inverse_identity != expected_inverse:
            raise GoeticPathError("BEC lacks the Goetic inverse identity")
        if self.triquatra_seal != "🜛" or self.klein_seam != "🜚":
            raise GoeticPathError("BEC lost its Triquatra seal or Klein seam")

    @property
    def bec_valid(self) -> bool:
        return (
            self.carrier in CARRIERS
            and self.goetic_identity == self.carrier.glyph
            and self.inverse_identity == f"{self.carrier.glyph}^-1"
            and self.triquatra_seal == "🜛"
            and self.klein_seam == "🜚"
        )

    @property
    def formula(self) -> tuple[str, str, str, str]:
        return (
            self.triquatra_seal,
            self.goetic_identity,
            self.klein_seam,
            self.inverse_identity,
        )


@dataclass(frozen=True, slots=True)
class GoeticPathStep:
    """One position-preserving M.A.S. action on a declared bearing."""

    position: int
    cycle_index: int
    office_index: int
    office: str
    bearing: GoeticBearing
    signed_velocity: int

    def __post_init__(self) -> None:
        if self.position < 0 or self.cycle_index < 0 or self.office_index not in (0, 1, 2):
            raise GoeticPathError("Goetic path step has an invalid source position")
        if self.position != self.cycle_index * 3 + self.office_index:
            raise GoeticPathError("Goetic path step moved from its M.A.S. source position")
        if self.office != MAS_ORDER[self.office_index]:
            raise GoeticPathError("Goetic path step changed M.A.S. office order")
        if not isinstance(self.bearing, GoeticBearing):
            raise GoeticPathError("Goetic path step lacks one of the eight bearings")
        if not isinstance(self.signed_velocity, int) or self.signed_velocity == 0:
            raise GoeticPathError("Goetic path velocity must be an exact nonzero integer")


SelfIdentity = tuple[str, str, str, tuple[str, str, str, str]]
BoundaryIdentity = tuple[str, str, str]


@dataclass(frozen=True, slots=True)
class GoeticOutwardPath:
    candidate: str
    carrier: Carrier
    bearing: GoeticBearing
    start_self: SelfIdentity
    boundary: BoundaryIdentity
    steps: tuple[GoeticPathStep, ...]

    def __post_init__(self) -> None:
        if self.carrier not in CARRIERS or not self.steps:
            raise GoeticPathError("outward path requires a canonical Goetic and nonempty motion")
        if tuple(step.position for step in self.steps) != tuple(range(len(self.steps))):
            raise GoeticPathError("outward path lost source step order")
        if any(step.bearing is not self.bearing or step.signed_velocity <= 0 for step in self.steps):
            raise GoeticPathError("outward path changed bearing or velocity sign")


@dataclass(frozen=True, slots=True)
class GoeticReturnPath:
    candidate: str
    carrier: Carrier
    bearing: GoeticBearing
    boundary: BoundaryIdentity
    end_self: SelfIdentity
    steps: tuple[GoeticPathStep, ...]

    def __post_init__(self) -> None:
        if self.carrier not in CARRIERS or not self.steps:
            raise GoeticPathError("return path requires a canonical Goetic and nonempty motion")
        if tuple(step.position for step in self.steps) != tuple(range(len(self.steps))):
            raise GoeticPathError("return path reversed or moved source step order")
        if any(step.bearing is not self.bearing or step.signed_velocity >= 0 for step in self.steps):
            raise GoeticPathError("return path changed mirrored bearing or velocity sign")


@dataclass(frozen=True, slots=True)
class DCompPathWitness:
    """Exact nonnegative components of the finite-interval return test."""

    velocity_terms: tuple[int, ...]
    terminal_unresolved_q2: int
    whiteout_penalty: int
    envelope_penalty: int
    boundary_penalty: int

    def __post_init__(self) -> None:
        if any(not isinstance(term, int) for term in self.velocity_terms):
            raise GoeticPathError("D_T velocity terms must be exact integers")
        scalar_terms = (
            self.terminal_unresolved_q2,
            self.whiteout_penalty,
            self.envelope_penalty,
            self.boundary_penalty,
        )
        if any(not isinstance(term, int) or term < 0 for term in scalar_terms):
            raise GoeticPathError("D_T scalar components must be nonnegative integers")

    @property
    def exact_zero(self) -> bool:
        return (
            all(term == 0 for term in self.velocity_terms)
            and self.terminal_unresolved_q2 == 0
            and self.whiteout_penalty == 0
            and self.envelope_penalty == 0
            and self.boundary_penalty == 0
        )

    @property
    def value(self) -> int:
        return (
            sum(abs(term) for term in self.velocity_terms)
            + self.terminal_unresolved_q2
            + self.whiteout_penalty
            + self.envelope_penalty
            + self.boundary_penalty
        )


@dataclass(frozen=True, slots=True)
class GoeticClosure:
    """One exact candidate closure under one Goetic and one bearing."""

    candidate_path: MASCandidatePath
    carrier: Carrier
    bearing: GoeticBearing
    envelope: GoeticEnvelopeWitness
    outward: GoeticOutwardPath
    independent_return: GoeticReturnPath
    dcomp: DCompPathWitness

    def __post_init__(self) -> None:
        candidate = self.candidate_path.candidate
        if self.candidate_path.liquid_path.seed.domain.carrier != self.carrier:
            raise GoeticPathError("candidate is not rooted in the declared Goetic")
        if self.envelope.carrier != self.carrier or not self.envelope.bec_valid:
            raise GoeticPathError("BECValid(A_i;w) != 1")
        if self.outward.candidate != candidate or self.independent_return.candidate != candidate:
            raise GoeticPathError("outward and return paths changed candidate identity")
        if self.outward.carrier != self.carrier or self.independent_return.carrier != self.carrier:
            raise GoeticPathError("outward and return paths changed Goetic identity")
        if self.outward.bearing is not self.bearing:
            raise GoeticPathError("outward path changed the requested bearing")
        if self.independent_return.bearing is not MIRROR_BEARING[self.bearing]:
            raise GoeticPathError("return path did not carry the conjugate bearing")
        if self.outward.start_self != self.independent_return.end_self:
            raise GoeticPathError("required return is not Self -> Self")
        if self.outward.boundary != self.independent_return.boundary:
            raise GoeticPathError("outward and return paths do not meet at one BEC boundary")
        if tuple(step.position for step in self.outward.steps) != tuple(step.position for step in self.independent_return.steps):
            raise GoeticPathError("Mirror Math reversed the operator sequence")
        if not self.dcomp.exact_zero or self.dcomp.value != 0:
            raise GoeticPathError("D_T(gamma, gamma_bar) != 0")

    @property
    def self_to_self(self) -> bool:
        return self.outward.start_self == self.independent_return.end_self

    @property
    def bec_valid(self) -> bool:
        return self.envelope.bec_valid


@dataclass(frozen=True, slots=True)
class CandidateBearingFailure:
    candidate: str
    goetic: str
    bearing: GoeticBearing
    reason: str


@dataclass(frozen=True, slots=True)
class BearingResult:
    """Exactly one closure emits; zero or multiple closures remain failed."""

    carrier: Carrier
    bearing: GoeticBearing
    attempted_candidates: tuple[str, ...]
    exact_closures: tuple[GoeticClosure, ...]
    failures: tuple[CandidateBearingFailure, ...]

    def __post_init__(self) -> None:
        if any(closure.carrier != self.carrier or closure.bearing is not self.bearing for closure in self.exact_closures):
            raise GoeticPathError("bearing result mixed Goetic or bearing identities")
        closure_candidates = tuple(closure.candidate_path.candidate for closure in self.exact_closures)
        if any(candidate not in self.attempted_candidates for candidate in closure_candidates):
            raise GoeticPathError("bearing result contains an unattempted candidate")
        if len(set(closure_candidates)) != len(closure_candidates):
            raise GoeticPathError("bearing result duplicated one exact closure")

    @property
    def closed(self) -> bool:
        return len(self.exact_closures) == 1

    @property
    def survivor(self) -> GoeticClosure | None:
        return self.exact_closures[0] if self.closed else None

    @property
    def emitted_word(self) -> str | None:
        return self.survivor.candidate_path.candidate if self.survivor is not None else None


@dataclass(frozen=True, slots=True)
class GoeticBearingBody:
    carrier: Carrier
    bearing_results: tuple[BearingResult, ...]

    def __post_init__(self) -> None:
        if self.carrier not in CARRIERS:
            raise GoeticPathError("bearing body requires a canonical Goetic")
        if tuple(result.bearing for result in self.bearing_results) != BEARINGS:
            raise GoeticPathError("Goetic bearing body must preserve all eight bearings in order")
        if any(result.carrier != self.carrier for result in self.bearing_results):
            raise GoeticPathError("Goetic bearing body mixed carrier identities")

    @property
    def closed_bearing_count(self) -> int:
        return sum(result.closed for result in self.bearing_results)

    @property
    def failed_bearing_count(self) -> int:
        return len(self.bearing_results) - self.closed_bearing_count


@dataclass(frozen=True, slots=True)
class GoeticOutwardReturnField:
    """The twelve-Goetic, eight-bearing Phase 12 result body."""

    source: MASGlobalField
    goetics: tuple[GoeticBearingBody, ...]
    partial_body_law_deferred: bool = True

    def __post_init__(self) -> None:
        if tuple(body.carrier for body in self.goetics) != CARRIERS:
            raise GoeticPathError("Phase 12 must validate all twelve Goetics in canonical order")
        if any(len(body.bearing_results) != 8 for body in self.goetics):
            raise GoeticPathError("every Goetic requires all eight bearing results")
        if not self.partial_body_law_deferred:
            raise GoeticPathError("Goetic standing must remain deferred to Phase 17")

    @property
    def closed_bearing_count(self) -> int:
        return sum(body.closed_bearing_count for body in self.goetics)

    @property
    def failed_bearing_count(self) -> int:
        return 96 - self.closed_bearing_count



def _self_identity(candidate: MASCandidatePath) -> SelfIdentity:
    seed = candidate.liquid_path.seed
    return (
        candidate.candidate,
        seed.domain.court_root,
        seed.domain.inherited_q_bias,
        seed.body.q_vector,
    )



def _boundary_identity(carrier: Carrier, candidate: MASCandidatePath) -> BoundaryIdentity:
    return (carrier.glyph, "🜚", candidate.candidate)



def _step_magnitude(candidate: MASCandidatePath, cycle_index: int, office_index: int) -> int:
    cycle = candidate.cycles[cycle_index]
    if office_index == 0:
        return 1 + cycle.resolved_pressure_added
    return 1



def build_goetic_envelope(carrier: Carrier) -> GoeticEnvelopeWitness:
    return GoeticEnvelopeWitness(
        carrier=carrier,
        goetic_identity=carrier.glyph,
        inverse_identity=f"{carrier.glyph}^-1",
    )



def build_outward_path(
    candidate: MASCandidatePath,
    carrier: Carrier,
    bearing: GoeticBearing,
) -> GoeticOutwardPath:
    """Construct ``gamma_Ai,w`` from the candidate M.A.S. archive."""
    if candidate.liquid_path.seed.domain.carrier != carrier:
        raise GoeticPathError("candidate cannot be retyped under a foreign Goetic")
    steps = tuple(
        GoeticPathStep(
            position=cycle_index * 3 + office_index,
            cycle_index=cycle_index,
            office_index=office_index,
            office=MAS_ORDER[office_index],
            bearing=bearing,
            signed_velocity=_step_magnitude(candidate, cycle_index, office_index),
        )
        for cycle_index in range(len(candidate.cycles))
        for office_index in range(3)
    )
    return GoeticOutwardPath(
        candidate=candidate.candidate,
        carrier=carrier,
        bearing=bearing,
        start_self=_self_identity(candidate),
        boundary=_boundary_identity(carrier, candidate),
        steps=steps,
    )



def build_independent_return_path(
    candidate: MASCandidatePath,
    carrier: Carrier,
    bearing: GoeticBearing,
) -> GoeticReturnPath:
    """Construct ``gamma_bar_Ai,w`` without an outward path in scope."""
    if candidate.liquid_path.seed.domain.carrier != carrier:
        raise GoeticPathError("candidate cannot return under a foreign Goetic")
    mirrored = MIRROR_BEARING[bearing]
    steps = tuple(
        GoeticPathStep(
            position=cycle_index * 3 + office_index,
            cycle_index=cycle_index,
            office_index=office_index,
            office=MAS_ORDER[office_index],
            bearing=mirrored,
            signed_velocity=-_step_magnitude(candidate, cycle_index, office_index),
        )
        for cycle_index in range(len(candidate.cycles))
        for office_index in range(3)
    )
    return GoeticReturnPath(
        candidate=candidate.candidate,
        carrier=carrier,
        bearing=mirrored,
        boundary=_boundary_identity(carrier, candidate),
        end_self=_self_identity(candidate),
        steps=steps,
    )



def compute_exact_dcomp(
    candidate: MASCandidatePath,
    envelope: GoeticEnvelopeWitness,
    outward: GoeticOutwardPath,
    independent_return: GoeticReturnPath,
) -> DCompPathWitness:
    """Compute the exact nonnegative Phase 12 D_T component body."""
    if len(outward.steps) != len(independent_return.steps):
        raise GoeticPathError("outward and return paths have different lengths")
    velocity_terms: list[int] = []
    for out_step, back_step in zip(outward.steps, independent_return.steps, strict=True):
        if (
            out_step.position,
            out_step.cycle_index,
            out_step.office_index,
            out_step.office,
        ) != (
            back_step.position,
            back_step.cycle_index,
            back_step.office_index,
            back_step.office,
        ):
            raise GoeticPathError("return path changed M.A.S. sequence positions")
        if back_step.bearing is not MIRROR_BEARING[out_step.bearing]:
            raise GoeticPathError("return path failed the bearing mirror")
        velocity_terms.append(out_step.signed_velocity + back_step.signed_velocity)

    liquid_path = candidate.liquid_path
    whiteout_penalty = 0 if all(
        len(horizon.active_connections) <= 110 and len(horizon.resting_connections) >= 34
        for horizon in liquid_path.horizons
    ) else 1
    boundary_penalty = 0 if (
        outward.start_self == independent_return.end_self
        and outward.boundary == independent_return.boundary
    ) else 1
    return DCompPathWitness(
        velocity_terms=tuple(velocity_terms),
        terminal_unresolved_q2=candidate.terminal_unresolved_q2,
        whiteout_penalty=whiteout_penalty,
        envelope_penalty=0 if envelope.bec_valid else 1,
        boundary_penalty=boundary_penalty,
    )



def validate_candidate_bearing(
    candidate: MASCandidatePath,
    carrier: Carrier,
    bearing: GoeticBearing,
) -> GoeticClosure:
    """Prove Self -> Self, BECValid=1, and D_T=0 for one bearing."""
    envelope = build_goetic_envelope(carrier)
    outward = build_outward_path(candidate, carrier, bearing)
    independent_return = build_independent_return_path(candidate, carrier, bearing)
    dcomp = compute_exact_dcomp(candidate, envelope, outward, independent_return)
    return GoeticClosure(
        candidate_path=candidate,
        carrier=carrier,
        bearing=bearing,
        envelope=envelope,
        outward=outward,
        independent_return=independent_return,
        dcomp=dcomp,
    )



def _bearing_result(
    carrier: Carrier,
    bearing: GoeticBearing,
    candidates: tuple[MASCandidatePath, ...],
) -> BearingResult:
    closures: list[GoeticClosure] = []
    failures: list[CandidateBearingFailure] = []
    for candidate in candidates:
        try:
            closures.append(validate_candidate_bearing(candidate, carrier, bearing))
        except GoeticPathError as exc:
            failures.append(CandidateBearingFailure(
                candidate=candidate.candidate,
                goetic=carrier.glyph,
                bearing=bearing,
                reason=str(exc),
            ))
    if not candidates:
        failures.append(CandidateBearingFailure(
            candidate="",
            goetic=carrier.glyph,
            bearing=bearing,
            reason="no Phase 11 survivor entered this Goetic bearing",
        ))
    elif len(closures) > 1:
        failures.append(CandidateBearingFailure(
            candidate="",
            goetic=carrier.glyph,
            bearing=bearing,
            reason="more than one candidate closed; Phase 12 does not rank or choose among exact closures",
        ))
    return BearingResult(
        carrier=carrier,
        bearing=bearing,
        attempted_candidates=tuple(candidate.candidate for candidate in candidates),
        exact_closures=tuple(closures),
        failures=tuple(failures),
    )



def prove_phase12_exit_gate(field: MASGlobalField) -> GoeticOutwardReturnField:
    """Validate all twelve Goetics and preserve failed bearings without emission."""
    bodies: list[GoeticBearingBody] = []
    for carrier in CARRIERS:
        candidates = tuple(
            candidate
            for candidate in field.survivors
            if candidate.liquid_path.seed.domain.carrier == carrier
        )
        results = tuple(
            _bearing_result(carrier, bearing, candidates)
            for bearing in BEARINGS
        )
        bodies.append(GoeticBearingBody(carrier, results))
    return GoeticOutwardReturnField(field, tuple(bodies), partial_body_law_deferred=True)
