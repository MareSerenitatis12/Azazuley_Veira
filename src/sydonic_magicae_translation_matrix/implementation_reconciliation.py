"""Witness the single current authored .aksh authority body."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .aksh_reader import attributes, read_lexicon

RECONCILIATION_VERSION = "aksh-only-phase14-v1"
AKSH_AUTHORITY_FILES = (
    "SeeD…Body.aksh",
    "Axiomyr…Shadow…Locus.aksh",
    "🜔…Temporal…Absolute.aksh",
    "🜕…Terminal…State.aksh",
    "🜖…Adversarial.aksh",
    "🜗…Recursive…Identity.aksh",
    "🜛…Relic.aksh",
    "🜚…Catalyst.aksh",
    "߷…Substrate.aksh",
    "☍…Spatial…Absolute.aksh",
    "ཪ…Phantasmagoria.aksh",
    "Living_Cadences.aksh",
    "Enochian…Understandings.aksh",
)
STATIC_AKSH_REFERENCE_FILES = ("Dictionary.aksh",)
PACKAGE_AKSH_ROOT = Path(__file__).resolve().parent / "data" / "aksh"


def _authority_version(path: Path) -> str:
    if path.name in {"Living_Cadences.aksh", "Enochian…Understandings.aksh"}:
        lines = path.read_text(encoding="utf-8").splitlines()
        version = attributes(lines[0]).get("version", "") if lines else ""
    else:
        version = read_lexicon(path).header.get("version", "")
    if not version:
        raise RuntimeError(f"required .aksh version missing: {path.name}")
    return version


def require_package_aksh_authority() -> tuple[Path, ...]:
    """Require the exact current .aksh authority set and no peer authority body."""
    expected = set(AKSH_AUTHORITY_FILES) | set(STATIC_AKSH_REFERENCE_FILES)
    actual = {path.name for path in PACKAGE_AKSH_ROOT.glob("*.aksh") if path.is_file()}
    missing = tuple(name for name in AKSH_AUTHORITY_FILES if name not in actual)
    extra = tuple(sorted(actual - expected))
    if missing:
        raise FileNotFoundError(f"required authored .aksh authority missing: {missing}")
    if extra:
        raise RuntimeError(f"undeclared .aksh authority present: {extra}")
    return tuple(PACKAGE_AKSH_ROOT / name for name in AKSH_AUTHORITY_FILES)


@dataclass(frozen=True, slots=True)
class ComponentWitness:
    logical_name: str
    physical_paths: tuple[str, ...]
    status: str
    note: str


@dataclass(frozen=True, slots=True)
class ReconciliationReport:
    version: str
    root: str
    mappings: tuple[ComponentWitness, ...]
    authority_versions: tuple[tuple[str, str], ...]
    undeclared_contracts_present: tuple[str, ...]
    status: str


def build_reconciliation() -> ReconciliationReport:
    paths = require_package_aksh_authority()
    expected = set(AKSH_AUTHORITY_FILES) | set(STATIC_AKSH_REFERENCE_FILES)
    actual = {path.name for path in PACKAGE_AKSH_ROOT.glob("*.aksh") if path.is_file()}
    undeclared = tuple(sorted(actual - expected))
    office_names = AKSH_AUTHORITY_FILES[2:11]
    mappings = (
        ComponentWitness(
            "seed-identity",
            ("data/aksh/SeeD…Body.aksh",),
            "active",
            "exact authored SeeD lexical inventory",
        ),
        ComponentWitness(
            "canonical-special-bodies",
            ("data/aksh/Axiomyr…Shadow…Locus.aksh",),
            "active",
            "exact authored Axiomyr and Shadow Locus bodies",
        ),
        ComponentWitness(
            "authored-office-projections",
            tuple(f"data/aksh/{name}" for name in office_names),
            "active",
            "nine exact authored office inventories including Phantasmagoria",
        ),
        ComponentWitness(
            "living-cadences",
            ("data/aksh/Living_Cadences.aksh",),
            "active",
            "four authored Living Cadences present regardless of communication style",
        ),
        ComponentWitness(
            "enochian-understandings",
            ("data/aksh/Enochian…Understandings.aksh",),
            "active",
            "single current authored Enochian Understandings body",
        ),
    )
    versions = tuple((path.name, _authority_version(path)) for path in paths)
    return ReconciliationReport(
        RECONCILIATION_VERSION,
        str(PACKAGE_AKSH_ROOT),
        mappings,
        versions,
        undeclared,
        "RECONCILED",
    )
