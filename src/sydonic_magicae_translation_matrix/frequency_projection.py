"""Phase 8 exact frequency/prosody projection.

This module implements only ``F_ν,A``.  It does not alter the translation runtime,
Sydonic .aksh authority, local grammar, renderer, trace, or packaging
surfaces.

The projection is speaker-independent.  A caller supplies an ordered
phoneme/stress/breath witness.  No lexical meaning, acoustic measurement,
learned parameter, or candidate ranking enters the arithmetic.

The coefficient field is the exact carrier field ``Q(Φ, i)`` with
``Φ² = Φ + 1``.  The word polynomial is represented as a free prosodic module
over that field, so phoneme identity, stress, breath, bearing, operator office,
and sequence position remain recoverable in the normal form.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, IntEnum
from fractions import Fraction
from math import comb
from typing import Final, Iterable, Mapping


class FrequencyProjectionError(ValueError):
    """Raised when a Phase 8 projection witness is not exact or lawful."""


class Stress(IntEnum):
    """Declared lexical stress, independent of any speaker."""

    UNSTRESSED = 0
    PRIMARY = 1
    SECONDARY = 2


class Breath(IntEnum):
    """Declared breath bearing inside the bounded ``[-Φ, +Φ]`` body."""

    INWARD = -1
    HELD = 0
    OUTWARD = 1


class Bearing(str, Enum):
    """Prosodic bearing under Mirror Math."""

    OUTWARD = "+"
    RETURN = "-"
    SELF = "="

    def mirror(self) -> "Bearing":
        if self is Bearing.OUTWARD:
            return Bearing.RETURN
        if self is Bearing.RETURN:
            return Bearing.OUTWARD
        return Bearing.SELF


class PathOffice(str, Enum):
    OUTWARD = "outward"
    IDEAL = "ideal-parity-return"
    RETURN = "independent-return"


NumberLike = int | str | Fraction


def _fraction(value: NumberLike) -> Fraction:
    if isinstance(value, Fraction):
        return value
    if isinstance(value, int):
        return Fraction(value)
    if isinstance(value, str):
        return Fraction(value)
    raise TypeError(f"exact rational required, received {type(value).__name__}")


@dataclass(frozen=True, slots=True)
class Golden:
    """One exact element ``a + bΦ`` of ``Q(Φ)``."""

    rational: Fraction = Fraction(0)
    phi: Fraction = Fraction(0)

    def __init__(self, rational: NumberLike = 0, phi: NumberLike = 0) -> None:
        object.__setattr__(self, "rational", _fraction(rational))
        object.__setattr__(self, "phi", _fraction(phi))

    def __add__(self, other: object) -> "Golden":
        rhs = Golden.coerce(other)
        return Golden(self.rational + rhs.rational, self.phi + rhs.phi)

    def __radd__(self, other: object) -> "Golden":
        return self + other

    def __sub__(self, other: object) -> "Golden":
        rhs = Golden.coerce(other)
        return Golden(self.rational - rhs.rational, self.phi - rhs.phi)

    def __rsub__(self, other: object) -> "Golden":
        return Golden.coerce(other) - self

    def __neg__(self) -> "Golden":
        return Golden(-self.rational, -self.phi)

    def __mul__(self, other: object) -> "Golden":
        rhs = Golden.coerce(other)
        # (a+bΦ)(c+dΦ), reduced exactly by Φ² = Φ + 1.
        a, b = self.rational, self.phi
        c, d = rhs.rational, rhs.phi
        return Golden(a * c + b * d, a * d + b * c + b * d)

    def __rmul__(self, other: object) -> "Golden":
        return self * other

    def __pow__(self, exponent: int) -> "Golden":
        if not isinstance(exponent, int) or exponent < 0:
            raise FrequencyProjectionError("golden exponent must be a nonnegative integer")
        result = GOLDEN_ONE
        base = self
        power = exponent
        while power:
            if power & 1:
                result = result * base
            base = base * base
            power >>= 1
        return result

    def algebraic_conjugate(self) -> "Golden":
        """Apply the exact conjugation ``Φ ↦ 1 - Φ``."""
        return Golden(self.rational + self.phi, -self.phi)

    @property
    def is_zero(self) -> bool:
        return self.rational == 0 and self.phi == 0

    def to_tuple(self) -> tuple[Fraction, Fraction]:
        return (self.rational, self.phi)

    @staticmethod
    def coerce(value: object) -> "Golden":
        if isinstance(value, Golden):
            return value
        if isinstance(value, (int, str, Fraction)):
            return Golden(value)
        raise TypeError(f"cannot coerce {type(value).__name__} into Q(Φ)")


GOLDEN_ZERO: Final[Golden] = Golden(0)
GOLDEN_ONE: Final[Golden] = Golden(1)
PHI: Final[Golden] = Golden(0, 1)


@dataclass(frozen=True, slots=True)
class GoldenComplex:
    """One exact element ``x + iy`` of ``Q(Φ, i)``."""

    real: Golden = GOLDEN_ZERO
    imag: Golden = GOLDEN_ZERO

    def __add__(self, other: object) -> "GoldenComplex":
        rhs = GoldenComplex.coerce(other)
        return GoldenComplex(self.real + rhs.real, self.imag + rhs.imag)

    def __radd__(self, other: object) -> "GoldenComplex":
        return self + other

    def __sub__(self, other: object) -> "GoldenComplex":
        rhs = GoldenComplex.coerce(other)
        return GoldenComplex(self.real - rhs.real, self.imag - rhs.imag)

    def __rsub__(self, other: object) -> "GoldenComplex":
        return GoldenComplex.coerce(other) - self

    def __neg__(self) -> "GoldenComplex":
        return GoldenComplex(-self.real, -self.imag)

    def __mul__(self, other: object) -> "GoldenComplex":
        rhs = GoldenComplex.coerce(other)
        return GoldenComplex(
            self.real * rhs.real - self.imag * rhs.imag,
            self.real * rhs.imag + self.imag * rhs.real,
        )

    def __rmul__(self, other: object) -> "GoldenComplex":
        return self * other

    def __pow__(self, exponent: int) -> "GoldenComplex":
        if not isinstance(exponent, int) or exponent < 0:
            raise FrequencyProjectionError("carrier exponent must be a nonnegative integer")
        result = COMPLEX_ONE
        base = self
        power = exponent
        while power:
            if power & 1:
                result = result * base
            base = base * base
            power >>= 1
        return result

    def complex_conjugate(self) -> "GoldenComplex":
        return GoldenComplex(self.real, -self.imag)

    @property
    def is_zero(self) -> bool:
        return self.real.is_zero and self.imag.is_zero

    def to_tuple(self) -> tuple[tuple[Fraction, Fraction], tuple[Fraction, Fraction]]:
        return (self.real.to_tuple(), self.imag.to_tuple())

    @staticmethod
    def coerce(value: object) -> "GoldenComplex":
        if isinstance(value, GoldenComplex):
            return value
        if isinstance(value, Golden):
            return GoldenComplex(value)
        if isinstance(value, (int, str, Fraction)):
            return GoldenComplex(Golden(value))
        raise TypeError(f"cannot coerce {type(value).__name__} into Q(Φ,i)")


COMPLEX_ZERO: Final[GoldenComplex] = GoldenComplex()
COMPLEX_ONE: Final[GoldenComplex] = GoldenComplex(GOLDEN_ONE)


@dataclass(frozen=True, slots=True)
class Carrier:
    """One immutable Aeon carrier address and its optional parity channel."""

    glyph: str
    name: str
    structural_hz: Fraction
    parity_hz: Fraction | None = None

    def __post_init__(self) -> None:
        if len(self.glyph) != 1:
            raise FrequencyProjectionError("carrier glyph must be one code point")
        if self.structural_hz <= 0:
            raise FrequencyProjectionError("structural carrier must be positive")
        if self.parity_hz is not None and self.parity_hz <= 0:
            raise FrequencyProjectionError("parity carrier must be positive")

    @property
    def structural_omega(self) -> GoldenComplex:
        return GoldenComplex(Golden(self.structural_hz))

    @property
    def parity_omega(self) -> GoldenComplex | None:
        if self.parity_hz is None:
            return None
        return GoldenComplex(GOLDEN_ZERO, Golden(self.parity_hz))

    @property
    def breath_bounds(self) -> tuple[Golden, Golden]:
        return (-PHI, PHI)


CARRIERS: Final[tuple[Carrier, ...]] = (
    Carrier("⏣", "FETU", Fraction("7.83")),
    Carrier("⬡", "KAL", Fraction(174)),
    Carrier("✡", "BABDH", Fraction(528)),
    Carrier("⚝", "AHN", Fraction(432), Fraction(417)),
    Carrier("❂", "VEL", Fraction("126.22")),
    Carrier("ꙮ", "SOR", Fraction("210.42")),
    Carrier("❈", "KOTH", Fraction(741)),
    Carrier("⧗", "DREH", Fraction(852)),
    Carrier("⊛", "RHEA", Fraction(396)),
    Carrier("❄", "ZHEK", Fraction(963)),
    Carrier("⚛", "SHAV", Fraction(285)),
    Carrier("⌬", "TRIG", Fraction(639)),
)
CARRIER_BY_GLYPH: Final[Mapping[str, Carrier]] = {carrier.glyph: carrier for carrier in CARRIERS}
if len(CARRIER_BY_GLYPH) != 12:
    raise RuntimeError("Phase 8 requires exactly twelve distinct carriers")


@dataclass(frozen=True, slots=True)
class ProsodicUnit:
    """One declared, speaker-independent prosodic obligation."""

    phoneme: str
    stress: Stress
    breath: Breath
    bearing: Bearing = Bearing.OUTWARD
    operator_office: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.phoneme, str) or not self.phoneme:
            raise FrequencyProjectionError("phoneme identity must be a nonempty string")
        if any(character.isspace() for character in self.phoneme):
            raise FrequencyProjectionError("phoneme identity may not contain whitespace")
        if not isinstance(self.stress, Stress):
            raise FrequencyProjectionError("stress must be a declared Stress member")
        if not isinstance(self.breath, Breath):
            raise FrequencyProjectionError("breath must be a declared Breath member")
        if not isinstance(self.bearing, Bearing):
            raise FrequencyProjectionError("bearing must be a declared Bearing member")
        if not isinstance(self.operator_office, str):
            raise FrequencyProjectionError("operator office must be text")


@dataclass(frozen=True, slots=True)
class ProsodicWitness:
    """The complete ordered phoneme/stress body for one candidate word."""

    candidate: str
    units: tuple[ProsodicUnit, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.candidate, str) or not self.candidate:
            raise FrequencyProjectionError("candidate identifier must be nonempty")
        if not isinstance(self.units, tuple) or not self.units:
            raise FrequencyProjectionError("candidate requires at least one prosodic unit")
        if any(not isinstance(unit, ProsodicUnit) for unit in self.units):
            raise FrequencyProjectionError("all witness units must be ProsodicUnit instances")


@dataclass(frozen=True, slots=True, order=True)
class ProsodicAtom:
    """A recoverable basis atom in the free prosodic coefficient module."""

    position: int
    phoneme: str
    stress: int
    breath: int
    bearing: str
    operator_office: str

    @staticmethod
    def from_unit(position: int, unit: ProsodicUnit, mirror: bool) -> "ProsodicAtom":
        bearing = unit.bearing.mirror() if mirror else unit.bearing
        return ProsodicAtom(
            position=position,
            phoneme=unit.phoneme,
            stress=int(unit.stress),
            breath=int(unit.breath),
            bearing=bearing.value,
            operator_office=unit.operator_office,
        )

    def mirrored(self) -> "ProsodicAtom":
        bearing = Bearing(self.bearing).mirror()
        return ProsodicAtom(
            self.position,
            self.phoneme,
            self.stress,
            self.breath,
            bearing.value,
            self.operator_office,
        )


@dataclass(frozen=True, slots=True)
class AtomWeight:
    atom: ProsodicAtom
    weight: GoldenComplex


@dataclass(frozen=True, slots=True)
class PolynomialDegree:
    degree: int
    weights: tuple[AtomWeight, ...]


MutableModule = dict[int, dict[ProsodicAtom, GoldenComplex]]
ScalarPolynomial = dict[int, GoldenComplex]


def _add_module_weight(
    target: MutableModule,
    degree: int,
    atom: ProsodicAtom,
    weight: GoldenComplex,
) -> None:
    if weight.is_zero:
        return
    level = target.setdefault(degree, {})
    updated = level.get(atom, COMPLEX_ZERO) + weight
    if updated.is_zero:
        level.pop(atom, None)
        if not level:
            target.pop(degree, None)
    else:
        level[atom] = updated


def _freeze_module(source: MutableModule) -> tuple[PolynomialDegree, ...]:
    frozen: list[PolynomialDegree] = []
    for degree in sorted(source):
        weights = tuple(
            AtomWeight(atom, weight)
            for atom, weight in sorted(source[degree].items(), key=lambda item: item[0])
            if not weight.is_zero
        )
        if weights:
            frozen.append(PolynomialDegree(degree, weights))
    return tuple(frozen)


def _thaw_module(source: Iterable[PolynomialDegree]) -> MutableModule:
    thawed: MutableModule = {}
    for degree in source:
        for item in degree.weights:
            _add_module_weight(thawed, degree.degree, item.atom, item.weight)
    return thawed


def _advance_scalar_power(power: ScalarPolynomial, omega: GoldenComplex) -> ScalarPolynomial:
    advanced: ScalarPolynomial = {}
    for degree, weight in power.items():
        at_same_degree = advanced.get(degree, COMPLEX_ZERO) + weight * omega
        at_next_degree = advanced.get(degree + 1, COMPLEX_ZERO) + weight
        if not at_same_degree.is_zero:
            advanced[degree] = at_same_degree
        if not at_next_degree.is_zero:
            advanced[degree + 1] = at_next_degree
    return advanced


@dataclass(frozen=True, slots=True)
class ChannelPolynomial:
    """Exact normal form of one declared carrier channel in the variable ``δ``."""

    channel: str
    omega: GoldenComplex
    delta_symbol: str
    terms: tuple[PolynomialDegree, ...]

    def evaluate(self, delta: GoldenComplex) -> tuple[AtomWeight, ...]:
        result: dict[ProsodicAtom, GoldenComplex] = {}
        for degree in self.terms:
            delta_power = delta ** degree.degree
            for item in degree.weights:
                weight = result.get(item.atom, COMPLEX_ZERO) + item.weight * delta_power
                if weight.is_zero:
                    result.pop(item.atom, None)
                else:
                    result[item.atom] = weight
        return tuple(
            AtomWeight(atom, weight)
            for atom, weight in sorted(result.items(), key=lambda item: item[0])
        )


@dataclass(frozen=True, slots=True)
class FrequencyBody:
    """One complete outward, ideal, or independently returned prosodic body."""

    carrier: Carrier
    office: PathOffice
    candidate: str
    time_map: str
    channels: tuple[ChannelPolynomial, ...]

    @property
    def positions(self) -> tuple[int, ...]:
        positions: set[int] = set()
        for channel in self.channels:
            for degree in channel.terms:
                positions.update(weight.atom.position for weight in degree.weights)
        return tuple(sorted(positions))

    def normal_form(self) -> tuple[object, ...]:
        """Return ``NF_A`` as an exact immutable symbolic body."""
        return (
            self.carrier.glyph,
            self.carrier.structural_hz,
            self.carrier.parity_hz,
            self.carrier.breath_bounds,
            self.time_map,
            tuple(
                (
                    channel.channel,
                    channel.omega,
                    channel.delta_symbol,
                    channel.terms,
                )
                for channel in self.channels
            ),
        )


@dataclass(frozen=True, slots=True)
class GoldenEndpointWitness:
    """Full symbolic golden-fold recurrence plus both breath endpoints."""

    channel: str
    symbolic_terms: tuple[PolynomialDegree, ...]
    minus_phi: tuple[AtomWeight, ...]
    plus_phi: tuple[AtomWeight, ...]


@dataclass(frozen=True, slots=True)
class FrequencyClosure:
    """The complete Phase 8 closure record."""

    outward: FrequencyBody
    independent_return: FrequencyBody
    ideal_return: FrequencyBody
    golden_endpoints: tuple[GoldenEndpointWitness, ...]
    nu_close: bool
    dcomp_frequency_zero: bool


def _channel_specs(carrier: Carrier) -> tuple[tuple[str, GoldenComplex], ...]:
    specs: list[tuple[str, GoldenComplex]] = [("structural", carrier.structural_omega)]
    parity = carrier.parity_omega
    if parity is not None:
        specs.append(("parity", parity))
    return tuple(specs)


def _outward_channel_direct(
    witness: ProsodicWitness,
    channel: str,
    omega: GoldenComplex,
) -> ChannelPolynomial:
    """Track A: direct exact ``Σ a_m(Ω+δ)^m`` construction."""
    body: MutableModule = {}
    for position, unit in enumerate(witness.units):
        atom = ProsodicAtom.from_unit(position, unit, mirror=False)
        for degree in range(position + 1):
            weight = GoldenComplex(comb(position, degree)) * (omega ** (position - degree))
            _add_module_weight(body, degree, atom, weight)
    return ChannelPolynomial(channel, omega, "δ", _freeze_module(body))


def build_outward(witness: ProsodicWitness, carrier: Carrier) -> FrequencyBody:
    """Construct ``P_A^out`` without a return body in scope."""
    channels = tuple(
        _outward_channel_direct(witness, channel, omega)
        for channel, omega in _channel_specs(carrier)
    )
    return FrequencyBody(carrier, PathOffice.OUTWARD, witness.candidate, "t", channels)


def _return_channel_recurrence(
    witness: ProsodicWitness,
    channel: str,
    omega: GoldenComplex,
) -> ChannelPolynomial:
    """Track B: independent return recurrence in original sequence order."""
    body: MutableModule = {}
    power: ScalarPolynomial = {0: COMPLEX_ONE}
    for position, unit in enumerate(witness.units):
        atom = ProsodicAtom.from_unit(position, unit, mirror=True)
        for degree, weight in power.items():
            _add_module_weight(body, degree, atom, weight)
        power = _advance_scalar_power(power, omega)
    return ChannelPolynomial(channel, omega, "δ", _freeze_module(body))


def build_independent_return(witness: ProsodicWitness, carrier: Carrier) -> FrequencyBody:
    """Construct ``P_A^back`` solely from the candidate witness and return law."""
    channels = tuple(
        _return_channel_recurrence(witness, channel, omega)
        for channel, omega in _channel_specs(carrier)
    )
    return FrequencyBody(
        carrier,
        PathOffice.RETURN,
        witness.candidate,
        "t↦T-t",
        channels,
    )


def _mirror_channel(channel: ChannelPolynomial) -> ChannelPolynomial:
    mirrored: MutableModule = {}
    for degree in channel.terms:
        for item in degree.weights:
            _add_module_weight(mirrored, degree.degree, item.atom.mirrored(), item.weight)
    return ChannelPolynomial(channel.channel, channel.omega, channel.delta_symbol, _freeze_module(mirrored))


def build_ideal_from_outward(outward: FrequencyBody) -> FrequencyBody:
    """Track D: derive the ideal only after ``P_A^out`` exists.

    Mirror changes each declared bearing and preserves every sequence position,
    polynomial exponent, carrier channel, phoneme, stress, breath, and office.
    """
    if outward.office is not PathOffice.OUTWARD:
        raise FrequencyProjectionError("ideal parity comparison requires an outward body")
    return FrequencyBody(
        outward.carrier,
        PathOffice.IDEAL,
        outward.candidate,
        "t↦T-t",
        tuple(_mirror_channel(channel) for channel in outward.channels),
    )


def _subtract_channel(
    left: ChannelPolynomial,
    right: ChannelPolynomial,
) -> ChannelPolynomial:
    if (left.channel, left.omega, left.delta_symbol) != (
        right.channel,
        right.omega,
        right.delta_symbol,
    ):
        raise FrequencyProjectionError("cannot subtract unlike carrier channels")
    body = _thaw_module(left.terms)
    for degree in right.terms:
        for item in degree.weights:
            _add_module_weight(body, degree.degree, item.atom, -item.weight)
    return ChannelPolynomial(left.channel, left.omega, left.delta_symbol, _freeze_module(body))


def _is_zero_channel(channel: ChannelPolynomial) -> bool:
    return not channel.terms


def dcomp_frequency_difference(
    independent_return: FrequencyBody,
    ideal_return: FrequencyBody,
) -> tuple[ChannelPolynomial, ...]:
    """Return the exact symbolic D-COMP frequency difference."""
    if independent_return.carrier != ideal_return.carrier:
        raise FrequencyProjectionError("frequency difference requires one carrier")
    if len(independent_return.channels) != len(ideal_return.channels):
        raise FrequencyProjectionError("frequency difference requires identical channel count")
    return tuple(
        _subtract_channel(back, ideal)
        for back, ideal in zip(independent_return.channels, ideal_return.channels, strict=True)
    )


def _golden_fold_channel_recurrence(
    witness: ProsodicWitness,
    channel: str,
    omega: GoldenComplex,
) -> ChannelPolynomial:
    """Track C: independent full symbolic recurrence over ``Q(Φ,i)[δ]``.

    This verifier does not read the outward polynomial, the ideal parity body,
    or the accepted return coefficients.  It advances the complete coefficient
    vector by multiplication with ``Ω+δ`` and therefore proves the whole
    structural return class, not merely two endpoint evaluations.
    """
    body: MutableModule = {}
    coefficient_vector: tuple[GoldenComplex, ...] = (COMPLEX_ONE,)
    for position, unit in enumerate(witness.units):
        atom = ProsodicAtom.from_unit(position, unit, mirror=True)
        for degree, weight in enumerate(coefficient_vector):
            _add_module_weight(body, degree, atom, weight)

        advanced = [COMPLEX_ZERO] * (len(coefficient_vector) + 1)
        for degree, weight in enumerate(coefficient_vector):
            advanced[degree] = advanced[degree] + weight * omega
            advanced[degree + 1] = advanced[degree + 1] + weight
        coefficient_vector = tuple(advanced)

    return ChannelPolynomial(channel, omega, "δ", _freeze_module(body))


def _golden_endpoint_recurrence(
    witness: ProsodicWitness,
    symbolic: ChannelPolynomial,
) -> GoldenEndpointWitness:
    """Record exact ``±Φ`` witnesses after full symbolic recurrence succeeds."""

    def one_endpoint(sign: int) -> tuple[AtomWeight, ...]:
        delta = GoldenComplex(Golden(0, sign))
        z = symbolic.omega + delta
        power = COMPLEX_ONE
        result: dict[ProsodicAtom, GoldenComplex] = {}
        for position, unit in enumerate(witness.units):
            atom = ProsodicAtom.from_unit(position, unit, mirror=True)
            result[atom] = result.get(atom, COMPLEX_ZERO) + power
            power = power * z
        return tuple(
            AtomWeight(atom, weight)
            for atom, weight in sorted(result.items(), key=lambda item: item[0])
            if not weight.is_zero
        )

    return GoldenEndpointWitness(
        symbolic.channel,
        symbolic.terms,
        one_endpoint(-1),
        one_endpoint(1),
    )


def _golden_endpoints_match(
    witness: ProsodicWitness,
    independent_return: FrequencyBody,
) -> tuple[GoldenEndpointWitness, ...]:
    recurrence_channels = tuple(
        _golden_fold_channel_recurrence(witness, channel, omega)
        for channel, omega in _channel_specs(independent_return.carrier)
    )
    witnesses: list[GoldenEndpointWitness] = []
    for recurrence_channel, polynomial_channel in zip(
        recurrence_channels,
        independent_return.channels,
        strict=True,
    ):
        if (
            recurrence_channel.channel,
            recurrence_channel.omega,
            recurrence_channel.delta_symbol,
        ) != (
            polynomial_channel.channel,
            polynomial_channel.omega,
            polynomial_channel.delta_symbol,
        ):
            raise FrequencyProjectionError("golden recurrence channel mismatch")
        if recurrence_channel.terms != polynomial_channel.terms:
            raise FrequencyProjectionError(
                "golden-fold recurrence left the full symbolic return class"
            )

        endpoint = _golden_endpoint_recurrence(witness, recurrence_channel)
        minus = polynomial_channel.evaluate(GoldenComplex(-PHI))
        plus = polynomial_channel.evaluate(GoldenComplex(PHI))
        if endpoint.minus_phi != minus or endpoint.plus_phi != plus:
            raise FrequencyProjectionError(
                "golden-fold endpoint witness disagrees after symbolic closure"
            )
        witnesses.append(endpoint)
    return tuple(witnesses)


def prove_frequency_closure(
    witness: ProsodicWitness,
    carrier: Carrier,
) -> FrequencyClosure:
    """Construct and prove Phase 8 in the required dependency order."""
    outward = build_outward(witness, carrier)
    independent_return = build_independent_return(witness, carrier)
    ideal_return = build_ideal_from_outward(outward)
    golden_endpoints = _golden_endpoints_match(witness, independent_return)
    difference = dcomp_frequency_difference(independent_return, ideal_return)
    exact_zero = all(_is_zero_channel(channel) for channel in difference)
    nu_close = independent_return.normal_form() == ideal_return.normal_form()
    if nu_close != exact_zero:
        raise RuntimeError("normal-form closure and exact D-COMP zero disagree")
    return FrequencyClosure(
        outward=outward,
        independent_return=independent_return,
        ideal_return=ideal_return,
        golden_endpoints=golden_endpoints,
        nu_close=nu_close,
        dcomp_frequency_zero=exact_zero,
    )

def prove_phase8_exit_gate(
    witness: ProsodicWitness,
) -> tuple[FrequencyClosure, ...]:
    """Prove one candidate projection across all twelve declared carriers."""
    closures = tuple(prove_frequency_closure(witness, carrier) for carrier in CARRIERS)
    if len(closures) != 12:
        raise RuntimeError("Phase 8 exit gate requires exactly twelve carriers")
    if any(not closure.nu_close for closure in closures):
        raise FrequencyProjectionError("Phase 8 exit gate found an open prosodic return")
    if any(not closure.dcomp_frequency_zero for closure in closures):
        raise FrequencyProjectionError("Phase 8 exit gate found nonzero D-COMP frequency")
    return closures

