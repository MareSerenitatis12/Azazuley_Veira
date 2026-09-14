"""Reversible content-addressed TardiSHA archive mode."""
from __future__ import annotations

import json
import os
import re
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path

from .alqc_digest import alqc_hexdigest
from .hashing import SOURCE_CHUNK_BYTES, TardiSHAError, file_emission
from .node import TardiSHANode
from .route import (
    SourceRouteWitness,
    parents_t,
    resolve_parents,
    source_route_witness_from_emission,
    verify_source,
)

ARCHIVE_ROOT_DOMAIN = b"TARDISHA:ARCHIVE-ROOT\x00"
ARCHIVE_CHUNK_DOMAIN = b"TARDISHA:ARCHIVE-CHUNK\x00"


def _atomic_write_bytes(path: Path, body: bytes) -> None:
    """Commit one persistent archive body without leaving temporary state."""
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".part", dir=path.parent)
    temp = Path(tmp_name)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(body)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp, path)
    except Exception:
        temp.unlink(missing_ok=True)
        raise
_CHUNK_DIGEST_RE = re.compile(r"^[0-9a-f]{64}$")


def _validate_chunk(chunk: "ArchiveChunk", *, expected_index: int | None = None) -> None:
    if isinstance(chunk.index, bool) or not isinstance(chunk.index, int) or chunk.index < 0:
        raise TardiSHAError("archive chunk index must be a non-negative integer")
    if expected_index is not None and chunk.index != expected_index:
        raise TardiSHAError("archive chunk indices must be contiguous and ordered")
    if isinstance(chunk.offset, bool) or not isinstance(chunk.offset, int) or chunk.offset < 0:
        raise TardiSHAError("archive chunk offset must be a non-negative integer")
    if isinstance(chunk.size, bool) or not isinstance(chunk.size, int) or chunk.size < 1:
        raise TardiSHAError("archive chunk size must be a positive integer")
    if not isinstance(chunk.digest, str) or not _CHUNK_DIGEST_RE.fullmatch(chunk.digest):
        raise TardiSHAError("archive chunk digest must be 64 lowercase hexadecimal characters")


@dataclass(frozen=True, slots=True)
class ArchiveChunk:
    index: int
    offset: int
    size: int
    digest: str


@dataclass(frozen=True, slots=True)
class TardiSHAArchiveManifest:
    archive_root: str
    source_name: str
    source_digest: str
    source_size: int
    physical_size: int
    chunk_size: int
    chunks: tuple[ArchiveChunk, ...]
    node: TardiSHANode

    def __post_init__(self) -> None:
        if self.node.mode != "ARCHIVE_REVERSIBLE":
            raise TardiSHAError("archive manifest requires an ARCHIVE_REVERSIBLE node")
        if self.node.archive_root != self.archive_root:
            raise TardiSHAError("archive manifest root must equal the node archive_root")
        if self.node.source_domain != "raw-file":
            raise TardiSHAError("archive manifest requires a raw-file source proof")
        try:
            resolve_parents(
                self.node.route_witness.emission, witness=self.node.route_witness
            )
        except (TypeError, ValueError, RuntimeError) as exc:
            raise TardiSHAError("archive manifest route witness does not close") from exc

    def as_dict(self) -> dict[str, object]:
        return {
             "archive_root": self.archive_root,
             "source_name": self.source_name,
             "source_size": self.source_size,
             "physical_size": self.physical_size,
             "chunk_size": self.chunk_size,
             "chunks": [asdict(chunk) for chunk in self.chunks],
        }



def _node_root_body(
    *,
    source_digest: str,
    source_size: int,
    origin_glyph: str,
    resolution_glyph: str,
    nonce: int,
    source_domain: str,
    route_witness: SourceRouteWitness,
) -> dict[str, object]:
    if source_domain != "raw-file":
        raise TardiSHAError("archive root body requires the raw-file source domain")
    if not verify_source(route_witness.emission, route_witness):
        raise TardiSHAError("archive root body requires exact return-bearing source proof")
    return {
        "source_digest": source_digest,
        "source_size": source_size,
        "origin_glyph": origin_glyph,
        "resolution_glyph": resolution_glyph,
        "nonce": nonce,
        "source_domain": source_domain,
        "route_witness": route_witness.as_dict(),
    }


def _node_root_body_from_node(node: TardiSHANode) -> dict[str, object]:
    return _node_root_body(
        source_digest=node.source_digest,
        source_size=node.source_size,
        origin_glyph=node.origin_glyph,
        resolution_glyph=node.resolution_glyph,
        nonce=node.nonce,
        source_domain=node.source_domain,
        route_witness=node.route_witness,
    )


def _root_payload(
    source_name: str,
    source_digest: str,
    source_size: int,
    physical_size: int,
    chunk_size: int,
    chunks: tuple[ArchiveChunk, ...],
    node_root_body: dict[str, object],
) -> bytes:
    return json.dumps(
        {
            "source_name": source_name,
            "source_digest": source_digest,
            "source_size": source_size,
            "physical_size": physical_size,
            "chunk_size": chunk_size,
            "chunks": [asdict(chunk) for chunk in chunks],
            "node": node_root_body,
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")

def _archive_root(
    source_name: str,
    source_digest: str,
    source_size: int,
    physical_size: int,
    chunk_size: int,
    chunks: tuple[ArchiveChunk, ...],
    node_root_body: dict[str, object],
) -> str:
    return alqc_hexdigest(
        _root_payload(
            source_name,
            source_digest,
            source_size,
            physical_size,
            chunk_size,
            chunks,
            node_root_body,
        ),
        domain=ARCHIVE_ROOT_DOMAIN,
    )

def _chunk_digest(data: bytes) -> str:
    return alqc_hexdigest(data, domain=ARCHIVE_CHUNK_DOMAIN)


def create_archive(
    source_path: str | Path,
    archive_dir: str | Path,
    *,
    chunk_size: int = SOURCE_CHUNK_BYTES,
) -> TardiSHAArchiveManifest:
    if isinstance(chunk_size, bool) or not isinstance(chunk_size, int) or chunk_size < 1:
        raise TardiSHAError("chunk_size must be a positive integer")
    source = Path(source_path)
    target = Path(archive_dir)
    chunks_dir = target / "chunks"
    chunks_dir.mkdir(parents=True, exist_ok=True)

    source_emission = file_emission(source)
    route_witness = source_route_witness_from_emission(source_emission)
    source_name = source.name

    chunks: list[ArchiveChunk] = []
    offset = 0
    index = 0

    with source.open("rb") as handle:
        while True:
            data = handle.read(chunk_size)
            if not data:
                break

            chunk_digest = _chunk_digest(data)
            chunk_path = chunks_dir / f"{chunk_digest}.bin"

            if chunk_path.exists():
                existing = chunk_path.read_bytes()
                if existing != data or _chunk_digest(existing) != chunk_digest:
                    raise TardiSHAError(
                        f"archive chunk {chunk_digest} already exists but its content is not true"
                    )
            else:
                _atomic_write_bytes(chunk_path, data)

            chunks.append(
                ArchiveChunk(
                    index=index,
                    offset=offset,
                    size=len(data),
                    digest=chunk_digest,
                )
            )
            offset += len(data)
            index += 1


    source_digest = source_emission.source_digest
    source_size = source_emission.source_size
    physical_size = offset

    if source_emission.source_size != physical_size:
        raise TardiSHAError("archive physical extent contradicts source emission")

    chunk_tuple = tuple(chunks)
    origin_glyph, resolution_glyph = parents_t(route_witness)
    proof_body = _node_root_body(
        source_digest=source_digest,
        source_size=source_size,
        origin_glyph=origin_glyph,
        resolution_glyph=resolution_glyph,
        nonce=0,
        source_domain="raw-file",
        route_witness=route_witness,
    )
    _verify_source_from_chunks(
        chunks_dir,
        chunk_tuple,
        route_witness,
        source_name=source_name,
    )

    root = _archive_root(
        source_name,
        source_digest,
        source_size,
        physical_size,
        chunk_size,
        chunk_tuple,
        proof_body,
    )

    node = TardiSHANode(
        mode="ARCHIVE_REVERSIBLE",
        source_digest=source_digest,
        source_size=source_size,
        origin_glyph=origin_glyph,
        resolution_glyph=resolution_glyph,
        nonce=0,
        source_domain="raw-file",
        route_witness=route_witness,
        archive_root=root,
        finite_extent=None,
    )
    if _node_root_body_from_node(node) != proof_body:
        raise TardiSHAError("source changed between archive-root proof and final archive node")
    manifest = TardiSHAArchiveManifest(
        root,
        source_name,
        source_digest,
        source_size,
        physical_size,
        chunk_size,
        chunk_tuple,
        node,
    )

    manifest_bytes = (json.dumps(manifest.as_dict(), ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    _atomic_write_bytes(target / "manifest.json", manifest_bytes)
    return manifest

def read_archive_manifest(manifest_path: str | Path) -> TardiSHAArchiveManifest:
    data = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TardiSHAError("archive manifest must be a JSON object")
    source_name = data.get("source_name")
    if not isinstance(source_name, str) or not source_name:
        raise TardiSHAError("archive source_name must be a non-empty filename")
    if Path(source_name).name != source_name:
        raise TardiSHAError("archive source_name must be a basename")
    source_size = data.get("source_size")
    physical_size = data.get("physical_size")
    chunk_size = data.get("chunk_size")

    if isinstance(source_size, bool) or not isinstance(source_size, int) or source_size < 0:
        raise TardiSHAError("archive source_size must be a non-negative integer")

    if isinstance(physical_size, bool) or not isinstance(physical_size, int) or physical_size < 0:
        raise TardiSHAError("archive physical_size must be a non-negative integer")

    if isinstance(chunk_size, bool) or not isinstance(chunk_size, int) or chunk_size < 1:
        raise TardiSHAError("archive chunk_size must be a positive integer")
    archive_root = data.get("archive_root")
    if not isinstance(archive_root, str) or not _CHUNK_DIGEST_RE.fullmatch(archive_root):
        raise TardiSHAError("archive archive_root must be 64 lowercase hexadecimal characters")
    raw_chunks = data.get("chunks")
    if not isinstance(raw_chunks, list):
        raise TardiSHAError("archive chunks must be a list")
    try:
        chunks = tuple(ArchiveChunk(**chunk) for chunk in raw_chunks)
    except (TypeError, KeyError) as exc:
        raise TardiSHAError("archive chunk body is malformed") from exc
    expected_count = (
        0
        if physical_size == 0
        else (physical_size + chunk_size - 1) // chunk_size
    )
    if len(chunks) != expected_count:
        raise TardiSHAError("archive chunk count contradicts physical_size and chunk_size")
    expected_offset = 0
    for expected_index, chunk in enumerate(chunks):
        _validate_chunk(chunk, expected_index=expected_index)
        if chunk.offset != expected_offset:
            raise TardiSHAError("archive chunk offsets must be contiguous")
        if chunk.size > chunk_size:
            raise TardiSHAError("archive chunk size exceeds declared chunk_size")
        if expected_index < len(chunks) - 1 and chunk.size != chunk_size:
            raise TardiSHAError("every non-terminal archive chunk must equal chunk_size")
        expected_offset += chunk.size
    if expected_offset != physical_size:
        raise TardiSHAError("archive chunk sizes do not equal physical_size")

    chunks_dir = Path(manifest_path).resolve().parent / "chunks"
    reconstruction = Path(manifest_path).resolve().parent / f".{source_name}.archive-read.part"
    try:
        with reconstruction.open("wb") as out:
            for chunk in chunks:
                chunk_data = (chunks_dir / f"{chunk.digest}.bin").read_bytes()
                if len(chunk_data) != chunk.size or _chunk_digest(chunk_data) != chunk.digest:
                    raise TardiSHAError(f"archive chunk {chunk.index} failed verification")
                out.write(chunk_data)
            out.flush()
            os.fsync(out.fileno())

        emission = file_emission(reconstruction, identity_name=source_name)
        route_witness = source_route_witness_from_emission(emission)
        origin, resolution = parents_t(route_witness)
        node = TardiSHANode(
            mode="ARCHIVE_REVERSIBLE",
            source_digest=emission.source_digest,
            source_size=emission.source_size,
            origin_glyph=origin,
            resolution_glyph=resolution,
            nonce=0,
            source_domain="raw-file",
            route_witness=route_witness,
            archive_root=archive_root,
            finite_extent=None,
        )
    finally:
        reconstruction.unlink(missing_ok=True)

    if emission.source_size != source_size:
        raise TardiSHAError("archive source_size does not match reconstructed source")
    root = _archive_root(
        source_name,
        emission.source_digest,
        source_size,
        physical_size,
        data["chunk_size"],
        chunks,
        _node_root_body_from_node(node),
    )
    if root != archive_root or node.archive_root != root:
        raise TardiSHAError("archive manifest root mismatch")
    return TardiSHAArchiveManifest(
        root,
        source_name,
        emission.source_digest,
        source_size,
        physical_size,
        data["chunk_size"],
        chunks,
        node,
    )


def _verify_source_from_chunks(
    chunks_dir: Path,
    chunks: tuple[ArchiveChunk, ...],
    route_witness: SourceRouteWitness,
    *,
    source_name: str,
) -> None:
    reconstruction = chunks_dir.parent / f".{source_name}.verify.part"

    try:
        with reconstruction.open("wb") as out:
            for chunk in chunks:
                data = (chunks_dir / f"{chunk.digest}.bin").read_bytes()

                if len(data) != chunk.size or _chunk_digest(data) != chunk.digest:
                    raise TardiSHAError(
                        f"archive chunk {chunk.index} failed verification"
                    )

                out.write(data)

            out.flush()
            os.fsync(out.fileno())

        emission = file_emission(
            reconstruction,
            identity_name=source_name,
        )

        if not verify_source(emission, route_witness):
            raise TardiSHAError(
                "archive chunk content does not reproduce the stored source route witness"
            )

    finally:
        reconstruction.unlink(missing_ok=True)

def restore_archive(
    manifest_path: str | Path,
    archive_dir: str | Path,
    output_path: str | Path,
) -> Path:
    manifest = read_archive_manifest(manifest_path)
    target = Path(output_path)

    if target.name != manifest.source_name:
        raise TardiSHAError(
            "archive restore basename must equal the archived source_name"
        )

    target.parent.mkdir(parents=True, exist_ok=True)
    temp = target.with_name(f".{target.name}.part")
    chunks_dir = Path(archive_dir) / "chunks"

    try:
        with temp.open("wb") as out:
            for chunk in manifest.chunks:
                data = (chunks_dir / f"{chunk.digest}.bin").read_bytes()

                if len(data) != chunk.size or _chunk_digest(data) != chunk.digest:
                    raise TardiSHAError(
                        f"archive chunk {chunk.index} failed verification"
                    )

                out.write(data)

            out.flush()
            os.fsync(out.fileno())

        if temp.stat().st_size != manifest.physical_size:
            raise TardiSHAError(
                "restored archive physical extent does not match archive witness"
            )

        restored_emission = file_emission(
            temp,
            identity_name=manifest.source_name,
        )

        if (
            restored_emission.source_digest != manifest.source_digest
            or restored_emission.source_size != manifest.source_size
            or not verify_source(
                restored_emission,
                manifest.node.route_witness,
            )
        ):
            raise TardiSHAError(
                "restored archive source route verification failed"
            )

        os.replace(temp, target)
        return target

    except Exception:
        temp.unlink(missing_ok=True)
        raise
