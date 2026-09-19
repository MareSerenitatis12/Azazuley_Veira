"""Persistent rotating journal for GrimChains created by the user."""
from __future__ import annotations

import gzip
import os
import shutil
import mmap
import tempfile
from datetime import datetime
from pathlib import Path

MAX_JOURNAL_BYTES = 32 * 1024 * 1024
RECORD_SEPARATOR = "⧟⧟⧟⧟⧟⧟⧟⧟⧟⧟⧟⧟⧟⧟⧟⧟⧟⧟⧟⧟⧟⧟⧟⧟⧟⧟⧟⧟⧟⧟"
JOURNAL_DIRECTORY = Path.home() / ".grimchain" / "azazuley" / "grimchains"
ACTIVE_JOURNAL = JOURNAL_DIRECTORY / "grimchains.bio"
BACKUP_JOURNALS = tuple(
    JOURNAL_DIRECTORY / f"grimchains.{index}.bio" for index in range(1, 4)
)


def ensure_grimchain_journal() -> Path:
    """Ensure only the active GrimChain journal exists before any rotation."""
    JOURNAL_DIRECTORY.mkdir(parents=True, exist_ok=True)
    ACTIVE_JOURNAL.touch(exist_ok=True)
    return ACTIVE_JOURNAL


def _rotate() -> None:
    ensure_grimchain_journal()
    BACKUP_JOURNALS[-1].unlink(missing_ok=True)
    for source, destination in zip(
        reversed(BACKUP_JOURNALS[:-1]), reversed(BACKUP_JOURNALS[1:])
    ):
        if source.exists():
            os.replace(source, destination)
    with ACTIVE_JOURNAL.open("rb") as source, gzip.open(BACKUP_JOURNALS[0], "wb") as destination:
        shutil.copyfileobj(source, destination)
    ACTIVE_JOURNAL.write_bytes(b"")


def _record_bytes(user_input: str, grimchain: str, timestamp: str, *, first_record: bool) -> bytes:
    prefix = RECORD_SEPARATOR + "\n" if first_record else ""
    return (
        prefix
        + f"⁖Timestamp჻{timestamp}⁖\n"
        + f"⁖User input჻{user_input}⁖\n"
        + f"⁖Grimchain჻{grimchain}⁖\n"
        + RECORD_SEPARATOR
        + "\n"
    ).encode("utf-8")


def read_grim_import(path: str | Path) -> tuple[tuple[str, str], ...]:
    """Read one .grim manifest as ordered (user input, GrimChain) journal records."""
    source = Path(path)
    if source.suffix != ".grim" or not source.is_file():
        raise ValueError(f"Grim import requires one .grim file: {source}")
    lines = source.read_text(encoding="utf-8").splitlines()
    try:
        close_index = len(lines) - 1 - lines[::-1].index("∴")
    except ValueError as exc:
        raise ValueError(f".grim manifest has no entries terminator: {source}") from exc
    if lines[close_index + 1:close_index + 2] != ["༻"] or len(lines[close_index + 2:]) != 1:
        raise ValueError(f".grim manifest has no singular trailing GrimChain: {source}")
    records: list[tuple[str, str]] = []
    entry_path: str | None = None
    entry_grimchain: str | None = None
    depth = 0
    for line in lines[:close_index]:
        if line == "༺":
            depth += 1
            if depth == 2:
                entry_path = None
                entry_grimchain = None
        elif line == "༻":
            if depth == 2 and entry_grimchain is not None:
                if entry_path is None:
                    raise ValueError(f".grim GrimChain entry has no path: {source}")
                records.append((entry_path, entry_grimchain))
            depth -= 1
        elif depth == 2 and line.startswith("჻path⁛") and line.endswith("⁖"):
            entry_path = line[len("჻path⁛"):-1]
        elif depth == 2 and line.startswith("჻grimchain⁛") and line.endswith("⁖"):
            entry_grimchain = line[len("჻grimchain⁛"):-1]
    records.append((source.name, lines[-1]))
    return tuple(records)


def _history_record_from_body(body: bytes, path: Path) -> tuple[str, str, str]:
    text = body.decode("utf-8").strip("\r\n")
    timestamp_prefix = "⁖Timestamp჻"
    user_prefix = "⁖User input჻"
    chain_prefix = "⁖Grimchain჻"
    if not text.startswith(timestamp_prefix):
        raise ValueError(f"incomplete GrimChain journal record in {path}")
    timestamp_end = text.find("⁖\n", len(timestamp_prefix))
    user_start = text.find(user_prefix, timestamp_end + 2)
    chain_start = text.rfind("\n" + chain_prefix)
    if timestamp_end < 0 or user_start < 0 or chain_start < 0:
        raise ValueError(f"incomplete GrimChain journal record in {path}")
    timestamp = text[len(timestamp_prefix):timestamp_end]
    user_value_start = user_start + len(user_prefix)
    if not text[chain_start - 1:chain_start].endswith("⁖"):
        raise ValueError(f"incomplete GrimChain journal record in {path}")
    user_input = text[user_value_start:chain_start - 1]
    chain_value_start = chain_start + 1 + len(chain_prefix)
    if not text.endswith("⁖"):
        raise ValueError(f"incomplete GrimChain journal record in {path}")
    grimchain = text[chain_value_start:-1]
    if not timestamp or not grimchain:
        raise ValueError(f"incomplete GrimChain journal record in {path}")
    return timestamp, user_input, grimchain


class GrimchainHistorySession:
    """Lazy newest-first history reader backed by disposable temporary generation caches."""

    def __init__(self) -> None:
        self._temporary = tempfile.TemporaryDirectory(prefix="azazuley-grimchain-history-")
        self._sources = tuple(path for path in (ACTIVE_JOURNAL, *BACKUP_JOURNALS) if path.exists())
        self._source_index = 0
        self._cache_file = None
        self._mapping = None
        self._right_separator = -1
        self._current_source: Path | None = None
        self._seen_chains: set[str] = set()
        self._exhausted = False

    @property
    def has_more(self) -> bool:
        return not self._exhausted

    def close(self) -> None:
        self._close_generation()
        if self._temporary is not None:
            self._temporary.cleanup()
            self._temporary = None
        self._exhausted = True

    def _close_generation(self) -> None:
        if self._mapping is not None:
            self._mapping.close()
            self._mapping = None
        if self._cache_file is not None:
            self._cache_file.close()
            self._cache_file = None
        self._right_separator = -1
        self._current_source = None

    def _load_next_generation(self) -> bool:
        self._close_generation()
        separator = RECORD_SEPARATOR.encode("utf-8")
        while self._source_index < len(self._sources):
            source = self._sources[self._source_index]
            self._source_index += 1
            cache_path = Path(self._temporary.name) / f"generation-{self._source_index}.bio"
            if source == ACTIVE_JOURNAL:
                shutil.copyfile(source, cache_path)
            else:
                with gzip.open(source, "rb") as input_stream, cache_path.open("wb") as output_stream:
                    shutil.copyfileobj(input_stream, output_stream)
            if cache_path.stat().st_size == 0:
                continue
            cache_file = cache_path.open("rb")
            mapping = mmap.mmap(cache_file.fileno(), 0, access=mmap.ACCESS_READ)
            right_separator = mapping.rfind(separator)
            if right_separator < 0:
                mapping.close()
                cache_file.close()
                raise ValueError(f"GrimChain journal separator is missing in {source}")
            self._cache_file = cache_file
            self._mapping = mapping
            self._right_separator = right_separator
            self._current_source = source
            return True
        self._exhausted = True
        return False

    def fetch(self, limit: int = 40) -> tuple[tuple[str, str, str], ...]:
        if limit <= 0:
            raise ValueError("history fetch limit must be positive")
        records: list[tuple[str, str, str]] = []
        separator = RECORD_SEPARATOR.encode("utf-8")
        while len(records) < limit and not self._exhausted:
            if self._mapping is None and not self._load_next_generation():
                break
            left_separator = self._mapping.rfind(separator, 0, self._right_separator)
            if left_separator < 0:
                self._close_generation()
                continue
            body_start = left_separator + len(separator)
            body = self._mapping[body_start:self._right_separator]
            self._right_separator = left_separator
            if not body.strip():
                continue
            record = _history_record_from_body(body, self._current_source)
            if record[2] in self._seen_chains:
                continue
            self._seen_chains.add(record[2])
            records.append(record)
        return tuple(records)

    def __enter__(self) -> "GrimchainHistorySession":
        return self

    def __exit__(self, _exc_type, _exc, _traceback) -> None:
        self.close()

def _generation_records(path: Path) -> tuple[tuple[str, str, str], ...]:
    """Read one journal generation in its physical oldest-to-newest order."""
    if not path.exists():
        return ()
    if path == ACTIVE_JOURNAL:
        payload = path.read_bytes()
    else:
        with gzip.open(path, "rb") as stream:
            payload = stream.read()
    if not payload:
        return ()
    separator = RECORD_SEPARATOR.encode("utf-8")
    return tuple(
        _history_record_from_body(body, path)
        for body in payload.split(separator)
        if body.strip()
    )


def _write_generation_records(path: Path, records: tuple[tuple[str, str, str], ...]) -> None:
    """Rewrite one generation with exactly the supplied ordered records."""
    if not records:
        if path == ACTIVE_JOURNAL:
            path.write_bytes(b"")
        else:
            path.unlink(missing_ok=True)
        return
    payload = b"".join(
        _record_bytes(user_input, grimchain, timestamp, first_record=index == 0)
        for index, (timestamp, user_input, grimchain) in enumerate(records)
    )
    temporary = path.with_name(path.name + ".tmp")
    try:
        if path == ACTIVE_JOURNAL:
            temporary.write_bytes(payload)
        else:
            with gzip.open(temporary, "wb") as stream:
                stream.write(payload)
        os.replace(temporary, path)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def _remove_existing_chain(grimchain: str) -> str | None:
    """Remove every stored occurrence and return the newest record's original user input."""
    generations: list[tuple[Path, tuple[tuple[str, str, str], ...]]] = []
    preserved_user_input: str | None = None
    for path in (ACTIVE_JOURNAL, *BACKUP_JOURNALS):
        records = _generation_records(path)
        generations.append((path, records))
        if preserved_user_input is None:
            preserved_user_input = next(
                (user_input for _timestamp, user_input, chain in reversed(records) if chain == grimchain),
                None,
            )
    if preserved_user_input is None:
        return None
    for path, records in generations:
        if any(chain == grimchain for _timestamp, _user_input, chain in records):
            _write_generation_records(
                path,
                tuple(record for record in records if record[2] != grimchain),
            )
    return preserved_user_input


def append_grimchain(user_input: str, grimchain: str) -> tuple[str, bool]:
    """Add a new GrimChain once, or promote an existing exact chain to newest history position."""
    if not grimchain:
        raise ValueError("cannot journal an empty GrimChain")
    if "\n" in grimchain or "\r" in grimchain:
        raise ValueError("a journaled GrimChain must occupy exactly one line")

    ensure_grimchain_journal()
    preserved_user_input = _remove_existing_chain(grimchain)
    if preserved_user_input is not None:
        user_input = preserved_user_input
    timestamp = datetime.now().astimezone().isoformat(timespec="seconds")
    entry = _record_bytes(user_input, grimchain, timestamp, first_record=ACTIVE_JOURNAL.stat().st_size == 0)
    rotated = bool(ACTIVE_JOURNAL.stat().st_size and ACTIVE_JOURNAL.stat().st_size + len(entry) > MAX_JOURNAL_BYTES)
    if rotated:
        _rotate()
        entry = _record_bytes(user_input, grimchain, timestamp, first_record=True)
    with ACTIVE_JOURNAL.open("ab") as stream:
        stream.write(entry)
    return timestamp, rotated
