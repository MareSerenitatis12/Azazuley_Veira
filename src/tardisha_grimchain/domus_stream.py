"""Bounded-memory streaming for the visible Court-rooted Domus Aeon.

The center is the Shadow Locus `⛎` at depth zero. Depth one is the Triple Horned God
`☽᳀☾`. Greater positive depths expose exactly their generated Synodic Magicae coordinates.
Their seed is derived through the governing Court C and alternating Court D, Infinite Yes,
and Sacred No. No Goetic boundary is reused as a Domus stream coordinate.

Vāhana means vehicle or carrier in Sanskrit. Here Vāhana is the invocation-local
medium through which raw data and completed witnesses travel on their way to becoming
permanent history. It is temporary working state, never persistent cache or saved state.
"""
from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import Literal

from .hashing import (
    iter_middle,
    TardiSHAError,
    directory_emission,
    file_emission,
    validate_nonce,
    validate_middle_length,
    RAW_FILE_SOURCE_DOMAIN,
    DIRECTORY_SOURCE_DOMAIN,
)
from .route import SourceRouteWitness, source_route_witness_from_emission
from .source_emission import SourceEmission
from .mirror_math import _render_self
from .domus import (
    resolve_domus,
    domus_center_seed,
    ZERO_MIDDLE_GLYPH,
    TRIPARTITE_AXIOMYR,
)

Kind = Literal["file", "directory"]



def _validate_kind(kind: Kind) -> Kind:
    if kind not in ("file", "directory"):
        raise TardiSHAError("kind must be exactly 'file' or 'directory'")
    return kind


def _fingerprint(
    source: Path, kind: Kind, *, identity_name: str | bytes | None = None,
    include_filename: bool = True,
) -> tuple[SourceEmission, bytes, SourceRouteWitness]:
    source_kind = _validate_kind(kind)
    if source_kind == "file":
        emission = file_emission(source, identity_name=identity_name, include_filename=include_filename)
        return emission, RAW_FILE_SOURCE_DOMAIN, source_route_witness_from_emission(emission)
    emission, _entries = directory_emission(source)
    return emission, DIRECTORY_SOURCE_DOMAIN, source_route_witness_from_emission(emission)



def living_domus_from_emission(
    emission: SourceEmission,
    middle: int,
    *,
    nonce: int = 0,
    route_witness: SourceRouteWitness,
) -> str:
    """Render the canonical GrimChain from an already witnessed raw-file emission."""
    salt = validate_nonce(nonce)
    width = validate_middle_length(middle)
    if emission.source_domain != "raw-file":
        raise ValueError("living_domus_from_emission requires a raw-file emission")
    return _render_self(
        emission, width, nonce=salt, route_witness=route_witness
    )



def file_domus_record(
    source: str | Path, middle: int, *, nonce: int = 0,
    identity_name: str | bytes | None = None, include_filename: bool = True,
) -> tuple[str, SourceEmission, SourceRouteWitness]:
    """Read one file, return its canonical GrimChain plus complete witnesses."""
    salt = validate_nonce(nonce)
    emission, _domain, witness = _fingerprint(
        Path(source), "file", identity_name=identity_name,
        include_filename=include_filename,
    )
    seal = living_domus_from_emission(
        emission, middle, nonce=salt, route_witness=witness
    )
    return seal, emission, witness


def living_domus_for_source(
    source: Path, middle: int, *, kind: Kind, nonce: int = 0,
    identity_name: str | bytes | None = None, include_filename: bool = True,
) -> str:
    """In-memory canonical GrimChain for a file or directory (bounded to small middle)."""
    salt = validate_nonce(nonce)
    source_kind = _validate_kind(kind)
    if source_kind == "file":
        seal, _emission, _witness = file_domus_record(
            source, middle, nonce=salt, identity_name=identity_name,
            include_filename=include_filename,
        )
        return seal
    emission, _, witness = _fingerprint(
        source, source_kind, identity_name=identity_name,
        include_filename=include_filename,
    )
    return _render_self(
        emission, middle, nonce=salt, route_witness=witness
    )


def write_public_domus(
    source_path: str | Path,
    output_path: str | Path,
    *,
    kind: Kind,
    middle_length: int,
    nonce: int = 0,
    identity_name: str | bytes | None = None,
    include_filename: bool = True,
) -> dict:
    """Stream the canonical public Grim to disk with bounded memory and atomic commit."""
    width = validate_middle_length(middle_length)
    salt = validate_nonce(nonce)
    source_kind = _validate_kind(kind)
    source = Path(source_path)
    output = Path(output_path)
    if source.resolve() == output.resolve():
        raise TardiSHAError("source_path and output_path must be different paths")

    emission, domain, witness = _fingerprint(
        source, source_kind, identity_name=identity_name,
        include_filename=include_filename,
    )
    digest, size = emission.source_digest, emission.source_size
    res = resolve_domus(witness, nonce=salt)
    output.parent.mkdir(parents=True, exist_ok=True)
    handle = tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", newline="", delete=False,
        dir=output.parent, prefix=f".{output.name}.", suffix=".part",
    )
    temp = Path(handle.name)
    center_len = len(ZERO_MIDDLE_GLYPH) if width == 0 else (len(TRIPARTITE_AXIOMYR) if width == 1 else width)
    try:
        with handle:
            if width == 0:
                handle.write(ZERO_MIDDLE_GLYPH)
            elif width == 1:
                handle.write(TRIPARTITE_AXIOMYR)
            else:
                seed = domus_center_seed(res, source_domain=domain, nonce=salt)
                for chunk in iter_middle(seed, width):
                    handle.write(chunk)
            handle.flush()
            os.fsync(handle.fileno())
    except Exception:
        temp.unlink(missing_ok=True)
        raise


    os.replace(temp, output)
    return {
        "output": str(output),
        "governing_goetic": witness.pair[0],
        "hyperbolic_parent": witness.pair[1],
        "root_court_glyph": res.root_court.glyph,
        "alternating_court_glyph": res.alternating_court.glyph,
        "middle_length": width,
        "grim_length": center_len,
        "source_digest": digest,
        "source_size": size,
    }


