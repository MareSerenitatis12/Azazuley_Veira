"""Deterministic coordinate-stream primitives for TardiSHA.

TardiSHA means Time and Relative Dimension in Space Hash.  There is one
canonical engine law: source identity plus Goetic boundaries produce a
continuation coordinate stream. Requested length is an extent/view, not a
separate identity law, so every finite manifestation is a window of the same
rooted manifold.
"""
from __future__ import annotations

import base64
import json
import math
import os
import stat
from dataclasses import asdict, is_dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Iterator, Mapping

from .canon import GLYPH_BODY
from .alqc_digest import ALQCDigest, alqc_digest, alqc_digest_prefix, validate_digest_hex
from .living_alphabet import ALPHABET
from .source_emission import PHASE_BYTES, SourceEmission, emission_from_sponge

SOURCE_CHUNK_BYTES = 8 * 1024 * 1024
OUTPUT_CHUNK_CHARACTERS = 8192

SEED_DOMAIN = b"TARDISHA:TIME-RELATIVE-DIMENSION-IN-SPACE:SEED\x00"
CHAR_DOMAIN = b"TARDISHA:CONTINUATION-CHAR-AT\x00"
CANONICAL_SOURCE_DOMAIN = b"TARDISHA:CANONICAL-SOURCE\x00"
RAW_FILE_SOURCE_DOMAIN = b"TARDISHA:RAW-FILE-SOURCE\x00"
FILE_NAME_FRAME = b"TARDISHA:FILE-NAME\x00"
DIRECTORY_SOURCE_DOMAIN = b"TARDISHA:DIRECTORY-SOURCE\x00"

GENERATED_FIELDS = frozenset(
    {
        "TardiSHA_id",
        "TardiSHA_nonce",
        "TardiSHA_middle_length",
        "origin_glyph",
        "resolution_glyph",
    }
)


class TardiSHAError(ValueError):
    """Raised when a TardiSHA invariant is violated."""


def validate_middle_length(value: int) -> int:
    """Resolve one declared middle depth; negative depth returns to Shadow Locus zero."""
    if isinstance(value, bool) or not isinstance(value, int):
        raise TardiSHAError("middle_length must be an integer")
    return 0 if value < 0 else value



def validate_nonce(value: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value < 2**64:
        raise TardiSHAError("nonce must be an integer in [0, 2^64)")
    return value


def validate_glyph(glyph: str, field: str = "glyph") -> str:
    if glyph not in GLYPH_BODY:
        raise TardiSHAError(f"{field} must be one exact Goetic glyph: {''.join(GLYPH_BODY)}")
    return glyph


def _json_key(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def _normalize(value: Any) -> Any:
    if hasattr(value, "model_dump"):
        value = value.model_dump(mode="json")
    elif is_dataclass(value) and not isinstance(value, type):
        value = asdict(value)
    elif isinstance(value, Enum):
        value = value.value

    if value is None:
        return ["null"]
    if isinstance(value, bool):
        return ["bool", value]
    if isinstance(value, int):
        return ["int", str(value)]
    if isinstance(value, float):
        if not math.isfinite(value):
            raise TardiSHAError("NaN and infinity cannot be canonicalized")
        return ["float", value.hex()]
    if isinstance(value, str):
        return ["str", value]
    if isinstance(value, (bytes, bytearray, memoryview)):
        return ["bytes", base64.b64encode(bytes(value)).decode("ascii")]
    if isinstance(value, Path):
        raise TardiSHAError("Path is not canonical material; use file_emission() for raw file content")
    if isinstance(value, Mapping):
        pairs = [[_normalize(key), _normalize(item)] for key, item in value.items()]
        pairs.sort(key=lambda pair: _json_key(pair[0]))
        return ["map", pairs]
    if isinstance(value, list):
        return ["list", [_normalize(item) for item in value]]
    if isinstance(value, tuple):
        return ["tuple", [_normalize(item) for item in value]]
    if isinstance(value, (set, frozenset)):
        items = [_normalize(item) for item in value]
        items.sort(key=_json_key)
        return ["set", items]
    raise TardiSHAError(f"unsupported material type: {type(value).__name__}")


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        _normalize(value),
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def identity_material(record: Mapping[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in record.items() if key not in GENERATED_FIELDS}


def canonical_emission(material: Any) -> tuple[SourceEmission, bytes]:
    """Return the complete canonical emission while preserving framed digest law."""
    source = canonical_bytes(material)
    sponge = ALQCDigest(CANONICAL_SOURCE_DOMAIN)
    sponge.update(source)
    # canonical_fingerprint historically uses digest_separated(32).  Carry that
    # exact separated state forward so Fraktur Z_0 remains byte-identical while
    # Fraktur Z_1 is the next equal-width cadence of the same state.
    separated = sponge.copy()
    separated._update_frame(b"DIGEST-LENGTH\x00", PHASE_BYTES.to_bytes(8, "big"))
    emission = emission_from_sponge(
        separated,
        source_size=len(source),
        source_domain="canonical",
    )
    return emission, source


def canonical_fingerprint(material: Any) -> tuple[str, int, bytes]:
    emission, source = canonical_emission(material)
    return emission.source_digest, emission.source_size, source


def canonical_digest(material: Any) -> str:
    return canonical_emission(material)[0].source_digest


def _stat_witness(result: os.stat_result) -> tuple[int, int, int, int, int, int]:
    return (
        result.st_dev,
        result.st_ino,
        result.st_mode,
        result.st_size,
        result.st_mtime_ns,
        result.st_ctime_ns,
    )


def file_emission(
    path: str | Path,
    *,
    identity_name: str | bytes | None = None,
    include_filename: bool = True,
) -> SourceEmission:
    """Return one temporally sealed raw-file emission from filename and unchanged file body."""
    target = Path(path)
    before_path = target.stat()
    if not stat.S_ISREG(before_path.st_mode):
        raise TardiSHAError("file_emission requires a regular file")

    sponge = ALQCDigest(RAW_FILE_SOURCE_DOMAIN)
    if include_filename:
        if identity_name is None:
            name_bytes = os.fsencode(target.name)
        elif isinstance(identity_name, str):
            name_bytes = os.fsencode(identity_name)
        elif isinstance(identity_name, bytes):
            name_bytes = identity_name
        else:
            raise TardiSHAError("identity_name must be str, bytes, or None")
        if not name_bytes:
            raise TardiSHAError("file identity requires a non-empty filename")
        sponge._update_frame(FILE_NAME_FRAME, name_bytes)
    elif identity_name is not None:
        raise TardiSHAError("identity_name requires filename identity to be enabled")
    size = 0
    with target.open("rb") as handle:
        before_handle = os.fstat(handle.fileno())
        if _stat_witness(before_handle) != _stat_witness(before_path):
            raise TardiSHAError("file identity changed before source witnessing began")
        for chunk in iter(lambda: handle.read(SOURCE_CHUNK_BYTES), b""):
            sponge._update_raw(chunk)
            size += len(chunk)
        after_handle = os.fstat(handle.fileno())

    after_path = target.stat()
    witness = _stat_witness(before_path)
    if _stat_witness(before_handle) != witness or _stat_witness(after_handle) != witness:
        raise TardiSHAError("file changed while its Q1 emission was being witnessed")
    if _stat_witness(after_path) != witness:
        raise TardiSHAError("file path no longer names the witnessed Q1 body")
    if size != before_path.st_size:
        raise TardiSHAError("witnessed byte count contradicts the sealed file size")

    return emission_from_sponge(
        sponge,
        source_size=size,
        source_domain="raw-file",
    )



def file_emission_from_bytes(
    body: bytes,
    *,
    identity_name: str | bytes | None,
    include_filename: bool = True,
) -> SourceEmission:
    """Return a raw-file emission from one invocation-local byte Vāhana.

    No body is retained after the call. Filename identity follows the same framed
    ALQC law as :func:`file_emission`; an in-memory body has no implicit filename.
    """
    if type(body) is not bytes:
        raise TypeError("file byte Vāhana must be exact bytes")
    sponge = ALQCDigest(RAW_FILE_SOURCE_DOMAIN)
    if include_filename:
        if isinstance(identity_name, str):
            name_bytes = os.fsencode(identity_name)
        elif isinstance(identity_name, bytes):
            name_bytes = identity_name
        elif identity_name is None:
            raise TardiSHAError("in-memory file identity requires explicit identity_name")
        else:
            raise TardiSHAError("identity_name must be str, bytes, or None")
        if not name_bytes:
            raise TardiSHAError("file identity requires a non-empty filename")
        sponge._update_frame(FILE_NAME_FRAME, name_bytes)
    elif identity_name is not None:
        raise TardiSHAError("identity_name requires filename identity to be enabled")
    sponge._update_raw(body)
    return emission_from_sponge(sponge, source_size=len(body), source_domain="raw-file")


def file_fingerprint(path: str | Path) -> tuple[str, int]:
    emission = file_emission(path)
    return emission.source_digest, emission.source_size


def _tree_record_bytes(record: Mapping[str, Any]) -> bytes:
    return json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8") + b"\n"


def _directory_entries(root: Path) -> Iterator[Path]:
    stack = [root]
    while stack:
        current = stack.pop()
        try:
            entries = sorted(os.scandir(current), key=lambda entry: entry.name)
        except OSError as exc:
            raise TardiSHAError(f"cannot read directory {current}: {exc}") from exc
        directories: list[Path] = []
        for entry in entries:
            child = Path(entry.path)
            yield child
            if entry.is_dir(follow_symlinks=False) and not entry.is_symlink():
                directories.append(child)
        stack.extend(reversed(directories))


def _directory_snapshot(
    root: Path,
) -> tuple[tuple[bytes, ...], tuple[tuple[object, ...], ...], int, int]:
    records: list[bytes] = [_tree_record_bytes({"type": "directory", "path": "."})]
    witnesses: list[tuple[object, ...]] = [
        (".", "directory", _stat_witness(root.lstat()))
    ]
    total_file_bytes = 0
    entry_count = 1

    for child in _directory_entries(root):
        rel = child.relative_to(root).as_posix()
        before = child.lstat()
        before_witness = _stat_witness(before)

        if stat.S_ISLNK(before.st_mode):
            target = os.readlink(child)
            after = child.lstat()
            if _stat_witness(after) != before_witness:
                raise TardiSHAError(f"symlink changed while being witnessed: {rel}")
            records.append(_tree_record_bytes({"type": "symlink", "path": rel, "target": target}))
            witnesses.append((rel, "symlink", before_witness, target))
        elif stat.S_ISDIR(before.st_mode):
            after = child.lstat()
            if _stat_witness(after) != before_witness:
                raise TardiSHAError(f"directory changed while being witnessed: {rel}")
            records.append(_tree_record_bytes({"type": "directory", "path": rel}))
            witnesses.append((rel, "directory", before_witness))
        elif stat.S_ISREG(before.st_mode):
            child_emission = file_emission(child)

            after = child.lstat()
            if _stat_witness(after) != before_witness:
                raise TardiSHAError(f"file identity changed during directory witnessing: {rel}")
            records.append(
                _tree_record_bytes(
                    {
                        "type": "file",
                        "path": rel,
                        "digest": child_emission.source_digest,
                        "size": child_emission.source_size,
                    }
                )
            )
            witnesses.append(
                (rel, "file", before_witness, child_emission.source_digest, child_emission.source_size)
            )
            total_file_bytes += child_emission.source_size
        else:
            raise TardiSHAError(f"unsupported directory entry type: {rel}")
        entry_count += 1

    return tuple(records), tuple(witnesses), total_file_bytes, entry_count


def directory_emission(path: str | Path) -> tuple[SourceEmission, int]:
    """Return one two-witness emission of a complete unchanged directory tree."""
    root = Path(path)
    before_root = root.lstat()
    if not stat.S_ISDIR(before_root.st_mode):
        raise TardiSHAError("directory_emission requires a directory path")

    first = _directory_snapshot(root)
    second = _directory_snapshot(root)
    after_root = root.lstat()
    if _stat_witness(before_root) != _stat_witness(after_root):
        raise TardiSHAError("directory root changed while its Q1 tree was being witnessed")
    if first != second:
        raise TardiSHAError("directory tree changed between its two complete Q1 witnesses")

    records, _witnesses, total_file_bytes, entry_count = first
    sponge = ALQCDigest(DIRECTORY_SOURCE_DOMAIN)
    for record in records:
        sponge._update_raw(record)
    emission = emission_from_sponge(
        sponge,
        source_size=total_file_bytes,
        source_domain="directory",
    )
    return emission, entry_count


def directory_fingerprint(path: str | Path) -> tuple[str, int, int]:
    emission, entry_count = directory_emission(path)
    return emission.source_digest, emission.source_size, entry_count


def _validate_source_digest(value: str) -> str:
    try:
        return validate_digest_hex(value, field="source_digest")
    except ValueError as exc:
        raise TardiSHAError(str(exc)) from exc


def _encode_uint(value: int) -> bytes:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise TardiSHAError("unsigned coordinate must be a non-negative integer")
    return str(value).encode("ascii") + b"\x00"


def coordinate_seed(
    *,
    source_digest: str,
    source_size: int,
    origin_glyph: str,
    resolution_glyph: str,
    middle_length: int,
    nonce: int = 0,
    source_domain: bytes = RAW_FILE_SOURCE_DOMAIN,
) -> bytes:
    """Bind source, boundaries, source kind, and nonce into one ALQC-native 256-bit root.

    ``middle_length`` is validated as a finite requested extent, but it does not
    enter the root. Extending a manifestation therefore preserves all earlier
    coordinates. The middle is a view of the rooted manifold, not a separate
    identity law.
    """
    source_hash = bytes.fromhex(_validate_source_digest(source_digest))
    if isinstance(source_size, bool) or not isinstance(source_size, int) or source_size < 0:
        raise TardiSHAError("source_size must be a non-negative integer")
    origin = validate_glyph(origin_glyph, "origin_glyph")
    resolution = validate_glyph(resolution_glyph, "resolution_glyph")
    validate_middle_length(middle_length)
    salt = validate_nonce(nonce)
    if not isinstance(source_domain, bytes) or not source_domain:
        raise TardiSHAError("source_domain must be non-empty bytes")

    # Terminal D-COMP is a finite-return witness, not an emission gate.  The
    # generic continuation root remains a source-identity body.  Court/Domus
    # commitments bind their own explicit D-COMP and layered-Aeon witnesses.

    seed_material = (
        SEED_DOMAIN
        + source_domain
        + origin.encode("utf-8")
        + b"\x00"
        + resolution.encode("utf-8")
        + b"\x00"
        + b"CONTINUATION-ROOT\x00"
        + _encode_uint(source_size)
        + salt.to_bytes(8, "big")
        + source_hash
    )
    return alqc_digest(seed_material, domain=SEED_DOMAIN)

def _validate_seed(seed: bytes) -> bytes:
    if not isinstance(seed, bytes) or len(seed) != 32:
        raise TardiSHAError("seed must be exactly 32 bytes")
    return seed


def _validate_chunk_characters(chunk_characters: int) -> int:
    if isinstance(chunk_characters, bool) or not isinstance(chunk_characters, int) or chunk_characters < 1:
        raise TardiSHAError("chunk_characters must be a positive integer")
    return chunk_characters



COORDINATE_BLOCK_CHARACTERS = 4096
COORDINATE_WORD_BYTES = 4
_COORDINATE_WORD_RANGE = 1 << (8 * COORDINATE_WORD_BYTES)
_COORDINATE_ACCEPTANCE_LIMIT = (
    _COORDINATE_WORD_RANGE // len(ALPHABET)
) * len(ALPHABET)


def _coordinate_block(seed: bytes, block_index: int, span_characters: int = COORDINATE_BLOCK_CHARACTERS) -> str:
    """Resolve only the requested prefix within one canonical 4096-coordinate epoch boundary.

    4096 is the internal deterministic epoch size, not a requested rendering length.
    Only the coordinates required by the caller are calculated.
    """
    _validate_seed(seed)

    if isinstance(block_index, bool) or not isinstance(block_index, int) or block_index < 0:
        raise TardiSHAError("block_index must be a non-negative integer")
    if isinstance(span_characters, bool) or not isinstance(span_characters, int) or not 1 <= span_characters <= COORDINATE_BLOCK_CHARACTERS:
        raise TardiSHAError("span_characters must be an integer in [1, 4096]")

    out: list[str] = []
    rejection_round = 0
    remaining = span_characters

    while remaining > 0:
        material = (
            seed
            + _encode_uint(block_index)
            + _encode_uint(rejection_round)
        )

        body = alqc_digest_prefix(
            material,
            domain=CHAR_DOMAIN,
            canonical_length=COORDINATE_BLOCK_CHARACTERS * COORDINATE_WORD_BYTES,
            prefix_length=remaining * COORDINATE_WORD_BYTES,
        )

        for offset in range(0, len(body), COORDINATE_WORD_BYTES):
            word = int.from_bytes(
                body[offset:offset + COORDINATE_WORD_BYTES],
                "big",
            )

            if word >= _COORDINATE_ACCEPTANCE_LIMIT:
                continue

            coordinate = word % len(ALPHABET)
            out.append(ALPHABET[coordinate])

            if len(out) == span_characters:
                break

        remaining = span_characters - len(out)
        rejection_round += 1

    return "".join(out)

def char_at(seed: bytes, position: int) -> str:
    """Return one TardiSHA continuation character at an arbitrary non-negative coordinate."""
    _validate_seed(seed)
    if isinstance(position, bool) or not isinstance(position, int) or position < 0:
        raise TardiSHAError("position must be a non-negative integer")
    block_index, offset = divmod(position, COORDINATE_BLOCK_CHARACTERS)
    return _coordinate_block(seed, block_index, offset + 1)[offset]


def iter_middle_window(
    seed: bytes,
    start_coordinate: int,
    span_length: int,
    *,
    chunk_characters: int = OUTPUT_CHUNK_CHARACTERS,
) -> Iterator[str]:
    """Yield a random-access window without materializing the whole stream."""
    _validate_seed(seed)
    if isinstance(start_coordinate, bool) or not isinstance(start_coordinate, int) or start_coordinate < 0:
        raise TardiSHAError("start_coordinate must be a non-negative integer")
    width = validate_middle_length(span_length)
    _validate_chunk_characters(chunk_characters)
    if width == 0:
        return

    stop = start_coordinate + width
    cursor = start_coordinate
    pending: list[str] = []
    while cursor < stop:
        block_index, offset = divmod(cursor, COORDINATE_BLOCK_CHARACTERS)
        take = min(stop - cursor, COORDINATE_BLOCK_CHARACTERS - offset)
        block = _coordinate_block(seed, block_index, offset + take)
        pending.append(block[offset:offset + take])
        cursor += take
        joined = "".join(pending)
        while len(joined) >= chunk_characters:
            yield joined[:chunk_characters]
            joined = joined[chunk_characters:]
        pending = [joined] if joined else []
    if pending:
        yield "".join(pending)


def iter_middle(
    seed: bytes,
    middle_length: int,
    *,
    chunk_characters: int = OUTPUT_CHUNK_CHARACTERS,
    start_coordinate: int = 0,
) -> Iterator[str]:
    """Yield the canonical deterministic Synodic Magicae continuation stream."""
    yield from iter_middle_window(
        seed,
        start_coordinate,
        middle_length,
        chunk_characters=chunk_characters,
    )

def create_middle_from_fingerprint(
    *,
    source_digest: str,
    source_size: int,
    origin_glyph: str,
    resolution_glyph: str,
    middle_length: int,
    nonce: int = 0,
    source_domain: bytes = RAW_FILE_SOURCE_DOMAIN,
    start_coordinate: int = 0,
) -> str:
    seed = coordinate_seed(
        source_digest=source_digest,
        source_size=source_size,
        origin_glyph=origin_glyph,
        resolution_glyph=resolution_glyph,
        middle_length=middle_length,
        nonce=nonce,
        source_domain=source_domain,
    )
    return "".join(iter_middle_window(seed, start_coordinate, middle_length))
