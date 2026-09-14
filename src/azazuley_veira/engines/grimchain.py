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
from tardisha_grimchain.domus_stream import living_domus_for_source


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


def string(source: str, middle: str) -> tuple[int, str]:
    """GrimChain one exact text body through TardiSHA's public callable authority."""
    try:
        middle_text = middle.strip()
        depth = int(middle_text) if middle_text else 0
        if depth < 0:
            depth = 0
        fd, tmp = tempfile.mkstemp(suffix=".grimchain")
        try:
            with os.fdopen(fd, "wb") as handle:
                handle.write(source.encode("utf-8"))
                handle.flush()
                os.fsync(handle.fileno())
            body = living_domus_for_source(
                Path(tmp),
                depth,
                kind="file",
                nonce=0,
                include_filename=False,
            )
        finally:
            Path(tmp).unlink(missing_ok=True)
        return 0, body
    except Exception as exc:
        return 1, f"grimchain: {exc}"


def string_cli(source: str, middle: str) -> tuple[int, str]:
    """Preserved in-process CLI adapter used for direct/callable equivalence tests."""
    argv: list[str] = []
    if middle.strip():
        argv.append(middle.strip())
    argv.extend(("--string", source))
    return execute(argv)


def validate(chain: str) -> None:
    """Require the current public TardiSHA GrimChain structure."""
    parse_public_living_domus(chain)
