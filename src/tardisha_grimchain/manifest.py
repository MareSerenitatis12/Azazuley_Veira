"""Grimchain file and directory manifests.

The public SOURCE_MANIFEST ledger shape is retained: a name, a file count,
and sorted entries. Each entry carries its Grimchain
value, and the complete entry body receives its own deterministic Grimchain.

Vāhana means vehicle or carrier in Sanskrit. Manifest Vāhana is the invocation-local
carrier for already-calculated entries and the current body on their way to becoming
permanent history. It is discarded after the operation and is not a cache.
"""
from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import Any

from .domus_stream import file_domus_record, living_domus_for_source
from .hashing import (
    TardiSHAError,
    validate_middle_length,
    validate_nonce,
)

_GRIM_OBJECT_OPEN = "\u0f3a"
_GRIM_OBJECT_CLOSE = "\u0f3b"
_GRIM_COLLECTION_OPEN = "\u2235"
_GRIM_COLLECTION_CLOSE = "\u2234"
_GRIM_FIELD_OPEN = "\u10fb"
_GRIM_FIELD_HINGE = "\u205b"
_GRIM_FIELD_CLOSE = "\u2056"

def default_manifest_name(target: Path, recursive: bool) -> str:
    name = target.name or "root"
    prefix = "manifest-recurse-" if target.is_dir() and recursive else "manifest-"
    return f"{prefix}{name}.grim"

def manifest_output_path(target: Path, output: Path | None, recursive: bool) -> Path:
    default_name = default_manifest_name(target, recursive)
    if output is None:
        return Path.cwd() / default_name
    candidate = output.expanduser()
    if candidate.exists() and candidate.is_dir():
        return candidate / default_name
    return candidate

def _lexical_absolute(path: Path) -> Path:
    return Path(os.path.abspath(os.fspath(path.expanduser())))

def _selected_entries(
    root: Path,
    recursive: bool,
    excludes: tuple[Path, ...] = (),
    root_file_name: str | None = None,
) -> list[tuple[str, Path, str]]:
    excluded = {_lexical_absolute(path) for path in excludes}
    if root.is_file() and not root.is_symlink():
        if _lexical_absolute(root) in excluded:
            raise TardiSHAError("manifest source cannot be excluded from itself")
        return [
            (
                "file",
                root,
                root.name if root_file_name is None else root_file_name,
            )
        ]
    if not root.is_dir() or root.is_symlink():
        raise TardiSHAError(f"manifest source is not a regular file or directory: {root}")

    selected: list[tuple[str, Path, str]] = [("directory", root, ".")]
    stack = [root]
    while stack:
        current = stack.pop()
        try:
            scanned = sorted(os.scandir(current), key=lambda entry: entry.name)
        except OSError as exc:
            raise TardiSHAError(f"cannot read manifest directory {current}: {exc}") from exc
        directories: list[Path] = []
        for entry in scanned:
            child = Path(entry.path)
            if _lexical_absolute(child) in excluded:
                continue
            relative = child.relative_to(root).as_posix()
            if entry.is_symlink():
                selected.append(("symlink", child, relative))
            elif entry.is_dir(follow_symlinks=False):
                selected.append(("directory", child, relative))
                if recursive:
                    directories.append(child)
            elif entry.is_file(follow_symlinks=False):
                selected.append(("file", child, relative))
            else:
                raise TardiSHAError(f"unsupported manifest entry type: {relative}")
        if recursive:
            stack.extend(reversed(directories))
    return sorted(selected, key=lambda item: item[2])

def _manifest_file_entry(
    source: Path,
    relative_path: str,
    middle: int,
    nonce: int,
    *,
    identity_name: str | bytes | None = None,
    include_filename: bool = True,
) -> dict[str, Any]:
    """Calculate one listed file exactly once for this manifest invocation."""
    seal, _, _ = file_domus_record(
        source, middle, nonce=nonce, identity_name=identity_name,
        include_filename=include_filename,
    )

    return {
        "type": "file",
        "path": relative_path,
        "grimchain": seal,
    }

def _nonfile_entry(kind: str, path: Path, relative: str) -> dict[str, Any]:
    if kind == "directory":
        return {"type": "directory", "path": relative}
    if kind == "symlink":
        return {"type": "symlink", "path": relative, "target": os.readlink(path)}
    raise TardiSHAError(f"unsupported manifest entry kind: {kind}")


def _build_manifest_entries(
    root: Path,
    *,
    middle: int,
    recursive: bool,
    nonce: int,
    exclusions: tuple[Path, ...],
    root_file_name: str | None = None,
    root_identity_name: str | bytes | None = None,
    root_include_filename: bool = True,
) -> list[dict[str, Any]]:
    selected = _selected_entries(
        root, recursive, exclusions, root_file_name=root_file_name
    )
    entries: list[dict[str, Any]] = []
    for kind, path, relative in selected:
        if kind == "file":
            entries.append(
                _manifest_file_entry(
                    path,
                    relative,
                    middle,
                    nonce,
                    identity_name=(
                        root_identity_name if root.is_file() and path == root else None
                    ),
                    include_filename=(
                        root_include_filename if root.is_file() and path == root else True
                    ),
                )
            )
        else:
            entries.append(_nonfile_entry(kind, path, relative))
    return entries


def build_grimchain_manifest(
    target: str | Path,
    *,
    middle: int,
    recursive: bool = False,
    nonce: int = 0,
    exclude: str | Path | None = None,
    entry_name: str | None = None,
    identity_name: str | bytes | None = None,
    include_filename: bool = True,
) -> dict[str, Any]:

    root = Path(target).expanduser().resolve()
    width = validate_middle_length(middle)
    salt = validate_nonce(nonce)
    exclusions = (() if exclude is None else (Path(exclude).expanduser().resolve(),))

    if recursive and not root.is_dir():
        raise TardiSHAError("-R/--recursive requires a directory manifest")

    entries = _build_manifest_entries(
        root,
        middle=width,
        recursive=recursive,
        nonce=salt,
        exclusions=exclusions,
        root_file_name=entry_name,
        root_identity_name=identity_name,
        root_include_filename=include_filename,
    )

    public_entries: list[dict[str, Any]] = []
    for entry in entries:
        kind_name = entry["type"]
        if kind_name == "file":
            public_entries.append({
                "type": "file",
                "path": entry["path"],
                "grimchain": entry["grimchain"],
            })
        elif kind_name == "directory":
            public_entries.append({
                "type": "directory",
                "path": entry["path"],
            })
        elif kind_name == "symlink":
            public_entries.append({
                "type": "symlink",
                "path": entry["path"],
                "target": entry["target"],
            })
        else:
            raise TardiSHAError(f"unsupported manifest entry kind: {kind_name}")

    manifest = {
        "scope": "recursive" if recursive else "direct",
        "entries": public_entries,
    }

    return manifest

def _grim_manifest_scalar(value: Any, *, field: str) -> str:
    if not isinstance(value, str):
        raise TardiSHAError(f"manifest {field} must be a string")
    if "\n" in value or "\r" in value:
        raise TardiSHAError(f"manifest {field} cannot contain a line break")
    return value


def _grim_field(name: str, value: str) -> str:
    return f"{_GRIM_FIELD_OPEN}{name}{_GRIM_FIELD_HINGE}{value}{_GRIM_FIELD_CLOSE}"


def _render_grim_manifest(manifest: dict[str, Any]) -> str:
    """Serialize one public manifest into the native .grim language."""
    scope = _grim_manifest_scalar(manifest.get("scope"), field="scope")
    entries = manifest.get("entries")
    if scope not in ("recursive", "direct"):
        raise TardiSHAError("manifest lacks a valid scope")
    if not isinstance(entries, list):
        raise TardiSHAError("manifest entries must be a list")

    lines = [
        _GRIM_OBJECT_OPEN,
        _grim_field("scope", scope),
        f"{_GRIM_FIELD_OPEN}entries{_GRIM_FIELD_HINGE}{_GRIM_COLLECTION_OPEN}",
    ]
    for entry in entries:
        if not isinstance(entry, dict):
            raise TardiSHAError("manifest entry is not an object")
        kind = _grim_manifest_scalar(entry.get("type"), field="entry type")
        path = _grim_manifest_scalar(entry.get("path"), field="entry path")
        lines.extend((
            _GRIM_OBJECT_OPEN,
            _grim_field("type", kind),
            _grim_field("path", path),
        ))
        if kind == "file":
            value = _grim_manifest_scalar(entry.get("grimchain"), field="entry grimchain")
            lines.append(_grim_field("grimchain", value))
        elif kind == "symlink":
            target = _grim_manifest_scalar(entry.get("target"), field="symlink target")
            lines.append(_grim_field("target", target))
        elif kind != "directory":
            raise TardiSHAError(f"unsupported manifest entry kind: {kind}")
        lines.append(_GRIM_OBJECT_CLOSE)

    lines.extend((
        _GRIM_COLLECTION_CLOSE,
        _GRIM_OBJECT_CLOSE,
    ))
    return "\n".join(lines) + "\n"



def write_grimchain_manifest(
    target: str | Path,
    output: str | Path,
    *,
    middle: int,
    recursive: bool = False,
    nonce: int = 0,
    entry_name: str | None = None,
    identity_name: str | bytes | None = None,
    include_filename: bool = True,
) -> str:
    destination = Path(output).expanduser().resolve()
    width = validate_middle_length(middle)
    salt = validate_nonce(nonce)

    manifest = build_grimchain_manifest(
        target,
        middle=width,
        recursive=recursive,
        nonce=salt,
        exclude=destination,
        entry_name=entry_name,
        identity_name=identity_name,
        include_filename=include_filename,
    )
    body_bytes = _render_grim_manifest(manifest).encode("utf-8")
    destination.parent.mkdir(parents=True, exist_ok=True)

    fd, tmp_name = tempfile.mkstemp(
        prefix=f".{destination.name}.",
        suffix=".part",
        dir=destination.parent,
    )
    temp = Path(tmp_name)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(body_bytes)
            handle.flush()
            os.fsync(handle.fileno())

        os.replace(temp, destination)
    except Exception:
        temp.unlink(missing_ok=True)
        raise

    first_grimchain = living_domus_for_source(
        destination,
        width,
        kind="file",
        nonce=salt,
    )

    with destination.open("ab") as handle:
        handle.write(first_grimchain.encode("utf-8"))
        handle.flush()
        os.fsync(handle.fileno())

    return living_domus_for_source(
        destination,
        width,
        kind="file",
        nonce=salt,
    )

