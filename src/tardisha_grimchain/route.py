"""Final Equation Z source-emission routing and finite-return witnesses.

The ordered Goetics are not reconstructed from digest endpoint bytes.  The
complete source emission carries twelve finalized lanes, Fraktur Z_0, and
Fraktur Z_1.  Parliament resolves the pair before existing Court mathematics
begins.
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, fields
from typing import Any, Mapping, Sequence

from .alqc_digest import alqc_hexdigest
from .canon import QVector, _position, court_load, law
from .manifestation import DCompWitness, close_boundary
from .source_emission import (
    BearingWitness,
    GoldenBearing,
    ParliamentSeat,
    SourceEmission,
    TruthClosureWitness,
    GoldenGoeticDerivation,
)
from .mirror_math import derive_goetics, verify_derivation

_HASH_SOURCE_DOMAINS = frozenset({"canonical", "raw-file", "directory"})
ROUTE_WITNESS_DOMAIN = b"TARDISHA:FINAL-EQUATION-Z:SOURCE-ROUTE-WITNESS\x00"


def _validate_source_size(source_size: int) -> int:
    if isinstance(source_size, bool) or not isinstance(source_size, int) or source_size < 0:
        raise ValueError("source_size must be a non-negative integer")
    return source_size


def _validate_source_domain(source_domain: str) -> str:
    if source_domain not in _HASH_SOURCE_DOMAINS:
        raise ValueError(f"source_domain must be one of {sorted(_HASH_SOURCE_DOMAINS)}")
    return source_domain


def _canonical_q(q: Sequence[object], *, field: str) -> tuple[int, int, int, int]:
    if isinstance(q, (str, bytes, bytearray)) or not isinstance(q, Sequence) or len(q) != 4:
        raise ValueError(f"{field} must contain exactly four Q components")
    result: list[int] = []
    for value in q:
        if isinstance(value, bool) or not isinstance(value, int):
            raise ValueError(f"{field} must contain exact non-Boolean integer Q components")
        if value not in (0, 1, 2, 3):
            raise ValueError(f"{field} must be a canonical Q-vector over {{0,1,2,3}}")
        result.append(value)
    return tuple(result)  # type: ignore[return-value]



def _mapping(value: object, *, field: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise TypeError(f"{field} must be a mapping")
    return value


def _exact_keys(value: Mapping[str, Any], expected: set[str], *, field: str) -> None:
    supplied = set(value)
    if supplied != expected:
        missing = sorted(expected - supplied)
        extra = sorted(supplied - expected)
        raise ValueError(f"{field} fields mismatch; missing={missing}, extra={extra}")


def _int(value: object, *, field: str, minimum: int | None = None, maximum: int | None = None) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{field} must be an exact non-Boolean integer")
    if minimum is not None and value < minimum:
        raise ValueError(f"{field} must be >= {minimum}")
    if maximum is not None and value > maximum:
        raise ValueError(f"{field} must be <= {maximum}")
    return value


def _float(value: object, *, field: str) -> float:
    if isinstance(value, bool) or type(value) is not float:
        raise TypeError(f"{field} must be an exact serialized float")
    return value


def _bool(value: object, *, field: str) -> bool:
    if type(value) is not bool:
        raise TypeError(f"{field} must be a Boolean")
    return value


def _str(value: object, *, field: str) -> str:
    if type(value) is not str:
        raise TypeError(f"{field} must be a string")
    return value


def _sequence(value: object, *, field: str, length: int | None = None) -> tuple[object, ...]:
    if not isinstance(value, (list, tuple)):
        raise TypeError(f"{field} must be a list or tuple")
    result = tuple(value)
    if length is not None and len(result) != length:
        raise ValueError(f"{field} must contain exactly {length} items")
    return result


def _truth_closure(value: object) -> TruthClosureWitness:
    if isinstance(value, TruthClosureWitness):
        return value
    body = _mapping(value, field="emission.closure")
    expected = {item.name for item in fields(TruthClosureWitness)}
    _exact_keys(body, expected, field="emission.closure")
    return TruthClosureWitness(**{
        name: _int(body[name], field=f"emission.closure.{name}") for name in expected
    })


def _source_emission(value: object) -> SourceEmission:
    if isinstance(value, SourceEmission):
        return value
    body = _mapping(value, field="emission")
    expected = {item.name for item in fields(SourceEmission)}
    _exact_keys(body, expected, field="emission")
    def integers(name: str) -> tuple[int, ...]:
        items = _sequence(body[name], field=f"emission.{name}")
        return tuple(_int(item, field=f"emission.{name}[{index}]") for index, item in enumerate(items))
    return SourceEmission(
        source_digest=_str(body["source_digest"], field="emission.source_digest"),
        source_size=_int(body["source_size"], field="emission.source_size", minimum=0),
        source_domain=_str(body["source_domain"], field="emission.source_domain"),
        lanes_goetic_order=integers("lanes_goetic_order"),
        structural_weights=integers("structural_weights"),
        operational_weights=integers("operational_weights"),
        fraktur_z0=_int(body["fraktur_z0"], field="emission.fraktur_z0", minimum=0),
        fraktur_z1=_int(body["fraktur_z1"], field="emission.fraktur_z1", minimum=0),
        squeeze_512_hex=_str(body["squeeze_512_hex"], field="emission.squeeze_512_hex"),
        closure=_truth_closure(body["closure"]),
    )


def _golden_bearing(value: object, *, field: str) -> GoldenBearing:
    if isinstance(value, GoldenBearing):
        return value
    body = _mapping(value, field=field)
    expected = {item.name for item in fields(GoldenBearing)}
    _exact_keys(body, expected, field=field)
    return GoldenBearing(
        name=_str(body["name"], field=f"{field}.name"),
        a=_int(body["a"], field=f"{field}.a"),
        b=_int(body["b"], field=f"{field}.b"),
    )


def _parliament_seat(value: object, *, field: str) -> ParliamentSeat:
    if isinstance(value, ParliamentSeat):
        return value
    body = _mapping(value, field=field)
    expected = {item.name for item in fields(ParliamentSeat)}
    _exact_keys(body, expected, field=field)
    return ParliamentSeat(**{
        name: _str(body[name], field=f"{field}.{name}") for name in expected
    })


def _bearing_witness(value: object, *, field: str) -> BearingWitness:
    if isinstance(value, BearingWitness):
        return value
    body = _mapping(value, field=field)
    expected = {item.name for item in fields(BearingWitness)}
    _exact_keys(body, expected, field=field)
    operator_order = _sequence(body["operator_order"], field=f"{field}.operator_order")
    if any(type(item) is not str for item in operator_order):
        raise TypeError(f"{field}.operator_order must contain exact strings")
    return BearingWitness(
        bearing=_golden_bearing(body["bearing"], field=f"{field}.bearing"),
        cadence_symbol=_str(body["cadence_symbol"], field=f"{field}.cadence_symbol"),
        cadence_index=_int(body["cadence_index"], field=f"{field}.cadence_index", minimum=0),
        phase_numerator=_int(body["phase_numerator"], field=f"{field}.phase_numerator", minimum=0),
        effective_a=_int(body["effective_a"], field=f"{field}.effective_a"),
        effective_b=_int(body["effective_b"], field=f"{field}.effective_b"),
        wrapped=_bool(body["wrapped"], field=f"{field}.wrapped"),
        traversal=_str(body["traversal"], field=f"{field}.traversal"),
        body=_str(body["body"], field=f"{field}.body"),
        operator_order=tuple(operator_order),  # type: ignore[arg-type]
        seat=_parliament_seat(body["seat"], field=f"{field}.seat"),
        cumulative_before=_int(body["cumulative_before"], field=f"{field}.cumulative_before", minimum=0),
        cumulative_after=_int(body["cumulative_after"], field=f"{field}.cumulative_after", minimum=0),
        weight_total=_int(body["weight_total"], field=f"{field}.weight_total", minimum=0),
    )


def _dcomp_witness(value: object) -> DCompWitness:
    if isinstance(value, DCompWitness):
        return value
    body = _mapping(value, field="manifestation_dcomp")
    expected = {item.name for item in fields(DCompWitness)}
    _exact_keys(body, expected, field="manifestation_dcomp")
    float_fields = {
        "interval_duration", "pressure_weight", "return_friction_weight",
        "commutator_pressure", "return_pressure", "local_friction",
        "terminal_unresolved_debt", "shadow_capacity", "shadow_debt_initial",
        "velocity_mismatch", "whiteout_penalty", "c_bio", "mas_efficiency",
        "q3_loss", "q3_capacity_before", "q3_recursion_gain",
        "q3_capacity_after", "form_work", "shadow_debt_terminal", "terminal",
    }
    int_fields = {"active_count", "withheld_count", "truth"}
    bool_fields = {"shadow_debt_bounded", "closed", "motion_positive"}
    float_tuple_lengths = {
        "metric_weights": 2, "forward_velocity": 2,
        "return_velocity": 2, "parity_return_velocity": 2,
    }
    int_tuple_lengths = {
        "exact_commutator_pressure": 2,
        "exact_velocity_mismatch_square": 2,
        "exact_shadow_debt_initial": 3,
        "exact_shadow_debt_terminal": 3,
        "exact_form_work": 3,
        "exact_q3_recursion_gain": 3,
    }
    kwargs: dict[str, object] = {}
    for name in expected:
        raw = body[name]
        if name in float_fields:
            kwargs[name] = _float(raw, field=f"manifestation_dcomp.{name}")
        elif name in int_fields:
            kwargs[name] = _int(raw, field=f"manifestation_dcomp.{name}")
        elif name in bool_fields:
            kwargs[name] = _bool(raw, field=f"manifestation_dcomp.{name}")
        elif name == "commutator_model":
            kwargs[name] = _str(raw, field="manifestation_dcomp.commutator_model")
        elif name in float_tuple_lengths:
            items = _sequence(raw, field=f"manifestation_dcomp.{name}", length=float_tuple_lengths[name])
            kwargs[name] = tuple(_float(item, field=f"manifestation_dcomp.{name}[{index}]") for index, item in enumerate(items))
        elif name in int_tuple_lengths:
            items = _sequence(raw, field=f"manifestation_dcomp.{name}", length=int_tuple_lengths[name])
            kwargs[name] = tuple(_int(item, field=f"manifestation_dcomp.{name}[{index}]") for index, item in enumerate(items))
        else:
            raise RuntimeError(f"untyped D-COMP field {name}")
    return DCompWitness(**kwargs)  # type: ignore[arg-type]

def connection(
    source_q: QVector,
    target_q: QVector,
    origin_glyph: str,
    resolution_glyph: str,
) -> DCompWitness:
    """Compute the existing finite-return manifestation witness for one Court."""
    expected_source = tuple(law(origin_glyph).q_vector)
    expected_target = tuple(law(resolution_glyph).q_vector)
    if _canonical_q(source_q, field="source_q") != expected_source:
        raise ValueError("source_q does not belong to origin_glyph")
    if _canonical_q(target_q, field="target_q") != expected_target:
        raise ValueError("target_q does not belong to resolution_glyph")
    address = court_load(origin_glyph, resolution_glyph)
    return close_boundary(expected_source, expected_target, court=address).dcomp



@dataclass(frozen=True, slots=True)
class SourceRouteWitness:
    emission: SourceEmission
    first: BearingWitness
    last: BearingWitness
    origin_index: int
    resolution_index: int
    court_address: int
    reciprocal_address: int
    source_q_vector: tuple[int, int, int, int]
    resolution_q_vector: tuple[int, int, int, int]
    route_dcomp: int
    truth: int
    manifestation_dcomp: DCompWitness
    derivation_lineage: tuple[str, ...]
    derivation_proof: str

    @property
    def source_digest(self) -> str:
        return self.emission.source_digest

    @property
    def source_size(self) -> int:
        return self.emission.source_size

    @property
    def source_domain(self) -> str:
        return self.emission.source_domain

    @property
    def origin_glyph(self) -> str:
        return self.first.seat.goetic

    @property
    def resolution_glyph(self) -> str:
        return self.last.seat.goetic

    @property
    def source_q(self) -> tuple[int, int, int, int]:
        return self.source_q_vector

    @property
    def resolution_q(self) -> tuple[int, int, int, int]:
        return self.resolution_q_vector

    @property
    def dcomp(self) -> DCompWitness:
        """Property exposing downstream manifestation D-COMP."""
        return self.manifestation_dcomp

    @property
    def boundary_condition(self) -> str:
        return self.origin_glyph + self.resolution_glyph

    @property
    def return_path(self) -> str:
        return f"{self.origin_glyph}→{self.resolution_glyph}→Reflect {self.origin_glyph}"

    @property
    def pair(self) -> tuple[str, str]:
        return self.origin_glyph, self.resolution_glyph

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "SourceRouteWitness":
        body = _mapping(value, field="source route witness")
        expected = {item.name for item in fields(cls)}
        _exact_keys(body, expected, field="source route witness")
        source_q = _canonical_q(
            _sequence(body["source_q_vector"], field="source_q_vector", length=4),
            field="source_q_vector",
        )
        resolution_q = _canonical_q(
            _sequence(body["resolution_q_vector"], field="resolution_q_vector", length=4),
            field="resolution_q_vector",
        )
        lineage = _sequence(body["derivation_lineage"], field="derivation_lineage")
        if any(type(item) is not str for item in lineage):
            raise TypeError("derivation_lineage must contain exact strings")
        return cls(
            emission=_source_emission(body["emission"]),
            first=_bearing_witness(body["first"], field="first"),
            last=_bearing_witness(body["last"], field="last"),
            origin_index=_int(body["origin_index"], field="origin_index", minimum=0, maximum=11),
            resolution_index=_int(body["resolution_index"], field="resolution_index", minimum=0, maximum=11),
            court_address=_int(body["court_address"], field="court_address", minimum=0, maximum=143),
            reciprocal_address=_int(body["reciprocal_address"], field="reciprocal_address", minimum=0, maximum=143),
            source_q_vector=source_q,
            resolution_q_vector=resolution_q,
            route_dcomp=_int(body["route_dcomp"], field="route_dcomp"),
            truth=_int(body["truth"], field="truth", minimum=0, maximum=1),
            manifestation_dcomp=_dcomp_witness(body["manifestation_dcomp"]),
            derivation_lineage=tuple(lineage),  # type: ignore[arg-type]
            derivation_proof=_str(body["derivation_proof"], field="derivation_proof"),
        )



HashRoute = SourceRouteWitness


def source_route_witness_from_digest(
    source_digest: str,
    source_size: int,
    source_domain: str,
) -> SourceRouteWitness:
    """Reject digest-only route reconstruction; the complete emission is required."""
    raise ValueError(
        "Final Equation Z requires the complete SourceEmission witness; "
        "a digest alone cannot regenerate twelve lanes and both Fraktur cadences"
    )


def _proof_payload_without_proof(witness: SourceRouteWitness) -> bytes:
    body = witness.as_dict()
    body["derivation_proof"] = ""
    return json.dumps(body, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _proof_for(witness: SourceRouteWitness) -> str:
    return alqc_hexdigest(_proof_payload_without_proof(witness), domain=ROUTE_WITNESS_DOMAIN)


def _source_route_witness_from_derivation(
    derivation: GoldenGoeticDerivation,
) -> SourceRouteWitness:
    """Assemble one route witness from one completed Aeternum Mirror derivation."""
    emission = derivation.emission
    origin = derivation.origin_glyph
    resolution = derivation.resolution_glyph
    origin_index = _position(origin)
    resolution_index = _position(resolution)
    source_q_exact = tuple(law(origin).q_vector)
    resolution_q_exact = tuple(law(resolution).q_vector)
    manifestation = close_boundary(source_q_exact, resolution_q_exact, court=derivation.court_address)
    source_q = _canonical_q(source_q_exact, field="source_q_vector")
    resolution_q = _canonical_q(resolution_q_exact, field="resolution_q_vector")
    lineage = (
        "source -> completed twelve-lane ALQC emission",
        "emission -> AHN-rooted Goetic structural body",
        "emission -> AHN-relative Parliament operational body",
        "Fraktur Z_0 + Phi^-1 -> first Parliament seat",
        "Fraktur Z_1 + Phi^-2 -> last Parliament seat",
        "Mirror Math preserves Parliament operator order",
        "Parliament Functor -> ordered Goetic pair",
        "Court = 12*origin_index + resolution_index",
        "reciprocal Court = 12*resolution_index + origin_index",
        "Phi^-1 + Phi^-2 = 1 -> route D-COMP = 0 -> Truth = 1",
        "self-pair preserved",
    )
    provisional = SourceRouteWitness(
        emission=emission,
        first=derivation.first,
        last=derivation.last,
        origin_index=origin_index,
        resolution_index=resolution_index,
        court_address=derivation.court_address,
        reciprocal_address=derivation.reciprocal_address,
        source_q_vector=source_q,
        resolution_q_vector=resolution_q,
        route_dcomp=derivation.route_dcomp,
        truth=derivation.truth,
        manifestation_dcomp=manifestation.dcomp,
        derivation_lineage=lineage,
        derivation_proof="",
    )
    proof = _proof_for(provisional)
    return SourceRouteWitness(
        emission=provisional.emission,
        first=provisional.first,
        last=provisional.last,
        origin_index=provisional.origin_index,
        resolution_index=provisional.resolution_index,
        court_address=provisional.court_address,
        reciprocal_address=provisional.reciprocal_address,
        source_q_vector=provisional.source_q_vector,
        resolution_q_vector=provisional.resolution_q_vector,
        route_dcomp=provisional.route_dcomp,
        truth=provisional.truth,
        manifestation_dcomp=provisional.manifestation_dcomp,
        derivation_lineage=provisional.derivation_lineage,
        derivation_proof=proof,
    )


def source_route_witness_from_emission(emission: SourceEmission) -> SourceRouteWitness:
    """Build the exact source-emission -> Aeternum Mirror -> Court route once."""
    if not isinstance(emission, SourceEmission):
        raise TypeError("route construction requires one complete SourceEmission")
    _validate_source_size(emission.source_size)
    _validate_source_domain(emission.source_domain)
    derivation = derive_goetics(emission)
    if not (
        derivation.same_operator_order
        and derivation.first.interval_verifies
        and derivation.last.interval_verifies
        and derivation.route_dcomp == 0
        and derivation.truth == 1
    ):
        raise RuntimeError("Aeternum Mirror derivation failed local route invariants")
    return _source_route_witness_from_derivation(derivation)


def verify_selection_alqc(witness: SourceRouteWitness) -> bool:
    """Independently verify the carried Mirror derivation, then its route assembly."""
    try:
        derivation = GoldenGoeticDerivation(
            witness.emission,
            witness.first,
            witness.last,
            witness.court_address,
            witness.reciprocal_address,
        )
        if not verify_derivation(derivation):
            return False
        if witness.derivation_proof != _proof_for(witness):
            return False
        expected = _source_route_witness_from_derivation(derivation)
    except (TypeError, ValueError, RuntimeError):
        return False
    return witness == expected

def verify_source(emission: SourceEmission, witness: SourceRouteWitness) -> bool:
    if not isinstance(emission, SourceEmission) or not isinstance(witness, SourceRouteWitness):
        return False
    return (
        witness.emission == emission
        and witness.source_digest == emission.source_digest
        and witness.source_size == emission.source_size
        and witness.source_domain == emission.source_domain
        and verify_selection_alqc(witness)
    )


def parents_t(witness: SourceRouteWitness) -> tuple[str, str]:
    if not isinstance(witness, SourceRouteWitness):
        raise TypeError("parents_t requires one exact SourceRouteWitness")
    return witness.pair


def resolve_parents(
    emission: SourceEmission,
    *,
    witness: SourceRouteWitness,
) -> tuple[str, str, SourceRouteWitness]:
    """Validate and return parents from one completed source-route Vāhana."""
    if not isinstance(witness, SourceRouteWitness):
        raise TypeError("supplied witness must be one exact SourceRouteWitness")
    resolved = witness
    if resolved.emission != emission:
        raise ValueError("source route witness does not belong to the supplied SourceEmission")
    if resolved.source_digest != emission.source_digest:
        raise ValueError("source route witness digest does not match SourceEmission")
    if resolved.source_size != emission.source_size:
        raise ValueError("source route witness size does not match SourceEmission")
    if resolved.source_domain != emission.source_domain:
        raise ValueError("source route witness domain does not match SourceEmission")
    if resolved.derivation_proof != _proof_for(resolved):
        raise ValueError("source route witness proof is not self-consistent")
    if resolved.route_dcomp != 0 or resolved.truth != 1:
        raise ValueError("source route witness does not carry D-COMP=0 / Truth=1")
    lawful = resolved.pair
    return lawful[0], lawful[1], resolved



def calculate_route(emission: SourceEmission) -> HashRoute:
    """Derive the complete route from one source emission and no lesser body."""
    return source_route_witness_from_emission(emission)
