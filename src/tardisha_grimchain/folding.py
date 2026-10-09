"""ALQC fold frames for open TardiSHA coordinate streams.

TardiSHA does not store an infinite string. It stores the lawful seed/manifold
that can unfold any finite coordinate window, and it can fold large manifested
windows back into compact child universe-nodes.

A fold frame is neither truncation nor a second engine. It is one exact ߷
checkpoint whose source node, outward manifestation, born child, and canonical
return body remain mutually derivable.
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, fields

from .alqc_digest import ALQCDigest, validate_digest_hex
from .canon import TOTAL_CAPACITY, court_load
from .hashing import (
    ALPHABET,
    TardiSHAError,
    _encode_uint,
    validate_middle_length,
    validate_nonce,
)
from .node import TardiSHANode
from .route import SourceRouteWitness

FOLD_DOMAIN = b"TARDISHA:ALQC-FOLD-FRAME\x00"
FOLD_LADDER_DOMAIN = b"TARDISHA:ALQC-SELF-COMPRESS-LADDER\x00"
BIRTH_DOMAIN = b"TARDISHA:ALQC-BABY-GLYPH-BIRTH\x00"
UNIVERSE_NODE_DOMAIN = b"TARDISHA:ALQC-UNIVERSE-NODE\x00"
FOLD_OPERATOR = "߷"
BIRTH_CODE_LENGTH = 18


@dataclass(frozen=True, slots=True)
class TardiSHAFoldFrame:
    """One exact Court-rooted ߷ checkpoint and its canonical return body."""

    level: int
    start_coordinate: int
    span_length: int
    fold_factor: int
    origin_glyph: str
    resolution_glyph: str
    source_digest: str
    fold_digest: str
    packet_count: int
    input_digest: str
    universe_node_id: str
    birth_digest: str
    born_glyph: str
    birth_court_load: int
    fold_operator: str
    return_node_id: str
    return_body: dict[str, object]
    nonce: int
    source_size: int
    source_domain: str

    def __post_init__(self) -> None:
        _validate_coordinate(self.level, "level")
        _validate_coordinate(self.start_coordinate, "start_coordinate")
        span = validate_middle_length(self.span_length)
        if isinstance(self.fold_factor, bool) or not isinstance(self.fold_factor, int) or self.fold_factor < 2:
            raise TardiSHAError("fold_factor must be an integer >= 2")
        if isinstance(self.packet_count, bool) or not isinstance(self.packet_count, int) or self.packet_count < 0:
            raise TardiSHAError("packet_count must be a non-negative integer")
        if self.packet_count != (span + TOTAL_CAPACITY - 1) // TOTAL_CAPACITY:
            raise TardiSHAError("packet_count contradicts the manifested span")
        _validate_coordinate(self.source_size, "source_size")
        validate_nonce(self.nonce)
        if not isinstance(self.source_domain, str) or not self.source_domain:
            raise TardiSHAError("source_domain must be a non-empty string")
        for field_name in (
            "source_digest", "fold_digest", "input_digest", "universe_node_id",
            "birth_digest", "return_node_id",
        ):
            validate_digest_hex(getattr(self, field_name), field=field_name)
        if self.fold_operator != FOLD_OPERATOR:
            raise TardiSHAError("fold frame must preserve the Canonical ߷ operator")
        if not isinstance(self.born_glyph, str) or len(self.born_glyph) != BIRTH_CODE_LENGTH + 2:
            raise TardiSHAError("born_glyph must contain two Goetic boundaries and eighteen Synodic coordinates")
        if self.born_glyph[0] != self.origin_glyph or self.born_glyph[-1] != self.resolution_glyph:
            raise TardiSHAError("born_glyph boundaries contradict the fold frame")
        if any(glyph not in ALPHABET for glyph in self.born_glyph[1:-1]):
            raise TardiSHAError("born_glyph center must contain only Synodic Magicae coordinates")
        if isinstance(self.birth_court_load, bool) or not isinstance(self.birth_court_load, int):
            raise TardiSHAError("birth_court_load must be an integer Court address")
        expected_load = court_load(self.origin_glyph, self.resolution_glyph)
        if self.birth_court_load != expected_load:
            raise TardiSHAError("birth_court_load contradicts the ordered Goetic pair")

        node = _return_node_from_serialized_body(self.return_body)
        if node.node_id != self.return_node_id:
            raise TardiSHAError("return_node_id contradicts the complete canonical return body")
        if (
            node.origin_glyph != self.origin_glyph
            or node.resolution_glyph != self.resolution_glyph
            or node.source_digest != self.source_digest
            or node.source_size != self.source_size
            or node.source_domain != self.source_domain
            or node.nonce != self.nonce
        ):
            raise TardiSHAError("fold frame contradicts its canonical return node")

    def as_dict(self) -> dict[str, object]:
        return asdict(self)

    @classmethod
    def from_dict(cls, value: dict[str, object]) -> "TardiSHAFoldFrame":
        if not isinstance(value, dict):
            raise TardiSHAError("serialized fold frame must be an object")
        expected = {item.name for item in fields(cls)}
        supplied = set(value)
        if supplied != expected:
            missing = sorted(expected - supplied)
            extra = sorted(supplied - expected)
            raise TardiSHAError(f"serialized fold frame fields mismatch; missing={missing}, extra={extra}")
        body = dict(value)
        if not isinstance(body["return_body"], dict):
            raise TardiSHAError("fold return_body must be an object")
        body["return_body"] = dict(body["return_body"])
        return cls(**body)


def _validate_coordinate(value: int, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise TardiSHAError(f"{field} must be a non-negative integer")
    return value


def _return_node_from_serialized_body(body: dict[str, object]) -> TardiSHANode:
    if not isinstance(body, dict):
        raise TardiSHAError("canonical return body must be an object")
    data = dict(body)
    try:
        supplied_node_id = validate_digest_hex(data.pop("node_id"), field="node_id")
        supplied_mode_witness = data.pop("mode_witness")
        route_body = data.get("route_witness")
        if not isinstance(route_body, dict):
            raise TardiSHAError("canonical return body requires a route_witness object")
        data["route_witness"] = SourceRouteWitness.from_dict(route_body)
        node = TardiSHANode(**data)
    except (KeyError, TypeError, ValueError) as exc:
        raise TardiSHAError("canonical return body cannot be reconstructed") from exc
    if supplied_mode_witness != node.mode_witness():
        raise TardiSHAError("canonical return body mode witness is forged or stale")
    if node.node_id != supplied_node_id:
        raise TardiSHAError("canonical return body node_id does not verify")
    return node


def _synodic_magicae_from_bytes(data: bytes) -> str:
    """Render one digest body as exactly eighteen Synodic coordinates, without reseeding."""
    if not isinstance(data, bytes) or not data:
        raise TardiSHAError("birth digest must be a non-empty bytes body")
    number = int.from_bytes(data, "big")
    chars: list[str] = []
    for _coordinate in range(BIRTH_CODE_LENGTH):
        number, remainder = divmod(number, len(ALPHABET))
        chars.append(ALPHABET[remainder])
    return "".join(reversed(chars))


def _universe_node_id(
    *,
    node: TardiSHANode,
    fold_digest: str,
    input_digest: str,
    level: int,
    start_coordinate: int,
    span_length: int,
    fold_factor: int,
) -> str:
    payload = json.dumps(
        {
            "node": node.as_dict(),
            "fold_operator": FOLD_OPERATOR,
            "fold_digest": fold_digest,
            "input_digest": input_digest,
            "level": level,
            "start_coordinate": start_coordinate,
            "span_length": span_length,
            "fold_factor": fold_factor,
            "boundary_equation": f"{node.origin_glyph}->{node.resolution_glyph}",
            "court_load": court_load(node.origin_glyph, node.resolution_glyph),
            "return_node_id": node.node_id,
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return ALQCDigest(UNIVERSE_NODE_DOMAIN).update(payload).hexdigest()


def _derive_birth(
    *,
    node: TardiSHANode,
    fold_digest: str,
    input_digest: str,
    level: int,
    start_coordinate: int,
    span_length: int,
    fold_factor: int,
) -> tuple[str, str, int, str]:
    """Derive a child only from one complete, source-bound fold calculation."""
    validate_digest_hex(fold_digest, field="fold_digest")
    validate_digest_hex(input_digest, field="input_digest")
    boundary_load = court_load(node.origin_glyph, node.resolution_glyph)
    universe_node_id = _universe_node_id(
        node=node,
        fold_digest=fold_digest,
        input_digest=input_digest,
        level=level,
        start_coordinate=start_coordinate,
        span_length=span_length,
        fold_factor=fold_factor,
    )
    digest = ALQCDigest(BIRTH_DOMAIN)
    digest._update_raw(
        node.origin_glyph.encode("utf-8")
        + b"\x00"
        + node.resolution_glyph.encode("utf-8")
        + b"\x00"
        + bytes.fromhex(node.source_digest)
        + bytes.fromhex(fold_digest)
        + bytes.fromhex(input_digest)
        + bytes.fromhex(universe_node_id)
        + bytes.fromhex(node.node_id)
        + FOLD_OPERATOR.encode("utf-8")
        + _encode_uint(level)
        + _encode_uint(start_coordinate)
        + _encode_uint(span_length)
        + _encode_uint(fold_factor)
        + _encode_uint(boundary_load)
    )
    birth_digest = digest.hexdigest()
    child_code = _synodic_magicae_from_bytes(bytes.fromhex(birth_digest))
    return (
        f"{node.origin_glyph}{child_code}{node.resolution_glyph}",
        birth_digest,
        boundary_load,
        universe_node_id,
    )


def fold_window(
    node: TardiSHANode,
    *,
    start_coordinate: int = 0,
    span_length: int,
    level: int,
    input_digest: str,
    fold_factor: int,
    chunk_characters: int = 8192,
) -> TardiSHAFoldFrame:
    """Fold one finite stream window and preserve its complete ߷ return body."""
    if isinstance(node, type) or not isinstance(node, TardiSHANode):
        raise TardiSHAError("node must be a TardiSHANode")
    start = _validate_coordinate(start_coordinate, "start_coordinate")
    span = validate_middle_length(span_length)
    _validate_coordinate(level, "level")
    if isinstance(fold_factor, bool) or not isinstance(fold_factor, int) or fold_factor < 2:
        raise TardiSHAError("fold_factor must be an integer >= 2")
    prior = validate_digest_hex(input_digest, field="input_digest")
    if level == 0 and prior != node.source_digest:
        raise TardiSHAError("level-zero fold input must be the node source digest")
    digest = ALQCDigest(FOLD_DOMAIN)
    digest._update_raw(
        node.origin_glyph.encode("utf-8")
        + b"\x00"
        + node.resolution_glyph.encode("utf-8")
        + b"\x00"
        + bytes.fromhex(node.source_digest)
        + bytes.fromhex(prior)
        + bytes.fromhex(node.node_id)
        + FOLD_OPERATOR.encode("utf-8")
        + _encode_uint(level)
        + _encode_uint(start)
        + _encode_uint(span)
        + _encode_uint(fold_factor)
        + _encode_uint(court_load(node.origin_glyph, node.resolution_glyph))
        + node.source_domain.encode("utf-8")
    )
    if node.archive_root is not None:
        digest._update_raw(bytes.fromhex(node.archive_root))
    produced = 0
    for chunk in node.iter_middle_chunks(
        start,
        span,
        chunk_characters=chunk_characters,
    ):
        encoded = chunk.encode("utf-8")
        digest._update_raw(_encode_uint(len(encoded)) + encoded)
        produced += len(chunk)
    if produced != span:
        raise TardiSHAError(f"fold window produced {produced} characters; expected {span}")

    fold_digest = digest.hexdigest()
    born, birth_digest, boundary_load, universe_node_id = _derive_birth(
        node=node,
        fold_digest=fold_digest,
        input_digest=prior,
        level=level,
        start_coordinate=start,
        span_length=span,
        fold_factor=fold_factor,
    )
    return TardiSHAFoldFrame(
        level=level,
        start_coordinate=start,
        span_length=span,
        fold_factor=fold_factor,
        origin_glyph=node.origin_glyph,
        resolution_glyph=node.resolution_glyph,
        source_digest=node.source_digest,
        fold_digest=fold_digest,
        packet_count=(span + TOTAL_CAPACITY - 1) // TOTAL_CAPACITY,
        input_digest=prior,
        universe_node_id=universe_node_id,
        birth_digest=birth_digest,
        born_glyph=born,
        birth_court_load=boundary_load,
        fold_operator=FOLD_OPERATOR,
        return_node_id=node.node_id,
        return_body=node.as_dict(),
        nonce=node.nonce,
        source_size=node.source_size,
        source_domain=node.source_domain,
    )


def _require_verified_fold_frame(frame: TardiSHAFoldFrame) -> TardiSHANode:
    if not isinstance(frame, TardiSHAFoldFrame):
        raise TardiSHAError("fold verification requires a TardiSHAFoldFrame")
    node = _return_node_from_serialized_body(frame.return_body)
    expected = fold_window(
        node,
        start_coordinate=frame.start_coordinate,
        span_length=frame.span_length,
        level=frame.level,
        input_digest=frame.input_digest,
        fold_factor=frame.fold_factor,
    )
    if expected != frame:
        raise TardiSHAError("fold frame does not return to its exact source-bound ߷ derivation")
    return node



def birth_glyph(frame: TardiSHAFoldFrame) -> tuple[str, str, int]:
    """Expose a born child only after the complete fold frame verifies."""
    _require_verified_fold_frame(frame)
    return frame.born_glyph, frame.birth_digest, frame.birth_court_load


def self_compress_ladder(
    node: TardiSHANode,
    *,
    start_coordinate: int = 0,
    span_length: int,
    levels: int = 8,
    fold_factor: int = 2,
    chunk_characters: int = 8192,
) -> tuple[TardiSHAFoldFrame, ...]:
    """Return an exact chain of source-bound ߷ checkpoints."""
    if isinstance(levels, bool) or not isinstance(levels, int) or levels < 1:
        raise TardiSHAError("levels must be a positive integer")
    if isinstance(fold_factor, bool) or not isinstance(fold_factor, int) or fold_factor < 2:
        raise TardiSHAError("fold_factor must be an integer >= 2")
    span = validate_middle_length(span_length)
    start = _validate_coordinate(start_coordinate, "start_coordinate")
    frames: list[TardiSHAFoldFrame] = []
    prior = node.source_digest
    current_span = span
    for level in range(levels):
        frame = fold_window(
            node,
            start_coordinate=start,
            span_length=current_span,
            level=level,
            input_digest=prior,
            fold_factor=fold_factor,
            chunk_characters=chunk_characters,
        )
        frames.append(frame)
        prior = frame.fold_digest
        if current_span == 0:
            break
        current_span //= fold_factor
    verified = tuple(frames)
    _require_verified_fold_ladder(verified)
    return verified


def _require_verified_fold_ladder(frames: tuple[TardiSHAFoldFrame, ...]) -> None:
    if not isinstance(frames, tuple) or not frames:
        raise TardiSHAError("fold ladder must contain at least one frame")
    first = frames[0]
    node = _require_verified_fold_frame(first)
    if first.level != 0 or first.input_digest != first.source_digest:
        raise TardiSHAError("fold ladder must begin at level zero with the source digest")
    for index, frame in enumerate(frames):
        _require_verified_fold_frame(frame)
        if frame.level != index:
            raise TardiSHAError("fold ladder levels must be contiguous from zero")
        if frame.return_node_id != first.return_node_id or frame.return_body != first.return_body:
            raise TardiSHAError("every fold level must return to the same canonical node")
        if frame.fold_factor != first.fold_factor or frame.start_coordinate != first.start_coordinate:
            raise TardiSHAError("fold ladder factor and start coordinate must remain invariant")
        if (
            frame.origin_glyph != node.origin_glyph
            or frame.resolution_glyph != node.resolution_glyph
            or frame.source_digest != node.source_digest
        ):
            raise TardiSHAError("fold ladder boundary or source identity changed")
        if index:
            previous = frames[index - 1]
            if frame.input_digest != previous.fold_digest:
                raise TardiSHAError("fold ladder input does not equal the prior fold digest")
            if previous.span_length == 0:
                raise TardiSHAError("no fold level may follow the zero-span terminal frame")
            if frame.span_length != previous.span_length // frame.fold_factor:
                raise TardiSHAError("fold ladder span does not follow its declared fold factor")



def ladder_avirbhava(frames: tuple[TardiSHAFoldFrame, ...]) -> dict[str, object]:
    """Bring one fully verified ߷ ladder and its complete return body into visible form."""
    _require_verified_fold_ladder(frames)
    root = ALQCDigest(FOLD_LADDER_DOMAIN)
    for frame in frames:
        payload = json.dumps(frame.as_dict(), ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        root._update_raw(_encode_uint(len(payload)) + payload)
    first = frames[0]
    return {
        "type": "TardiSHA_ALQC_self_compression_ladder",
        "fold_operator": FOLD_OPERATOR,
        "root_digest": root.hexdigest(),
        "return_node_id": first.return_node_id,
        "return_body": first.return_body,
        "origin_glyph": first.origin_glyph,
        "resolution_glyph": first.resolution_glyph,
        "boundary_equation": f"{first.origin_glyph}->{first.resolution_glyph}",
        "birth_court_load": first.birth_court_load,
        "fold_factor": first.fold_factor,
        "nonce": first.nonce,
        "source_size": first.source_size,
        "source_domain": first.source_domain,
        "born_glyphs": [frame.born_glyph for frame in frames],
        "universe_node_ids": [frame.universe_node_id for frame in frames],
        "frames": [frame.as_dict() for frame in frames],
    }


def public_ladder_avirbhava(frames: tuple[TardiSHAFoldFrame, ...]) -> dict[str, object]:
    """Bring the verified public fold result into visible form without internal closure-status proof bodies."""
    full = ladder_avirbhava(frames)
    return {
        "type": full["type"],
        "fold_operator": full["fold_operator"],
        "root_digest": full["root_digest"],
        "return_node_id": full["return_node_id"],
        "origin_glyph": full["origin_glyph"],
        "resolution_glyph": full["resolution_glyph"],
        "boundary_equation": full["boundary_equation"],
        "birth_court_load": full["birth_court_load"],
        "fold_factor": full["fold_factor"],
        "nonce": full["nonce"],
        "source_size": full["source_size"],
        "source_domain": full["source_domain"],
        "born_glyphs": full["born_glyphs"],
        "universe_node_ids": full["universe_node_ids"],
    }


