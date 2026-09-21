#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

from .domus import parse_public_living_domus
from .domus_stream import living_domus_for_source
from .hashing import validate_nonce


PDF_GRIMCHAIN_MARKER = b"\n%GrimChain "


def _embedded_grimchain(path: str | Path) -> tuple[str, int, int] | None:
    target = Path(path)
    data = target.read_bytes()
    marker = data.rfind(PDF_GRIMCHAIN_MARKER)
    if marker < 0:
        return None
    start = marker + len(PDF_GRIMCHAIN_MARKER)
    raw = data[start:]
    if not raw:
        return None
    try:
        value = raw.decode("utf-8")
        parse_public_living_domus(value)
    except (UnicodeError, TypeError, ValueError):
        return None
    return value, marker, start


def pdf_embed(path: str | Path, middle: int, *, nonce: int = 0) -> str:
    target = Path(path)
    salt = validate_nonce(nonce)
    if _embedded_grimchain(target) is not None:
        raise ValueError("PDF already contains an embedded GrimChain")
    with target.open("ab") as handle:
        handle.write(PDF_GRIMCHAIN_MARKER)
    grimchain = living_domus_for_source(target, middle, kind="file", nonce=salt)
    with target.open("ab") as handle:
        handle.write(grimchain.encode("utf-8"))
    returned = living_domus_for_source(target, middle, kind="file", nonce=salt)
    if returned != grimchain:
        raise RuntimeError("PDF GrimChain did not close through Mirror return")
    return returned


def pdf_dive(path: str | Path, *, nonce: int = 0) -> tuple[str | None, str | None, str]:
    target = Path(path)
    salt = validate_nonce(nonce)
    found = _embedded_grimchain(target)
    if found is None:
        return None, None, "ZYGOTIC"
    embedded, _marker, _start = found
    middle = parse_public_living_domus(embedded).depth
    if middle is None:
        return None, embedded, "HETEROZYGOTIC"
    correct = living_domus_for_source(target, middle, kind="file", nonce=salt)
    return correct, embedded, "MONOZYGOTIC" if correct == embedded else "HETEROZYGOTIC"


def pdf_abort(path: str | Path) -> str | None:
    target = Path(path)
    found = _embedded_grimchain(target)
    if found is None:
        return None
    embedded, marker, _start = found
    target.write_bytes(target.read_bytes()[:marker])
    return embedded
