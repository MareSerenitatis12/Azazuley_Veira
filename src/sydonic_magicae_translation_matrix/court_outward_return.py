"""Phase 13 Court outward and independently constructed return paths.

Every ordered Court C_i,j inherits Bias and its four-coordinate Q-vector from
its governing parent A_i, while its live frequency/prosody coordinate is rebuilt
under the alternating carrier A_j with the exact ``[-Phi,+Phi]`` breath body.

The Court L-BEC is nested with the governing Goetic BEC.  The required return
is Court -> governing parent, never Court -> Court.  Mirror Math changes the
bearing and velocity sign while preserving every M.A.S. source position.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from .frequency_projection import CARRIERS, PHI, Carrier
from .goetic_outward_return import (
    BEARINGS,
    MIRROR_BEARING,
    GoeticBearing,
    GoeticEnvelopeWitness,
    build_goetic_envelope,
)
from .liquid_candidate_path import LiquidPathError, run_liquid_candidate_path
from .mas_shadow_conversion import (
    MAS_ORDER,
    MASCandidatePath,
    MASGlobalField,
    MASShadowError,
    run_mas_shadow_conversion,
)
from .triadic_bridge import (
    CandidatePathSeed,
    QMicrostep,
    QAction,
    TriadicBridgeError,
    TriadicDomain,
    compose_triadic_bridge,
)


class CourtPathError(ValueError):
    """Raised when a Phase 13 Court violates inheritance or nested return."""


@dataclass(frozen=True, slots=True, order=True)
class CourtIdentity:
    """One ordered Court C_i,j in canonical 12 x 12 order."""

    index: int
    governing: Carrier
    alternating: Carrier

    def __post_init__(self) -> None:
        try:
            governing_index = CARRIERS.index(self.governing)
            alternating_index = CARRIERS.index(self.alternating)
        except ValueError as exc:
            raise CourtPathError("Court roots must be canonical Goetics") from exc
        if self.index != governing_index * 12 + alternating_index:
            raise CourtPathError("Court index does not match its ordered parents")

    @property
    def key(self) -> str:
        return f"C[{self.governing.glyph}->{self.alternating.glyph}]"


COURTS: Final[tuple[CourtIdentity, ...]] = tuple(
    CourtIdentity(i * 12 + j, governing, alternating)
    for i, governing in enumerate(CARRIERS)
    for j, alternating in enumerate(CARRIERS)
)
if len(COURTS) != 144 or len({court.key for court in COURTS}) != 144:
    raise RuntimeError("Phase 13 requires exactly 144 unique ordered Courts")


@dataclass(frozen=True, slots=True)
class CourtEnvelopeWitness:
    """Exact L-BEC word ``🜚 A_i C_i,j 🜛``."""

    court: CourtIdentity
    klein_seam: str = "🜚"
    governing_identity: str = ""
    court_identity: str = ""
    triquatra_seal: str = "🜛"

    def __post_init__(self) -> None:
        if self.governing_identity != self.court.governing.glyph:
            raise CourtPathError("L-BEC changed the governing parent")
        if self.court_identity != self.court.key:
            raise CourtPathError("L-BEC changed the Court identity")
        if self.klein_seam != "🜚" or self.triquatra_seal != "🜛":
            raise CourtPathError("L-BEC lost its Klein seam or Triquatra seal")

    @property
    def lbec_valid(self) -> bool:
        return (
            self.klein_seam == "🜚"
            and self.governing_identity == self.court.governing.glyph
            and self.court_identity == self.court.key
            and self.triquatra_seal == "🜛"
        )

    @property
    def formula(self) -> tuple[str, str, str, str]:
        return (
            self.klein_seam,
            self.governing_identity,
            self.court_identity,
            self.triquatra_seal,
        )


@dataclass(frozen=True, slots=True)
class CourtInheritanceWitness:
    """Bias and vector from A_i; carrier and breath from A_j."""

    court: CourtIdentity
    parent_q_bias: str
    candidate_q_bias: str
    parent_q_vector: tuple[str, str, str, str]
    candidate_q_vector: tuple[str, str, str, str]
    candidate_carrier: Carrier
    breath_bounds: tuple[object, object]

    @property
    def valid(self) -> bool:
        return (
            self.parent_q_bias == self.candidate_q_bias
            and self.parent_q_vector == self.candidate_q_vector
            and self.candidate_carrier == self.court.alternating
            and self.breath_bounds == (-PHI, PHI)
            and self.breath_bounds == self.court.alternating.breath_bounds
        )


@dataclass(frozen=True, slots=True)
class CourtCandidate:
    """One parent survivor rebuilt as J_Cij(w) and rerun through Phases 10-11."""

    source_parent: MASCandidatePath
    court: CourtIdentity
    seed: CandidatePathSeed
    mas_path: MASCandidatePath
    inheritance: CourtInheritanceWitness

    def __post_init__(self) -> None:
        parent_seed = self.source_parent.liquid_path.seed
        if parent_seed.domain.carrier != self.court.governing:
            raise CourtPathError("candidate did not enter through the governing parent")
        if self.seed.domain.court_root != self.court.key:
            raise CourtPathError("J_Cij(w) changed the ordered Court root")
        if self.seed.domain.carrier != self.court.alternating:
            raise CourtPathError("J_Cij(w) did not receive the alternating carrier")
        if self.seed.witness != parent_seed.witness:
            raise CourtPathError("Court projection changed the candidate witness")
        if self.mas_path.liquid_path.seed != self.seed:
            raise CourtPathError("Court M.A.S. path is detached from J_Cij(w)")
        if self.mas_path.terminal_unresolved_q2 != 0:
            raise CourtPathError("Court candidate retains terminal unresolved Q2")
        if not self.mas_path.positive_local_mass_gap or self.mas_path.motion <= 0:
            raise CourtPathError("Court candidate lacks persistent positive motion")
        if not self.inheritance.valid:
            raise CourtPathError("Court inheritance witness failed")

    @property
    def candidate(self) -> str:
        return self.seed.witness.candidate


@dataclass(frozen=True, slots=True)
class CourtPathStep:
    position: int
    cycle_index: int
    office_index: int
    office: str
    bearing: GoeticBearing
    signed_velocity: int

    def __post_init__(self) -> None:
        if self.position != self.cycle_index * 3 + self.office_index:
            raise CourtPathError("Court path step moved from its M.A.S. source position")
        if self.office_index not in (0, 1, 2) or self.office != MAS_ORDER[self.office_index]:
            raise CourtPathError("Court path step changed M.A.S. order")
        if not isinstance(self.bearing, GoeticBearing):
            raise CourtPathError("Court path step lacks one of the eight bearings")
        if not isinstance(self.signed_velocity, int) or self.signed_velocity == 0:
            raise CourtPathError("Court path velocity must be an exact nonzero integer")


CourtStartIdentity = tuple[str, str, str, tuple[str, str, str, str], str]
ParentIdentity = tuple[str, str, str, tuple[str, str, str, str]]
CourtBoundary = tuple[str, str, str, str]


@dataclass(frozen=True, slots=True)
class CourtOutwardPath:
    candidate: str
    court: CourtIdentity
    bearing: GoeticBearing
    start_court: CourtStartIdentity
    parent_boundary: CourtBoundary
    steps: tuple[CourtPathStep, ...]

    def __post_init__(self) -> None:
        if not self.steps or tuple(step.position for step in self.steps) != tuple(range(len(self.steps))):
            raise CourtPathError("Court outward path lost source step order")
        if any(step.bearing is not self.bearing or step.signed_velocity <= 0 for step in self.steps):
            raise CourtPathError("Court outward path changed bearing or velocity sign")


@dataclass(frozen=True, slots=True)
class CourtReturnPath:
    candidate: str
    court: CourtIdentity
    bearing: GoeticBearing
    parent_boundary: CourtBoundary
    end_parent: ParentIdentity
    steps: tuple[CourtPathStep, ...]

    def __post_init__(self) -> None:
        if not self.steps or tuple(step.position for step in self.steps) != tuple(range(len(self.steps))):
            raise CourtPathError("Court return path reversed or moved source step order")
        if any(step.bearing is not self.bearing or step.signed_velocity >= 0 for step in self.steps):
            raise CourtPathError("Court return path changed mirrored bearing or velocity sign")


@dataclass(frozen=True, slots=True)
class CourtDCompWitness:
    velocity_terms: tuple[int, ...]
    terminal_unresolved_q2: int
    whiteout_penalty: int
    lbec_penalty: int
    parent_bec_penalty: int
    inheritance_penalty: int
    parent_return_penalty: int

    def __post_init__(self) -> None:
        if any(not isinstance(term, int) for term in self.velocity_terms):
            raise CourtPathError("Court D_T velocity terms must be exact integers")
        scalars = (
            self.terminal_unresolved_q2,
            self.whiteout_penalty,
            self.lbec_penalty,
            self.parent_bec_penalty,
            self.inheritance_penalty,
            self.parent_return_penalty,
        )
        if any(not isinstance(term, int) or term < 0 for term in scalars):
            raise CourtPathError("Court D_T components must be nonnegative integers")

    @property
    def exact_zero(self) -> bool:
        return all(term == 0 for term in self.velocity_terms) and all(
            term == 0
            for term in (
                self.terminal_unresolved_q2,
                self.whiteout_penalty,
                self.lbec_penalty,
                self.parent_bec_penalty,
                self.inheritance_penalty,
                self.parent_return_penalty,
            )
        )

    @property
    def value(self) -> int:
        return sum(abs(term) for term in self.velocity_terms) + sum((
            self.terminal_unresolved_q2,
            self.whiteout_penalty,
            self.lbec_penalty,
            self.parent_bec_penalty,
            self.inheritance_penalty,
            self.parent_return_penalty,
        ))


@dataclass(frozen=True, slots=True)
class CourtClosure:
    court_candidate: CourtCandidate
    bearing: GoeticBearing
    court_envelope: CourtEnvelopeWitness
    parent_envelope: GoeticEnvelopeWitness
    outward: CourtOutwardPath
    independent_return: CourtReturnPath
    dcomp: CourtDCompWitness

    def __post_init__(self) -> None:
        court = self.court_candidate.court
        if self.court_envelope.court != court or not self.court_envelope.lbec_valid:
            raise CourtPathError("LBECValid(C_i,j;w) != 1")
        if self.parent_envelope.carrier != court.governing or not self.parent_envelope.bec_valid:
            raise CourtPathError("BECValid(A_i;w) != 1")
        if self.outward.court != court or self.independent_return.court != court:
            raise CourtPathError("Court path changed C_i,j")
        if self.outward.candidate != self.court_candidate.candidate or self.independent_return.candidate != self.court_candidate.candidate:
            raise CourtPathError("Court path changed candidate identity")
        if self.outward.bearing is not self.bearing:
            raise CourtPathError("Court outward path changed requested bearing")
        if self.independent_return.bearing is not MIRROR_BEARING[self.bearing]:
            raise CourtPathError("Court return path lacks conjugate bearing")
        if self.outward.parent_boundary != self.independent_return.parent_boundary:
            raise CourtPathError("Court paths do not meet at one parent boundary")
        if self.independent_return.end_parent != _parent_identity(self.court_candidate):
            raise CourtPathError("required return is not Court -> governing parent")
        if tuple(step.position for step in self.outward.steps) != tuple(step.position for step in self.independent_return.steps):
            raise CourtPathError("Court Mirror Math reversed operator sequence")
        if not self.court_candidate.inheritance.valid:
            raise CourtPathError("Court closure lost inherited Bias, vector, or carrier")
        if not self.dcomp.exact_zero or self.dcomp.value != 0:
            raise CourtPathError("D_T(gamma_Cij,w,gamma_bar_Cij,w) != 0")

    @property
    def court_to_parent(self) -> bool:
        return self.independent_return.end_parent == _parent_identity(self.court_candidate)

    @property
    def lbec_valid(self) -> bool:
        return self.court_envelope.lbec_valid

    @property
    def bec_valid(self) -> bool:
        return self.parent_envelope.bec_valid


@dataclass(frozen=True, slots=True)
class CourtCandidateFailure:
    candidate: str
    court: str
    bearing: GoeticBearing
    reason: str


@dataclass(frozen=True, slots=True)
class CourtBearingResult:
    court: CourtIdentity
    bearing: GoeticBearing
    attempted_candidates: tuple[str, ...]
    exact_closures: tuple[CourtClosure, ...]
    failures: tuple[CourtCandidateFailure, ...]

    def __post_init__(self) -> None:
        if any(closure.court_candidate.court != self.court or closure.bearing is not self.bearing for closure in self.exact_closures):
            raise CourtPathError("Court bearing result mixed Court or bearing identities")
        names = tuple(closure.court_candidate.candidate for closure in self.exact_closures)
        if any(name not in self.attempted_candidates for name in names):
            raise CourtPathError("Court bearing result contains an unattempted candidate")
        if len(set(names)) != len(names):
            raise CourtPathError("Court bearing result duplicated an exact closure")

    @property
    def closed(self) -> bool:
        return len(self.exact_closures) == 1

    @property
    def survivor(self) -> CourtClosure | None:
        return self.exact_closures[0] if self.closed else None

    @property
    def emitted_word(self) -> str | None:
        return self.survivor.court_candidate.candidate if self.survivor is not None else None


@dataclass(frozen=True, slots=True)
class CourtBearingBody:
    court: CourtIdentity
    bearing_results: tuple[CourtBearingResult, ...]

    def __post_init__(self) -> None:
        if tuple(result.bearing for result in self.bearing_results) != BEARINGS:
            raise CourtPathError("Court body must preserve all eight bearings in order")
        if any(result.court != self.court for result in self.bearing_results):
            raise CourtPathError("Court body mixed Court identities")

    @property
    def closed_bearing_count(self) -> int:
        return sum(result.closed for result in self.bearing_results)

    @property
    def failed_bearing_count(self) -> int:
        return 8 - self.closed_bearing_count


@dataclass(frozen=True, slots=True)
class CourtOutwardReturnField:
    source: MASGlobalField
    courts: tuple[CourtBearingBody, ...]
    partial_body_law_deferred: bool = True

    def __post_init__(self) -> None:
        if tuple(body.court for body in self.courts) != COURTS:
            raise CourtPathError("Phase 13 must validate all 144 Courts in canonical order")
        if any(len(body.bearing_results) != 8 for body in self.courts):
            raise CourtPathError("every Court requires all eight bearing results")
        if not self.partial_body_law_deferred:
            raise CourtPathError("Court standing must remain deferred to Phase 17")

    @property
    def closed_bearing_count(self) -> int:
        return sum(body.closed_bearing_count for body in self.courts)

    @property
    def failed_bearing_count(self) -> int:
        return 1152 - self.closed_bearing_count


def _source_q_action(candidate: MASCandidatePath) -> tuple[tuple[str, str, str, str], QAction]:
    seed = candidate.liquid_path.seed
    if len(seed.microsteps) != 3 or not isinstance(seed.microsteps[1], QMicrostep):
        raise CourtPathError("governing candidate lacks its complete Q microstep")
    q_step = seed.microsteps[1]
    return q_step.before.q_vector, q_step.action


def build_court_candidate(source_parent: MASCandidatePath, court: CourtIdentity) -> CourtCandidate:
    """Build J_Cij(w), then rerun its Liquid and M.A.S. bodies exactly once."""
    parent_seed = source_parent.liquid_path.seed
    if parent_seed.domain.carrier != court.governing:
        raise CourtPathError("candidate does not belong to the governing parent A_i")
    q_source, q_action = _source_q_action(source_parent)
    domain = TriadicDomain(
        court_root=court.key,
        inherited_q_bias=parent_seed.domain.inherited_q_bias,
        carrier=court.alternating,
    )
    try:
        seed = compose_triadic_bridge(domain, parent_seed.witness, q_source, q_action)
        liquid = run_liquid_candidate_path(seed, len(source_parent.liquid_path.horizons))
        mas_path = run_mas_shadow_conversion(liquid)
    except (TriadicBridgeError, LiquidPathError, MASShadowError) as exc:
        raise CourtPathError("Court candidate failed its nested Phase 9-11 body") from exc
    inheritance = CourtInheritanceWitness(
        court=court,
        parent_q_bias=parent_seed.domain.inherited_q_bias,
        candidate_q_bias=seed.domain.inherited_q_bias,
        parent_q_vector=parent_seed.body.q_vector,
        candidate_q_vector=seed.body.q_vector,
        candidate_carrier=seed.domain.carrier,
        breath_bounds=seed.domain.carrier.breath_bounds,
    )
    return CourtCandidate(source_parent, court, seed, mas_path, inheritance)


def build_court_envelope(court: CourtIdentity) -> CourtEnvelopeWitness:
    return CourtEnvelopeWitness(
        court=court,
        governing_identity=court.governing.glyph,
        court_identity=court.key,
    )


def _court_start(candidate: CourtCandidate) -> CourtStartIdentity:
    seed = candidate.seed
    return (
        candidate.candidate,
        candidate.court.key,
        seed.domain.inherited_q_bias,
        seed.body.q_vector,
        seed.domain.carrier.glyph,
    )


def _parent_identity(candidate: CourtCandidate) -> ParentIdentity:
    parent_seed = candidate.source_parent.liquid_path.seed
    return (
        candidate.candidate,
        candidate.court.governing.glyph,
        parent_seed.domain.inherited_q_bias,
        parent_seed.body.q_vector,
    )


def _parent_boundary(candidate: CourtCandidate) -> CourtBoundary:
    return (
        candidate.court.governing.glyph,
        "🜚",
        candidate.court.key,
        candidate.candidate,
    )


def _step_magnitude(candidate: CourtCandidate, cycle_index: int, office_index: int) -> int:
    cycle = candidate.mas_path.cycles[cycle_index]
    return 1 + cycle.resolved_pressure_added if office_index == 0 else 1


def build_court_outward_path(candidate: CourtCandidate, bearing: GoeticBearing) -> CourtOutwardPath:
    steps = tuple(
        CourtPathStep(
            position=cycle_index * 3 + office_index,
            cycle_index=cycle_index,
            office_index=office_index,
            office=MAS_ORDER[office_index],
            bearing=bearing,
            signed_velocity=_step_magnitude(candidate, cycle_index, office_index),
        )
        for cycle_index in range(len(candidate.mas_path.cycles))
        for office_index in range(3)
    )
    return CourtOutwardPath(
        candidate=candidate.candidate,
        court=candidate.court,
        bearing=bearing,
        start_court=_court_start(candidate),
        parent_boundary=_parent_boundary(candidate),
        steps=steps,
    )


def build_independent_court_return_path(candidate: CourtCandidate, bearing: GoeticBearing) -> CourtReturnPath:
    """Construct the parent return without receiving an outward path."""
    mirrored = MIRROR_BEARING[bearing]
    steps = tuple(
        CourtPathStep(
            position=cycle_index * 3 + office_index,
            cycle_index=cycle_index,
            office_index=office_index,
            office=MAS_ORDER[office_index],
            bearing=mirrored,
            signed_velocity=-_step_magnitude(candidate, cycle_index, office_index),
        )
        for cycle_index in range(len(candidate.mas_path.cycles))
        for office_index in range(3)
    )
    return CourtReturnPath(
        candidate=candidate.candidate,
        court=candidate.court,
        bearing=mirrored,
        parent_boundary=_parent_boundary(candidate),
        end_parent=_parent_identity(candidate),
        steps=steps,
    )


def compute_court_dcomp(
    candidate: CourtCandidate,
    court_envelope: CourtEnvelopeWitness,
    parent_envelope: GoeticEnvelopeWitness,
    outward: CourtOutwardPath,
    independent_return: CourtReturnPath,
) -> CourtDCompWitness:
    if len(outward.steps) != len(independent_return.steps):
        raise CourtPathError("Court outward and return paths have different lengths")
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
            raise CourtPathError("Court return changed M.A.S. sequence positions")
        if back_step.bearing is not MIRROR_BEARING[out_step.bearing]:
            raise CourtPathError("Court return failed bearing mirror")
        velocity_terms.append(out_step.signed_velocity + back_step.signed_velocity)
    whiteout_penalty = 0 if all(
        len(h.active_connections) <= 110 and len(h.resting_connections) >= 34
        for h in candidate.mas_path.liquid_path.horizons
    ) else 1
    return CourtDCompWitness(
        velocity_terms=tuple(velocity_terms),
        terminal_unresolved_q2=candidate.mas_path.terminal_unresolved_q2,
        whiteout_penalty=whiteout_penalty,
        lbec_penalty=0 if court_envelope.lbec_valid else 1,
        parent_bec_penalty=0 if parent_envelope.bec_valid else 1,
        inheritance_penalty=0 if candidate.inheritance.valid else 1,
        parent_return_penalty=0 if independent_return.end_parent == _parent_identity(candidate) else 1,
    )


def validate_prepared_court_bearing(candidate: CourtCandidate, bearing: GoeticBearing) -> CourtClosure:
    court_envelope = build_court_envelope(candidate.court)
    parent_envelope = build_goetic_envelope(candidate.court.governing)
    outward = build_court_outward_path(candidate, bearing)
    independent_return = build_independent_court_return_path(candidate, bearing)
    dcomp = compute_court_dcomp(candidate, court_envelope, parent_envelope, outward, independent_return)
    return CourtClosure(
        candidate,
        bearing,
        court_envelope,
        parent_envelope,
        outward,
        independent_return,
        dcomp,
    )


def validate_court_candidate_bearing(
    source_parent: MASCandidatePath,
    court: CourtIdentity,
    bearing: GoeticBearing,
) -> CourtClosure:
    return validate_prepared_court_bearing(build_court_candidate(source_parent, court), bearing)


def _bearing_result(
    court: CourtIdentity,
    bearing: GoeticBearing,
    attempted: tuple[MASCandidatePath, ...],
    prepared: tuple[CourtCandidate, ...],
    preparation_failures: tuple[CourtCandidateFailure, ...],
) -> CourtBearingResult:
    closures: list[CourtClosure] = []
    failures = list(preparation_failures)
    for candidate in prepared:
        try:
            closures.append(validate_prepared_court_bearing(candidate, bearing))
        except CourtPathError as exc:
            failures.append(CourtCandidateFailure(candidate.candidate, court.key, bearing, str(exc)))
    if not attempted:
        failures.append(CourtCandidateFailure("", court.key, bearing, "no governing-parent survivor entered this Court bearing"))
    elif len(closures) > 1:
        failures.append(CourtCandidateFailure("", court.key, bearing, "more than one candidate closed; Phase 13 does not rank or choose"))
    return CourtBearingResult(
        court=court,
        bearing=bearing,
        attempted_candidates=tuple(candidate.candidate for candidate in attempted),
        exact_closures=tuple(closures),
        failures=tuple(failures),
    )


def prove_phase13_exit_gate(field: MASGlobalField) -> CourtOutwardReturnField:
    """Validate all 144 Courts under nested L-BEC/BEC and parent return."""
    bodies: list[CourtBearingBody] = []
    for court in COURTS:
        attempted = tuple(
            candidate
            for candidate in field.survivors
            if candidate.liquid_path.seed.domain.carrier == court.governing
        )
        prepared: list[CourtCandidate] = []
        failed_preparation: list[tuple[str, str]] = []
        for candidate in attempted:
            try:
                prepared.append(build_court_candidate(candidate, court))
            except CourtPathError as exc:
                failed_preparation.append((candidate.candidate, str(exc)))
        results = tuple(
            _bearing_result(
                court,
                bearing,
                attempted,
                tuple(prepared),
                tuple(
                    CourtCandidateFailure(name, court.key, bearing, reason)
                    for name, reason in failed_preparation
                ),
            )
            for bearing in BEARINGS
        )
        bodies.append(CourtBearingBody(court, results))
    return CourtOutwardReturnField(field, tuple(bodies), partial_body_law_deferred=True)
