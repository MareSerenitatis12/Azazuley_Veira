"""grimchain — one command: content in, ALQC seal out.

Positional middle is USER-CHOSEN at call time (any integer; negative depth returns to Shadow Locus zero):

    grimchain <N> <path>            # seal a file with declared middle depth N
    grimchain <path>                # zero body ⛎⛎⛎ (manifested from Shadow Locus ⛎)
    echo -n "text" | grimchain <N>  # seal stdin with declared middle depth N
"""
from __future__ import annotations

import os
import sys
import json
import tempfile
from pathlib import Path
from argparse import ArgumentParser, SUPPRESS

from .hashing import SOURCE_CHUNK_BYTES, TardiSHAError


_MIDDLE_UNSET = object()


def _materialize(data: bytes) -> str:
    """Write one exact in-memory byte body to a temporary source file."""
    if not isinstance(data, bytes):
        raise TypeError("materialized source must be bytes")
    fd, tmp = tempfile.mkstemp(suffix=".grimchain")
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        return tmp
    except Exception:
        Path(tmp).unlink(missing_ok=True)
        raise


def _materialize_stream(reader) -> str:
    """Copy one binary stream exactly, with bounded memory and no normalization."""
    fd, tmp = tempfile.mkstemp(suffix=".grimchain")
    try:
        with os.fdopen(fd, "wb") as handle:
            while True:
                chunk = reader.read(SOURCE_CHUNK_BYTES)
                if not chunk:
                    break
                if not isinstance(chunk, (bytes, bytearray, memoryview)):
                    raise TypeError("grimchain stream must yield bytes")
                handle.write(bytes(chunk))
            handle.flush()
            os.fsync(handle.fileno())
        return tmp
    except Exception:
        Path(tmp).unlink(missing_ok=True)
        raise



BASIC_HELP = """usage:
  grimchain PATH
  grimchain NUMBER PATH
  grimchain --string "TEXT"
  grimchain NUMBER --string "TEXT"
  grimchain NUMBER --manifest PATH
  grimchain NUMBER -R --manifest DIRECTORY
  grimchain NUMBER --manifest --string "TEXT"
  grimchain NUMBER --pdf-embed PDF
  grimchain NUMBER --pdf-embed PDF --manifest
  grimchain --pdf-rm-embed PDF
  grimchain --help -a

NUMBER is the declared middle depth you choose. Every non-positive NUMBER returns to
the zero body ⛎⛎⛎. Depth 1 is the Triple Horned God ☽᳀☾. Every depth greater
than 1 is exactly that many generated Synodic Magicae coordinates.
Leave NUMBER out to use the zero body ⛎⛎⛎.

basic use:
  grimchain PATH
      Grimchain one file or one directory.

  grimchain NUMBER PATH
      Grimchain one file or directory using the declared middle depth you choose.

  grimchain --string "TEXT"
  grimchain NUMBER --string "TEXT"
      Grimchain the exact UTF-8 content supplied by the quoted argument.
      The quotes belong to the shell and are not part of the source.

  grimchain NUMBER --manifest FILE
      Create manifest-FILENAME.grim, append its exact same-width Grimchain,
      then Grimchain the completed manifest again and print that same return.

  grimchain NUMBER --manifest DIRECTORY
      Create manifest-DIRECTORYNAME.grim for the files directly inside that
      directory, append its Grimchain, then Grimchain the completed manifest again.

  grimchain NUMBER -R --manifest DIRECTORY
      Create manifest-recurse-DIRECTORYNAME.grim for all subdirectories, append
      its Grimchain, then Grimchain the completed manifest again.

  grimchain NUMBER --pdf-embed PDF
      Append the current GrimChain of the exact base PDF as the single PDF self-return, 
      then verify that the complete PDF revision closes exactly to the same source witness.

  grimchain --pdf-rm-embed PDF
      Verify and remove that one explicit PDF return, restoring the exact base bytes.
"""

ADVANCED_HELP = """usage:
  grimchain [NUMBER] PATH [OPTIONS]
  grimchain [NUMBER] --string "TEXT" [OPTIONS]
  grimchain NUMBER --pdf-embed PDF [--nonce INTEGER]
  grimchain --pdf-rm-embed PDF

NUMBER is any whole-number middle depth you choose. Every non-positive NUMBER returns
to the zero body ⛎⛎⛎. Depth 1 is the Triple Horned God ☽᳀☾. Every depth greater
than 1 is exactly that many generated Synodic Magicae coordinates.
Leave NUMBER out to use the zero body ⛎⛎⛎.

ordinary use:
  grimchain PATH
      Grimchain one file or directory with the zero body ⛎⛎⛎.

  grimchain NUMBER PATH
  grimchain --middle NUMBER PATH
      Grimchain one file or directory with declared middle depth NUMBER.

  grimchain --string "TEXT"
  grimchain NUMBER --string "TEXT"
      Grimchain the exact UTF-8 content inside the quoted shell argument.
      No newline, trimming, normalization, or separate string algorithm is added.

  grimchain NUMBER PATH --output FILE
      Save the Grimchain in FILE instead of printing it.

manifests:
  grimchain [NUMBER] --manifest FILE
      Create manifest-FILENAME.grim, append its exact same-width Grimchain,
      then Grimchain the completed manifest again and print that same return.

  grimchain [NUMBER] --manifest DIRECTORY
      Create manifest-DIRECTORYNAME.grim for direct files, append its Grimchain,
      then Grimchain the completed manifest again and print that same return.

  grimchain [NUMBER] -R --manifest DIRECTORY
      Create manifest-recurse-DIRECTORYNAME.grim for the complete tree, append
      its Grimchain, then Grimchain the completed manifest again and print it.

  grimchain [NUMBER] --manifest PATH --output FILE
      Write the manifest to the filename you choose, append its exact Grimchain,
      then Grimchain the completed file again and print that same return.

  grimchain [NUMBER] --manifest --string "TEXT"
      Create a manifest whose source name and source identity are the exact shell
      argument supplied to --string, append its Grimchain, and return it again.

  grimchain [NUMBER] --pdf-embed PDF --manifest
      Perform the normal PDF embed and print its Grimchain, then create the
      manifest, append its Grimchain, and return that completed manifest again.

PDF return:
      Append the current GrimChain of the exact base PDF as the single PDF self-return, 
      then verify that the complete PDF revision closes exactly to the same source witness.

  grimchain --pdf-rm-embed PDF
      Verify that single return and restore the exact base PDF bytes.

inspection and lists:
  grimchain SEAL --inspect
      Show the parts contained in one Grimchain.

input and optional controls:
  printf 'text' | grimchain [NUMBER]
      Grimchain text received through standard input.

  grimchain --binary PATH
      Use the file's exact bytes. This is the only file-body law; line endings are never normalized.

  grimchain PATH --nonce INTEGER
      Use the chosen integer to create another repeatable Grimchain for PATH.

  grimchain PATH --fold --span NUMBER --levels NUMBER
      Create the fold-ladder output for PATH. Both dimensions are explicit and required.

  grimchain PATH1 PATH2 DIRECTORY
      Grimchain several sources in one command.

information:
  grimchain --version
      Show the installed TardiSHA version.

  grimchain --help
      Show basic use.

  grimchain --help -a
      Show all commands.
"""


def _installed_version() -> str:
    from importlib.metadata import PackageNotFoundError, version as package_version

    try:
        return package_version("TardiSHA")
    except PackageNotFoundError as exc:
        raise TardiSHAError("installed TardiSHA package metadata is required for --version") from exc


def main() -> None:
    argv = sys.argv[1:]
    separator_index = argv.index("--") if "--" in argv else None
    if separator_index is None:
        parser_argv = argv
        protected_args: list[str] = []
    else:
        parser_argv = argv[:separator_index]
        protected_args = argv[separator_index + 1:]

    p = ArgumentParser(prog="grimchain", description="content in, ALQC seal out", add_help=False)
    p.add_argument("args", nargs="*",
                   help="[MIDDLE] [PATH] — omit MIDDLE for the zero body ⛎⛎⛎; PATH omitted reads stdin")
    p.add_argument("-h", "--help", action="store_true", help=SUPPRESS)
    p.add_argument("-a", "--advanced", action="store_true", help=SUPPRESS)
    p.add_argument("--version", action="store_true", help=SUPPRESS)
    p.add_argument("--middle", type=int, default=SUPPRESS, help="explicit middle length")
    p.add_argument("--string", metavar="TEXT", help="Grimchain the exact UTF-8 bytes of one shell argument")
    p.add_argument("-b", "--binary", action="store_true", help="read exact bytes; this is the only file-body law")
    p.add_argument("--pdf-embed", type=Path, metavar="PDF", help="write or replace the single PDF GrimChain self-return")
    p.add_argument("--pdf-rm-embed", type=Path, metavar="PDF", help="remove the verified terminal PDF GrimChain self-return")
    p.add_argument("--output", type=Path, help="write the seal or manifest to a file")
    p.add_argument("--manifest", action="store_true", help="write a Grimchain source manifest")
    p.add_argument("-R", "--recursive", action="store_true", help="include nested files in a directory manifest")
    p.add_argument("--fold", action="store_true", help="emit the born-glyph fold ladder")
    p.add_argument("--span", type=int, default=SUPPRESS, help="explicit fold span length")
    p.add_argument("--levels", type=int, default=SUPPRESS, help="explicit fold level count")
    p.add_argument("--inspect", action="store_true", help="parse one seal value")
    p.add_argument("--nonce", type=int, default=0)
    a = p.parse_intermixed_args(parser_argv)

    try:
        raw_args = list(a.args)
        unprotected_args = raw_args

        option_conflicts = any((
            a.version, a.string is not None, a.binary, a.pdf_embed is not None, a.pdf_rm_embed is not None, a.output is not None,
            a.manifest, a.recursive, a.fold, a.inspect,
            hasattr(a, "middle"), hasattr(a, "span"), hasattr(a, "levels"), bool(raw_args),
        ))
        if a.help:
            if option_conflicts:
                p.error("--help may be combined only with -a/--advanced")
            print(ADVANCED_HELP if a.advanced else BASIC_HELP, end="")
            return
        if a.advanced:
            p.error("-a/--advanced is used only with --help")
        if a.version:
            if any((a.string is not None, a.binary, a.pdf_embed is not None, a.pdf_rm_embed is not None, a.output is not None,
                    a.manifest, a.recursive, a.fold, a.inspect, hasattr(a, "middle"),
                    hasattr(a, "span"), hasattr(a, "levels"), bool(raw_args))):
                p.error("--version cannot be combined with another mode or source")
            print(_installed_version())
            return

        middle_value: int | object = getattr(a, "middle", _MIDDLE_UNSET)
        middle_was_supplied = middle_value is not _MIDDLE_UNSET
        if unprotected_args and not middle_was_supplied:
            token = unprotected_args[0]
            if token.lstrip("+-").isdigit():
                middle_value = int(token)
                middle_was_supplied = True
                unprotected_args = unprotected_args[1:]
        if middle_was_supplied and isinstance(middle_value, int) and not isinstance(middle_value, bool) and middle_value < 0:
            middle_value = 0
        paths = unprotected_args + protected_args

        if a.pdf_rm_embed is not None:
            if any((
                middle_was_supplied,
                paths,
                a.string is not None,
                a.binary,
                a.pdf_embed is not None,
                a.output is not None,
                a.manifest,
                a.recursive,
                a.fold,
                a.inspect,
                hasattr(a, "span"),
                hasattr(a, "levels"),
            )):
                p.error("--pdf-rm-embed cannot be combined with another source or mode")

            target = a.pdf_rm_embed.expanduser().resolve()
            if not target.is_file():
                raise FileNotFoundError(f"does not exist: {a.pdf_rm_embed}")
            if target.suffix.lower() != ".pdf":
                raise TardiSHAError("--pdf-rm-embed requires a PDF file")

            from .pdf_return import remove_embed

            result = remove_embed(target)
            print(result["seal"])
            return

        if a.pdf_embed is not None:
            if any((paths, a.string is not None, a.binary,
                    a.output is not None and not a.manifest, a.recursive,
                    a.fold, a.inspect, hasattr(a, "span"), hasattr(a, "levels"))):
                p.error("--pdf-embed cannot be combined with another source or mode")
            target = a.pdf_embed.expanduser().resolve()
            if not target.is_file():
                raise FileNotFoundError(f"does not exist: {a.pdf_embed}")
            if target.suffix.lower() != ".pdf":
                raise TardiSHAError("--pdf-embed requires a PDF file")
            from .pdf_return import embed
            manifest_middle = middle_value if middle_was_supplied else 0
            assert isinstance(manifest_middle, int)
            result = embed(target, manifest_middle, nonce=a.nonce)
            print(result["seal"])
            if a.manifest:
                from .manifest import manifest_output_path, write_grimchain_manifest
                destination = manifest_output_path(target, a.output, False).resolve()
                manifest_parity = write_grimchain_manifest(
                    target, destination, middle=manifest_middle, recursive=False, nonce=a.nonce
                )
                print(manifest_parity)
            return

        if a.recursive and not a.manifest:
            p.error("-R/--recursive is used only with --manifest")
        if hasattr(a, "span") != hasattr(a, "levels"):
            p.error("--span and --levels must be supplied together")
        if a.fold:
            if not hasattr(a, "span") or not hasattr(a, "levels"):
                p.error("--fold requires explicit --span and --levels")
            if a.output is not None or a.manifest or a.inspect or a.string is not None:
                p.error("--fold cannot be combined with --output, --manifest, --inspect, or --string")
        elif hasattr(a, "span") or hasattr(a, "levels"):
            p.error("--span and --levels are used only with --fold")

        if a.inspect:
            if any((middle_was_supplied, a.string is not None, a.binary, a.output is not None,
                    a.manifest, a.recursive, a.fold)):
                p.error("--inspect cannot be combined with another mode, output, or middle")
            if len(paths) != 1:
                p.error("--inspect requires exactly one seal value")
            from .domus import parse_public_living_domus
            print(json.dumps(_public_grim_payload(parse_public_living_domus(paths[0])), ensure_ascii=False, indent=2))
            return

        if a.manifest:
            from .manifest import manifest_output_path, write_grimchain_manifest
            if a.binary or a.fold or a.inspect:
                p.error("--manifest cannot be combined with --binary, --fold, or --inspect")
            if a.string is None and len(paths) != 1:
                p.error("--manifest requires exactly one file or directory")
            if a.string is not None and paths:
                p.error("--string --manifest cannot be combined with file or directory paths")

        if a.string is not None:
            if paths:
                p.error("--string cannot be combined with file or directory paths")
            if a.recursive or a.inspect or a.binary or a.fold:
                p.error("--string cannot be combined with -R, --inspect, --binary, or --fold")

        if len(paths) > 1 and a.output is not None:
            p.error("one --output cannot receive multiple sources")

        if a.string is not None and a.manifest:
            tmp = _materialize(a.string.encode("utf-8"))
            try:
                manifest_middle = middle_value if middle_was_supplied else 0
                assert isinstance(manifest_middle, int)
                destination = (
                    a.output.expanduser().resolve()
                    if a.output is not None
                    else (Path.cwd() / f"manifest-{a.string}.grim").resolve()
                )
                manifest_parity = write_grimchain_manifest(
                    tmp, destination, middle=manifest_middle, recursive=False, nonce=a.nonce,
                    entry_name=a.string, identity_name=None, include_filename=False,
                )
                print(manifest_parity)
            finally:
                os.unlink(tmp)
            return

        if a.manifest:
            target = Path(paths[0]).expanduser().resolve()
            if not target.exists():
                raise FileNotFoundError(f"does not exist: {paths[0]}")
            destination = manifest_output_path(target, a.output, a.recursive).resolve()
            manifest_middle = middle_value if middle_was_supplied else 0
            assert isinstance(manifest_middle, int)
            manifest_parity = write_grimchain_manifest(
                target, destination, middle=manifest_middle, recursive=a.recursive, nonce=a.nonce
            )
            print(manifest_parity)
            return

        if a.string is not None:
            tmp = _materialize(a.string.encode("utf-8"))
            try:
                if middle_was_supplied:
                    assert isinstance(middle_value, int)
                    out = _do_file(Path(tmp), middle_value, a, source_label="--string")
                else:
                    out = _do_file_shadow_locus(Path(tmp), a, source_label="--string")
                print(out)
            finally:
                os.unlink(tmp)
            return

        if not paths:
            if sys.stdin.isatty():
                p.error("path required (or pipe input)")
            tmp = _materialize_stream(sys.stdin.buffer)
            try:
                if middle_was_supplied:
                    assert isinstance(middle_value, int)
                    print(_do_file(Path(tmp), middle_value, a, source_label="<stdin>"))
                else:
                    print(_do_file_shadow_locus(Path(tmp), a, source_label="<stdin>"))
            finally:
                os.unlink(tmp)
            return

        for raw in paths:
            target = Path(raw).expanduser().resolve()
            if not target.exists():
                raise FileNotFoundError(f"does not exist: {raw}")
            if target.is_dir():
                if middle_was_supplied:
                    assert isinstance(middle_value, int)
                    out = _do_dir(target, middle_value, a)
                else:
                    out = _do_dir_shadow_locus(target, a)
            else:
                if middle_was_supplied:
                    assert isinstance(middle_value, int)
                    out = _do_file(target, middle_value, a, source_label=raw)
                else:
                    out = _do_file_shadow_locus(target, a, source_label=raw)
            print(out)

    except BrokenPipeError:
        try:
            sys.stdout.close()
        except Exception:
            pass
    except (TardiSHAError, FileNotFoundError, OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(f"grimchain: {exc}", file=sys.stderr)
        sys.exit(1)


def _do_file_shadow_locus(target: Path, a, *, source_label: str | None = None) -> str:
    """Dispatch an omitted middle argument through the Shadow Locus zero path."""
    from .domus_stream import living_domus_for_source, write_public_domus
    include_filename = source_label not in {"--string", "<stdin>"}
    if a.fold:
        from .folding import public_ladder_avirbhava, self_compress_ladder
        from .node import node_from_file
        node = node_from_file(target, nonce=a.nonce)
        return json.dumps(
            public_ladder_avirbhava(self_compress_ladder(node, span_length=a.span, levels=a.levels)),
            ensure_ascii=False,
            indent=2,
        )
    if a.output:
        r = write_public_domus(
            target,
            a.output,
            kind="file",
            middle_length=0,
            nonce=a.nonce,
            include_filename=include_filename,
        )
        return json.dumps(r, ensure_ascii=False, indent=2)
    if include_filename and target.suffix.lower() == ".pdf":
        from .pdf_return import grimchain_for_pdf
        return grimchain_for_pdf(target, 0, nonce=a.nonce)
    return living_domus_for_source(
        target,
        0,
        kind="file",
        nonce=a.nonce,
        include_filename=include_filename,
    )


def _do_dir_shadow_locus(target: Path, a) -> str:
    """Dispatch an omitted middle argument through the Shadow Locus zero path."""
    from .domus_stream import living_domus_for_source, write_public_domus
    if a.fold:
        from .folding import public_ladder_avirbhava, self_compress_ladder
        from .node import node_from_directory
        node = node_from_directory(target, nonce=a.nonce)
        return json.dumps(
            public_ladder_avirbhava(self_compress_ladder(node, span_length=a.span, levels=a.levels)),
            ensure_ascii=False,
            indent=2,
        )
    if a.output:
        r = write_public_domus(
            target,
            a.output,
            kind="directory",
            middle_length=0,
            nonce=a.nonce,
        )
        return json.dumps(r, ensure_ascii=False, indent=2)
    return living_domus_for_source(target, 0, kind="directory", nonce=a.nonce)


def _do_file(target: Path, middle: int, a, *, source_label: str | None = None) -> str:
    from .domus_stream import living_domus_for_source, write_public_domus
    include_filename = source_label not in {"--string", "<stdin>"}
    if a.fold:
        from .folding import public_ladder_avirbhava, self_compress_ladder
        from .node import node_from_file
        node = node_from_file(target, nonce=a.nonce)
        return json.dumps(public_ladder_avirbhava(self_compress_ladder(node, span_length=a.span, levels=a.levels)),
                          ensure_ascii=False, indent=2)
    if a.output:
        r = write_public_domus(
            target, a.output, kind="file", middle_length=middle, nonce=a.nonce,
            include_filename=include_filename,
        )
        return json.dumps(r, ensure_ascii=False, indent=2)
# Default content-in / GrimChain-out uses the canonical public GrimChain.
    if include_filename and target.suffix.lower() == ".pdf":
        from .pdf_return import grimchain_for_pdf
        return grimchain_for_pdf(target, middle, nonce=a.nonce)
    return living_domus_for_source(
        target, middle, kind="file", nonce=a.nonce, include_filename=include_filename
    )


def _do_dir(target: Path, middle: int, a) -> str:
    from .domus_stream import living_domus_for_source, write_public_domus
    if a.fold:
        from .folding import public_ladder_avirbhava, self_compress_ladder
        from .node import node_from_directory
        node = node_from_directory(target, nonce=a.nonce)
        return json.dumps(public_ladder_avirbhava(self_compress_ladder(node, span_length=a.span, levels=a.levels)),
                          ensure_ascii=False, indent=2)
    if a.output:
        r = write_public_domus(target, a.output, kind="directory", middle_length=middle, nonce=a.nonce)
        return json.dumps(r, ensure_ascii=False, indent=2)
# Default directory output uses the canonical public GrimChain.
    return living_domus_for_source(target, middle, kind="directory", nonce=a.nonce)


def _public_grim_payload(parsed) -> dict:
    """Structural inspection of one canonical public Grim. No source recomputation."""
    return {
        "center": parsed.center,
        "depth": parsed.depth,
    }


if __name__ == "__main__":
    main()
