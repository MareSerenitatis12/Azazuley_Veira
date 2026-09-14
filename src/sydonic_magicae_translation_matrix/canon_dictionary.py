"""Static reader for the Canon Glossary AKSH document."""
from __future__ import annotations

from pathlib import Path

from .aksh_reader import closed_field


CANON_DICTIONARY_FILE = Path(__file__).resolve().parent / "data" / "aksh" / "Dictionary.aksh"


def read_canon_dictionary(path: str | Path = CANON_DICTIONARY_FILE) -> str:
    """Return the exact Markdown presentation stored in Dictionary.aksh."""
    source = Path(path)
    if not source.is_file():
        raise RuntimeError(f"Canon Glossary authority is missing: {source}")

    lines = source.read_text(encoding="utf-8").splitlines()
    if not lines:
        raise RuntimeError(f"Canon Glossary authority is empty: {source}")

    markdown: list[str] = []
    for line in lines[1:]:
        parsed = closed_field(line)
        if parsed is None:
            continue
        name, value = parsed
        if name == "line":
            markdown.append(value)

    if not markdown:
        raise RuntimeError(f"Canon Glossary authority has no presentation body: {source}")
    return "\n".join(markdown)
