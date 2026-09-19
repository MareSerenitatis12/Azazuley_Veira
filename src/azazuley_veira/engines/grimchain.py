"""Azazuley boundary to TardiSHA GrimChain."""
from __future__ import annotations

import contextlib
import io
import sys
import os
import tempfile
from pathlib import Path

from tardisha_grimchain import grimchain as _grimchain
from tardisha_grimchain.domus import parse_public_living_domus
from tardisha_grimchain.domus_stream import file_domus_record, living_domus_from_emission


def execute(argv: list[str]) -> tuple[int, str]:
    stdout = io.StringIO()
    stderr = io.StringIO()
    old_argv = sys.argv
    sys.argv = ["grimchain", *argv]
    try:
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            try:
                result = _grimchain.main()
                code = 0 if result is None else int(result)
            except SystemExit as exc:
                code = int(exc.code or 0)
    finally:
        sys.argv = old_argv

    body = stdout.getvalue()
    error = stderr.getvalue()
    if error:
        body += ("\n" if body and not body.endswith("\n") else "") + error
    return code, body.rstrip("\n")



class GrimChainContinuationError(RuntimeError):
    """Raised when continuation of an already-witnessed GrimChain identity fails."""


class GrimChainContinuationSession:
    """Invocation-local continuation of one witnessed TardiSHA GrimChain identity."""
    def __init__(self, source: str, requested_depth: int) -> None:
        fd, tmp = tempfile.mkstemp(suffix=".grimchain")
        path = Path(tmp)
        try:
            with os.fdopen(fd, "wb") as handle:
                handle.write(source.encode("utf-8"))
                handle.flush()
                os.fsync(handle.fileno())
            chain, emission, route = file_domus_record(
                path, requested_depth, nonce=0, include_filename=False
            )
        finally:
            path.unlink(missing_ok=True)
        self.emission = emission
        self.route = route
        self.current_depth = requested_depth
        self.current_chain = chain

    def chain_at(self, depth: int) -> str:
        try:
            chain = living_domus_from_emission(
                self.emission, depth, nonce=0, route_witness=self.route
            )
        except Exception as exc:
            raise GrimChainContinuationError(str(exc)) from exc
        if depth > self.current_depth and not chain.startswith(self.current_chain):
            raise GrimChainContinuationError("GrimChain continuation changed the witnessed prefix")
        self.current_depth = depth
        self.current_chain = chain
        return chain

def string(source: str, middle: str) -> tuple[int, str]:
    """GrimChain one exact text body through TardiSHA's public callable authority."""
    try:
        middle_text = middle.strip()
        depth = int(middle_text) if middle_text else 0
        if depth < 0:
            depth = 0
        session = GrimChainContinuationSession(source, depth)
        return 0, session.current_chain
    except Exception as exc:
        return 1, f"grimchain: {exc}"


def string_cli(source: str, middle: str) -> tuple[int, str]:
    """Preserved in-process CLI adapter used for direct/callable equivalence tests."""
    argv: list[str] = []
    if middle.strip():
        argv.append(middle.strip())
    argv.extend(("--string", source))
    return execute(argv)


def file(source: str | Path, middle: str) -> tuple[int, str]:
    """GrimChain one exact file body through TardiSHA's raw-file authority."""
    try:
        middle_text = middle.strip()
        depth = int(middle_text) if middle_text else 0
        if depth < 0:
            depth = 0
        chain, _emission, _route = file_domus_record(
            Path(source), depth, nonce=0, include_filename=True
        )
        return 0, chain
    except Exception as exc:
        return 1, f"grimchain: {exc}"


def pdf_embed(source: str | Path, middle: str) -> tuple[int, str]:
    """Apply the exact public `grimchain NUMBER --pdf-embed PDF` command path."""
    middle_text = middle.strip()
    argv: list[str] = []
    if middle_text:
        argv.append(middle_text)
    argv.extend(("--pdf-embed", str(Path(source))))
    try:
        return execute(argv)
    except Exception as exc:
        return 1, f"grimchain: {exc}"


def validate(chain: str) -> None:
    """Require the current public TardiSHA GrimChain structure."""
    parse_public_living_domus(chain)
