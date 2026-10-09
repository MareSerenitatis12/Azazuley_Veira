"""Phase 9 complete triadic bridge.

The bridge composes the inherited Bias witness, one declared Q action, and
Phase 8's exact frequency/prosody action into one candidate path seed:

    J_A(w) = F_nu,A o F_v,A o F_beta,A

All three microsteps act on one declared Court-rooted domain.  Each step keeps
the coordinates it does not govern.  A matching frequency body, Q body, or
prosodic witness is never accepted in place of the complete triad.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Final, Literal, TypeAlias

from .frequency_projection import (
    Carrier,
    FrequencyClosure,
    FrequencyProjectionError,
    PHI,
    ProsodicWitness,
    prove_frequency_closure,
)


QState = Literal["Q0", "Q1", "Q2", "Q3"]
QSTATE_CYCLE: Final[tuple[QState, ...]] = ("Q0", "Q1", "Q2", "Q3")
class TriadicBridgeError(ValueError):
    """Raised when a Phase 9 candidate does not carry the complete triad."""


QVector: TypeAlias = tuple[QState, QState, QState, QState]
MICROSTEP_ORDER: Final[tuple[str, str, str]] = ("F_beta", "F_v", "F_nu")


def _validate_q_vector(vector: object, label: str) -> QVector:
    if not isinstance(vector, tuple) or len(vector) != 4:
        raise TriadicBridgeError(f"{label} must contain exactly four Q-state coordinates")
    if any(state not in QSTATE_CYCLE for state in vector):
        raise TriadicBridgeError(f"{label} contains an undefined Q-state")
    return vector  # type: ignore[return-value]


@dataclass(frozen=True, slots=True)
class TriadicDomain:
    """The one declared subset of the Court triplet domain used by all steps."""

    court_root: str
    inherited_q_bias: QState
    carrier: Carrier
    q_vector_arity: int = 4
    breath_bounds: tuple[object, object] = (-PHI, PHI)

    def __post_init__(self) -> None:
        if not isinstance(self.court_root, str) or not self.court_root:
            raise TriadicBridgeError("the triadic domain requires one declared Court root")
        if self.inherited_q_bias not in QSTATE_CYCLE:
            raise TriadicBridgeError("the triadic domain requires one inherited Q Bias")
        if not isinstance(self.carrier, Carrier):
            raise TriadicBridgeError("the triadic domain requires one declared Aeon carrier")
        if self.q_vector_arity != 4:
            raise TriadicBridgeError("the Domus Q vector has exactly four coordinates")
        if self.breath_bounds != self.carrier.breath_bounds:
            raise TriadicBridgeError("the declared frequency domain must retain [-Phi,+Phi]")


@dataclass(frozen=True, slots=True)
class QAction:
    """One explicit Q-state-vector action on the declared domain."""

    name: str
    source: QVector
    target: QVector

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name.strip():
            raise TriadicBridgeError("F_v requires a named, defined Q action")
        _validate_q_vector(self.source, "Q action source")
        _validate_q_vector(self.target, "Q action target")

    def apply(self, vector: QVector) -> QVector:
        _validate_q_vector(vector, "Q action input")
        if vector != self.source:
            raise TriadicBridgeError("Q action input lies outside its declared source body")
        return self.target


@dataclass(frozen=True, slots=True)
class CandidateTripletBody:
    """One typed candidate body inside a single TriadicDomain."""

    domain: TriadicDomain
    witness: ProsodicWitness
    court_root: str
    q_bias: QState
    q_vector: QVector
    frequency_action: FrequencyClosure | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.domain, TriadicDomain):
            raise TriadicBridgeError("candidate body lacks a declared triadic domain")
        if not isinstance(self.witness, ProsodicWitness):
            raise TriadicBridgeError("candidate body lacks a typed prosodic witness")
        if self.court_root != self.domain.court_root:
            raise TriadicBridgeError("candidate body changed its Court root")
        if self.q_bias != self.domain.inherited_q_bias:
            raise TriadicBridgeError("candidate body changed inherited Q Bias")
        _validate_q_vector(self.q_vector, "candidate Q vector")
        if self.frequency_action is not None:
            closure = self.frequency_action
            if closure.outward.carrier != self.domain.carrier:
                raise TriadicBridgeError("frequency action changed the declared Aeon carrier")
            if closure.outward.candidate != self.witness.candidate:
                raise TriadicBridgeError("frequency action belongs to a different candidate")
            if not closure.nu_close or not closure.dcomp_frequency_zero:
                raise TriadicBridgeError("frequency action is not exactly closed")


@dataclass(frozen=True, slots=True)
class BiasMicrostep:
    name: str
    domain: TriadicDomain
    before: CandidateTripletBody
    after: CandidateTripletBody
    inherited_q_bias: QState


@dataclass(frozen=True, slots=True)
class QMicrostep:
    name: str
    domain: TriadicDomain
    before: CandidateTripletBody
    after: CandidateTripletBody
    action: QAction


@dataclass(frozen=True, slots=True)
class FrequencyMicrostep:
    name: str
    domain: TriadicDomain
    before: CandidateTripletBody
    after: CandidateTripletBody
    action: FrequencyClosure


Microstep: TypeAlias = BiasMicrostep | QMicrostep | FrequencyMicrostep


@dataclass(frozen=True, slots=True)
class CandidatePathSeed:
    """The one typed body admitted to the complete Aeon phase engine."""

    domain: TriadicDomain
    witness: ProsodicWitness
    microsteps: tuple[Microstep, ...]
    body: CandidateTripletBody



def F_beta(body: CandidateTripletBody) -> BiasMicrostep:
    """Declare inherited Bias as an exact identity microstep."""
    after = CandidateTripletBody(
        domain=body.domain,
        witness=body.witness,
        court_root=body.court_root,
        q_bias=body.q_bias,
        q_vector=body.q_vector,
        frequency_action=body.frequency_action,
    )
    return BiasMicrostep("F_beta", body.domain, body, after, body.q_bias)



def F_v(body: CandidateTripletBody, action: QAction) -> QMicrostep:
    """Apply one defined Q action while preserving root, Bias, and frequency."""
    if body.frequency_action is not None:
        raise TriadicBridgeError("F_v must precede F_nu in the ordered triad")
    target = action.apply(body.q_vector)
    after = CandidateTripletBody(
        domain=body.domain,
        witness=body.witness,
        court_root=body.court_root,
        q_bias=body.q_bias,
        q_vector=target,
        frequency_action=None,
    )
    return QMicrostep("F_v", body.domain, body, after, action)



def F_nu(body: CandidateTripletBody) -> FrequencyMicrostep:
    """Attach Phase 8's exact frequency action while preserving root and Q body."""
    if body.frequency_action is not None:
        raise TriadicBridgeError("F_nu cannot overwrite an existing frequency action")
    try:
        closure = prove_frequency_closure(body.witness, body.domain.carrier)
    except FrequencyProjectionError as exc:
        raise TriadicBridgeError("candidate frequency action failed exact Phase 8 closure") from exc
    after = CandidateTripletBody(
        domain=body.domain,
        witness=body.witness,
        court_root=body.court_root,
        q_bias=body.q_bias,
        q_vector=body.q_vector,
        frequency_action=closure,
    )
    return FrequencyMicrostep("F_nu", body.domain, body, after, closure)



def triad_A(candidate: object) -> bool:
    """Return the exact Phase 9 completeness predicate Triad_A(J_A(w))."""
    if not isinstance(candidate, CandidatePathSeed):
        return False
    if len(candidate.microsteps) != 3:
        return False
    beta_step, q_step, nu_step = candidate.microsteps
    if not isinstance(beta_step, BiasMicrostep):
        return False
    if not isinstance(q_step, QMicrostep):
        return False
    if not isinstance(nu_step, FrequencyMicrostep):
        return False
    if tuple(step.name for step in candidate.microsteps) != MICROSTEP_ORDER:
        return False

    domain = candidate.domain
    if any(step.domain != domain for step in candidate.microsteps):
        return False
    if beta_step.before.domain != domain or candidate.body.domain != domain:
        return False
    if beta_step.before.witness != candidate.witness or candidate.body.witness != candidate.witness:
        return False

    # F_beta is the inherited-Bias identity and changes nothing.
    if beta_step.inherited_q_bias != domain.inherited_q_bias:
        return False
    if beta_step.before != beta_step.after:
        return False
    if beta_step.before.q_bias != domain.inherited_q_bias:
        return False

    # The chain is one body, not three disconnected matching records.
    if q_step.before != beta_step.after or nu_step.before != q_step.after:
        return False
    if candidate.body != nu_step.after:
        return False

    # F_v governs only the Q vector.
    if q_step.before.court_root != q_step.after.court_root:
        return False
    if q_step.before.q_bias != q_step.after.q_bias:
        return False
    if q_step.before.witness != q_step.after.witness:
        return False
    if q_step.before.frequency_action is not None or q_step.after.frequency_action is not None:
        return False
    try:
        if q_step.action.apply(q_step.before.q_vector) != q_step.after.q_vector:
            return False
    except TriadicBridgeError:
        return False

    # F_nu governs only the frequency/prosody coordinate.
    if nu_step.before.court_root != nu_step.after.court_root:
        return False
    if nu_step.before.q_bias != nu_step.after.q_bias:
        return False
    if nu_step.before.q_vector != nu_step.after.q_vector:
        return False
    if nu_step.before.witness != nu_step.after.witness:
        return False
    if nu_step.before.frequency_action is not None:
        return False
    if nu_step.after.frequency_action != nu_step.action:
        return False
    if not nu_step.action.nu_close or not nu_step.action.dcomp_frequency_zero:
        return False
    if nu_step.action.outward.carrier != domain.carrier:
        return False
    if nu_step.action.outward.candidate != candidate.witness.candidate:
        return False

    return True



def require_complete_triad(candidate: object) -> CandidatePathSeed:
    """Reject every incomplete, disconnected, or identity-changing bridge."""
    if not triad_A(candidate):
        raise TriadicBridgeError("Triad_A(J_A(w)) != 1")
    return candidate



def compose_triadic_bridge(
    domain: TriadicDomain,
    witness: ProsodicWitness,
    q_vector: QVector,
    q_action: QAction,
) -> CandidatePathSeed:
    """Construct J_A(w) in the required F_beta -> F_v -> F_nu order."""
    initial = CandidateTripletBody(
        domain=domain,
        witness=witness,
        court_root=domain.court_root,
        q_bias=domain.inherited_q_bias,
        q_vector=_validate_q_vector(q_vector, "initial Q vector"),
    )
    beta_step = F_beta(initial)
    q_step = F_v(beta_step.after, q_action)
    nu_step = F_nu(q_step.after)
    seed = CandidatePathSeed(domain, witness, (beta_step, q_step, nu_step), nu_step.after)
    return require_complete_triad(seed)



def prove_phase9_exit_gate(
    domain: TriadicDomain,
    witness: ProsodicWitness,
    q_vector: QVector,
    q_action: QAction,
) -> CandidatePathSeed:
    """Admit one candidate to the Aeon phase engine as one complete typed body."""
    return compose_triadic_bridge(domain, witness, q_vector, q_action)
