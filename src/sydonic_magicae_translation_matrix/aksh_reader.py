"""Minimal native reader for Sydonic .aksh authority bodies."""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import re

_FIELD = re.compile(r"^⁖(?P<name>[^჻]+)჻(?P<value>.*)⁖⋰(?P=name)჻$")
_ATTR = re.compile(r"(?P<key>[^\s⧟]+)⧟𝇍(?P<value>.*?)𝇎")
def decode_value(value: str) -> str:
    return value

def field_name(value: str) -> str:
    return value.translate(str.maketrans({"…": "_", "⊹": "_", "∷": "_"}))

def attributes(line: str) -> dict[str, str]:
    return {field_name(m.group("key")): decode_value(m.group("value")) for m in _ATTR.finditer(line)}

def closed_field(line: str) -> tuple[str, str] | None:
    match = _FIELD.match(line)
    if match is None:
        return None
    return field_name(match.group("name")), decode_value(match.group("value"))

@dataclass(frozen=True, slots=True)
class AkshGlyph:
    symbol: str
    category: str
    lookup_attributes: dict[str, str]
    fields: dict[str, str]

@dataclass(frozen=True, slots=True)
class AkshLexicon:
    path: Path
    header: dict[str, str]
    glyphs: tuple[AkshGlyph, ...]

def read_lexicon(path: str | Path) -> AkshLexicon:
    source = Path(path)
    lines = source.read_text(encoding="utf-8").splitlines()
    if not lines:
        raise ValueError(f"empty .aksh authority: {source.name}")
    header = attributes(lines[0])
    glyphs: list[AkshGlyph] = []
    current_symbol: str | None = None
    current_category = ""
    current_lookup: dict[str, str] = {}
    current_fields: dict[str, str] = {}
    def finish() -> None:
        nonlocal current_symbol, current_category, current_lookup, current_fields
        if current_symbol is None:
            return
        glyphs.append(AkshGlyph(current_symbol, current_category, dict(current_lookup), dict(current_fields)))
        current_symbol = None
        current_category = ""
        current_lookup = {}
        current_fields = {}
    for line in lines[1:]:
        if line.startswith("⁖glyph "):
            finish()
            attrs = attributes(line)
            current_symbol = attrs.get("symbol")
            current_category = attrs.get("category", "")
            if not current_symbol:
                raise ValueError(f"{source.name}: glyph declaration lacks symbol")
            continue
        if current_symbol is None:
            continue
        if line.startswith("⁖lookup") and line.endswith("჻"):
            current_lookup = attributes(line)
            continue
        parsed = closed_field(line)
        if parsed is not None:
            name, value = parsed
            current_fields[name] = value
    finish()
    return AkshLexicon(source, header, tuple(glyphs))

def read_enochian_inventory(path: str | Path) -> tuple[tuple[str, ...], tuple[str, ...]]:
    source = Path(path)
    visible: list[str] = []
    non_runtime: list[str] = []
    enoch_count = 0
    for line in source.read_text(encoding="utf-8").splitlines():
        if not line.startswith("⁖enoch "):
            continue
        attrs = attributes(line)
        glyph_text = attrs.get("glyph", "")
        if not glyph_text:
            raise ValueError(f"{source.name}: Enochian Understanding lacks authored glyph identity")
        enoch_count += 1
        is_written_runtime = attrs.get("written") == "true" and attrs.get("parser_trigger") == "true"
        if is_written_runtime:
            if len(glyph_text) != 1:
                raise ValueError(f"runtime Enochian Understanding must use one exact glyph: {glyph_text!r}")
            visible.append(glyph_text)
        else:
            if any(attrs.get(k) != "false" for k in ("tokenized", "written", "spoken", "parser_trigger")):
                raise ValueError(f"non-runtime Enochian Understanding {glyph_text!r} must remain non-tokenized/non-written/non-spoken/non-triggering")
            non_runtime.extend(glyph_text)
    if enoch_count != 10:
        raise ValueError(f"{source.name}: expected 10 authored Enochian Understanding entries, found {enoch_count}")
    return tuple(visible), tuple(dict.fromkeys(non_runtime))
