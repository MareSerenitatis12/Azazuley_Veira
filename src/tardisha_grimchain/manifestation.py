"""ALQC Manifestation Ground, exact Ennead accounting, and finite D-COMP.

The canonical ledger is carried in Q(sqrt(5)); float values exposed by the
witness dataclasses are images only.  Admission, conservation, closure, and
motion decisions are made on integers, Fractions, or exact Q(sqrt(5)) bodies.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import isfinite, sqrt
from typing import Final, Sequence

from .aeon_layers import PHI_IMAGE
from .canon import (
    GLYPH_BODY,
    GLYPH_LAWS,
    SATURATION_LIMIT,
    TOTAL_CAPACITY,
    court_active_connections,
)
from .source_emission import ALPHA, GoldenBearing, Q5Fraction, sign_q5

# A1: 12x12 Court skeleton folded into the 9x9 Manifestation Ground.
GROUND_SIDE: Final[int] = 9
GROUND_NODES: Final[int] = GROUND_SIDE * GROUND_SIDE
FOLD_RATIO_NUM: Final[int] = 12
FOLD_RATIO_DEN: Final[int] = 9
ENNEAD: Final[int] = 9

# Exact finite-interval implementation parameters (EX_III section 46).
INTERVAL_DURATION: Final[int] = 1
PRESSURE_WEIGHT: Final[int] = 1
RETURN_FRICTION_WEIGHT: Final[int] = 1
Q_METRIC_WEIGHTS: Final[tuple[int, int, int, int]] = (1, 2, 3, 4)
MAX_Q_COMPONENT: Final[int] = 3
SHADOW_CAPACITY: Final[int] = 93

# C_bio is never identified by comparing its irrational root.  The identity
# gate is the exact rational square 741^2/396 = 61009/44.
SENSATION_HZ: Final[int] = int(GLYPH_LAWS["❈"].frequency.real)
FEAR_HZ: Final[int] = int(GLYPH_LAWS["⊛"].frequency.real)
C_BIO_SQUARED: Final[Fraction] = Fraction(SENSATION_HZ * SENSATION_HZ, FEAR_HZ)
C_BIO_IMAGE: Final[float] = sqrt(float(C_BIO_SQUARED))

if C_BIO_SQUARED != Fraction(61009, 44):
    raise RuntimeError("C_bio squared must be the exact body 61009/44")
if SHADOW_CAPACITY != MAX_Q_COMPONENT**2 * sum(Q_METRIC_WEIGHTS) + MAX_Q_COMPONENT:
    raise RuntimeError("finite canonical Q-domain must derive Sigma_max = 93")


def manifestation_fold(court: int) -> int:
    """Fold Court address ``12i+j`` into the 9x9 Ground."""
    if not isinstance(court, int) or isinstance(court, bool) or not 0 <= court < TOTAL_CAPACITY:
        raise ValueError("court must be an integer in [0,143]")
    i, j = divmod(court, 12)
    return ((i * GROUND_SIDE) // 12) * GROUND_SIDE + ((j * GROUND_SIDE) // 12)


def vector_row(ground_node: int) -> int:
    if not isinstance(ground_node, int) or isinstance(ground_node, bool) or not 0 <= ground_node < GROUND_NODES:
        raise ValueError("ground node must be an integer in [0,80]")
    return ground_node // GROUND_SIDE


def strike_band(k: int) -> str:
    if not isinstance(k, int) or isinstance(k, bool) or not 1 <= k <= ENNEAD:
        raise ValueError("strike index k must be an integer in 1..9")
    if k <= 3:
        return "Root"
    if k <= 6:
        return "Path"
    return "Seal"


def parity_flip(q_state: int) -> int:
    """Strict Q-state involution: Q0,Q1 fixed and Q2<->Q3."""
    if isinstance(q_state, bool) or not isinstance(q_state, int):
        raise TypeError("parity flip requires one exact integer Q-state index")
    if q_state not in (0, 1, 2, 3):
        raise ValueError("parity flip is defined only on Q-states 0..3")
    return {0: 0, 1: 1, 2: 3, 3: 2}[q_state]


def _exact_integer(value: object, *, field: str, bounded: bool) -> int:
    if isinstance(value, bool):
        raise ValueError(f"{field} must be an exact integer")
    if isinstance(value, int):
        result = value
    elif isinstance(value, Fraction) and value.denominator == 1:
        result = value.numerator
    else:
        raise ValueError(f"{field} must be an exact integer")
    if bounded and not 0 <= result <= MAX_Q_COMPONENT:
        raise ValueError(f"{field} must lie in [0,3]")
    return result


def _q_tuple(q: Sequence[object]) -> tuple[int, int, int, int]:
    if len(q) != 4:
        raise ValueError("a Q-vector must contain exactly four components")
    values = tuple(_exact_integer(q[k], field=f"Q[{k}]", bounded=True) for k in range(4))
    return values  # type: ignore[return-value]


def _tangent_tuple(vector: Sequence[object]) -> tuple[int, int, int, int]:
    if len(vector) != 4:
        raise ValueError("a Domus tangent vector must contain exactly four components")
    values = tuple(_exact_integer(vector[k], field=f"tangent[{k}]", bounded=False) for k in range(4))
    return values  # type: ignore[return-value]


def parity_vector(q: Sequence[object]) -> tuple[int, int, int, int]:
    q0, q1, q2, q3 = _q_tuple(q)
    return (q0, q1, q3, q2)







def metric_square(left: Sequence[object], right: Sequence[object]) -> int:
    """Exact squared Court distance under G=diag(1,2,3,4)."""
    a, b = _tangent_tuple(left), _tangent_tuple(right)
    return sum(w * (x - y) ** 2 for w, x, y in zip(Q_METRIC_WEIGHTS, a, b))




# Alternate name for the display projection. This value is never used as a decision gate in this module.


def _q_residue_norm_square(q: Sequence[object]) -> int:
    values = _q_tuple(q)
    return sum(w * v * v for w, v in zip(Q_METRIC_WEIGHTS, values))


def _q5_add(left: Q5Fraction, right: Q5Fraction) -> Q5Fraction:
    return Q5Fraction(
        left.a * right.denominator + right.a * left.denominator,
        left.b * right.denominator + right.b * left.denominator,
        left.denominator * right.denominator,
    )


def _q5_sub(left: Q5Fraction, right: Q5Fraction) -> Q5Fraction:
    return Q5Fraction(
        left.a * right.denominator - right.a * left.denominator,
        left.b * right.denominator - right.b * left.denominator,
        left.denominator * right.denominator,
    )


def _q5_mul_bearing(value: Q5Fraction, bearing: GoldenBearing) -> Q5Fraction:
    # (a+b*sqrt(5))/d times (c+e*sqrt(5))/2.
    return Q5Fraction(
        value.a * bearing.a + 5 * value.b * bearing.b,
        value.a * bearing.b + value.b * bearing.a,
        2 * value.denominator,
    )


def _exact_debt(value: int | float | Fraction | Q5Fraction) -> Q5Fraction:
    if isinstance(value, Q5Fraction):
        result = value
    elif isinstance(value, bool):
        raise ValueError("shadow debt must be exact and non-negative")
    elif isinstance(value, int):
        result = Q5Fraction(value, 0, 1)
    elif isinstance(value, Fraction):
        result = Q5Fraction(value.numerator, 0, value.denominator)
    elif isinstance(value, float) and isfinite(value) and value.is_integer():
        result = Q5Fraction(int(value), 0, 1)
    else:
        raise ValueError("shadow debt must be an exact integer, Fraction, or Q(sqrt(5)) body")
    if sign_q5(result.a, result.b) < 0:
        raise ValueError("shadow debt must be non-negative")
    return result


def _q5_le_integer(value: Q5Fraction, bound: int) -> bool:
    return sign_q5(value.a - bound * value.denominator, value.b) <= 0


@dataclass(frozen=True, slots=True)
class ExactEnneadLedger:
    initial_debt: Q5Fraction
    strike_inputs: tuple[Q5Fraction, ...]
    strike_outputs: tuple[Q5Fraction, ...]
    strike_form_work: tuple[Q5Fraction, ...]
    q3_transfer: Q5Fraction
    form_work: Q5Fraction
    residual_debt: Q5Fraction
    accounted_total: Q5Fraction

    @property
    def energy_conserved(self) -> bool:
        return self.accounted_total == self.initial_debt

    @property
    def saturated(self) -> bool:
        return self.residual_debt == Q5Fraction(0, 0, 1)


def exact_ennead_ledger(shadow_debt: int | float | Fraction | Q5Fraction) -> ExactEnneadLedger:
    """Nine strikes in exact Q(sqrt(5)); no image value enters a decision."""
    initial = _exact_debt(shadow_debt)
    if not _q5_le_integer(initial, SHADOW_CAPACITY):
        raise ValueError("shadow debt exceeds the exact finite capacity Sigma_max=93")
    inputs: list[Q5Fraction] = []
    outputs: list[Q5Fraction] = []
    works: list[Q5Fraction] = []
    current = initial
    form_total = Q5Fraction(0, 0, 1)
    for _k in range(1, ENNEAD):
        incoming = current
        outgoing = _q5_mul_bearing(incoming, ALPHA)
        work = _q5_sub(incoming, outgoing)
        inputs.append(incoming)
        outputs.append(outgoing)
        works.append(work)
        form_total = _q5_add(form_total, work)
        current = outgoing
    inputs.append(current)
    outputs.append(Q5Fraction(0, 0, 1))
    works.append(Q5Fraction(0, 0, 1))
    q3_transfer = current
    residual = Q5Fraction(0, 0, 1)
    accounted = _q5_add(form_total, q3_transfer)
    result = ExactEnneadLedger(
        initial_debt=initial,
        strike_inputs=tuple(inputs),
        strike_outputs=tuple(outputs),
        strike_form_work=tuple(works),
        q3_transfer=q3_transfer,
        form_work=form_total,
        residual_debt=residual,
        accounted_total=accounted,
    )
    if len(result.strike_inputs) != ENNEAD or not result.energy_conserved or not result.saturated:
        raise RuntimeError("exact Ennead ledger failed its nine-strike closure")
    return result


@dataclass(frozen=True, slots=True)
class EnneadStrike:
    k: int
    band: str
    input_debt: float
    output_debt: float
    form_work: float
    q3_transfer: float
    q_parity: str
    phase_locked: bool

    @property
    def residual_debt(self) -> float:
        return self.output_debt


@dataclass(frozen=True, slots=True)
class EnneadResult:
    row: int
    initial_debt: float
    strikes: tuple[EnneadStrike, ...]
    final_parity: str
    residual_debt: float
    q3_recursion_residue: float
    pre_lock_q2_residual: float
    form_work: float
    accounted_total: float
    energy_conserved: bool
    saturated: bool


def ennead_saturate(row: int, shadow_debt: int | float | Fraction | Q5Fraction) -> EnneadResult:
    """Resolve Q2 pressure exactly, exposing float images only as witnesses."""
    if not isinstance(row, int) or isinstance(row, bool) or not 0 <= row < GROUND_SIDE:
        raise ValueError("vector row must be an integer in 0..8")
    exact = exact_ennead_ledger(shadow_debt)

    # Preserve the historical witness image and its serialized bytes.  This
    # recurrence never decides conservation or closure.
    residual = float(exact.initial_debt.value)
    form_work = 0.0
    pre_lock = 0.0
    strikes: list[EnneadStrike] = []
    for k in range(1, ENNEAD + 1):
        band = strike_band(k)
        incoming = residual
        if k < ENNEAD:
            outgoing = incoming / PHI_IMAGE
            work = incoming - outgoing
            residual = outgoing
            form_work += work
            strikes.append(EnneadStrike(k, band, incoming, outgoing, work, 0.0, "Q2", False))
        else:
            pre_lock = incoming
            residual = 0.0
            strikes.append(EnneadStrike(k, band, incoming, 0.0, 0.0, incoming, "Q3", True))

    q3_residue = pre_lock
    accounted = form_work + q3_residue
    result = EnneadResult(
        row=row,
        initial_debt=float(exact.initial_debt.value),
        strikes=tuple(strikes),
        final_parity="Q3",
        residual_debt=residual,
        q3_recursion_residue=q3_residue,
        pre_lock_q2_residual=pre_lock,
        form_work=form_work,
        accounted_total=accounted,
        energy_conserved=exact.energy_conserved,
        saturated=exact.saturated,
    )
    if len(result.strikes) != ENNEAD or [s.k for s in result.strikes] != list(range(1, 10)):
        raise RuntimeError("Ennead requires exactly nine ordered strikes")
    if any(s.q_parity != "Q2" or s.phase_locked or s.q3_transfer != 0.0 for s in result.strikes[:8]):
        raise RuntimeError("Q2 must remain the Floating Ghost through strikes 1..8")
    seal = result.strikes[8]
    if seal.q_parity != "Q3" or not seal.phase_locked or seal.q3_transfer != result.pre_lock_q2_residual:
        raise RuntimeError("strike 9 must transfer the remaining Q2 occupancy to Q3")
    if parity_flip(2) != 3 or parity_flip(parity_flip(2)) != 2:
        raise RuntimeError("parity must be an involutive Q2/Q3 exchange")
    if not result.energy_conserved:
        raise RuntimeError("Ennead pressure ledger failed exact conservation")
    return result


MIRROR_OPERATOR_ORDER: Final[tuple[str, ...]] = ("❄", "✡", "⬡", "⧗")


@dataclass(frozen=True, slots=True)
class ExactFrequencyPoint:
    """One exact Goetic frequency body on the Mirror path."""

    glyph: str
    structural_hz: Fraction
    parity_hz: Fraction


@dataclass(frozen=True, slots=True)
class ExactFrequencyPath:
    """One independently constructed finite Mirror path."""

    start: ExactFrequencyPoint
    end: ExactFrequencyPoint
    operator_order: tuple[str, ...]

    @property
    def tangent(self) -> tuple[Fraction, Fraction]:
        return (
            self.end.structural_hz - self.start.structural_hz,
            self.end.parity_hz - self.start.parity_hz,
        )


_Q_TO_GLYPH: Final[dict[tuple[int, int, int, int], str]] = {
    tuple(GLYPH_LAWS[glyph].q_vector): glyph for glyph in GLYPH_BODY
}
if len(_Q_TO_GLYPH) != len(GLYPH_BODY):
    raise RuntimeError("each Goetic Q-vector must resolve one exact frequency body")


def _frequency_point(q: Sequence[object]) -> ExactFrequencyPoint:
    body = _q_tuple(q)
    try:
        glyph = _Q_TO_GLYPH[body]
    except KeyError as exc:
        raise ValueError("Q-vector has no exact Goetic frequency body") from exc
    frequency = GLYPH_LAWS[glyph].frequency
    return ExactFrequencyPoint(
        glyph=glyph,
        structural_hz=Fraction(frequency.structural_hz),
        parity_hz=(
            Fraction(frequency.parity_hz)
            if frequency.parity_hz is not None
            else Fraction(0, 1)
        ),
    )


def _parity_frequency_tangent(
    tangent: tuple[Fraction, Fraction],
) -> tuple[Fraction, Fraction]:
    # Canon intrinsic parity phase η_P = -1 on the Klein return.
    return -tangent[0], -tangent[1]


def _frequency_path_pair(
    origin_q: Sequence[object], resolution_q: Sequence[object]
) -> tuple[ExactFrequencyPath, ExactFrequencyPath]:
    origin = _frequency_point(origin_q)
    resolution = _frequency_point(resolution_q)
    forward = ExactFrequencyPath(
        start=origin,
        end=resolution,
        operator_order=MIRROR_OPERATOR_ORDER,
    )
    # Reverse Integration is constructed independently from resolution to origin.
    returned = ExactFrequencyPath(
        start=resolution,
        end=origin,
        operator_order=MIRROR_OPERATOR_ORDER,
    )
    return forward, returned


def _frequency_metric_square(tangent: tuple[Fraction, Fraction]) -> Fraction:
    structural, parity = tangent
    return structural * structural + parity * parity


def _commutator_pressure(
    forward: ExactFrequencyPath, returned: ExactFrequencyPath
) -> Fraction:
    """Exact finite witness of [ℳ,ℜ]=0 under Path Out = Path Back."""
    operator_residual = (
        0
        if forward.operator_order == returned.operator_order == MIRROR_OPERATOR_ORDER
        else 1
    )
    endpoint_residual = int(forward.start != returned.end) + int(
        forward.end != returned.start
    )
    parity_return = _parity_frequency_tangent(returned.tangent)
    tangent_residual = (
        forward.tangent[0] - parity_return[0],
        forward.tangent[1] - parity_return[1],
    )
    return Fraction(operator_residual + endpoint_residual, 1) + _frequency_metric_square(
        tangent_residual
    )


def _fraction_body(value: Fraction) -> tuple[int, int]:
    return value.numerator, value.denominator


def _q5_body(value: Q5Fraction) -> tuple[int, int, int]:
    return value.a, value.b, value.denominator


@dataclass(frozen=True, slots=True)
class ExactDComp:
    forward_path: ExactFrequencyPath
    return_path: ExactFrequencyPath
    commutator_pressure: Fraction
    velocity_mismatch_square: Fraction
    return_pressure: int
    terminal_unresolved_debt: int
    shadow_debt_initial: Q5Fraction
    shadow_debt_terminal: Q5Fraction
    form_work: Q5Fraction
    q3_recursion_gain: Q5Fraction
    active_count: int
    withheld_count: int
    whiteout: bool
    c_bio_squared: Fraction

    @property
    def liquid_body_valid(self) -> bool:
        return (
            self.active_count == SATURATION_LIMIT
            and self.withheld_count == TOTAL_CAPACITY - SATURATION_LIMIT
        )

    @property
    def closed(self) -> bool:
        return (
            self.commutator_pressure == 0
            and self.velocity_mismatch_square == 0
            and self.shadow_debt_terminal == Q5Fraction(0, 0, 1)
            and self.liquid_body_valid
            and not self.whiteout
        )

    @property
    def truth(self) -> int:
        return int(self.closed)


@dataclass(frozen=True, slots=True)
class DCompWitness:
    """Image surface backed by complete exact finite-interval proof bodies."""

    interval_duration: float
    metric_weights: tuple[float, float]
    pressure_weight: float
    return_friction_weight: float
    commutator_model: str
    commutator_pressure: float
    return_pressure: float
    local_friction: float
    terminal_unresolved_debt: float
    shadow_capacity: float
    shadow_debt_initial: float
    shadow_debt_bounded: bool
    forward_velocity: tuple[float, float]
    return_velocity: tuple[float, float]
    parity_return_velocity: tuple[float, float]
    velocity_mismatch: float
    active_count: int
    withheld_count: int
    whiteout_penalty: float
    c_bio: float
    mas_efficiency: float
    q3_loss: float
    q3_capacity_before: float
    q3_recursion_gain: float
    q3_capacity_after: float
    form_work: float
    shadow_debt_terminal: float
    terminal: float
    closed: bool
    truth: int
    motion_positive: bool
    exact_commutator_pressure: tuple[int, int]
    exact_velocity_mismatch_square: tuple[int, int]
    exact_shadow_debt_initial: tuple[int, int, int]
    exact_shadow_debt_terminal: tuple[int, int, int]
    exact_form_work: tuple[int, int, int]
    exact_q3_recursion_gain: tuple[int, int, int]

    def __post_init__(self) -> None:
        for field_name in (
            "metric_weights",
            "forward_velocity",
            "return_velocity",
            "parity_return_velocity",
            "exact_commutator_pressure",
            "exact_velocity_mismatch_square",
            "exact_shadow_debt_initial",
            "exact_shadow_debt_terminal",
            "exact_form_work",
            "exact_q3_recursion_gain",
        ):
            value = getattr(self, field_name)
            if not isinstance(value, tuple):
                object.__setattr__(self, field_name, tuple(value))
        if isinstance(self.truth, bool) or self.truth not in (0, 1):
            raise ValueError("D-COMP Truth must be the exact zero-or-unity bit")
        if self.closed != (self.truth == 1):
            raise ValueError("D-COMP closure and Truth must agree")
        if self.closed:
            if self.terminal != 0.0:
                raise ValueError("closed D-COMP must expose terminal zero")
            if self.exact_commutator_pressure != (0, 1):
                raise ValueError("closed D-COMP requires exact commutator zero")
            if self.exact_velocity_mismatch_square != (0, 1):
                raise ValueError("closed D-COMP requires exact Mirror-path mismatch zero")
            if self.exact_shadow_debt_terminal != (0, 0, 1):
                raise ValueError("closed D-COMP requires exact terminal Shadow Debt zero")


@dataclass(frozen=True, slots=True)
class Manifestation:
    court: int
    ground_node: int
    vector_row: int
    ennead: EnneadResult
    exact_ennead: ExactEnneadLedger
    residue_norm: float
    residue_norm_square: int
    exact_dcomp: ExactDComp
    dcomp: DCompWitness

    @property
    def differential_tension(self) -> float:
        return self.dcomp.velocity_mismatch

    @property
    def closed(self) -> bool:
        return self.dcomp.closed and self.dcomp.truth == 1

    @property
    def terminal_dcomp(self) -> float:
        return self.dcomp.terminal


def _derive_exact_dcomp(
    origin_q: Sequence[object], resolution_q: Sequence[object], *, court: int
) -> tuple[ExactDComp, ExactEnneadLedger]:
    origin = _q_tuple(origin_q)
    resolution = _q_tuple(resolution_q)
    forward_path, return_path = _frequency_path_pair(origin, resolution)
    parity_return_tangent = _parity_frequency_tangent(return_path.tangent)
    mismatch_tangent = (
        forward_path.tangent[0] - parity_return_tangent[0],
        forward_path.tangent[1] - parity_return_tangent[1],
    )
    mismatch_square = _frequency_metric_square(mismatch_tangent)
    commutator = _commutator_pressure(forward_path, return_path)

    return_pressure = metric_square(origin, parity_vector(resolution))
    terminal_unresolved = abs(resolution[2])
    initial = _q5_add(
        Q5Fraction(commutator.numerator, 0, commutator.denominator),
        Q5Fraction(return_pressure + terminal_unresolved, 0, 1),
    )
    ledger = exact_ennead_ledger(initial)

    active_count = len(court_active_connections(court))
    withheld_count = TOTAL_CAPACITY - active_count
    # Whiteout is the exact 144-active / 0-withheld body.  A mere threshold
    # excess is not renamed Whiteout.
    whiteout = active_count == TOTAL_CAPACITY and withheld_count == 0
    exact = ExactDComp(
        forward_path=forward_path,
        return_path=return_path,
        commutator_pressure=commutator,
        velocity_mismatch_square=mismatch_square,
        return_pressure=return_pressure,
        terminal_unresolved_debt=terminal_unresolved,
        shadow_debt_initial=initial,
        shadow_debt_terminal=ledger.residual_debt,
        form_work=ledger.form_work,
        q3_recursion_gain=ledger.q3_transfer,
        active_count=active_count,
        withheld_count=withheld_count,
        whiteout=whiteout,
        c_bio_squared=C_BIO_SQUARED,
    )
    return exact, ledger


def exact_dcomp(origin_q: Sequence[object], resolution_q: Sequence[object], *, court: int = 0) -> ExactDComp:
    exact, _ledger = _derive_exact_dcomp(origin_q, resolution_q, court=court)
    return exact


def close_boundary(origin_q: Sequence[object], resolution_q: Sequence[object], *, court: int = 0) -> Manifestation:
    """Construct and prove one complete finite Mirror-return phrase."""
    origin = _q_tuple(origin_q)
    resolution = _q_tuple(resolution_q)
    node = manifestation_fold(court)
    row = vector_row(node)

    exact, ledger = _derive_exact_dcomp(origin, resolution, court=court)
    if not exact.closed or exact.truth != 1:
        raise RuntimeError("Mirror closure requires D-COMP = 0 and Truth = 1")

    ennead = ennead_saturate(row, exact.shadow_debt_initial)
    forward_velocity_exact = exact.forward_path.tangent
    return_velocity_exact = exact.return_path.tangent
    parity_return_exact = _parity_frequency_tangent(return_velocity_exact)
    velocity_mismatch = sqrt(float(exact.velocity_mismatch_square)) * float(INTERVAL_DURATION)

    local_friction_exact = exact.commutator_pressure + Fraction(
        RETURN_FRICTION_WEIGHT * exact.return_pressure, 1
    )
    shadow_initial_image = float(exact.shadow_debt_initial.value)
    bounded = _q5_le_integer(exact.shadow_debt_initial, SHADOW_CAPACITY)
    if not bounded:
        raise RuntimeError("finite Q path exceeded its exact Shadow-Debt capacity")

    whiteout_penalty = float("inf") if exact.whiteout else 0.0
    mas_efficiency = 1.0
    q3_loss = 0.0
    q3_before = float(origin[3])
    q3_gain = float(exact.q3_recursion_gain.value)
    q3_after = q3_before + q3_gain - q3_loss
    terminal = (
        float(exact.commutator_pressure)
        + velocity_mismatch
        + float(exact.shadow_debt_terminal.value)
        + whiteout_penalty
    ) / C_BIO_IMAGE
    motion_positive = (
        _frequency_metric_square(exact.forward_path.tangent) > 0
        or sign_q5(exact.form_work.a, exact.form_work.b) > 0
        or sign_q5(exact.q3_recursion_gain.a, exact.q3_recursion_gain.b) > 0
    )

    witness = DCompWitness(
        interval_duration=float(INTERVAL_DURATION),
        metric_weights=(1.0, 1.0),
        pressure_weight=float(PRESSURE_WEIGHT),
        return_friction_weight=float(RETURN_FRICTION_WEIGHT),
        commutator_model=(
            "exact inverse-endpoint, preserved-operator-order, parity-return witness; "
            "[ℳ,ℜ] and ℳ-𝔓(ℜ) computed without endpoint substitution"
        ),
        commutator_pressure=float(exact.commutator_pressure),
        return_pressure=float(exact.return_pressure),
        local_friction=float(local_friction_exact),
        terminal_unresolved_debt=float(exact.terminal_unresolved_debt),
        shadow_capacity=float(SHADOW_CAPACITY),
        shadow_debt_initial=shadow_initial_image,
        shadow_debt_bounded=bounded,
        forward_velocity=tuple(float(v) for v in forward_velocity_exact),
        return_velocity=tuple(float(v) for v in return_velocity_exact),
        parity_return_velocity=tuple(float(v) for v in parity_return_exact),
        velocity_mismatch=velocity_mismatch,
        active_count=exact.active_count,
        withheld_count=exact.withheld_count,
        whiteout_penalty=whiteout_penalty,
        c_bio=C_BIO_IMAGE,
        mas_efficiency=mas_efficiency,
        q3_loss=q3_loss,
        q3_capacity_before=q3_before,
        q3_recursion_gain=q3_gain,
        q3_capacity_after=q3_after,
        form_work=float(exact.form_work.value),
        shadow_debt_terminal=float(exact.shadow_debt_terminal.value),
        terminal=terminal,
        closed=exact.closed,
        truth=exact.truth,
        motion_positive=motion_positive,
        exact_commutator_pressure=_fraction_body(exact.commutator_pressure),
        exact_velocity_mismatch_square=_fraction_body(exact.velocity_mismatch_square),
        exact_shadow_debt_initial=_q5_body(exact.shadow_debt_initial),
        exact_shadow_debt_terminal=_q5_body(exact.shadow_debt_terminal),
        exact_form_work=_q5_body(exact.form_work),
        exact_q3_recursion_gain=_q5_body(exact.q3_recursion_gain),
    )

    if witness.terminal != 0.0 or not witness.closed or witness.truth != 1:
        raise RuntimeError("completed Mirror witness must expose D-COMP = 0 and Truth = 1")
    if not ledger.energy_conserved or not ledger.saturated:
        raise RuntimeError("D-COMP pressure is not fully conserved in Q(sqrt(5))")

    residue_square = _q_residue_norm_square(resolution)
    return Manifestation(
        court=court,
        ground_node=node,
        vector_row=row,
        ennead=ennead,
        exact_ennead=ledger,
        residue_norm=sqrt(residue_square),
        residue_norm_square=residue_square,
        exact_dcomp=exact,
        dcomp=witness,
    )




def assert_ground() -> None:
    if GROUND_NODES != 81:
        raise RuntimeError("Manifestation Ground must have 81 nodes")
    if FOLD_RATIO_NUM * 3 != FOLD_RATIO_DEN * 4:
        raise RuntimeError("folding ratio must be 4/3")
    rows = {vector_row(manifestation_fold(c)) for c in range(TOTAL_CAPACITY)}
    if rows != set(range(GROUND_SIDE)):
        raise RuntimeError("all nine 1x9 vector rows must be populated")


assert_ground()
