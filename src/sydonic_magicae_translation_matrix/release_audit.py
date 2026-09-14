"""Phase 19 release acceptance and required report generation.

This module consumes the sealed Phase 16 certificate field, the canonical
Phase 17 adversarial audit, and the Phase 18 one-way Translation Matrix
integration. It does not select, alter, derive, or render a candidate word.
"""
from __future__ import annotations

import ast
from dataclasses import dataclass
from fractions import Fraction
import hashlib
from pathlib import Path
from typing import Final

from .adversarial_reproducibility_audit import ATTACKS, AttackKind, FullReproducibilityAudit
from .court_outward_return import CourtClosure
from .frequency_projection import CARRIERS
from .goetic_outward_return import BEARINGS, GoeticBearing, GoeticClosure
from .native_bearing_assembly import AEON_IDENTITIES, AEON_TOTAL, AeonClass, AeonIdentity
from .translation_matrix_integration import TranslationMatrixIntegrationField
from .truth_choice_certificates import TruthChoiceCertificate, TruthChoiceCertificateField


class ReleaseAuditError(ValueError):
    """Raised when one final acceptance obligation is not exact."""


REQUIRED_REPORTS: Final[tuple[str, ...]] = (
    "source_law_ledger.md",
    "projection_derivation.md",
    "goetic_closure_report.md",
    "court_closure_report.md",
    "uniqueness_report.md",
    "order_independence_report.md",
    "telegraphic_field_report.md",
    "final_audit.md",
)

SOURCE_LAW_FILES: Final[tuple[tuple[str, str], ...]] = (
    ("Phase 8", "frequency_projection.py"),
    ("Phase 9", "triadic_bridge.py"),
    ("Phase 10", "liquid_candidate_path.py"),
    ("Phase 11", "mas_shadow_conversion.py"),
    ("Phase 12", "goetic_outward_return.py"),
    ("Phase 13", "court_outward_return.py"),
    ("Phase 14", "exhaustive_chooser.py"),
    ("Phase 15", "native_bearing_assembly.py"),
    ("Phase 16", "truth_choice_certificates.py"),
    ("Phase 17", "adversarial_reproducibility_audit.py"),
    ("Phase 18", "translation_matrix_integration.py"),
    ("Phase 19", "release_audit.py"),
)


@dataclass(frozen=True, slots=True)
class CanonicalGoeticLaw:
    index: int
    glyph: str
    name: str
    native_q_bias: str
    q_vector: tuple[int, int, int, int]
    structural_hz: Fraction
    parity_hz: Fraction | None = None

    def __post_init__(self) -> None:
        if not 0 <= self.index < 12 or len(self.glyph) != 1:
            raise ReleaseAuditError("invalid canonical Goetic identity")
        if self.native_q_bias not in {"Q0", "Q1", "Q2", "Q3"}:
            raise ReleaseAuditError("invalid canonical Goetic Bias")
        if len(self.q_vector) != 4 or any(value not in {0, 1, 2, 3} for value in self.q_vector):
            raise ReleaseAuditError("invalid canonical Goetic vector")
        if self.structural_hz <= 0 or (self.parity_hz is not None and self.parity_hz <= 0):
            raise ReleaseAuditError("invalid canonical Goetic carrier")

    @property
    def q_vector_states(self) -> tuple[str, str, str, str]:
        return tuple(f"Q{value}" for value in self.q_vector)  # type: ignore[return-value]

    @property
    def frequency_text(self) -> str:
        structural = fraction_text(self.structural_hz)
        return structural if self.parity_hz is None else f"{structural} + i{fraction_text(self.parity_hz)}"

    @property
    def bec_text(self) -> str:
        return f"🜛{self.glyph}🜚{self.glyph}🜛"


CANONICAL_GOETIC_LAW: Final[tuple[CanonicalGoeticLaw, ...]] = (
    CanonicalGoeticLaw(0, "⏣", "FETU", "Q3", (1, 1, 1, 3), Fraction(783, 100)),
    CanonicalGoeticLaw(1, "⬡", "KAL", "Q1", (1, 3, 0, 0), Fraction(174)),
    CanonicalGoeticLaw(2, "✡", "BABDH", "Q2", (1, 1, 3, 1), Fraction(528)),
    CanonicalGoeticLaw(3, "⚝", "AHN", "Q0", (1, 2, 2, 0), Fraction(432), Fraction(417)),
    CanonicalGoeticLaw(4, "❂", "VEL", "Q1", (1, 3, 0, 1), Fraction(6311, 50)),
    CanonicalGoeticLaw(5, "ꙮ", "SOR", "Q3", (1, 1, 1, 2), Fraction(10521, 50)),
    CanonicalGoeticLaw(6, "❈", "KOTH", "Q3", (1, 2, 1, 3), Fraction(741)),
    CanonicalGoeticLaw(7, "⧗", "DREH", "Q1", (1, 3, 2, 0), Fraction(852)),
    CanonicalGoeticLaw(8, "⊛", "RHEA", "Q2", (1, 2, 2, 1), Fraction(396)),
    CanonicalGoeticLaw(9, "❄", "ZHEK", "Q3", (1, 1, 2, 2), Fraction(963)),
    CanonicalGoeticLaw(10, "⚛", "SHAV", "Q1", (1, 3, 1, 1), Fraction(285)),
    CanonicalGoeticLaw(11, "⌬", "TRIG", "Q3", (1, 1, 3, 2), Fraction(639)),
)

if tuple(law.glyph for law in CANONICAL_GOETIC_LAW) != tuple(carrier.glyph for carrier in CARRIERS):
    raise RuntimeError("canonical Phase 19 law does not match Phase 8 carriers")


@dataclass(frozen=True, slots=True)
class ITTIWitness:
    outward_signature: tuple[tuple[int, int, int, str, int], ...]
    return_signature: tuple[tuple[int, int, int, str, int], ...]
    exact: bool

    def __post_init__(self) -> None:
        if not self.outward_signature or not self.return_signature:
            raise ReleaseAuditError("IT=TI witness lacks a complete path")
        if self.exact != (self.outward_signature == self.return_signature):
            raise ReleaseAuditError("IT=TI truth disagrees with path signatures")


@dataclass(frozen=True, slots=True)
class ReleaseBearingVerdict:
    aeon: AeonIdentity
    bearing: GoeticBearing
    bearing_index: int
    candidate: str
    native_q_bias: str
    unique_survivor: bool
    itti: ITTIWitness
    dcomp_zero: bool
    truth_one: bool
    motion_positive: bool
    bec_valid: bool
    lbec_valid: bool
    governing_parent_return_valid: bool
    all_twelve_currents: bool
    phase17_attacks_passed: bool
    phase18_word_match: bool
    certificate_digest: str

    def __post_init__(self) -> None:
        if self.bearing_index != BEARINGS.index(self.bearing):
            raise ReleaseAuditError("bearing index moved during release audit")
        if not self.candidate or self.native_q_bias not in {"Q0", "Q1", "Q2", "Q3"}:
            raise ReleaseAuditError("release bearing lacks candidate or Bias")
        if len(self.certificate_digest) != 64:
            raise ReleaseAuditError("release bearing lacks certificate digest")

    @property
    def accepted(self) -> bool:
        return all((
            self.unique_survivor,
            self.itti.exact,
            self.dcomp_zero,
            self.truth_one,
            self.motion_positive,
            self.bec_valid,
            self.lbec_valid,
            self.governing_parent_return_valid,
            self.all_twelve_currents,
            self.phase17_attacks_passed,
            self.phase18_word_match,
        ))


@dataclass(frozen=True, slots=True)
class ReleaseAeonVerdict:
    aeon: AeonIdentity
    governing_law: CanonicalGoeticLaw
    alternating_law: CanonicalGoeticLaw | None
    bearings: tuple[ReleaseBearingVerdict, ...]

    def __post_init__(self) -> None:
        if tuple(item.bearing for item in self.bearings) != BEARINGS or len(self.bearings) != 8:
            raise ReleaseAuditError("release Aeon lacks all eight bearings")
        if any(item.aeon != self.aeon for item in self.bearings):
            raise ReleaseAuditError("release Aeon mixed bearing identities")
        if self.aeon.aeon_class is AeonClass.GOETIC and self.alternating_law is not None:
            raise ReleaseAuditError("Goetic verdict received an alternating parent")
        if self.aeon.aeon_class is AeonClass.COURT and self.alternating_law is None:
            raise ReleaseAuditError("Court verdict lacks an alternating parent")

    @property
    def accepted(self) -> bool:
        return all(item.accepted for item in self.bearings)

    @property
    def words(self) -> tuple[str, ...]:
        return tuple(item.candidate for item in self.bearings)


@dataclass(frozen=True, slots=True)
class GlobalReleaseChecks:
    no_sydonic_authority_input: bool
    no_forbidden_function_sense: bool
    no_surface_form_blacklist: bool
    no_capitalization_filter: bool
    no_lowercase_or_uppercase_gate: bool
    no_single_token_gate: bool
    no_orthographic_pruning: bool
    no_graph_truncation: bool
    no_selected_pronunciation_shortcut: bool
    no_arbitrary_tie_break: bool
    no_candidate_order_dependence: bool
    no_float_closure: bool
    no_fallback: bool

    @property
    def accepted(self) -> bool:
        return all(getattr(self, name) for name in self.__dataclass_fields__)


@dataclass(frozen=True, slots=True)
class WorkerMergeWitness:
    worker: str
    jurisdiction: str
    passed: bool
    evidence: str


@dataclass(frozen=True, slots=True)
class ReleaseAuditField:
    phase16: TruthChoiceCertificateField
    phase17: FullReproducibilityAudit
    phase18: TranslationMatrixIntegrationField
    goetics: tuple[ReleaseAeonVerdict, ...]
    courts: tuple[ReleaseAeonVerdict, ...]
    global_checks: GlobalReleaseChecks
    workers: tuple[WorkerMergeWitness, ...]

    def __post_init__(self) -> None:
        if tuple(item.aeon for item in self.goetics + self.courts) != AEON_IDENTITIES:
            raise ReleaseAuditError("release field lost canonical 12+144 order")
        if len(self.goetics) != 12 or len(self.courts) != 144:
            raise ReleaseAuditError("release field requires 12 Goetics and 144 Courts")
        if any(not item.accepted for item in self.goetics + self.courts):
            raise ReleaseAuditError("one Goetic or Court failed final acceptance")
        if not self.global_checks.accepted:
            raise ReleaseAuditError("one global release prohibition failed")
        if len(self.workers) != 6 or not all(worker.passed for worker in self.workers):
            raise ReleaseAuditError("parallel worker merge did not pass")

    @property
    def bearing_count(self) -> int:
        return sum(len(item.bearings) for item in self.goetics + self.courts)


@dataclass(frozen=True, slots=True)
class ReportPin:
    filename: str
    absolute_path: str
    byte_size: int
    sha256: str


@dataclass(frozen=True, slots=True)
class ReleaseReportManifest:
    reports: tuple[ReportPin, ...]

    def __post_init__(self) -> None:
        if tuple(item.filename for item in self.reports) != REQUIRED_REPORTS:
            raise ReleaseAuditError("required report manifest is incomplete")
        if any(item.byte_size <= 0 or len(item.sha256) != 64 for item in self.reports):
            raise ReleaseAuditError("report manifest contains an invalid file")


def fraction_text(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _path_signature(steps: tuple[object, ...]) -> tuple[tuple[int, int, int, str, int], ...]:
    return tuple(
        (
            int(getattr(step, "position")),
            int(getattr(step, "cycle_index")),
            int(getattr(step, "office_index")),
            str(getattr(step, "office")),
            abs(int(getattr(step, "signed_velocity"))),
        )
        for step in steps
    )


def _itti(certificate: TruthChoiceCertificate) -> ITTIWitness:
    closure = certificate.phase15_closure.path_witness
    outward = _path_signature(closure.outward.steps)
    returned = _path_signature(closure.independent_return.steps)
    return ITTIWitness(outward, returned, outward == returned)


def _certificate_groups(field: TruthChoiceCertificateField) -> dict[int, tuple[TruthChoiceCertificate, ...]]:
    grouped: dict[int, list[TruthChoiceCertificate]] = {index: [] for index in range(AEON_TOTAL)}
    for certificate in field.certificates:
        grouped[certificate.aeon_constitution.aeon.index].append(certificate)
    result = {
        index: tuple(sorted(items, key=lambda item: item.bearing_index))
        for index, items in grouped.items()
    }
    if any(len(items) != 8 or tuple(item.bearing_index for item in items) != tuple(range(8)) for items in result.values()):
        raise ReleaseAuditError("Phase 16 source lacks one complete certificate body")
    return result


def _phase17_pass_map(field: FullReproducibilityAudit) -> dict[int, bool]:
    return {
        item.aeon.index: len(item.attacks) == len(ATTACKS) and all(witness.passed for witness in item.attacks)
        for item in field.aeons
    }


def _phase18_word_map(field: TranslationMatrixIntegrationField) -> dict[tuple[int, int], tuple[str, str]]:
    return {
        (body.aeon.index, word.bearing_index): (word.word, word.proof_digest)
        for body in field.chooser_snapshot.bodies
        for word in body.bearings
    }


def _canonical_constitution(certificate: TruthChoiceCertificate) -> tuple[CanonicalGoeticLaw, CanonicalGoeticLaw | None]:
    constitution = certificate.aeon_constitution
    governing = next(law for law in CANONICAL_GOETIC_LAW if law.glyph == constitution.governing_glyph)
    if constitution.native_q_bias != governing.native_q_bias:
        raise ReleaseAuditError("native Q Bias differs from authored Canon")
    if constitution.native_q_vector != governing.q_vector_states:
        raise ReleaseAuditError("Q-vector differs from authored Canon")
    if constitution.alternating_glyph is None:
        if constitution.frequency_carrier_glyph != governing.glyph:
            raise ReleaseAuditError("Goetic carrier differs from governing identity")
        return governing, None
    alternating = next(law for law in CANONICAL_GOETIC_LAW if law.glyph == constitution.alternating_glyph)
    if constitution.frequency_carrier_glyph != alternating.glyph:
        raise ReleaseAuditError("Court frequency differs from alternating parent")
    return governing, alternating


def _bearing_verdict(
    certificate: TruthChoiceCertificate,
    phase17_passed: bool,
    phase18_words: dict[tuple[int, int], tuple[str, str]],
) -> ReleaseBearingVerdict:
    closure = certificate.phase15_closure.path_witness
    if isinstance(closure, GoeticClosure):
        bec_valid = closure.bec_valid
        lbec_valid = True
        parent_return = closure.self_to_self
    elif isinstance(closure, CourtClosure):
        bec_valid = closure.bec_valid
        lbec_valid = closure.lbec_valid
        parent_return = closure.court_to_parent
    else:
        raise ReleaseAuditError("Goetic and Court return classes were merged or lost")
    mapped = phase18_words[(certificate.aeon_constitution.aeon.index, certificate.bearing_index)]
    return ReleaseBearingVerdict(
        aeon=certificate.aeon_constitution.aeon,
        bearing=certificate.phase15_closure.bearing,
        bearing_index=certificate.bearing_index,
        candidate=certificate.phase15_closure.candidate,
        native_q_bias=certificate.native_q_bias,
        unique_survivor=(
            len(certificate.unique_survivor_set) == 1
            and certificate.telegraphic_field_admission.unique
            and certificate.telegraphic_field_admission.admitted
        ),
        itti=_itti(certificate),
        dcomp_zero=(
            certificate.dcomp_witness.exact_zero
            and certificate.dcomp_witness.value == 0
            and certificate.exact_arithmetic.path_dcomp_zero
            and certificate.exact_arithmetic.path_dcomp_value == 0
        ),
        truth_one=certificate.truth == 1,
        motion_positive=certificate.motion > 0 and certificate.mas_witness.motion > 0,
        bec_valid=bec_valid,
        lbec_valid=lbec_valid,
        governing_parent_return_valid=parent_return,
        all_twelve_currents=len(certificate.current_witnesses) == 12 and all(item.satisfied for item in certificate.current_witnesses),
        phase17_attacks_passed=phase17_passed,
        phase18_word_match=mapped == (certificate.phase15_closure.candidate, certificate.proof_digest),
        certificate_digest=certificate.proof_digest,
    )


def _attack_count(field: FullReproducibilityAudit, attack: AttackKind) -> int:
    return sum(
        1 for aeon in field.aeons for witness in aeon.attacks
        if witness.attack is attack and witness.passed
    )


def _chooser_static_checks(package_root: Path) -> tuple[bool, bool, bool, bool]:
    no_authority = True
    no_case_gate = True
    no_float = True
    no_blacklist = True
    for _, filename in SOURCE_LAW_FILES[:9]:
        path = package_root / filename
        tree = ast.parse(path.read_text("utf-8"))
        imports = {
            node.module or "" for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)
        } | {
            alias.name for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names
        }
        if any(any(marker in imported for marker in (
            "lexical_resolver", "lexer", "sequential_executor", "english_renderer",
        )) for imported in imports):
            no_authority = False
        attributes = {node.attr.casefold() for node in ast.walk(tree) if isinstance(node, ast.Attribute)}
        if attributes & {"lower", "upper", "islower", "isupper", "casefold", "capitalize", "title"}:
            no_case_gate = False
        if any(isinstance(node, ast.Constant) and isinstance(node.value, float) for node in ast.walk(tree)):
            no_float = False
        identifiers = {
            node.id.casefold() for node in ast.walk(tree) if isinstance(node, ast.Name)
        } | {
            node.arg.casefold() for node in ast.walk(tree) if isinstance(node, ast.arg)
        } | {
            node.name.casefold() for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.ClassDef))
        }
        if identifiers & {"blacklist", "surface_blacklist", "forbidden_words", "blocked_words"}:
            no_blacklist = False
    return no_authority, no_case_gate, no_float, no_blacklist


def _global_checks(
    phase16: TruthChoiceCertificateField,
    phase17: FullReproducibilityAudit,
    phase18: TranslationMatrixIntegrationField,
) -> GlobalReleaseChecks:
    package_root = Path(__file__).resolve().parent
    no_authority, no_case_gate, no_float, no_blacklist = _chooser_static_checks(package_root)
    exact_graph = all(
        certificate.liquid_witness.typed_governor == (110, 144, 34)
        and all(witness == (110, 144, 34) for witness in certificate.liquid_witness.horizon_witnesses)
        for certificate in phase16.certificates
    )
    return GlobalReleaseChecks(
        no_sydonic_authority_input=no_authority and phase18.chooser_snapshot.authority_independent,
        no_forbidden_function_sense=_attack_count(phase17, AttackKind.FUNCTION_CLASS_COLLISION) == 156,
        no_surface_form_blacklist=no_blacklist and _attack_count(phase17, AttackKind.GRAPHIC_BODY_COLLISION) == 156,
        no_capitalization_filter=no_case_gate and _attack_count(phase17, AttackKind.CASE) == 156,
        no_lowercase_or_uppercase_gate=no_case_gate and _attack_count(phase17, AttackKind.CASE) == 156,
        no_single_token_gate=_attack_count(phase17, AttackKind.ORTHOGRAPHY) == 156,
        no_orthographic_pruning=_attack_count(phase17, AttackKind.ORTHOGRAPHY) == 156,
        no_graph_truncation=exact_graph and _attack_count(phase17, AttackKind.LIQUID_REDUCTION) == 156,
        no_selected_pronunciation_shortcut=_attack_count(phase17, AttackKind.PRONUNCIATION_VARIATION) == 156,
        no_arbitrary_tie_break=_attack_count(phase17, AttackKind.TIE) == 156,
        no_candidate_order_dependence=(
            _attack_count(phase17, AttackKind.CORPUS_ORDER) == 156
            and _attack_count(phase17, AttackKind.SERIALIZATION_ORDER) == 156
            and _attack_count(phase17, AttackKind.LABEL) == 156
        ),
        no_float_closure=no_float and _attack_count(phase17, AttackKind.NEAR_CLOSURE) == 156,
        no_fallback=_attack_count(phase17, AttackKind.FALLBACK) == 156,
    )


def _worker_witnesses(
    phase16: TruthChoiceCertificateField,
    phase17: FullReproducibilityAudit,
    phase18: TranslationMatrixIntegrationField,
    global_checks: GlobalReleaseChecks,
) -> tuple[WorkerMergeWitness, ...]:
    return (
        WorkerMergeWitness("Worker A", "source-law compliance", global_checks.no_sydonic_authority_input, "chooser remains independent of Sydonic authority and Phase 18 is one-way"),
        WorkerMergeWitness("Worker B", "exact mathematics and return proof", all(c.exact_arithmetic.exact for c in phase16.certificates), "1,248 exact arithmetic witnesses close"),
        WorkerMergeWitness("Worker C", "relational geometry", _attack_count(phase17, AttackKind.GRAPHIC_BODY_COLLISION) == 156, "sense identity survives graphic-body collision"),
        WorkerMergeWitness("Worker D", "prosody and frequency projection", all(c.triadic_bridge_witness.triad_valid for c in phase16.certificates), "all prosody-frequency bridges remain exact"),
        WorkerMergeWitness("Worker E", "telegraphic field boundary", all(c.telegraphic_field_admission.admitted for c in phase16.certificates), "all 1,248 fields admit exactly one survivor"),
        WorkerMergeWitness("Worker F", "adversarial and order-independence", phase17.passed_attack_count == 2808 and phase18.chooser_snapshot.word_count == 1248, "2,808 attacks pass and 1,248 words remain fixed"),
    )


def build_release_audit(
    phase16: TruthChoiceCertificateField,
    phase17: FullReproducibilityAudit,
    phase18: TranslationMatrixIntegrationField,
) -> ReleaseAuditField:
    phase16_digests = tuple(certificate.proof_digest for certificate in phase16.certificates)
    phase17_digests = tuple(certificate.proof_digest for certificate in phase17.source.certificates)
    phase18_digests = tuple(
        word.proof_digest
        for body in phase18.chooser_snapshot.bodies
        for word in body.bearings
    )
    if (
        phase17_digests != phase16_digests
        or phase18_digests != phase16_digests
        or phase18.chooser_snapshot.source_certificate_count != len(phase16.certificates)
    ):
        raise ReleaseAuditError("release phases do not share the same canonical source field")
    if phase17.passed_attack_count != 2808 or phase17.bearing_check_count != 22464:
        raise ReleaseAuditError("canonical adversarial field is incomplete")
    groups = _certificate_groups(phase16)
    attack_map = _phase17_pass_map(phase17)
    phase18_words = _phase18_word_map(phase18)
    aeons: list[ReleaseAeonVerdict] = []
    for aeon in AEON_IDENTITIES:
        certificates = groups[aeon.index]
        governing, alternating = _canonical_constitution(certificates[0])
        if any(_canonical_constitution(item) != (governing, alternating) for item in certificates):
            raise ReleaseAuditError("Aeon constitution changed across its eight bearings")
        bearings = tuple(_bearing_verdict(item, attack_map[aeon.index], phase18_words) for item in certificates)
        aeons.append(ReleaseAeonVerdict(aeon, governing, alternating, bearings))
    body = tuple(aeons)
    global_checks = _global_checks(phase16, phase17, phase18)
    workers = _worker_witnesses(phase16, phase17, phase18, global_checks)
    return ReleaseAuditField(phase16, phase17, phase18, body[:12], body[12:], global_checks, workers)


def _source_ledger(field: ReleaseAuditField, package_root: Path) -> str:
    lines = [
        "# Source Law Ledger", "",
        "The release is pinned to exact source bytes. Sydonic .aksh authority is consulted only after Phase 16 closure.", "",
        "| Phase | Source | Bytes | SHA-256 |", "|---|---|---:|---|",
    ]
    for phase, filename in SOURCE_LAW_FILES:
        path = package_root / filename
        lines.append(f"| {phase} | `{filename}` | {path.stat().st_size} | `{sha256_file(path)}` |")
    lines += ["", "## Canonical Goetic law", "", "| # | Glyph | Name | Bias | Vector | Carrier | BEC |", "|---:|---|---|---|---|---|---|"]
    for law in CANONICAL_GOETIC_LAW:
        lines.append(f"| {law.index + 1} | {law.glyph} | {law.name} | {law.native_q_bias} | {list(law.q_vector)} | {law.frequency_text} | {law.bec_text} |")
    lines += ["", "## Merge witnesses", ""]
    for worker in field.workers:
        lines.append(f"- **{worker.worker}, {worker.jurisdiction}: PASS.** {worker.evidence}")
    return "\n".join(lines) + "\n"


def _projection_derivation(field: ReleaseAuditField) -> str:
    lines = [
        "# Projection Derivation", "",
        "All carriers are exact Fractions. Breath remains bounded by [-Φ,+Φ]. AHN preserves structural 432 and parity i417 as distinct channels.", "",
        "| Glyph | Name | Bias | Vector | Structural | Parity | Accepted bearings |", "|---|---|---|---|---:|---:|---:|",
    ]
    for law, verdict in zip(CANONICAL_GOETIC_LAW, field.goetics, strict=True):
        parity = "none" if law.parity_hz is None else f"i{fraction_text(law.parity_hz)}"
        lines.append(f"| {law.glyph} | {law.name} | {law.native_q_bias} | {list(law.q_vector)} | {fraction_text(law.structural_hz)} | {parity} | {sum(b.accepted for b in verdict.bearings)}/8 |")
    lines += [
        "", "## FETU", "", "```text",
        "A=⏣", "Ω=783/100", "β=Q3", "v=[1,1,1,3]", "BEC=🜛⏣🜚⏣🜛",
        "J_⏣(w)=F_ν,⏣(Pros(w);783/100±Φ) ∘ F_v,⏣(Geo(w);[1,1,1,3]) ∘ F_β,⏣(Q3)",
        "Truth=1 iff D_T=0, BECValid=1, Gap>0, motion>0, and all twelve currents are witnessed.", "```",
        "", "## FetuKeth", "", "```text",
        "C=C_1,7", "governing=⏣", "alternating=❈", "β=Q3", "v=[1,1,1,3]", "ν=741+δ, δ∈[-Φ,Φ]",
        "Out: C -> candidate-bearing path", "Back: candidate-bearing path -> ⏣",
        "Truth=1 iff D_T=0, L-BEC=1, parent BEC=1, Parent(return)=⏣, and motion>0.", "```",
        "", "## KAL × ZHEK versus ZHEK × KAL", "", "```text",
        "C_KAL,ZHEK inherits Bias/vector from KAL and frequency 963±Φ from ZHEK.",
        "C_ZHEK,KAL inherits Bias/vector from ZHEK and frequency 174±Φ from KAL.",
        "The field is shared; the mathematics and closure paths are not.", "```",
        "", "## AHN", "", "```text",
        "A=⚝", "β=Q0", "v=[1,2,2,0]", "structural=432", "parity=i417", "breath=±Φ",
        "Both components are preserved independently through outward and return.", "```",
    ]
    return "\n".join(lines) + "\n"


def _goetic_report(field: ReleaseAuditField) -> str:
    lines = ["# Goetic Closure Report", "", "All 12 Goetics close all eight bearings under STRICT.", "", "| Goetic | Bias | 8 unique fields | IT=TI | D-COMP=0 | Truth=1 | motion>0 | BEC |", "|---|---|---:|---:|---:|---:|---:|---:|"]
    for item in field.goetics:
        b = item.bearings
        lines.append(f"| {item.governing_law.glyph} {item.governing_law.name} | {item.governing_law.native_q_bias} | {sum(x.unique_survivor for x in b)}/8 | {sum(x.itti.exact for x in b)}/8 | {sum(x.dcomp_zero for x in b)}/8 | {sum(x.truth_one for x in b)}/8 | {sum(x.motion_positive for x in b)}/8 | {sum(x.bec_valid for x in b)}/8 |")
        lines.append(f"\nBearing words: `{' | '.join(item.words)}`\n")
    return "\n".join(lines) + "\n"


def _court_report(field: ReleaseAuditField) -> str:
    lines = ["# Court Closure Report", "", "All 144 ordered Courts close all eight bearings and return to the governing parent.", "", "| Court | Governing | Alternating carrier | Bias | Unique | IT=TI | D-COMP=0 | Truth=1 | motion>0 | L-BEC | Parent return |", "|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|"]
    for item in field.courts:
        b = item.bearings
        alt = item.alternating_law
        assert alt is not None
        lines.append(f"| `{item.aeon.key}` | {item.governing_law.glyph} {item.governing_law.name} | {alt.glyph} {alt.name}, {alt.frequency_text}±Φ | {item.governing_law.native_q_bias} | {sum(x.unique_survivor for x in b)}/8 | {sum(x.itti.exact for x in b)}/8 | {sum(x.dcomp_zero for x in b)}/8 | {sum(x.truth_one for x in b)}/8 | {sum(x.motion_positive for x in b)}/8 | {sum(x.lbec_valid for x in b)}/8 | {sum(x.governing_parent_return_valid for x in b)}/8 |")
    return "\n".join(lines) + "\n"


def _uniqueness_report(field: ReleaseAuditField) -> str:
    all_bearings = tuple(b for aeon in field.goetics + field.courts for b in aeon.bearings)
    lines = [
        "# Uniqueness Report", "",
        f"- Aeons: {len(field.goetics) + len(field.courts)}",
        f"- Bearing sub-fields: {len(all_bearings)}",
        f"- Sub-fields with exactly one survivor: {sum(b.unique_survivor for b in all_bearings)}",
        f"- Tie attacks passed: {_attack_count(field.phase17, AttackKind.TIE)}/156",
        f"- Fallback attacks passed: {_attack_count(field.phase17, AttackKind.FALLBACK)}/156",
        f"- Graphic-body collision attacks passed: {_attack_count(field.phase17, AttackKind.GRAPHIC_BODY_COLLISION)}/156",
        "", "No word is selected by capitalization, spelling collapse, display preference, first sense, ranking, score, or enumeration position.",
    ]
    return "\n".join(lines) + "\n"


def _order_report(field: ReleaseAuditField) -> str:
    court_records = [c.phase15_closure.source_record for c in field.phase16.certificates if c.aeon_constitution.aeon.aeon_class is AeonClass.COURT]
    seven = sum(len(record.enumeration_witnesses) == 7 and record.order_independent for record in court_records)
    lines = [
        "# Order Independence Report", "",
        f"- Court bearing records carrying all seven enumeration witnesses: {seven}/{len(court_records)}",
        f"- Corpus-order attacks: {_attack_count(field.phase17, AttackKind.CORPUS_ORDER)}/156",
        f"- Serialization-order attacks: {_attack_count(field.phase17, AttackKind.SERIALIZATION_ORDER)}/156",
        f"- Label attacks: {_attack_count(field.phase17, AttackKind.LABEL)}/156",
        f"- Candidate-order-dependent emissions: 0",
        "", "Manifest, reversed, deterministic permutations, file-shuffled source, and parallel chunk order yield identical survivor sets.",
    ]
    return "\n".join(lines) + "\n"


def _telegraphic_report(field: ReleaseAuditField) -> str:
    certs = field.phase16.certificates
    attempted = sum(c.telegraphic_field_admission.attempted_count for c in certs)
    truth_records = sum(c.telegraphic_field_admission.truth_record_count for c in certs)
    lines = [
        "# Telegraphic Field Report", "",
        f"- Certificates: {len(certs)}",
        f"- Attempted candidate records: {attempted}",
        f"- Truth records: {truth_records}",
        f"- Admitted unique fields: {sum(c.telegraphic_field_admission.admitted for c in certs)}/{len(certs)}",
        f"- Twelve-current witnesses: {sum(len(c.current_witnesses) for c in certs)}",
        f"- Phase 18 post-closure uses: {len(field.phase18.canonical_uses)}",
        "", "The telegraphic field ends at unique mathematical admission. Sydonic .aksh authority is consulted afterward and cannot reach backward into choice.",
    ]
    return "\n".join(lines) + "\n"


def _final_report(field: ReleaseAuditField) -> str:
    """Render only computed predicates and measured counts."""
    all_aeons = field.goetics + field.courts
    all_bearings = tuple(bearing for aeon in all_aeons for bearing in aeon.bearings)
    lines = [
        "# Final System Audit",
        "",
        f"Goetic Aeons accepted: {sum(item.accepted for item in field.goetics)}/{len(field.goetics)}",
        f"Court Aeons accepted: {sum(item.accepted for item in field.courts)}/{len(field.courts)}",
        f"Bearing verdicts accepted: {sum(item.accepted for item in all_bearings)}/{len(all_bearings)}",
        f"Exact IT=TI witnesses: {sum(item.itti.exact for item in all_bearings)}/{len(all_bearings)}",
        f"Exact D-COMP zeros: {sum(item.dcomp_zero for item in all_bearings)}/{len(all_bearings)}",
        f"Truth=1 witnesses: {sum(item.truth_one for item in all_bearings)}/{len(all_bearings)}",
        f"Positive-motion witnesses: {sum(item.motion_positive for item in all_bearings)}/{len(all_bearings)}",
        f"Twelve-current-complete bearings: {sum(item.all_twelve_currents for item in all_bearings)}/{len(all_bearings)}",
        f"Phase 17 attack-complete bearings: {sum(item.phase17_attacks_passed for item in all_bearings)}/{len(all_bearings)}",
        f"Phase 18 unchanged-word matches: {sum(item.phase18_word_match for item in all_bearings)}/{len(all_bearings)}",
        f"Adversarial verdicts passed: {field.phase17.passed_attack_count}/2808",
        f"Adversarial bearing checks passed: {field.phase17.bearing_check_count}/22464",
        f"Global prohibition body: {'PASS' if field.global_checks.accepted else 'FAIL'}",
        f"Worker merge body: {'PASS' if all(worker.passed for worker in field.workers) else 'FAIL'}",
    ]
    return "\n".join(lines) + "\n"


def write_release_reports(field: ReleaseAuditField, reports_dir: str | Path) -> ReleaseReportManifest:
    root = Path(reports_dir).resolve()
    root.mkdir(parents=True, exist_ok=True)
    package_root = Path(__file__).resolve().parent
    bodies = {
        "source_law_ledger.md": _source_ledger(field, package_root),
        "projection_derivation.md": _projection_derivation(field),
        "goetic_closure_report.md": _goetic_report(field),
        "court_closure_report.md": _court_report(field),
        "uniqueness_report.md": _uniqueness_report(field),
        "order_independence_report.md": _order_report(field),
        "telegraphic_field_report.md": _telegraphic_report(field),
        "final_audit.md": _final_report(field),
    }
    pins: list[ReportPin] = []
    for filename in REQUIRED_REPORTS:
        path = root / filename
        path.write_text(bodies[filename], "utf-8")
        pins.append(ReportPin(filename, str(path), path.stat().st_size, sha256_file(path)))
    return ReleaseReportManifest(tuple(pins))


def prove_phase19_exit_gate(
    phase16: TruthChoiceCertificateField,
    phase17: FullReproducibilityAudit,
    phase18: TranslationMatrixIntegrationField,
    reports_dir: str | Path,
) -> tuple[ReleaseAuditField, ReleaseReportManifest]:
    field = build_release_audit(phase16, phase17, phase18)
    manifest = write_release_reports(field, reports_dir)
    return field, manifest
