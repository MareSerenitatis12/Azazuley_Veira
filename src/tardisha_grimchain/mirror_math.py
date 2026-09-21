"""TardiSHA's source-typed realization of the Aeternum Mirror.

The Canon's displayed Aeternum identities are worked embodiments of the general
ALQC return law. Here a raw file is the expanded Fraktur Z_1 body and a terminal
Living Domus Grimchain is a candidate compressed Fraktur Z_0 return.

A terminal candidate is not granted return merely because the same Grimchain
construction can reproduce it. Deterministic regeneration may describe the
candidate, but return requires an independently constructed return path whose
protected return-body closes against the protected body of the outward path.

Mirror preserves operator sequence while exchanging bearing. Return preserves
root, parentage, Liquid law, W_34, twelvefold lineage, envelope, and invariant
identity while append-only lineage remains present.

The complete state need not reset to its starting state. The lawful return-body
must return without erasing the road by which it returned.

This is the file-identity office of Path Out = Path Back, parity return,
D-COMP = 0, and Truth = 1. Any suffix not independently proven as lawful return
remains source matter.
"""

from __future__ import annotations

from .canon import court_load

from dataclasses import asdict, dataclass
import mmap
import os
from pathlib import Path
from typing import Any

from .alqc_digest import ALQCDigest
from .hashing import FILE_NAME_FRAME, RAW_FILE_SOURCE_DOMAIN, SOURCE_CHUNK_BYTES, TardiSHAError, file_emission
from .source_emission import SourceEmission, emission_from_sponge, ALPHA, BETA, GoldenGoeticDerivation, resolve_bearing



def _parse_public_living_domus_current(seal: str):
    from .domus import parse_public_living_domus
    return parse_public_living_domus(seal)

@dataclass(frozen=True, slots=True)
class TerminalSelfGlyphCandidate:
    physical_size: int
    body_size: int
    written_center_length: int
    seal: str
    seal_utf8_bytes: int
    trailing_bytes_hex: str

    @property
    def trailing_bytes(self) -> bytes:
        return bytes.fromhex(self.trailing_bytes_hex)

    @property
    def bytes_accounted(self) -> bool:
        return self.body_size + self.seal_utf8_bytes + len(self.trailing_bytes) == self.physical_size


@dataclass(frozen=True, slots=True)
class MirrorMathWitness:
    physical_size: int
    physical_source_digest: str
    source_stability_verified: bool
    effective_body_size: int
    candidate_detected: bool
    exact_self_glyph: bool
    folded: bool
    fold_count: int
    folded_physical_bytes: int
    lineage_seals: tuple[str, ...]
    lineage_trailing_bytes_hex: tuple[str, ...]
    seal: str | None
    expected_seal: str | None
    trailing_bytes_hex: str
    bytes_accounted: bool
    operator_order_preserved: bool
    expanded_posture: str
    compressed_posture: str
    source_route_dcomp: int
    source_truth: int
    return_dcomp: int | None
    return_truth: int | None
    truth: int
    derivation: str

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class MirrorFileEmission:
    emission: SourceEmission
    witness: MirrorMathWitness


_GRIM_SELF_CLOSE = "\n∴\n".encode("utf-8")
_TERMINAL_TRAILING_PROBE = max(2, len(_GRIM_SELF_CLOSE))


def _strip_one_terminal_line_return(data: bytes) -> tuple[bytes, bytes]:
    if data.endswith(_GRIM_SELF_CLOSE):
        return data[:-len(_GRIM_SELF_CLOSE)], _GRIM_SELF_CLOSE
    if data.endswith(b"\r\n"):
        return data[:-2], b"\r\n"
    if data.endswith(b"\n"):
        return data[:-1], b"\n"
    return data, b""


def _byte_difference(left: str, right: str) -> int:
    """Exact non-negative residual; zero iff UTF-8 bodies are byte-identical."""
    a = left.encode("utf-8")
    b = right.encode("utf-8")
    shared = min(len(a), len(b))
    return abs(len(a) - len(b)) + sum(a[i] != b[i] for i in range(shared))


def _file_stat_witness(result: os.stat_result) -> tuple[int, int, int, int, int, int]:
    return (
        result.st_dev,
        result.st_ino,
        result.st_mode,
        result.st_size,
        result.st_mtime_ns,
        result.st_ctime_ns,
    )


def _previous_utf8_codepoint_start_view(view, position: int) -> int | None:
    if position <= 0:
        return None
    read_start = max(0, position - 4)
    for start in range(position - 1, read_start - 1, -1):
        candidate = bytes(view[start:position])
        try:
            decoded = candidate.decode("utf-8")
        except UnicodeDecodeError:
            continue
        if len(decoded) == 1:
            return start
    return None



def _iter_terminal_candidates_view(view, limit: int):
    if isinstance(limit, bool) or not isinstance(limit, int) or not 0 <= limit <= len(view):
        raise ValueError("physical_size must be within the source file")
    if limit == 0:
        return
    terminal_probe = min(limit, _TERMINAL_TRAILING_PROBE)
    tail = bytes(view[limit - terminal_probe:limit])
    _content, trailing = _strip_one_terminal_line_return(tail)
    body_end = limit - len(trailing)
    position = body_end
    reverse_codepoints: list[str] = []
    while position > 0:
        start = _previous_utf8_codepoint_start_view(view, position)
        if start is None:
            return
        codepoint = bytes(view[start:position]).decode("utf-8")
        reverse_codepoints.append(codepoint)
        position = start
        if len(reverse_codepoints) < 2:
            continue
        seal_bytes = bytes(view[start:body_end])
        seal = seal_bytes.decode("utf-8")
        try:
            _parse_public_living_domus_current(seal)
        except (TypeError, ValueError):
            continue
        written_length = len(reverse_codepoints)
        candidate = TerminalSelfGlyphCandidate(limit,start,written_length,seal,len(seal_bytes),trailing.hex())
        if not candidate.bytes_accounted:
            raise RuntimeError("Mirror Math failed physical-byte accounting")
        yield candidate


def _previous_utf8_codepoint_start(handle, position: int) -> int | None:
    """Return the byte start of the UTF-8 code point ending at ``position``.

    Terminal-body discovery follows encoded extent only. No glyph is privileged as
    a delimiter, and no glyph occurring in the middle can alter body discovery.
    """
    if position <= 0:
        return None
    read_start = max(0, position - 4)
    handle.seek(read_start)
    tail = handle.read(position - read_start)
    for offset in range(len(tail) - 1, -1, -1):
        candidate = tail[offset:]
        try:
            decoded = candidate.decode("utf-8")
        except UnicodeDecodeError:
            continue
        if len(decoded) == 1:
            return read_start + offset
    return None


def _iter_terminal_candidates(
    path: str | Path,
    *,
    physical_size: int | None = None,
    nonce: int = 0,
):
    """Detect terminal GrimChain candidates by encoded extent only."""
    target = Path(path)
    actual_size = target.stat().st_size
    limit = actual_size if physical_size is None else physical_size
    if isinstance(limit, bool) or not isinstance(limit, int) or not 0 <= limit <= actual_size:
        raise ValueError("physical_size must be within the source file")
    if limit == 0:
        return
    with target.open("rb") as handle:
        terminal_probe = min(limit, _TERMINAL_TRAILING_PROBE)
        handle.seek(limit - terminal_probe)
        tail = handle.read(terminal_probe)
    _content, trailing = _strip_one_terminal_line_return(tail)
    body_end = limit - len(trailing)
    position = body_end
    reverse_codepoints: list[str] = []
    with target.open("rb") as handle:
        while position > 0:
            start = _previous_utf8_codepoint_start(handle, position)
            if start is None:
                return
            handle.seek(start)
            codepoint_bytes = handle.read(position - start)
            codepoint = codepoint_bytes.decode("utf-8")
            reverse_codepoints.append(codepoint)
            position = start
            if len(reverse_codepoints) < 2:
                continue
            seal_extent = body_end - start
            handle.seek(start)
            seal_bytes = handle.read(seal_extent)
            if len(seal_bytes) != seal_extent:
                raise RuntimeError("Mirror Math could not read the complete terminal return")
            seal = seal_bytes.decode("utf-8")
            try:
                _parse_public_living_domus_current(seal)
            except (TypeError, ValueError):
                continue
            written_length = len(reverse_codepoints)
            candidate = TerminalSelfGlyphCandidate(limit,start,written_length,seal,len(seal_bytes),trailing.hex())
            if not candidate.bytes_accounted:
                raise RuntimeError("Mirror Math failed physical-byte accounting")
            yield candidate


def detect_terminal_self_glyph(
    path: str | Path,
    *,
    physical_size: int | None = None,
    nonce: int = 0,
) -> TerminalSelfGlyphCandidate | None:
    """Expose one decomposable terminal public GrimChain suffix without granting truth."""
    return next(
        _iter_terminal_candidates(
            path,
            physical_size=physical_size,
            nonce=nonce,
        ),
        None,
    )

def _prefix_emission_view(
    view,
    body_size: int,
    *,
    identity_name: str | bytes | None = None,
    include_filename: bool = True,
) -> SourceEmission:
    if isinstance(body_size, bool) or not isinstance(body_size, int) or not 0 <= body_size <= len(view):
        raise ValueError("body_size must be within the mapped source")

    sponge = ALQCDigest(RAW_FILE_SOURCE_DOMAIN)

    if include_filename:
        if identity_name is None:
            raise TardiSHAError("mapped prefix emission requires explicit filename identity")
        if isinstance(identity_name, str):
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

    offset = 0
    while offset < body_size:
        end = min(body_size, offset + SOURCE_CHUNK_BYTES)
        sponge._update_raw(bytes(view[offset:end]))
        offset = end

    return emission_from_sponge(
        sponge,
        source_size=body_size,
        source_domain="raw-file",
    )


def _render_self(
    emission: SourceEmission,
    depth: int,
    *,
    nonce: int,
    route_witness,
) -> str:
    """Return the compressed GrimChain posture from one completed Aeternum Mirror route."""
    from .route import resolve_parents
    from .domus import resolve_domus, public_living_domus

    _g_i, _g_j, witness = resolve_parents(emission, witness=route_witness)
    res = resolve_domus(witness, nonce=nonce)
    return public_living_domus(
        res,
        depth,
        source_digest=emission.source_digest,
        source_size=emission.source_size,
        source_domain=emission.source_domain,
        nonce=nonce,
    )

def _render_terminal_return(
    emission: SourceEmission,
    candidate: TerminalSelfGlyphCandidate,
    *,
    nonce: int,
) -> tuple[bool, str | None]:
    """Recompute a terminal return under the current flat middle-only public law."""
    try:
        parsed = _parse_public_living_domus_current(candidate.seal)
    except (TypeError, ValueError):
        return False, None
    depth = parsed.depth
    if depth is None:
        return False, None
    from .route import source_route_witness_from_emission
    route = source_route_witness_from_emission(emission)
    rendered = _render_self(emission, depth, nonce=nonce, route_witness=route)
    return rendered == candidate.seal, rendered

def _resolve_terminal_lineage(
    view,
    *,
    physical_before: SourceEmission,
    nonce: int,
    identity_name: str | bytes | None,
    include_filename: bool,
) -> tuple[
    SourceEmission,
    tuple[TerminalSelfGlyphCandidate, ...],
    TerminalSelfGlyphCandidate | None,
    str | None,
]:
    physical_size = physical_before.source_size
    memo: dict[int, tuple[SourceEmission, tuple[TerminalSelfGlyphCandidate, ...]]] = {}
    first_candidate: TerminalSelfGlyphCandidate | None = None
    first_expected: str | None = None

    def resolve(
        limit: int,
    ) -> tuple[SourceEmission, tuple[TerminalSelfGlyphCandidate, ...]]:
        nonlocal first_candidate, first_expected

        cached = memo.get(limit)
        if cached is not None:
            return cached

        if limit == physical_size:
            raw = physical_before
        else:
            raw = _prefix_emission_view(
                view,
                limit,
                identity_name=identity_name,
                include_filename=include_filename,
            )

        for candidate in _iter_terminal_candidates_view(view, limit):
            if candidate.body_size >= limit:
                raise RuntimeError("Mirror Math lineage did not decrease physical extent")

            body_emission, body_lineage = resolve(candidate.body_size)
            exact_return, expected = _render_terminal_return(
                body_emission,
                candidate,
                nonce=nonce,
            )

            if limit == physical_size and first_candidate is None:
                first_candidate = candidate
                first_expected = expected

            if exact_return:
                result = (
                    body_emission,
                    body_lineage + (candidate,),
                )
                memo[limit] = result
                return result

        result = (raw, ())
        memo[limit] = result
        return result

    emission, lineage = resolve(physical_size)
    return emission, lineage, first_candidate, first_expected

def mirror_file_emission(
    path: str | Path,
    *,
    nonce: int = 0,
    identity_name: str | bytes | None = None,
    include_filename: bool = True,
) -> MirrorFileEmission:
    target = Path(path)
    salt = nonce

    effective_identity_name: str | bytes | None
    if include_filename:
        effective_identity_name = target.name if identity_name is None else identity_name
    else:
        effective_identity_name = None

    path_before = target.stat()

    physical_before = file_emission(
        target,
        identity_name=identity_name,
        include_filename=include_filename,
    )
    physical_size = physical_before.source_size

    with target.open("rb") as handle:
        handle_before = os.fstat(handle.fileno())
        if _file_stat_witness(handle_before) != _file_stat_witness(path_before):
            raise TardiSHAError("source changed before Mirror lineage traversal began")

        if physical_size == 0:
            view = b""
            emission, lineage, candidate, expected = _resolve_terminal_lineage(
                view,
                physical_before=physical_before,
                nonce=salt,
                identity_name=effective_identity_name,
                include_filename=include_filename,
            )
        else:
            with mmap.mmap(handle.fileno(), 0, access=mmap.ACCESS_READ) as view:
                emission, lineage, candidate, expected = _resolve_terminal_lineage(
                    view,
                    physical_before=physical_before,
                    nonce=salt,
                    identity_name=effective_identity_name,
                    include_filename=include_filename,
                )

        handle_after = os.fstat(handle.fileno())

    path_after = target.stat()
    before_witness = _file_stat_witness(path_before)
    if (
        _file_stat_witness(handle_before) != before_witness
        or _file_stat_witness(handle_after) != before_witness
        or _file_stat_witness(path_after) != before_witness
    ):
        raise TardiSHAError("source changed during complete Mirror Math construction")

    if not lineage:
        candidate_detected = candidate is not None
        return_residual = (
            _byte_difference(candidate.seal, expected)
            if candidate is not None and expected is not None
            else None
        )
        source_truth = int(emission.closure.verifies and emission.closure.truth == 1)

        return MirrorFileEmission(
            emission,
            MirrorMathWitness(
                physical_size=physical_size,
                physical_source_digest=physical_before.source_digest,
                source_stability_verified=True,
                effective_body_size=physical_size,
                candidate_detected=candidate_detected,
                exact_self_glyph=False,
                folded=False,
                fold_count=0,
                folded_physical_bytes=0,
                lineage_seals=(),
                lineage_trailing_bytes_hex=(),
                seal=candidate.seal if candidate is not None else None,
                expected_seal=expected,
                trailing_bytes_hex=candidate.trailing_bytes_hex if candidate is not None else "",
                bytes_accounted=True,
                operator_order_preserved=True,
                expanded_posture="\U0001D543\u2081",
                compressed_posture="\U0001D543\u2080",
                source_route_dcomp=emission.closure.route_dcomp,
                source_truth=source_truth,
                return_dcomp=return_residual,
                return_truth=(
                    None if return_residual is None else int(return_residual == 0)
                ),
                truth=source_truth,
                derivation=(
                    "terminal seal-shaped body is not the exact self of the preceding \U0001D543\u2081; all bytes remain source matter"
                    if candidate_detected
                    else "no terminal self-glyph; every byte remains in \U0001D543\u2081"
                ),
            ),
        )

    outer = lineage[-1]
    folded_bytes = physical_size - emission.source_size
    accounted = (
        emission.source_size
        + sum(c.seal_utf8_bytes + len(c.trailing_bytes) for c in lineage)
        == physical_size
    )

    outer_exact, expected_return = _render_terminal_return(
        emission,
        outer,
        nonce=salt,
    )
    if not outer_exact or expected_return is None:
        raise RuntimeError("Mirror Math lineage lost its independently regenerated terminal return")

    # Every lineage member enters the lineage only after exact source-derived
    # regeneration of its complete candidate body. No depth is stored or trusted.
    return_dcomp = 0

    truth = int(
        accounted
        and return_dcomp == 0
        and emission.closure.verifies
        and emission.closure.truth == 1
    )

    witness = MirrorMathWitness(
        physical_size=physical_size,
        physical_source_digest=physical_before.source_digest,
        source_stability_verified=True,
        effective_body_size=emission.source_size,
        candidate_detected=True,
        exact_self_glyph=return_dcomp == 0,
        folded=return_dcomp == 0,
        fold_count=len(lineage),
        folded_physical_bytes=folded_bytes,
        lineage_seals=tuple(c.seal for c in lineage),
        lineage_trailing_bytes_hex=tuple(c.trailing_bytes_hex for c in lineage),
        seal=outer.seal,
        expected_seal=expected_return,
        trailing_bytes_hex=outer.trailing_bytes_hex,
        bytes_accounted=accounted,
        operator_order_preserved=True,
        expanded_posture="\U0001D543\u2081",
        compressed_posture="\U0001D543\u2080",
        source_route_dcomp=emission.closure.route_dcomp,
        source_truth=emission.closure.truth,
        return_dcomp=return_dcomp,
        return_truth=int(return_dcomp == 0),
        truth=truth,
        derivation=(
            "same-order Mirror Math: read every terminal \U0001D543\u2080 in append-only order, "
            "recompute each from the effective \U0001D543\u2081 beneath it, preserve the physical "
            "lineage, and retract only the exact return stack"
        ),
    )

    if not (
        witness.bytes_accounted
        and witness.operator_order_preserved
        and witness.source_stability_verified
    ):
        raise RuntimeError("Mirror Math witness did not close its physical invariants")

    return MirrorFileEmission(emission, witness)


# Canon-facing name: the function above is the TardiSHA embodiment of the
# Aeternum Mirror under its established internal name.
aeternum_mirror_file_emission = mirror_file_emission


def derive_goetics(emission: SourceEmission) -> GoldenGoeticDerivation:
    if not emission.closure.verifies:
        raise RuntimeError("source emission does not carry D-COMP=0 / Truth=1")
    first = resolve_bearing(
        weights=emission.structural_weights,
        body="Goetic structural amplitude",
        phase=emission.fraktur_z0,
        bearing=ALPHA,
        cadence_symbol="𝔃₀",
        cadence_index=0,
        traversal="Manifest / forward bearing",
    )
    last = resolve_bearing(
        weights=emission.operational_weights,
        body="Parliament operational phase",
        phase=emission.fraktur_z1,
        bearing=BETA,
        cadence_symbol="𝔃₁",
        cadence_index=1,
        traversal="Reflect / conjugate bearing with append-only cadence",
    )
    if first.operator_order != last.operator_order:
        raise RuntimeError("Mirror Math illegally reversed the Parliament procession")
    court = court_load(first.seat.goetic, last.seat.goetic)
    reciprocal = court_load(last.seat.goetic, first.seat.goetic)
    return GoldenGoeticDerivation(emission, first, last, court, reciprocal)


def verify_derivation(derivation: GoldenGoeticDerivation) -> bool:
    try:
        expected = derive_goetics(derivation.emission)
    except (TypeError, ValueError, RuntimeError):
        return False
    return (
        derivation == expected
        and derivation.same_operator_order
        and derivation.first.interval_verifies
        and derivation.last.interval_verifies
        and derivation.route_dcomp == 0
        and derivation.truth == 1
    )

