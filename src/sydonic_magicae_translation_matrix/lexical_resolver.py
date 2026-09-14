"""Exact-glyph resolver for the nine authored Sydonic Magicae lexical offices."""
from __future__ import annotations

from dataclasses import asdict, dataclass
import json
import secrets
from pathlib import Path
from .aksh_reader import read_lexicon, field_name


OFFICE_FILES: dict[str, tuple[str, str]] = {
    "recursive_identity": ("🜗…Recursive…Identity.aksh", "🜗"),
    "relic": ("🜛…Relic.aksh", "🜛"),
    "spatial_absolute": ("☍…Spatial…Absolute.aksh", "☍"),
    "temporal_absolute": ("🜔…Temporal…Absolute.aksh", "🜔"),
    "catalyst": ("🜚…Catalyst.aksh", "🜚"),
    "substrate": ("߷…Substrate.aksh", "߷"),
    "terminal_state": ("🜕…Terminal…State.aksh", "🜕"),
    "adversarial": ("🜖…Adversarial.aksh", "🜖"),
    "phantasmagoria": ("ཪ…Phantasmagoria.aksh", "ཪ"),
}
SEED_FILE = "SeeD…Body.aksh"
SPECIAL_FILE = "Axiomyr…Shadow…Locus.aksh"
SPECIAL_GLYPHS = frozenset({"᳀", "⛎"})

# These are the ten peer-aligned 179-glyph lexical/office authorities.
# The two-body Axiomyr/Shadow authority is intentionally separate.
LEXICAL_AUTHORITY_FILES: tuple[str, ...] = (SEED_FILE, *(filename for filename, _ in OFFICE_FILES.values()))
LEXICON_VERSION = "nine-office-three-definition-v3"
GRAMMAR_VERSION = "enochian-understandings-v1"


class LexicalResolverError(RuntimeError):
    pass


class UnknownGlyphError(LexicalResolverError):
    pass





@dataclass(frozen=True, slots=True)
class ApprovedLexicalEntry:
    glyph: str
    authored_lemma: str
    pronunciation: str
    origin_language: str
    font: str
    cadence: str
    non_ostensive: str
    ostensive: str
    leysyff: str
    grimchain: str
    category: str
    source_authority: str
    authored_office: str
    ostensive_variants: tuple[str, str, str] = ()


@dataclass(frozen=True, slots=True)
class LexicalResolution:
    source_glyph: str
    resolved_body: str
    traversal_path: tuple[str, ...]
    semantic_lexicon_version: str
    grammar_version: str
    non_ostensive: str
    ostensive: str
    leysyff: str
    source_authority: str
    authored_office: str
    ostensive_variant: str | None = None

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False, sort_keys=True, separators=(",", ":"))


class LexicalResolver:
    def __init__(self, authority_root: str | Path) -> None:
        self.authority_dir = Path(authority_root).resolve()
        if not self.authority_dir.is_dir():
            raise LexicalResolverError(f"authored .aksh root is not a directory: {self.authority_dir}")
        self.seed_path = self.authority_dir / SEED_FILE
        self.special_path = self.authority_dir / SPECIAL_FILE
        self.office_paths = {
            office: self.authority_dir / filename
            for office, (filename, _) in OFFICE_FILES.items()
        }
        missing = tuple(str(path) for path in (self.seed_path, self.special_path, *self.office_paths.values()) if not path.is_file())
        if missing:
            raise LexicalResolverError(f"authored lexical authority set incomplete: {missing}")
        self._authority_versions: dict[str, str] = {}
        self._seed_entries = self._load_seed_inventory(self.seed_path)
        self._special_entries = self._load_special_inventory(self.special_path)
        self._office_entries = {
            office: self._load_inventory(
                path,
                office=office,
                expected_enoch=OFFICE_FILES[office][1],
                allow_unfilled=(office == "phantasmagoria"),
            )
            for office, path in self.office_paths.items()
        }
        self._validate_alignment()

    def _record_authority_version(self, path: Path, version: str) -> None:
        if not version:
            raise LexicalResolverError(f"{path.name}: required .aksh version missing")
        self._authority_versions[path.name] = version

    def _entry_from_aksh(self, item, *, office: str, source_name: str, allow_unfilled: bool) -> ApprovedLexicalEntry:
        values = item.fields
        required_fields = [
            "word",
            "pronunciation",
            "origin_language",
            "font",
            "cadence",
            "non_ostensive",
            "grimchain",
        ]
        if office == "phantasmagoria":
            required_fields.extend(("ostensiveI", "ostensiveII", "ostensiveIII"))
        elif not allow_unfilled:
            required_fields.append("ostensive")
        missing = tuple(name for name in required_fields if name not in values)
        if missing:
            raise LexicalResolverError(f"{source_name}: glyph {item.symbol!r} lacks required authored fields {missing!r}")

        word = values.get("word", "")
        pronunciation = values.get("pronunciation", "")
        origin_language = values.get("origin_language", "")
        font = values.get("font", "")
        cadence = values.get("cadence", "")
        non_ostensive = values.get("non_ostensive", "")
        ostensive = values.get("ostensive", "")
        ostensive_variants = (
            values.get("ostensiveI", ""),
            values.get("ostensiveII", ""),
            values.get("ostensiveIII", ""),
        ) if office == "phantasmagoria" else ()
        leysyff = values.get("leysyff", "")
        grimchain = values.get("grimchain", "")
        return ApprovedLexicalEntry(
            item.symbol, word, pronunciation, origin_language, font, cadence, non_ostensive, ostensive,
            leysyff, grimchain, item.category, source_name, office, ostensive_variants,
        )

    def _load_seed_inventory(self, path: Path) -> dict[str, ApprovedLexicalEntry]:
        body = read_lexicon(path)
        self._record_authority_version(path, body.header.get("version", ""))
        entries: dict[str, ApprovedLexicalEntry] = {}
        for item in body.glyphs:
            if len(item.symbol) != 1 or item.symbol in entries:
                raise LexicalResolverError(f"{path.name}: invalid or duplicate exact glyph key {item.symbol!r}")
            entries[item.symbol] = self._entry_from_aksh(item, office="seed_identity", source_name=path.name, allow_unfilled=False)
        if len(entries) != 179:
            raise LexicalResolverError(f"{path.name}: expected 179 lexical entries, found {len(entries)}")
        return entries

    def _load_special_inventory(self, path: Path) -> dict[str, ApprovedLexicalEntry]:
        body = read_lexicon(path)
        self._record_authority_version(path, body.header.get("version", ""))
        entries: dict[str, ApprovedLexicalEntry] = {}
        for item in body.glyphs:
            if len(item.symbol) != 1 or item.symbol in entries:
                raise LexicalResolverError(f"{path.name}: invalid or duplicate exact glyph key {item.symbol!r}")
            entries[item.symbol] = self._entry_from_aksh(
                item, office=field_name(item.category), source_name=path.name, allow_unfilled=False
            )
        if frozenset(entries) != SPECIAL_GLYPHS or len(entries) != 2:
            raise LexicalResolverError(
                f"{path.name}: expected exactly the Axiomyr and Shadow Locus glyphs {tuple(sorted(SPECIAL_GLYPHS))!r}"
            )
        expected_categories = {"᳀": "axiomyr", "⛎": "shadow_locus"}
        actual_categories = {glyph: field_name(entry.category) for glyph, entry in entries.items()}
        if actual_categories != expected_categories:
            raise LexicalResolverError(
                f"{path.name}: special body categories changed: {actual_categories!r}"
            )
        return entries

    def _load_inventory(self, path: Path, *, office: str, expected_enoch: str, allow_unfilled: bool) -> dict[str, ApprovedLexicalEntry]:
        body = read_lexicon(path)
        self._record_authority_version(path, body.header.get("version", ""))
        entries: dict[str, ApprovedLexicalEntry] = {}
        for item in body.glyphs:
            if len(item.symbol) != 1 or item.symbol in entries:
                raise LexicalResolverError(f"{path.name}: invalid or duplicate exact glyph key {item.symbol!r}")
            if field_name(item.lookup_attributes.get("office", "")) != office:
                raise LexicalResolverError(f"{path.name}: glyph {item.symbol!r} lookup office is not {office!r}")
            if item.lookup_attributes.get("enoch") != expected_enoch:
                raise LexicalResolverError(f"{path.name}: glyph {item.symbol!r} lookup Enoch is not {expected_enoch!r}")
            entries[item.symbol] = self._entry_from_aksh(item, office=office, source_name=path.name, allow_unfilled=allow_unfilled)
        if len(entries) != 179:
            raise LexicalResolverError(f"{path.name}: expected 179 lexical entries, found {len(entries)}")
        return entries

    def _validate_alignment(self) -> None:
        inventories = tuple(self._office_entries.items())
        reference_name = "seed_identity"
        reference_entries = self._seed_entries
        reference_glyphs = frozenset(reference_entries)
        if len(reference_glyphs) != 179:
            raise LexicalResolverError(f"{reference_name} must carry exactly 179 exact glyph keys")
        for name, entries in inventories:
            glyphs = frozenset(entries)
            if glyphs != reference_glyphs:
                missing = tuple(sorted(reference_glyphs - glyphs))
                extra = tuple(sorted(glyphs - reference_glyphs))
                raise LexicalResolverError(
                    f"{name} glyph set differs from {reference_name}: missing={missing!r}, extra={extra!r}"
                )
        reference_categories = {glyph: reference_entries[glyph].category for glyph in reference_glyphs}
        for name, entries in inventories:
            categories = {glyph: entries[glyph].category for glyph in reference_glyphs}
            if categories != reference_categories:
                raise LexicalResolverError(
                    f"{name} disagrees with {reference_name} on authored glyph category identity"
                )
        self.glyph_order = tuple(reference_entries)
        self.glyph_categories = reference_categories
        self.lexical_glyphs = reference_glyphs

    def office_entry(self, glyph: str, office: str) -> ApprovedLexicalEntry:
        if office not in self._office_entries:
            raise LexicalResolverError(f"unsupported authored office: {office!r}")
        try:
            return self._office_entries[office][glyph]
        except KeyError as exc:
            raise UnknownGlyphError(f"unknown ordinary lexical glyph: {glyph!r}") from exc


    @staticmethod
    def _resolution(entry: ApprovedLexicalEntry, glyph: str) -> LexicalResolution:
        return LexicalResolution(
            source_glyph=glyph,
            resolved_body=entry.authored_lemma,
            traversal_path=(f"{entry.source_authority}:{glyph}",),
            semantic_lexicon_version=LEXICON_VERSION,
            grammar_version=GRAMMAR_VERSION,
            non_ostensive=entry.non_ostensive,
            ostensive=entry.ostensive,
            leysyff=entry.leysyff,
            source_authority=entry.source_authority,
            authored_office=entry.authored_office,
        )

    def resolve(self, glyph: str) -> LexicalResolution:
        try:
            entry = self._seed_entries[glyph]
        except KeyError as exc:
            raise UnknownGlyphError(f"unknown ordinary lexical glyph: {glyph!r}") from exc
        return self._resolution(entry, glyph)

    def resolve_special(self, glyph: str) -> LexicalResolution:
        """Resolve one of the two contextual Ostensive special bodies.

        Callers are responsible for enforcing the GrimChain depth context. The
        resolver only provides exact authored body lookup.
        """
        try:
            entry = self._special_entries[glyph]
        except KeyError as exc:
            raise UnknownGlyphError(f"unknown Axiomyr/Shadow special glyph: {glyph!r}") from exc
        return self._resolution(entry, glyph)

    def resolve_office(self, glyph: str, office: str) -> LexicalResolution:
        entry = self.office_entry(glyph, office)
        if office == "phantasmagoria":
            ostensives = entry.ostensive_variants
            index = secrets.randbelow(3)
            variant = ("I", "II", "III")[index]
            return LexicalResolution(
                source_glyph=glyph,
                resolved_body=ostensives[index],
                traversal_path=(f"{entry.source_authority}:{glyph}:ostensive{variant}",),
                semantic_lexicon_version=LEXICON_VERSION,
                grammar_version=GRAMMAR_VERSION,
                non_ostensive=entry.non_ostensive,
                ostensive=ostensives[index],
                leysyff=entry.leysyff,
                source_authority=entry.source_authority,
                authored_office=entry.authored_office,
                ostensive_variant=variant,
            )
        return self._resolution(entry, glyph)

    def authority_entries(self) -> tuple[tuple[str, tuple[ApprovedLexicalEntry, ...]], ...]:
        """Return the ten peer-aligned 179-glyph lexical/office inventories."""
        return (
            (self.seed_path.name, tuple(self._seed_entries.values())),
            *((self.office_paths[office].name, tuple(entries.values())) for office, entries in self._office_entries.items()),
        )

    def special_authority_entries(self) -> tuple[tuple[str, tuple[ApprovedLexicalEntry, ...]], ...]:
        return ((self.special_path.name, tuple(self._special_entries.values())),)

    def all_authority_entries(self) -> tuple[tuple[str, tuple[ApprovedLexicalEntry, ...]], ...]:
        return (*self.authority_entries(), *self.special_authority_entries())

    def authority_version_items(self) -> tuple[tuple[str, str], ...]:
        return tuple(
            (filename, self._authority_versions[filename])
            for filename, _entries in self.all_authority_entries()
        )

    def entry_from_authority(self, glyph: str, source_authority: str) -> ApprovedLexicalEntry:
        if source_authority == self.special_path.name:
            try:
                return self._special_entries[glyph]
            except KeyError as exc:
                raise UnknownGlyphError(f"unknown Axiomyr/Shadow special glyph: {glyph!r}") from exc
        if source_authority == self.seed_path.name:
            try:
                return self._seed_entries[glyph]
            except KeyError as exc:
                raise UnknownGlyphError(f"unknown ordinary lexical glyph: {glyph!r}") from exc
        for office, path in self.office_paths.items():
            if source_authority == path.name:
                return self.office_entry(glyph, office)
        raise LexicalResolverError(f"unknown authored source authority: {source_authority!r}")

    def define_word(self, word: str) -> ApprovedLexicalEntry:
        matches = tuple(
            entry
            for _, entries in self.all_authority_entries()
            for entry in entries
            if entry.authored_lemma and entry.authored_lemma == word
        )
        if not matches:
            raise LexicalResolverError(f"unknown authored lexical word: {word!r}")
        if len(matches) != 1:
            authorities = tuple(entry.source_authority for entry in matches)
            raise LexicalResolverError(
                f"authored lexical word is not unique: {word!r}; authorities={authorities!r}"
            )
        return matches[0]


    def office_entries(self, office: str) -> tuple[ApprovedLexicalEntry, ...]:
        if office not in self._office_entries:
            raise LexicalResolverError(f"unsupported authored office: {office!r}")
        return tuple(self._office_entries[office].values())
