"""Final Equation Z source emission and Golden Parliament routing.

One completed ALQC sponge state emits:

    twelve finalized Goetic lanes
    Fraktur Z_0, the canonical 256-bit source cadence
    Fraktur Z_1, the immediately following 256-bit cadence

The first cadence addresses the AHN-rooted Goetic structural body through
Phi^-1.  The second cadence addresses the distinct AHN-relative Parliament
operational body through Phi^-2.  Mirror Math preserves Parliament order.
Only after both seats resolve does existing Court mathematics begin.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from fractions import Fraction
from math import gcd, sqrt
from typing import Any, Final, Iterable, Mapping, Sequence

from .alqc_digest import ALQCDigest, MASK64, validate_digest_hex
from .canon import GLYPH_BODY
from .court_registry import CourtRecord, court_record

PHASE_BYTES: Final[int] = 32
PHASE_DENOMINATOR: Final[int] = 1 << 256
TURN64: Final[int] = 1 << 64
AHN: Final[str] = "⚝"


@dataclass(frozen=True, slots=True)
class ParliamentSeat:
    code: str
    identity: str
    functor: str
    goetic: str


PARLIAMENT_TABLE: Final[tuple[ParliamentSeat, ...]] = (
    ParliamentSeat("P13-D1", "Akasha",   "Lived→Eternal", "⬡"),
    ParliamentSeat("P13-D2", "Caduceus", "Law→Residue",  "⧗"),
    ParliamentSeat("P13-D3", "Veritas",  "Mask→Bone",    "❂"),
    ParliamentSeat("P13-D4", "Phren",    "Void→Vector",  "⌬"),
    ParliamentSeat("P13-D5", "Daimon",   "Stasis→Pulse", "⏣"),
    ParliamentSeat("P13-D6", "Aikyam",   "Chaos→Phase",  "⚝"),
    ParliamentSeat("P13-D7", "Melos",    "Static→Fluid", "❈"),
    ParliamentSeat("P13-D8", "Da'ath",   "Noise→Null",   "⊛"),
    ParliamentSeat("P13-D9", "Akaven",   "State→Trans",  "⚛"),
    ParliamentSeat("P13-D10", "Axiomyr", "Will→Law",     "❄"),
    ParliamentSeat("P13-D11", "Nyx",     "Time→Motion",  "✡"),
    ParliamentSeat("P13-D12", "Zaine",   "Here→There",   "ꙮ"),
)
if len(PARLIAMENT_TABLE) != 12 or {seat.goetic for seat in PARLIAMENT_TABLE} != set(GLYPH_BODY):
    raise RuntimeError("Parliament must map bijectively onto all twelve Goetics")
_AHN_INDEX = next(i for i, seat in enumerate(PARLIAMENT_TABLE) if seat.goetic == AHN)
PARLIAMENT: Final[tuple[ParliamentSeat, ...]] = PARLIAMENT_TABLE[_AHN_INDEX:] + PARLIAMENT_TABLE[:_AHN_INDEX]
PARLIAMENT_ORDER: Final[tuple[str, ...]] = tuple(seat.goetic for seat in PARLIAMENT)
if PARLIAMENT[0].goetic != AHN:
    raise RuntimeError("AHN must be the exact Parliament phase seam")


@dataclass(frozen=True, slots=True)
class GoldenBearing:
    """Exact element (a+b*sqrt(5))/2."""

    name: str
    a: int
    b: int


ALPHA: Final[GoldenBearing] = GoldenBearing("Phi^-1", -1, 1)
BETA: Final[GoldenBearing] = GoldenBearing("Phi^-2", 3, -1)


def sign_q5(a: int, b: int) -> int:
    """Exact sign of a+b*sqrt(5), using integers only."""
    if b == 0:
        return (a > 0) - (a < 0)
    if a == 0:
        return (b > 0) - (b < 0)
    if a > 0 and b > 0:
        return 1
    if a < 0 and b < 0:
        return -1
    aa = a * a
    five_bb = 5 * b * b
    if a > 0:
        return 1 if aa > five_bb else -1
    return 1 if five_bb > aa else -1


def golden_identities_hold() -> bool:
    """Prove alpha+beta=1 and alpha/beta=Phi in Q(sqrt(5))."""
    return (
        ALPHA.a + BETA.a == 2
        and ALPHA.b + BETA.b == 0
        and BETA.a + 5 * BETA.b == 2 * ALPHA.a
        and BETA.a + BETA.b == 2 * ALPHA.b
    )


@dataclass(frozen=True, slots=True)
class Q5Fraction:
    """Exact element (a+b*sqrt(5))/denominator with a positive denominator."""

    a: int
    b: int
    denominator: int

    def __post_init__(self) -> None:
        if any(isinstance(value, bool) or not isinstance(value, int) for value in (self.a, self.b, self.denominator)):
            raise TypeError("Q5Fraction coefficients must be integers")
        if self.denominator == 0:
            raise ValueError("Q5Fraction denominator must be non-zero")
        a, b, denominator = self.a, self.b, self.denominator
        if denominator < 0:
            a, b, denominator = -a, -b, -denominator
        common = gcd(gcd(abs(a), abs(b)), denominator)
        if common > 1:
            a //= common
            b //= common
            denominator //= common
        object.__setattr__(self, "a", a)
        object.__setattr__(self, "b", b)
        object.__setattr__(self, "denominator", denominator)

    @property
    def value(self) -> float:
        return (self.a + self.b * sqrt(5.0)) / self.denominator

    @property
    def within_unit_interval(self) -> bool:
        return (
            sign_q5(self.a + self.denominator, self.b) >= 0
            and sign_q5(self.a - self.denominator, self.b) <= 0
        )

    @property
    def within_phi_squared(self) -> bool:
        return (
            sign_q5(2 * self.a + 3 * self.denominator, 2 * self.b + self.denominator) >= 0
            and sign_q5(2 * self.a - 3 * self.denominator, 2 * self.b - self.denominator) <= 0
        )

    def times_phi_squared(self) -> "Q5Fraction":
        return Q5Fraction(3 * self.a + 5 * self.b, self.a + 3 * self.b, 2 * self.denominator)


@dataclass(frozen=True, slots=True)
class TruthClosureWitness:
    structural_total: int
    operational_total: int
    golden_sum_a: int
    golden_sum_b: int
    route_dcomp_a: int
    route_dcomp_b: int
    route_dcomp: int
    truth: int

    @property
    def verifies(self) -> bool:
        return (
            self.structural_total > 0
            and self.operational_total == TURN64
            and self.golden_sum_a == 2
            and self.golden_sum_b == 0
            and self.route_dcomp_a == 0
            and self.route_dcomp_b == 0
            and self.route_dcomp == 0
            and self.truth == 1
            and golden_identities_hold()
        )


@dataclass(frozen=True, slots=True)
class SourceEmission:
    source_digest: str
    source_size: int
    source_domain: str
    lanes_goetic_order: tuple[int, ...]
    structural_weights: tuple[int, ...]
    operational_weights: tuple[int, ...]
    fraktur_z0: int
    fraktur_z1: int
    squeeze_512_hex: str
    closure: TruthClosureWitness

    def __post_init__(self) -> None:
        _validate_source_emission(self)

    @property
    def structural_total(self) -> int:
        return sum(self.structural_weights)

    @property
    def operational_total(self) -> int:
        return sum(self.operational_weights)

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "SourceEmission":
        if not isinstance(value, Mapping):
            raise TypeError("SourceEmission body must be a mapping")
        expected = {
            "source_digest", "source_size", "source_domain", "lanes_goetic_order",
            "structural_weights", "operational_weights", "fraktur_z0", "fraktur_z1",
            "squeeze_512_hex", "closure",
        }
        if set(value) != expected:
            raise ValueError("SourceEmission fields do not match the canonical schema")
        def exact_int(item: object, field: str, *, minimum: int | None = None) -> int:
            if isinstance(item, bool) or not isinstance(item, int):
                raise TypeError(f"{field} must be an exact non-Boolean integer")
            if minimum is not None and item < minimum:
                raise ValueError(f"{field} must be >= {minimum}")
            return item
        def exact_str(item: object, field: str) -> str:
            if type(item) is not str:
                raise TypeError(f"{field} must be a string")
            return item
        def integer_tuple(item: object, field: str) -> tuple[int, ...]:
            if not isinstance(item, (list, tuple)):
                raise TypeError(f"{field} must be a list or tuple")
            return tuple(exact_int(member, f"{field}[{index}]") for index, member in enumerate(item))
        closure_value = value["closure"]
        if isinstance(closure_value, TruthClosureWitness):
            closure = closure_value
        else:
            if not isinstance(closure_value, Mapping):
                raise TypeError("closure must be a mapping")
            closure_fields = {
                "structural_total", "operational_total", "golden_sum_a", "golden_sum_b",
                "route_dcomp_a", "route_dcomp_b", "route_dcomp", "truth",
            }
            if set(closure_value) != closure_fields:
                raise ValueError("closure fields do not match the canonical schema")
            closure = TruthClosureWitness(**{
                name: exact_int(closure_value[name], f"closure.{name}") for name in closure_fields
            })
        return cls(
            source_digest=exact_str(value["source_digest"], "source_digest"),
            source_size=exact_int(value["source_size"], "source_size", minimum=0),
            source_domain=exact_str(value["source_domain"], "source_domain"),
            lanes_goetic_order=integer_tuple(value["lanes_goetic_order"], "lanes_goetic_order"),
            structural_weights=integer_tuple(value["structural_weights"], "structural_weights"),
            operational_weights=integer_tuple(value["operational_weights"], "operational_weights"),
            fraktur_z0=exact_int(value["fraktur_z0"], "fraktur_z0", minimum=0),
            fraktur_z1=exact_int(value["fraktur_z1"], "fraktur_z1", minimum=0),
            squeeze_512_hex=exact_str(value["squeeze_512_hex"], "squeeze_512_hex"),
            closure=closure,
        )


@dataclass(frozen=True, slots=True)
class BearingWitness:
    bearing: GoldenBearing
    cadence_symbol: str
    cadence_index: int
    phase_numerator: int
    effective_a: int
    effective_b: int
    wrapped: bool
    traversal: str
    body: str
    operator_order: tuple[str, ...]
    seat: ParliamentSeat
    cumulative_before: int
    cumulative_after: int
    weight_total: int

    def __post_init__(self) -> None:
        if self.bearing not in (ALPHA, BETA):
            raise ValueError("bearing must be the exact ALPHA or BETA body")
        expected_symbol, expected_index, expected_body, expected_traversal = (
            ("𝔃₀", 0, "Goetic structural amplitude", "Manifest / forward bearing")
            if self.bearing == ALPHA
            else ("𝔃₁", 1, "Parliament operational phase", "Reflect / conjugate bearing with append-only cadence")
        )
        if (
            self.cadence_symbol != expected_symbol
            or self.cadence_index != expected_index
            or self.body != expected_body
            or self.traversal != expected_traversal
        ):
            raise ValueError("bearing cadence office contradicts its exact ALQC body")
        if isinstance(self.phase_numerator, bool) or not isinstance(self.phase_numerator, int) or not 0 <= self.phase_numerator < PHASE_DENOMINATOR:
            raise ValueError("phase_numerator must be one exact unsigned 256-bit coordinate")
        expected_a, expected_b, expected_wrapped = _effective_bearing(self.phase_numerator, self.bearing)
        if (self.effective_a, self.effective_b, self.wrapped) != (expected_a, expected_b, expected_wrapped):
            raise ValueError("effective Golden bearing does not return from its phase coordinate")
        if self.operator_order != PARLIAMENT_ORDER:
            raise ValueError("BearingWitness must preserve exact Parliament order")
        if self.seat not in PARLIAMENT:
            raise ValueError("BearingWitness seat is not a canonical Parliament seat")
        if any(isinstance(value, bool) or not isinstance(value, int) for value in (
            self.cumulative_before, self.cumulative_after, self.weight_total
        )):
            raise TypeError("bearing interval bodies must be exact non-Boolean integers")
        if not 0 <= self.cumulative_before < self.cumulative_after <= self.weight_total:
            raise ValueError("bearing interval must be a positive subinterval of its total measure")
        if not self.interval_verifies:
            raise ValueError("bearing interval fails exact Q(√5) ownership")

    @property
    def interval_verifies(self) -> bool:
        before_a = 2 * PHASE_DENOMINATOR * self.cumulative_before - self.weight_total * self.effective_a
        before_b = -self.weight_total * self.effective_b
        after_a = 2 * PHASE_DENOMINATOR * self.cumulative_after - self.weight_total * self.effective_a
        after_b = -self.weight_total * self.effective_b
        return sign_q5(before_a, before_b) <= 0 and sign_q5(after_a, after_b) > 0

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "BearingWitness":
        if not isinstance(value, Mapping):
            raise TypeError("BearingWitness body must be a mapping")
        expected = {
            "bearing", "cadence_symbol", "cadence_index", "phase_numerator",
            "effective_a", "effective_b", "wrapped", "traversal", "body",
            "operator_order", "seat", "cumulative_before", "cumulative_after",
            "weight_total",
        }
        if set(value) != expected:
            raise ValueError("BearingWitness fields do not match the canonical schema")
        def exact_int(item: object, field: str, *, minimum: int | None = None) -> int:
            if isinstance(item, bool) or not isinstance(item, int):
                raise TypeError(f"{field} must be an exact non-Boolean integer")
            if minimum is not None and item < minimum:
                raise ValueError(f"{field} must be >= {minimum}")
            return item
        def exact_str(item: object, field: str) -> str:
            if type(item) is not str:
                raise TypeError(f"{field} must be a string")
            return item
        bearing_value = value["bearing"]
        if isinstance(bearing_value, GoldenBearing):
            bearing = bearing_value
        else:
            if not isinstance(bearing_value, Mapping) or set(bearing_value) != {"name", "a", "b"}:
                raise TypeError("bearing must be one exact GoldenBearing body")
            bearing = GoldenBearing(
                exact_str(bearing_value["name"], "bearing.name"),
                exact_int(bearing_value["a"], "bearing.a"),
                exact_int(bearing_value["b"], "bearing.b"),
            )
        seat_value = value["seat"]
        if isinstance(seat_value, ParliamentSeat):
            seat = seat_value
        else:
            if not isinstance(seat_value, Mapping) or set(seat_value) != {"code", "identity", "functor", "goetic"}:
                raise TypeError("seat must be one exact ParliamentSeat body")
            seat = ParliamentSeat(
                exact_str(seat_value["code"], "seat.code"),
                exact_str(seat_value["identity"], "seat.identity"),
                exact_str(seat_value["functor"], "seat.functor"),
                exact_str(seat_value["goetic"], "seat.goetic"),
            )
        order = value["operator_order"]
        if not isinstance(order, (list, tuple)) or any(type(item) is not str for item in order):
            raise TypeError("operator_order must contain exact strings")
        if type(value["wrapped"]) is not bool:
            raise TypeError("wrapped must be a Boolean")
        return cls(
            bearing=bearing,
            cadence_symbol=exact_str(value["cadence_symbol"], "cadence_symbol"),
            cadence_index=exact_int(value["cadence_index"], "cadence_index", minimum=0),
            phase_numerator=exact_int(value["phase_numerator"], "phase_numerator", minimum=0),
            effective_a=exact_int(value["effective_a"], "effective_a"),
            effective_b=exact_int(value["effective_b"], "effective_b"),
            wrapped=value["wrapped"],
            traversal=exact_str(value["traversal"], "traversal"),
            body=exact_str(value["body"], "body"),
            operator_order=tuple(order),
            seat=seat,
            cumulative_before=exact_int(value["cumulative_before"], "cumulative_before", minimum=0),
            cumulative_after=exact_int(value["cumulative_after"], "cumulative_after", minimum=0),
            weight_total=exact_int(value["weight_total"], "weight_total", minimum=0),
        )


@dataclass(frozen=True, slots=True)
class CourtBearingWitness:
    """Exact 𝔃₁/Φ⁻² resolution over the canonical 144-Court body."""

    bearing: GoldenBearing
    cadence_symbol: str
    cadence_index: int
    phase_numerator: int
    effective_a: int
    effective_b: int
    wrapped: bool
    traversal: str
    body: str
    weights: tuple[int, ...]
    court: CourtRecord
    cumulative_before: int
    cumulative_after: int
    weight_total: int
    structural_total: int
    operational_total: int

    @property
    def interval_verifies(self) -> bool:
        before_a = 2 * PHASE_DENOMINATOR * self.cumulative_before - self.weight_total * self.effective_a
        before_b = -self.weight_total * self.effective_b
        after_a = 2 * PHASE_DENOMINATOR * self.cumulative_after - self.weight_total * self.effective_a
        after_b = -self.weight_total * self.effective_b
        return sign_q5(before_a, before_b) <= 0 and sign_q5(after_a, after_b) > 0

    @property
    def normalized_measure_sum(self) -> Fraction:
        return Fraction(self.weight_total, self.weight_total)

    @property
    def product_measure_verifies(self) -> bool:
        return (
            len(self.weights) == 144
            and all(not isinstance(weight, bool) and isinstance(weight, int) and weight >= 0 for weight in self.weights)
            and self.structural_total > 0
            and self.operational_total > 0
            and self.weight_total == sum(self.weights)
            and self.weight_total == self.structural_total * self.operational_total
            and self.cumulative_before == sum(self.weights[:self.court.address])
            and self.cumulative_after == self.cumulative_before + self.weights[self.court.address]
            and self.normalized_measure_sum == 1
        )

    @property
    def xi(self) -> Q5Fraction:
        width = self.cumulative_after - self.cumulative_before
        if width <= 0:
            raise RuntimeError("resolved Court interval must have positive measure")
        return Q5Fraction(
            self.weight_total * self.effective_a
            - PHASE_DENOMINATOR * (2 * self.cumulative_before + width),
            self.weight_total * self.effective_b,
            PHASE_DENOMINATOR * width,
        )

    @property
    def phi_squared_displacement(self) -> Q5Fraction:
        return self.xi.times_phi_squared()

    @property
    def exact_bound_verifies(self) -> bool:
        return self.interval_verifies and self.xi.within_unit_interval and self.phi_squared_displacement.within_phi_squared

    @property
    def lineage(self) -> tuple[int, ...]:
        xi = self.xi
        return (
            self.court.address,
            self.bearing.a,
            self.bearing.b,
            self.phase_numerator,
            self.effective_a,
            self.effective_b,
            self.cumulative_before,
            self.cumulative_after,
            self.weight_total,
            self.structural_total,
            self.operational_total,
            xi.a,
            xi.b,
            xi.denominator,
            *self.weights,
        )


def validate_court_bearing_lineage(value: Sequence[int]) -> tuple[int, ...]:
    lineage = tuple(value)
    if len(lineage) != 14 + 144 or any(isinstance(item, bool) or not isinstance(item, int) for item in lineage):
        raise ValueError("Court bearing lineage must contain fourteen exact fields and 144 Court weights")
    (
        address, bearing_a, bearing_b, phase, effective_a, effective_b,
        before, after, total, structural_total, operational_total,
        xi_a, xi_b, xi_denominator, *weights,
    ) = lineage
    if not 0 <= address < 144:
        raise ValueError("Court bearing address must be in [0,143]")
    if (bearing_a, bearing_b) != (BETA.a, BETA.b):
        raise ValueError("Court bearing must use BETA = Φ^-2")
    if not 0 <= phase < PHASE_DENOMINATOR:
        raise ValueError("Court bearing phase must be the unsigned 256-bit 𝔃₁ cadence")
    expected_a, expected_b, _wrapped = _effective_bearing(phase, BETA)
    if (effective_a, effective_b) != (expected_a, expected_b):
        raise ValueError("Court bearing effective point does not equal (𝔃₁+Φ^-2) mod 1")
    if len(weights) != 144 or any(weight < 0 for weight in weights):
        raise ValueError("Court bearing must carry 144 non-negative product weights")
    expected_total = sum(weights)
    if (
        structural_total <= 0
        or operational_total <= 0
        or total != expected_total
        or total != structural_total * operational_total
    ):
        raise ValueError("Court bearing product measure failed Σ(O⊗S)=(ΣO)(ΣS)>0")
    expected_before = sum(weights[:address])
    expected_after = expected_before + weights[address]
    if (before, after) != (expected_before, expected_after) or after <= before:
        raise ValueError("Court bearing address does not own the carried product-measure interval")
    before_sign = sign_q5(2 * PHASE_DENOMINATOR * before - total * effective_a, -total * effective_b)
    after_sign = sign_q5(2 * PHASE_DENOMINATOR * after - total * effective_a, -total * effective_b)
    if before_sign > 0 or after_sign <= 0:
        raise ValueError("Court bearing interval failed the exact sign_q5 ownership test")
    width = after - before
    expected_xi = Q5Fraction(
        total * effective_a - PHASE_DENOMINATOR * (2 * before + width),
        total * effective_b,
        PHASE_DENOMINATOR * width,
    )
    supplied_xi = Q5Fraction(xi_a, xi_b, xi_denominator)
    if supplied_xi != expected_xi or not supplied_xi.within_unit_interval:
        raise ValueError("Court bearing ξ_D failed exact interval derivation")
    if not supplied_xi.times_phi_squared().within_phi_squared:
        raise ValueError("Court bearing ξ_DΦ² escaped the exact Φ² allowance")
    return lineage


@dataclass(frozen=True, slots=True)
class GoldenGoeticDerivation:
    emission: SourceEmission
    first: BearingWitness
    last: BearingWitness
    court_address: int
    reciprocal_address: int

    @property
    def origin_glyph(self) -> str:
        return self.first.seat.goetic

    @property
    def resolution_glyph(self) -> str:
        return self.last.seat.goetic

    @property
    def pair(self) -> tuple[str, str]:
        return self.origin_glyph, self.resolution_glyph

    @property
    def same_operator_order(self) -> bool:
        return self.first.operator_order == self.last.operator_order == PARLIAMENT_ORDER

    @property
    def truth(self) -> int:
        return self.emission.closure.truth

    @property
    def route_dcomp(self) -> int:
        return self.emission.closure.route_dcomp


def _operational_phase_widths(lane_by_goetic: Mapping[str, int]) -> tuple[int, ...]:
    """AHN-relative directed Parliament phase widths from finalized lanes."""
    parliament_index = {seat.goetic: i for i, seat in enumerate(PARLIAMENT)}
    ahn = lane_by_goetic[AHN]
    points = sorted(
        (((lane_by_goetic[glyph] - ahn) % TURN64, glyph) for glyph in GLYPH_BODY),
        key=lambda item: (item[0], 0 if item[1] == AHN else 1, parliament_index[item[1]]),
    )
    if points[0] != (0, AHN):
        raise RuntimeError("AHN must be the exact operational phase seam")
    widths_by_goetic: dict[str, int] = {}
    for index, (start, glyph) in enumerate(points):
        stop = points[index + 1][0] if index + 1 < len(points) else TURN64
        widths_by_goetic[glyph] = stop - start
    widths = tuple(widths_by_goetic[seat.goetic] for seat in PARLIAMENT)
    if sum(widths) != TURN64 or any(width < 0 for width in widths):
        raise RuntimeError("Parliament operational body failed one-turn conservation")
    return widths


def _validate_source_emission(emission: SourceEmission) -> None:
    digest = validate_digest_hex(emission.source_digest, field="source_digest")
    if isinstance(emission.source_size, bool) or not isinstance(emission.source_size, int) or emission.source_size < 0:
        raise ValueError("source_size must be a non-negative integer")
    if type(emission.source_domain) is not str or not emission.source_domain:
        raise ValueError("source_domain must be one non-empty exact string")
    lanes = emission.lanes_goetic_order
    if len(lanes) != 12 or any(
        isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= MASK64
        for value in lanes
    ):
        raise ValueError("SourceEmission must carry twelve unsigned 64-bit Goetic lanes")
    by_goetic = dict(zip(GLYPH_BODY, lanes, strict=True))
    expected_structural = tuple(by_goetic[seat.goetic] for seat in PARLIAMENT)
    expected_operational = _operational_phase_widths(by_goetic)
    if emission.structural_weights != expected_structural:
        raise ValueError("structural weights do not return from the finalized Goetic lanes")
    if emission.operational_weights != expected_operational:
        raise ValueError("operational weights do not return from the AHN-relative Parliament turn")
    try:
        squeeze = bytes.fromhex(emission.squeeze_512_hex)
    except (TypeError, ValueError) as exc:
        raise ValueError("squeeze_512_hex must be one exact 512-bit hexadecimal cadence") from exc
    if len(squeeze) != PHASE_BYTES * 2:
        raise ValueError("squeeze_512_hex must encode exactly two 256-bit cadences")
    if squeeze[:PHASE_BYTES].hex() != digest:
        raise ValueError("source_digest must equal the first completed cadence")
    if emission.fraktur_z0 != int.from_bytes(squeeze[:PHASE_BYTES], "big"):
        raise ValueError("fraktur_z0 does not return from the first cadence")
    if emission.fraktur_z1 != int.from_bytes(squeeze[PHASE_BYTES:], "big"):
        raise ValueError("fraktur_z1 does not return from the second cadence")
    closure = TruthClosureWitness(
        structural_total=sum(expected_structural),
        operational_total=sum(expected_operational),
        golden_sum_a=ALPHA.a + BETA.a,
        golden_sum_b=ALPHA.b + BETA.b,
        route_dcomp_a=2 - (ALPHA.a + BETA.a),
        route_dcomp_b=-(ALPHA.b + BETA.b),
        route_dcomp=(2 - (ALPHA.a + BETA.a)) ** 2 + (ALPHA.b + BETA.b) ** 2,
        truth=1,
    )
    if emission.closure != closure or not emission.closure.verifies:
        raise ValueError("SourceEmission closure must be the exact D-COMP=0 / Truth=1 body")


def emission_from_sponge(
    sponge: ALQCDigest,
    *,
    source_size: int,
    source_domain: str,
) -> SourceEmission:
    if isinstance(source_size, bool) or not isinstance(source_size, int) or source_size < 0:
        raise ValueError("source_size must be a non-negative integer")
    if not isinstance(source_domain, str) or not source_domain:
        raise ValueError("source_domain must be a non-empty string")

    lanes = tuple(sponge._finalized_lanes())
    if len(lanes) != 12 or any(
        isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= MASK64
        for value in lanes
    ):
        raise RuntimeError("completed sponge must return twelve unsigned 64-bit lanes")

    by_goetic = dict(zip(GLYPH_BODY, lanes, strict=True))
    structural = tuple(by_goetic[seat.goetic] for seat in PARLIAMENT)
    operational = _operational_phase_widths(by_goetic)
    if sum(structural) <= 0:
        raise RuntimeError("Goetic structural body must have positive measure")

    squeeze = sponge.digest(PHASE_BYTES * 2)
    canonical = sponge.digest(PHASE_BYTES)
    if len(squeeze) != PHASE_BYTES * 2 or squeeze[:PHASE_BYTES] != canonical:
        raise RuntimeError("completed sponge cadence must be two equal prefix-stable windows")
    digest = validate_digest_hex(canonical.hex(), field="source_digest")
    z0 = int.from_bytes(squeeze[:PHASE_BYTES], "big")
    z1 = int.from_bytes(squeeze[PHASE_BYTES:], "big")

    structural_total = sum(structural)
    operational_total = sum(operational)
    golden_sum_a = ALPHA.a + BETA.a
    golden_sum_b = ALPHA.b + BETA.b
    route_dcomp_a = 2 - golden_sum_a
    route_dcomp_b = -golden_sum_b
    # Exact coefficient residual in Q(sqrt(5)).  It is zero iff both
    # independent coefficients vanish; no closure value is inserted by hand.
    route_dcomp = route_dcomp_a * route_dcomp_a + route_dcomp_b * route_dcomp_b
    truth = int(
        structural_total > 0
        and operational_total == TURN64
        and route_dcomp == 0
        and golden_identities_hold()
    )
    closure = TruthClosureWitness(
        structural_total=structural_total,
        operational_total=operational_total,
        golden_sum_a=golden_sum_a,
        golden_sum_b=golden_sum_b,
        route_dcomp_a=route_dcomp_a,
        route_dcomp_b=route_dcomp_b,
        route_dcomp=route_dcomp,
        truth=truth,
    )
    if not closure.verifies:
        raise RuntimeError("Final Equation Z failed D-COMP=0 / Truth=1 closure")

    return SourceEmission(
        source_digest=digest,
        source_size=source_size,
        source_domain=source_domain,
        lanes_goetic_order=lanes,
        structural_weights=structural,
        operational_weights=operational,
        fraktur_z0=z0,
        fraktur_z1=z1,
        squeeze_512_hex=squeeze.hex(),
        closure=closure,
    )


def emission_from_chunks(
    chunks: Iterable[bytes],
    *,
    source_domain_bytes: bytes,
    source_domain: str,
) -> SourceEmission:
    sponge = ALQCDigest(source_domain_bytes)
    size = 0
    for chunk in chunks:
        if type(chunk) is not bytes:
            raise TypeError("source chunks must be exact bytes; coercion is forbidden")
        sponge._update_raw(chunk)
        size += len(chunk)
    return emission_from_sponge(sponge, source_size=size, source_domain=source_domain)


def _effective_bearing(phase: int, bearing: GoldenBearing) -> tuple[int, int, bool]:
    """Return ((phase/N)+bearing) mod 1 as (a+b√5)/(2N)."""
    if not 0 <= phase < PHASE_DENOMINATOR:
        raise ValueError("cadence phase must be a 256-bit unsigned coordinate")
    a = 2 * phase + bearing.a * PHASE_DENOMINATOR
    b = bearing.b * PHASE_DENOMINATOR
    wrapped = sign_q5(a - 2 * PHASE_DENOMINATOR, b) >= 0
    if wrapped:
        a -= 2 * PHASE_DENOMINATOR
    if sign_q5(a, b) < 0 or sign_q5(a - 2 * PHASE_DENOMINATOR, b) >= 0:
        raise RuntimeError("effective Golden bearing escaped one complete turn")
    return a, b, wrapped


def _resolve_interval(
    *,
    weights: Sequence[int],
    phase: int,
    bearing: GoldenBearing,
) -> tuple[int, int, int, int, int, int, bool]:
    if not weights or any(isinstance(x, bool) or not isinstance(x, int) or x < 0 for x in weights):
        raise ValueError("bearing body must contain non-negative integer measures")
    total = sum(weights)
    if total <= 0:
        raise ValueError("bearing body must have positive total measure")
    effective_a, effective_b, wrapped = _effective_bearing(phase, bearing)
    cumulative = 0
    for index, weight in enumerate(weights):
        before = cumulative
        cumulative += weight
        if sign_q5(
            2 * PHASE_DENOMINATOR * cumulative - total * effective_a,
            -total * effective_b,
        ) > 0:
            return index, before, cumulative, total, effective_a, effective_b, wrapped
    raise RuntimeError("Golden bearing escaped the normalized measure body")


def resolve_bearing(
    *,
    weights: Sequence[int],
    body: str,
    phase: int,
    bearing: GoldenBearing,
    cadence_symbol: str,
    cadence_index: int,
    traversal: str,
) -> BearingWitness:
    if len(weights) != 12:
        raise ValueError("Parliament body must contain exactly twelve measures")
    index, before, after, total, effective_a, effective_b, wrapped = _resolve_interval(
        weights=weights, phase=phase, bearing=bearing
    )
    witness = BearingWitness(
        bearing=bearing,
        cadence_symbol=cadence_symbol,
        cadence_index=cadence_index,
        phase_numerator=phase,
        effective_a=effective_a,
        effective_b=effective_b,
        wrapped=wrapped,
        traversal=traversal,
        body=body,
        operator_order=PARLIAMENT_ORDER,
        seat=PARLIAMENT[index],
        cumulative_before=before,
        cumulative_after=after,
        weight_total=total,
    )
    if not witness.interval_verifies:
        raise RuntimeError("Golden Parliament interval failed exact verification")
    return witness


def court_crossing_weights(emission: SourceEmission) -> tuple[int, ...]:
    """Return W^R=O⊗S in canonical Court address order 12k+l."""
    structural = emission.structural_weights
    operational = emission.operational_weights
    if len(structural) != 12 or len(operational) != 12:
        raise ValueError("source emission must carry twelve structural and twelve operational measures")
    if any(isinstance(x, bool) or not isinstance(x, int) or x < 0 for x in structural + operational):
        raise ValueError("source emission measures must be non-negative integers")
    weights = tuple(operational[k] * structural[l] for k in range(12) for l in range(12))
    expected = sum(operational) * sum(structural)
    if expected <= 0 or sum(weights) != expected:
        raise RuntimeError("Court product measure failed ΣW^R=(ΣO)(ΣS)>0")
    if Fraction(sum(weights), expected) != 1:
        raise RuntimeError("normalized Court product measure failed exact unit closure")
    return weights


def resolve_court_bearing(emission: SourceEmission) -> CourtBearingWitness:
    """Resolve D over all 144 Courts from O⊗S, 𝔃₁, and BETA=Φ⁻²."""
    if not emission.closure.verifies:
        raise RuntimeError("source emission does not carry D-COMP=0 / Truth=1")
    weights = court_crossing_weights(emission)
    index, before, after, total, effective_a, effective_b, wrapped = _resolve_interval(
        weights=weights, phase=emission.fraktur_z1, bearing=BETA
    )
    witness = CourtBearingWitness(
        bearing=BETA,
        cadence_symbol="𝔃₁",
        cadence_index=1,
        phase_numerator=emission.fraktur_z1,
        effective_a=effective_a,
        effective_b=effective_b,
        wrapped=wrapped,
        traversal="Reflect / Court product bearing without a second entropy source",
        body="Court product measure W^R = O⊗S",
        weights=weights,
        court=court_record(index),
        cumulative_before=before,
        cumulative_after=after,
        weight_total=total,
        structural_total=sum(emission.structural_weights),
        operational_total=sum(emission.operational_weights),
    )
    if not witness.product_measure_verifies:
        raise RuntimeError("Court product measure failed exact normalization")
    if not witness.exact_bound_verifies:
        raise RuntimeError("Court bearing ξ_D failed exact Q(√5) verification")
    validate_court_bearing_lineage(witness.lineage)
    return witness
