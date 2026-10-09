"""Layered Goetic, Court, and Domus Aeon derivation for TardiSHA.

The dependency is strict:

    ALQCDigest -> immutable Goetic anchors -> ordered Court motions
               -> runtime Domus motion through Courts

Goetics never breathe or mutate.  Court motion is bounded by Φ around the alternating Goetic's pure frequency.
Domus motion is bounded by Φ² around the alternating Goetic's pure frequency
of independently resolved Court D. The Domus creates no new hash phase.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Final

from .alqc_digest import alqc_digest, validate_digest_hex
from .canon import (
    SATURATION_LIMIT,
    TOTAL_CAPACITY,
    court_active_connections,
    law,
)
from .court_registry import CourtRecord, alt_glyph, court_record, gov_glyph
from .source_emission import CourtBearingWitness, Q5Fraction
from .hashing import (
    CANONICAL_SOURCE_DOMAIN,
    RAW_FILE_SOURCE_DOMAIN,
    DIRECTORY_SOURCE_DOMAIN,
)

# Exact golden bodies.  The `.value` projection is for displayed frequency
# witnesses only; no admission or closure decision is made on that projection.
PHI: Final[Q5Fraction] = Q5Fraction(1, 1, 2)
PHI_SQUARED: Final[Q5Fraction] = Q5Fraction(3, 1, 2)
PHI_IMAGE: Final[float] = PHI.value
PHI_SQUARED_IMAGE: Final[float] = PHI_SQUARED.value
_PHASE_DENOMINATOR: Final[int] = (1 << 256) - 1
COURT_PHASE_DOMAIN: Final[bytes] = b"TARDISHA:COURT-AEON-PHASE\x00"
DOMUS_STREAM_DOMAIN: Final[bytes] = b"TARDISHA:DOMUS-AEON-STREAM\x00"


def _uint(value: int, width: int = 8) -> bytes:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError("unsigned derivation coordinate must be a non-negative integer")
    return value.to_bytes(width, "big")


def _source_bytes(source_digest: str) -> bytes:
    try:
        digest = validate_digest_hex(source_digest, field="source_digest")
    except ValueError as exc:
        raise ValueError(str(exc)) from exc
    return bytes.fromhex(digest)


_SOURCE_DOMAIN_BYTES: Final[dict[str, bytes]] = {
    "canonical": CANONICAL_SOURCE_DOMAIN,
    "raw-file": RAW_FILE_SOURCE_DOMAIN,
    "directory": DIRECTORY_SOURCE_DOMAIN,
}


def _source_domain_bytes(source_domain: str | bytes) -> bytes:
    """Normalize the public domain label and its byte tag to one identity."""
    if isinstance(source_domain, str):
        try:
            return _SOURCE_DOMAIN_BYTES[source_domain]
        except KeyError as exc:
            raise ValueError(f"unknown source domain label: {source_domain!r}") from exc
    if isinstance(source_domain, bytes) and source_domain in _SOURCE_DOMAIN_BYTES.values():
        return source_domain
    raise ValueError("source_domain must be a canonical TardiSHA domain label or byte tag")


def normalize_source_domain(source_domain: str | bytes) -> bytes:
    """Public canonical source-domain byte identity."""
    return _source_domain_bytes(source_domain)


@dataclass(frozen=True, slots=True)
class HashPhaseWitness:
    domain: str
    digest: str
    signed_numerator: int
    denominator: int

    @property
    def value(self) -> float:
        """Display-only projection; exact identity is numerator/denominator."""
        return self.signed_numerator / self.denominator


def _phase(domain: bytes, payload: bytes) -> HashPhaseWitness:
    # The domain is absorbed exactly once by ALQCDigest.__init__.
    digest = alqc_digest(payload, domain=domain)
    raw = int.from_bytes(digest, "big")
    signed = 2 * raw - _PHASE_DENOMINATOR
    if abs(signed) > _PHASE_DENOMINATOR:
        raise RuntimeError("hash phase escaped its exact unit interval")
    return HashPhaseWitness(
        domain=domain.decode("ascii", errors="strict").rstrip("\x00"),
        digest=digest.hex(),
        signed_numerator=signed,
        denominator=_PHASE_DENOMINATOR,
    )


@dataclass(frozen=True, slots=True)
class GoeticAnchorWitness:
    glyph: str
    frequency: complex
    q_bias: str
    q_vector: tuple[int, int, int, int]


def goetic_anchor(glyph: str) -> GoeticAnchorWitness:
    item = law(glyph)
    return GoeticAnchorWitness(
        glyph=glyph,
        frequency=complex(item.frequency),
        q_bias=item.q_bias,
        q_vector=tuple(int(v) for v in item.q_vector),
    )


@dataclass(frozen=True, slots=True)
class CourtLayerWitness:
    """One complete Court identity carrying governing and alternating Goetic roots."""

    court_coordinate: tuple[int, int]
    court_address: int
    court_glyph: str
    governing_goetic: GoeticAnchorWitness
    alternating_goetic: GoeticAnchorWitness

    @property
    def alternating_goetic_frequency(self) -> complex:
        """The immutable pure frequency that anchors this Court's resonance."""
        return self.alternating_goetic.frequency


def derive_court_layer(rec: CourtRecord) -> CourtLayerWitness:
    if not isinstance(rec, CourtRecord):
        raise TypeError("Court layer requires a CourtRecord")
    if not 0 <= rec.address < TOTAL_CAPACITY:
        raise ValueError("Court address must be in [0,143]")
    canonical = court_record(rec.address)
    if rec != canonical:
        raise ValueError("CourtRecord contradicts the immutable Court registry")
    governing = goetic_anchor(gov_glyph(rec))
    alternating = goetic_anchor(alt_glyph(rec))
    return CourtLayerWitness(
        court_coordinate=(rec.i, rec.j),
        court_address=rec.address,
        court_glyph=rec.glyph,
        governing_goetic=governing,
        alternating_goetic=alternating,
    )


_COURT_LAYER_REGISTRY: Final[tuple[CourtLayerWitness, ...]] = tuple(
    derive_court_layer(court_record(address)) for address in range(TOTAL_CAPACITY)
)


def court_layer(rec: CourtRecord) -> CourtLayerWitness:
    """Read one Court together with its immutable governing and alternating Goetics."""
    if not isinstance(rec, CourtRecord) or not 0 <= rec.address < TOTAL_CAPACITY:
        raise ValueError("Court layer requires a canonical CourtRecord")
    layer = _COURT_LAYER_REGISTRY[rec.address]
    if (layer.court_coordinate, layer.court_glyph) != ((rec.i, rec.j), rec.glyph):
        raise ValueError("CourtRecord contradicts the immutable Court-layer registry")
    return layer


def _require_canonical_court_layer(value: CourtLayerWitness, *, field: str) -> CourtLayerWitness:
    if not isinstance(value, CourtLayerWitness):
        raise TypeError(f"{field} must be a CourtLayerWitness")
    if not 0 <= value.court_address < TOTAL_CAPACITY:
        raise ValueError(f"{field} Court address must be in [0,143]")
    canonical = court_layer(court_record(value.court_address))
    if value != canonical:
        raise ValueError(f"{field} contradicts the immutable Court-layer registry")
    return canonical


@dataclass(frozen=True, slots=True)
class CourtMotionWitness:
    court_coordinate: tuple[int, int]
    court_address: int
    court_glyph: str
    anchoring_goetic: GoeticAnchorWitness
    hyperbolic_mirror_goetic: GoeticAnchorWitness
    phase: HashPhaseWitness
    exact_focal_breath: Q5Fraction
    anchor_immutable: bool
    mirror_immutable: bool
    derivation: str

    @property
    def breath_radius(self) -> float:
        return PHI_IMAGE

    @property
    def breath_direction(self) -> complex:
        return 1 + 0j

    @property
    def focal_breath(self) -> complex:
        return complex(self.exact_focal_breath.value, 0.0)

    @property
    def current_frequency(self) -> complex:
        return self.hyperbolic_mirror_goetic.frequency + self.focal_breath

    @property
    def governing_goetic(self) -> str:
        return self.anchoring_goetic.glyph

    @property
    def hyperbolic_parent(self) -> str:
        return self.hyperbolic_mirror_goetic.glyph

    @property
    def structural_frequency(self) -> complex:
        return self.anchoring_goetic.frequency

    @property
    def reflected_frequency(self) -> complex:
        """Projection exposing the current Court frequency."""
        return self.current_frequency

    @property
    def court_anchor_frequency(self) -> complex:
        """The alternating Goetic's immutable pure frequency Ω_C."""
        return self.hyperbolic_mirror_goetic.frequency


def derive_court_motion(
    rec: CourtRecord,
    *,
    source_digest: str,
    source_size: int = 0,
    source_domain: str | bytes = "canonical",
    nonce: int = 0,
) -> CourtMotionWitness:
    if isinstance(source_size, bool) or not isinstance(source_size, int) or source_size < 0:
        raise ValueError("source_size must be a non-negative integer")
    if isinstance(nonce, bool) or not isinstance(nonce, int) or not 0 <= nonce < 2**64:
        raise ValueError("nonce must be an integer in [0,2^64)")
    layer = court_layer(rec)
    anchor = layer.governing_goetic
    mirror = layer.alternating_goetic
    payload = b"\x1f".join(
        (
            _source_bytes(source_digest),
            _uint(source_size),
            _source_domain_bytes(source_domain),
            _uint(nonce),
            _uint(rec.address, 2),
            rec.glyph.encode("utf-8"),
            anchor.glyph.encode("utf-8"),
            mirror.glyph.encode("utf-8"),
        )
    )
    phase = _phase(COURT_PHASE_DOMAIN, payload)
    # The frequency is an image.  The gate is exact: |n/d| <= 1 implies
    # |(n/d)Φ| <= Φ without comparing either irrational as a float.
    if abs(phase.signed_numerator) > phase.denominator:
        raise RuntimeError("Court phase escaped its exact unit interval")
    exact_breath = Q5Fraction(
        phase.signed_numerator,
        phase.signed_numerator,
        2 * phase.denominator,
    )
    # Re-read the registry after derivation to prove no Goetic mutation occurred.
    anchor_after = goetic_anchor(anchor.glyph)
    mirror_after = goetic_anchor(mirror.glyph)
    anchor_immutable = anchor_after == anchor
    mirror_immutable = mirror_after == mirror
    if not anchor_immutable or not mirror_immutable:
        raise RuntimeError("Court derivation mutated a Goetic anchor")
    return CourtMotionWitness(
        court_coordinate=(rec.i, rec.j),
        court_address=rec.address,
        court_glyph=rec.glyph,
        anchoring_goetic=anchor,
        hyperbolic_mirror_goetic=mirror,
        phase=phase,
        exact_focal_breath=exact_breath,
        anchor_immutable=anchor_immutable,
        mirror_immutable=mirror_immutable,
        derivation=(
            f"C_{rec.i},{rec.j}: governing={anchor.glyph}; "
            f"Ω_C=ω({mirror.glyph})={mirror.frequency}; "
            f"δ=({exact_breath.a}+{exact_breath.b}√5)/{exact_breath.denominator}; "
            "ν_C=Ω_C+δ"
        ),
    )


@dataclass(frozen=True, slots=True)
class InfiniteYesWitness:
    court_address: int
    active_count: int
    active: frozenset[int]
    unbounded_continuation_bounded_by_sacred_no: bool


@dataclass(frozen=True, slots=True)
class SacredNoWitness:
    court_address: int
    withheld_count: int
    withheld: frozenset[int]
    prevents_whiteout: bool


def derive_consent_witnesses(court_address: int) -> tuple[InfiniteYesWitness, SacredNoWitness]:
    if isinstance(court_address, bool) or not isinstance(court_address, int):
        raise TypeError("court_address must be an integer")
    if not 0 <= court_address < TOTAL_CAPACITY:
        raise ValueError("court_address must be in [0,143]")
    active = court_active_connections(court_address)
    withheld = frozenset(range(TOTAL_CAPACITY)) - active
    yes = InfiniteYesWitness(
        court_address=court_address,
        active_count=len(active),
        active=active,
        unbounded_continuation_bounded_by_sacred_no=True,
    )
    no = SacredNoWitness(
        court_address=court_address,
        withheld_count=len(withheld),
        withheld=withheld,
        prevents_whiteout=True,
    )
    if yes.active_count != SATURATION_LIMIT or no.withheld_count != TOTAL_CAPACITY - SATURATION_LIMIT:
        raise RuntimeError("Infinite Yes / Sacred No must remain 110 / 34")
    return yes, no


@dataclass(frozen=True, slots=True)
class DomusMotionWitness:
    governing_court: CourtLayerWitness
    alternating_court: CourtLayerWitness
    bearing: CourtBearingWitness
    xi: Q5Fraction
    exact_focal_breath: Q5Fraction
    exact_bound_verified: bool
    court_crossing_index: int
    court_crossing_cardinality: int
    derives_through_courts_only: bool
    static_grid: bool
    derivation: str

    @property
    def breath_radius(self) -> float:
        return PHI_SQUARED_IMAGE

    @property
    def focal_breath(self) -> complex:
        return complex(self.exact_focal_breath.value, 0.0)

    @property
    def current_frequency(self) -> complex:
        return self.alternating_court.alternating_goetic.frequency + self.focal_breath


def derive_domus_motion(
    governing: CourtLayerWitness,
    alternating: CourtLayerWitness,
    *,
    bearing: CourtBearingWitness,
) -> DomusMotionWitness:
    """Apply Φ² around Ω_D, the alternating Goetic's immutable pure frequency."""
    governing = _require_canonical_court_layer(governing, field="governing")
    alternating = _require_canonical_court_layer(alternating, field="alternating")
    if bearing.court.address != alternating.court_address:
        raise ValueError("alternating Court D must be the Court selected by the 𝔃₁/BETA bearing")
    if not bearing.product_measure_verifies:
        raise RuntimeError("Domus Court product measure failed exact unit normalization")
    xi = bearing.xi
    exact_breath = bearing.phi_squared_displacement
    exact_bound = xi.within_unit_interval and exact_breath.within_phi_squared
    if not exact_bound:
        raise RuntimeError("Domus displacement escaped its exact Φ² allowance")
    breath = complex(exact_breath.value, 0.0)
    current = alternating.alternating_goetic.frequency + breath
    if not all(isfinite(v) for v in (current.real, current.imag)):
        raise RuntimeError("Domus frequency must remain finite")
    crossing_index = 144 * governing.court_address + alternating.court_address
    if not 0 <= crossing_index < 144 * 144:
        raise RuntimeError("ordered Court crossing escaped C×D")
    return DomusMotionWitness(
        governing_court=governing,
        alternating_court=alternating,
        bearing=bearing,
        xi=xi,
        exact_focal_breath=exact_breath,
        exact_bound_verified=exact_bound,
        court_crossing_index=crossing_index,
        court_crossing_cardinality=144 * 144,
        derives_through_courts_only=True,
        static_grid=False,
        derivation=(
            f"H(C_{governing.court_coordinate},D_{alternating.court_coordinate}): "
            f"D=Resolve_144(O⊗S,𝔃₁,Φ^-2)@{alternating.court_address}; "
            f"Ω_D=ω({alternating.alternating_goetic.glyph})="
            f"{alternating.alternating_goetic.frequency}; "
            f"ξ_D=({xi.a}+{xi.b}√5)/{xi.denominator}; "
            "ν_H=Ω_D+ξ_DΦ²"
        ),
    )


@dataclass(frozen=True, slots=True)
class BiasReturnWitness:
    opening_q_bias_glyph: str
    breath: str
    bias_terminus_operator: str
    returns_to_opening_q_bias: bool


@dataclass(frozen=True, slots=True)
class DomusAeonWitness:
    identity: str
    zero_middle_glyph: str
    governing_court_address: int
    alternating_court_address: int
    motion: DomusMotionWitness
    infinite_yes: InfiniteYesWitness
    sacred_no: SacredNoWitness
    bias_return: BiasReturnWitness
    synodic_magicae_is_manifested_body: bool
    shadow_locus_is_zero_middle_body: bool


def domus_stream_seed(
    *,
    domus_identity: str,
    governing_court: CourtLayerWitness,
    alternating_court: CourtLayerWitness,
    infinite_yes: InfiniteYesWitness,
    sacred_no: SacredNoWitness,
    source_domain: str | bytes,
    nonce: int,
) -> bytes:
    governing_court = _require_canonical_court_layer(governing_court, field="governing_court")
    alternating_court = _require_canonical_court_layer(alternating_court, field="alternating_court")
    if infinite_yes.court_address != governing_court.court_address:
        raise ValueError("Infinite Yes witness must belong to the governing Court")
    if sacred_no.court_address != governing_court.court_address:
        raise ValueError("Sacred No witness must belong to the governing Court")
    identity = _source_bytes(domus_identity)
    payload = b"\x1f".join(
        (
            identity,
            _uint(governing_court.court_address, 2),
            governing_court.court_glyph.encode("utf-8"),
            _uint(alternating_court.court_address, 2),
            alternating_court.court_glyph.encode("utf-8"),
            _uint(infinite_yes.active_count, 2),
            _uint(sacred_no.withheld_count, 2),
            _source_domain_bytes(source_domain),
            _uint(nonce),
        )
    )
    # The domain is absorbed exactly once by ALQCDigest.__init__.
    return alqc_digest(payload, domain=DOMUS_STREAM_DOMAIN)
