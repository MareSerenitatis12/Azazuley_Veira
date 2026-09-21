"""Production font authority for Azazuley's engine-facing rendering.

Azazuley-private fantasy/custom fonts resolve from the installed /usr/local/share/fonts/azazuley custom office. Standard historical Unicode and GrimChain faces resolve through the host font system. Et Sonyera remains the explicit user-selected font surface.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
import ctypes
import os
import sys

from fontTools.ttLib import TTFont



if sys.platform == "win32":
    FONT_ROOT = Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts" / "azazuley"
elif sys.platform == "darwin":
    FONT_ROOT = Path("/Library/Fonts/azazuley")
else:
    FONT_ROOT = Path("/usr/local/share/fonts/azazuley")
FONT_SUFFIXES = frozenset({".ttf", ".otf"})
EXPECTED_AZAZULEY_PRIVATE_FONT_COUNT = 76
FANTASY_LEXICAL_AUTHORITIES = frozenset(("SeeD…Body.aksh", "ཪ…Phantasmagoria.aksh"))
DEFAULT_POINT_SIZE = 9

CANONICAL_REGULAR_FONT_FILES = {
    "Daedra": "Daedra.otf",
    "Dovahkiin": "Dovahkiin.otf",
    "Falmer": "Falmer.otf",
    "Iokharic": "Iokharic.otf",
    "Mage Script": "Mage Script.otf",
    "Rellanic": "Rellanic.otf",
    "Tengwar Annatar": "tngan.ttf",
    "Tirion Sarati": "TirionSarati-BWOd.ttf",
}

@dataclass(frozen=True, slots=True)
class GrimChainFace:
    family: str
    file: Path

_FONT_FAMILY_BY_FILE: dict[Path, str] = {}


def _font_identity(path: Path) -> tuple[str, str]:
    """Read family and style directly from one physical font file."""
    with TTFont(path, lazy=False) as font:
        names = font["name"]
        family = names.getDebugName(16) or names.getDebugName(1)
        style = names.getDebugName(17) or names.getDebugName(2) or "Regular"
        if not family:
            raise RuntimeError(f"physical font exposes no family name: {path}")
    return family, style


@lru_cache(maxsize=1)
def grimchain_display_codepoints() -> frozenset[int]:
    """Return the TardiSHA-visible GrimChain code points accepted by Azuzaley surfaces."""
    from tardisha_grimchain.living_alphabet import DAEMONIC_TONGUE
    return frozenset(ord(glyph) for glyph in (*DAEMONIC_TONGUE, "᳀", "⛎", "𑁦", "࿂", "⟠"))


class _FcFontSet(ctypes.Structure):
    _fields_ = (
        ("nfont", ctypes.c_int),
        ("sfont", ctypes.c_int),
        ("fonts", ctypes.POINTER(ctypes.c_void_p)),
    )


_USE_FONTCONFIG = sys.platform.startswith("linux")
_FC = None
_SYSTEM_FONT_SET: ctypes.POINTER(_FcFontSet) | None = None

if _USE_FONTCONFIG:
    _FC = ctypes.CDLL("libfontconfig.so.1")
    _FC.FcInit.argtypes = []
    _FC.FcInit.restype = ctypes.c_int
    _FC.FcPatternCreate.argtypes = []
    _FC.FcPatternCreate.restype = ctypes.c_void_p
    _FC.FcPatternDestroy.argtypes = [ctypes.c_void_p]
    _FC.FcPatternDestroy.restype = None
    _FC.FcPatternAddString.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_char_p]
    _FC.FcPatternAddString.restype = ctypes.c_int
    _FC.FcConfigGetCurrent.argtypes = []
    _FC.FcConfigGetCurrent.restype = ctypes.c_void_p
    _FC.FcConfigSubstitute.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_int]
    _FC.FcConfigSubstitute.restype = ctypes.c_int
    _FC.FcDefaultSubstitute.argtypes = [ctypes.c_void_p]
    _FC.FcDefaultSubstitute.restype = None
    _FC.FcFontMatch.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.POINTER(ctypes.c_int)]
    _FC.FcFontMatch.restype = ctypes.c_void_p
    _FC.FcFontSort.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_int, ctypes.POINTER(ctypes.c_void_p), ctypes.POINTER(ctypes.c_int)]
    _FC.FcFontSort.restype = ctypes.POINTER(_FcFontSet)
    _FC.FcPatternGetString.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_int, ctypes.POINTER(ctypes.c_char_p)]
    _FC.FcPatternGetString.restype = ctypes.c_int
    _FC.FcPatternGetCharSet.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_int, ctypes.POINTER(ctypes.c_void_p)]
    _FC.FcPatternGetCharSet.restype = ctypes.c_int
    _FC.FcCharSetHasChar.argtypes = [ctypes.c_void_p, ctypes.c_uint]
    _FC.FcCharSetHasChar.restype = ctypes.c_int
    if not _FC.FcInit():
        raise RuntimeError("Fontconfig initialization failed")


def _fontconfig_config() -> int:
    config = _FC.FcConfigGetCurrent()
    if not config:
        raise RuntimeError("Fontconfig has no current configuration")
    return int(config)


def _prepare_fontconfig_pattern(pattern: int) -> None:
    config = _fontconfig_config()
    if not _FC.FcConfigSubstitute(config, pattern, 0):
        raise RuntimeError("Fontconfig pattern substitution failed")
    _FC.FcDefaultSubstitute(pattern)


def _fontconfig_family_match(font_family: str) -> Path:
    pattern = _FC.FcPatternCreate()
    if not pattern:
        raise RuntimeError("Fontconfig could not create a family pattern")
    matched = None
    try:
        if not _FC.FcPatternAddString(pattern, b"family", font_family.encode("utf-8")):
            raise RuntimeError(f"Fontconfig could not add family: {font_family!r}")
        if not _FC.FcPatternAddString(pattern, b"style", b"Regular"):
            raise RuntimeError("Fontconfig could not request the regular style")
        _prepare_fontconfig_pattern(pattern)
        result = ctypes.c_int()
        matched = _FC.FcFontMatch(_fontconfig_config(), pattern, ctypes.byref(result))
        if not matched:
            raise RuntimeError(f"Fontconfig returned no match for family {font_family!r}")
        file_value = ctypes.c_char_p()
        if _FC.FcPatternGetString(matched, b"file", 0, ctypes.byref(file_value)) != 0 or not file_value.value:
            raise RuntimeError("Fontconfig family match exposes no physical font file")
        path = Path(file_value.value.decode("utf-8"))
        if not path.is_file():
            raise RuntimeError(f"Fontconfig returned a missing font file: {path}")
        return path
    finally:
        if matched:
            _FC.FcPatternDestroy(matched)
        _FC.FcPatternDestroy(pattern)


def _system_font_set() -> ctypes.POINTER(_FcFontSet):
    global _SYSTEM_FONT_SET
    if _SYSTEM_FONT_SET is not None:
        return _SYSTEM_FONT_SET
    pattern = _FC.FcPatternCreate()
    if not pattern:
        raise RuntimeError("Fontconfig could not create the system fallback pattern")
    try:
        _prepare_fontconfig_pattern(pattern)
        result = ctypes.c_int()
        font_set = _FC.FcFontSort(_fontconfig_config(), pattern, 1, None, ctypes.byref(result))
        if not font_set or font_set.contents.nfont <= 0:
            raise RuntimeError("Fontconfig returned an empty system fallback set")
        _SYSTEM_FONT_SET = font_set
        return font_set
    finally:
        _FC.FcPatternDestroy(pattern)


def _native_font_roots() -> tuple[Path, ...]:
    if sys.platform == "win32":
        windows = Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts"
        local = Path(os.environ.get("LOCALAPPDATA", str(Path.home() / "AppData/Local"))) / "Microsoft" / "Windows" / "Fonts"
        return (windows / "tardisha", windows / "azazuley", windows, local)
    if sys.platform == "darwin":
        return (Path("/Library/Fonts/tardisha"), Path("/Library/Fonts/azazuley"), Path("/Library/Fonts"), Path("/System/Library/Fonts"), Path.home() / "Library" / "Fonts")
    return ()


@lru_cache(maxsize=1)
def _native_font_files() -> tuple[Path, ...]:
    seen: set[Path] = set()
    files: list[Path] = []
    for root in _native_font_roots():
        if not root.is_dir():
            continue
        for path in sorted(root.rglob("*"), key=lambda value: str(value).casefold()):
            if not path.is_file() or path.suffix.lower() not in FONT_SUFFIXES or path in seen:
                continue
            seen.add(path)
            files.append(path)
    return tuple(files)


@lru_cache(maxsize=1)
def _native_font_records() -> tuple[tuple[Path, str, frozenset[int]], ...]:
    records: list[tuple[Path, str, frozenset[int]]] = []
    for path in _native_font_files():
        try:
            with TTFont(path, fontNumber=0, lazy=True) as font:
                names = font["name"]
                family = names.getDebugName(16) or names.getDebugName(1)
                cmap = frozenset((font.getBestCmap() or {}).keys())
        except Exception:
            continue
        if family:
            records.append((path, family, cmap))
    return tuple(records)


@lru_cache(maxsize=256)
def system_font_file_for_family(font_family: str) -> Path:
    if not font_family:
        raise ValueError("system font family must be non-empty")
    if _USE_FONTCONFIG:
        path = _fontconfig_family_match(font_family)
        physical_family, _style = _font_identity(path)
        if physical_family != font_family:
            raise RuntimeError(f"system font resolver substituted {physical_family!r} for required family {font_family!r}")
        return path
    for path, family, _cmap in _native_font_records():
        if family == font_family:
            return path
    raise RuntimeError(f"system font resolver returned no exact family {font_family!r}")


@lru_cache(maxsize=256)
def system_font_file_for_codepoint(codepoint: int) -> Path:
    if not 0 <= codepoint <= 0x10FFFF:
        raise ValueError(f"Unicode code point outside range: {codepoint}")
    if _USE_FONTCONFIG:
        font_set = _system_font_set()
        for index in range(font_set.contents.nfont):
            pattern = font_set.contents.fonts[index]
            charset = ctypes.c_void_p()
            if _FC.FcPatternGetCharSet(pattern, b"charset", 0, ctypes.byref(charset)) != 0 or not charset.value:
                continue
            if not _FC.FcCharSetHasChar(charset, codepoint):
                continue
            file_value = ctypes.c_char_p()
            if _FC.FcPatternGetString(pattern, b"file", 0, ctypes.byref(file_value)) != 0 or not file_value.value:
                continue
            path = Path(file_value.value.decode("utf-8"))
            if not path.is_file():
                raise RuntimeError(f"Fontconfig fallback set returned a missing font file: {path}")
            return path
        raise RuntimeError(f"system font fallback set has no face for U+{codepoint:04X}")
    for path, _family, cmap in _native_font_records():
        if codepoint in cmap:
            return path
    raise RuntimeError(f"system font fallback set has no face for U+{codepoint:04X}")


@lru_cache(maxsize=256)
def grimchain_face_for_character(character: str) -> GrimChainFace:
    """Resolve a standard GrimChain Unicode glyph through the host font system."""
    if len(character) != 1:
        raise ValueError("GrimChain face routing accepts exactly one Unicode code point")
    codepoint = ord(character)
    if codepoint not in grimchain_display_codepoints():
        raise RuntimeError(f"GrimChain display code point is outside TardiSHA's visible body: U+{codepoint:04X}")
    path = system_font_file_for_codepoint(codepoint)
    family, _style = _font_identity(path)
    return GrimChainFace(family, path)


@dataclass(frozen=True, slots=True)
class InstalledFontBody:
    root: Path
    files: tuple[Path, ...]
    families: tuple[str, ...]


_LOADED_BODY: InstalledFontBody | None = None
_FONT_FILES_BY_FAMILY: dict[str, tuple[Path, ...]] = {}


def installed_font_files() -> tuple[Path, ...]:
    """Return Azazuley's private installed font body."""
    if not FONT_ROOT.is_dir():
        raise RuntimeError(f"Azazuley production font authority is missing: {FONT_ROOT}")
    files = tuple(
        sorted(
            path
            for path in FONT_ROOT.rglob("*")
            if path.is_file()
            and path.suffix.lower() in FONT_SUFFIXES
        )
    )
    if len(files) != EXPECTED_AZAZULEY_PRIVATE_FONT_COUNT:
        raise RuntimeError(
            f"Azazuley private font authority must contain exactly "
            f"{EXPECTED_AZAZULEY_PRIVATE_FONT_COUNT} fonts: "
            f"{FONT_ROOT} -> {len(files)}"
        )
    return files


def load_installed_fonts() -> InstalledFontBody:
    """Index Azazuley custom/fantasy fonts only; standard fonts remain system-resolved."""
    global _LOADED_BODY, _FONT_FILES_BY_FAMILY, _FONT_FAMILY_BY_FILE
    if _LOADED_BODY is not None:
        return _LOADED_BODY
    files = installed_font_files()
    families: set[str] = set()
    family_files: dict[str, list[Path]] = {}
    family_by_file: dict[Path, str] = {}
    for path in files:
        family, _style = _font_identity(path)
        families.add(family)
        family_files.setdefault(family, []).append(path)
        family_by_file[path] = family
    _FONT_FILES_BY_FAMILY = {family: tuple(sorted(paths)) for family, paths in family_files.items()}
    _FONT_FAMILY_BY_FILE = family_by_file
    _LOADED_BODY = InstalledFontBody(
        root=FONT_ROOT,
        files=files,
        families=tuple(sorted(families, key=str.casefold)),
    )
    return _LOADED_BODY


@lru_cache(maxsize=1)
def _system_font_families() -> tuple[str, ...]:
    if _USE_FONTCONFIG:
        font_set = _system_font_set()
        families: set[str] = set()
        for index in range(font_set.contents.nfont):
            value = ctypes.c_char_p()
            pattern = font_set.contents.fonts[index]
            if _FC.FcPatternGetString(pattern, b"family", 0, ctypes.byref(value)) == 0 and value.value:
                families.add(value.value.decode("utf-8"))
        return tuple(sorted(families, key=str.casefold))
    return tuple(sorted({family for _path, family, _cmap in _native_font_records()}, key=str.casefold))

def installed_font_families() -> tuple[str, ...]:
    """Return custom fantasy and normal system-installed font families available to Et Sonyera."""
    if _LOADED_BODY is None:
        raise RuntimeError("Azazuley production fonts have not been loaded yet")
    return tuple(sorted(set(_LOADED_BODY.families).union(_system_font_families()), key=str.casefold))



@lru_cache(maxsize=256)
def authored_lexical_font_file(font_family: str, source_authority: str) -> Path:
    """Resolve custom fantasy faces explicitly; standard families through the host font system."""
    if _LOADED_BODY is None:
        raise RuntimeError("Azazuley production fonts have not been loaded yet")
    candidates = _FONT_FILES_BY_FAMILY.get(font_family, ())
    azazuley_candidates = tuple(path for path in candidates if path.is_relative_to(FONT_ROOT))
    if azazuley_candidates:
        if source_authority not in FANTASY_LEXICAL_AUTHORITIES:
            raise RuntimeError(
                f"fantasy lexical font is outside its authored authorities: "
                f"{source_authority!r} -> {font_family!r}"
            )
        if len(azazuley_candidates) == 1:
            return azazuley_candidates[0]
        canonical_name = CANONICAL_REGULAR_FONT_FILES.get(font_family)
        canonical = tuple(path for path in azazuley_candidates if path.name == canonical_name)
        if len(canonical) != 1:
            raise RuntimeError(
                f"authored fantasy family does not resolve to one canonical physical face: "
                f"{font_family!r} -> {azazuley_candidates!r}"
            )
        return canonical[0]
    return system_font_file_for_family(font_family)


def physical_font_family(font_file: Path) -> str:
    """Return the physical family for an authored or system-resolved font file."""
    path = Path(font_file)
    indexed = _FONT_FAMILY_BY_FILE.get(path)
    if indexed is not None:
        return indexed
    if not path.is_file():
        raise RuntimeError(f"physical font file does not exist: {path}")
    family, _style = _font_identity(path)
    return family


def et_sonyera_font_file(font_family: str) -> Path:
    """Resolve custom fantasy selections explicitly and standard selections through Fontconfig."""
    if not font_family:
        raise RuntimeError("Et Sonyera font family is empty")
    if _LOADED_BODY is None:
        raise RuntimeError("Azazuley production fonts have not been loaded yet")
    candidates = _FONT_FILES_BY_FAMILY.get(font_family, ())
    if not candidates:
        return system_font_file_for_family(font_family)
    if len(candidates) == 1:
        return candidates[0]
    canonical_name = CANONICAL_REGULAR_FONT_FILES.get(font_family)
    canonical = tuple(path for path in candidates if path.name == canonical_name)
    if len(canonical) == 1:
        return canonical[0]
    raise RuntimeError(
        f"Et Sonyera custom family does not resolve to one authored physical face: {font_family!r} -> {candidates!r}"
    )
