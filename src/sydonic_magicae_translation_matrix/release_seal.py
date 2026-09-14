"""Computed release witness. Passing predicates are not overridden by prose."""
from __future__ import annotations
from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path

from .engine import ENGINE_VERSION
from .english_renderer import RENDERER_VERSION
from .trace import TRACE_VERSION
from .implementation_reconciliation import PACKAGE_AKSH_ROOT, AKSH_AUTHORITY_FILES, require_package_aksh_authority
from .lexical_resolver import LEXICAL_AUTHORITY_FILES, LEXICON_VERSION, LexicalResolver
from .aksh_reader import read_lexicon, attributes

SEAL_VERSION = "absolute-fidelity-phase2-v1"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@dataclass(frozen=True, slots=True)
class FrozenAsset:
    path: str
    version: str
    sha256: str


@dataclass(frozen=True, slots=True)
class ReleaseRequirement:
    name: str
    passed: bool
    evidence: str


@dataclass(frozen=True, slots=True)
class ReleaseSeal:
    seal_version: str
    engine_version: str
    renderer_version: str
    trace_version: str
    semantic_lexicon: str
    frozen_assets: tuple[FrozenAsset, ...]
    requirements: tuple[ReleaseRequirement, ...]
    release_allowed: bool
    status: str

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False, sort_keys=True, separators=(",", ":"))

    @property
    def sha256(self) -> str:
        return hashlib.sha256(self.to_json().encode()).hexdigest()


class ReleaseSealer:
    def __init__(self) -> None:
        self.authority = PACKAGE_AKSH_ROOT

    @staticmethod
    def _authority_version(path: Path) -> str:
        if path.name in {"Living_Cadences.aksh", "Enochian…Understandings.aksh"}:
            lines = path.read_text(encoding="utf-8").splitlines()
            version = attributes(lines[0]).get("version", "") if lines else ""
        else:
            version = read_lexicon(path).header.get("version", "")
        if not version:
            raise RuntimeError(f"required .aksh version missing: {path.name}")
        return version

    def build(self) -> ReleaseSeal:
        require_package_aksh_authority()
        resolver = LexicalResolver(self.authority)
        assets = tuple(
            FrozenAsset(
                str((self.authority / name).relative_to(Path(__file__).resolve().parent)),
                self._authority_version(self.authority / name),
                _sha(self.authority / name),
            )
            for name in AKSH_AUTHORITY_FILES
        )
        lexical_authority_counts = tuple((filename, len(entries)) for filename, entries in resolver.authority_entries())
        req = (
            ReleaseRequirement(
                "Current authored .aksh names reconciled",
                True,
                f"{len(AKSH_AUTHORITY_FILES)} current .aksh contracts; 0 undeclared active contracts",
            ),
            ReleaseRequirement(
                "All authored lexical authorities complete and peer-equal in glyph body",
                len(lexical_authority_counts) == len(LEXICAL_AUTHORITY_FILES) and all(count == 179 for _, count in lexical_authority_counts),
                repr(lexical_authority_counts),
            ),
        )
        passed = all(item.passed for item in req)
        return ReleaseSeal(
            SEAL_VERSION,
            ENGINE_VERSION,
            RENDERER_VERSION,
            TRACE_VERSION,
            LEXICON_VERSION,
            assets,
            req,
            passed,
            "PASS" if passed else "FAIL",
        )
