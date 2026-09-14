"""Phase 18 one-way integration from closed chooser bodies into Sydonic Magicae use.

The chooser boundary is absolute.  ``build_chooser_snapshot`` accepts only the
Phase 16 certificate field and does not import, parse, locate, or inspect Sydonic authority files.
It freezes the 156 STRICT bodies and their 1,248 natively closed bearing words.

The current .aksh Translation Matrix contracts are loaded only after that snapshot exists.  A
Domus use plan may reference a closed bearing and attach authored grammar
operators around that reference.  It has no word field and therefore cannot
replace, derive, score, rank, or reopen a closed bearing.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
from pathlib import Path
from typing import Iterable

from .goetic_outward_return import BEARINGS, GoeticBearing
from .aksh_reader import attributes
from .implementation_reconciliation import AKSH_AUTHORITY_FILES
from .native_bearing_assembly import (
    AEON_IDENTITIES,
    AEON_TOTAL,
    PARTIAL_BODY_LAW,
    AeonIdentity,
    PartialBodyLaw,
    StrictLexicalBody,
)
from .truth_choice_certificates import (
    TruthChoiceCertificate,
    TruthChoiceCertificateField,
)


class TranslationMatrixIntegrationError(ValueError):
    """Raised when a post-chooser use attempts to cross the closed boundary."""



def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _digest(value: object) -> str:
    return _sha256_bytes(repr(value).encode("utf-8"))


def _canonical_aksh_digest(text: str) -> str:
    """Digest the exact authored .aksh logical lines without newline-style dependence."""
    return _digest(tuple(text.splitlines()))


@dataclass(frozen=True, slots=True)
class MatrixContractPin:
    filename: str
    absolute_path: str
    byte_size: int
    sha256: str
    version: str
    semantic_digest: str

    def __post_init__(self) -> None:
        if self.filename not in AKSH_AUTHORITY_FILES:
            raise TranslationMatrixIntegrationError("unknown Translation Matrix .aksh contract")
        if self.byte_size <= 0 or len(self.sha256) != 64 or len(self.semantic_digest) != 64:
            raise TranslationMatrixIntegrationError("Translation Matrix .aksh pin is incomplete")
        if not self.version:
            raise TranslationMatrixIntegrationError("Translation Matrix .aksh pin lacks a version")


@dataclass(frozen=True, slots=True)
class EnochContract:
    enoch_id: str
    glyphs: tuple[str, ...]
    operation_type: str
    presence: str
    order: int | None
    parser_trigger: bool
    written: bool
    spoken: bool

    def __post_init__(self) -> None:
        if not self.enoch_id or not self.glyphs or any(len(glyph) != 1 for glyph in self.glyphs) or not self.operation_type:
            raise TranslationMatrixIntegrationError("Enoch contract is incomplete")
        if self.order is not None and self.order <= 0:
            raise TranslationMatrixIntegrationError("Enoch runtime order must be positive when present")


@dataclass(frozen=True, slots=True)
class CadenceContract:
    cadence_id: str
    glyphs: tuple[str, ...]
    operation_type: str
    presence: str
    parser_trigger: bool
    written: bool
    spoken: bool

    def __post_init__(self) -> None:
        if not self.cadence_id or not self.glyphs or any(len(glyph) != 1 for glyph in self.glyphs) or not self.operation_type:
            raise TranslationMatrixIntegrationError("Living Cadence contract is incomplete")



@dataclass(frozen=True, slots=True)
class TranslationMatrixContracts:
    pins: tuple[MatrixContractPin, ...]
    enochs: tuple[EnochContract, ...]
    cadences: tuple[CadenceContract, ...]
    semantic_digest: str
    byte_manifest_digest: str

    def __post_init__(self) -> None:
        if tuple(pin.filename for pin in self.pins) != AKSH_AUTHORITY_FILES:
            raise TranslationMatrixIntegrationError("Translation Matrix contracts must contain the exact .aksh authority set")
        if len(self.enochs) != 10 or len({item.enoch_id for item in self.enochs}) != 10:
            raise TranslationMatrixIntegrationError("Translation Matrix must preserve the ten authored Enoch entries")
        ordered = tuple(item.order for item in self.enochs)
        if ordered != tuple(range(1, 11)):
            raise TranslationMatrixIntegrationError("Enoch runtime records must preserve authored order 1..10")
        if not all(item.parser_trigger and item.written and item.spoken for item in self.enochs):
            raise TranslationMatrixIntegrationError("all ten Enochs must remain written parser-active spoken grammar")
        if len(self.cadences) != 4 or len({item.cadence_id for item in self.cadences}) != 4:
            raise TranslationMatrixIntegrationError("Translation Matrix must preserve the four authored Living Cadences")
        cadence_by_id = {item.cadence_id: item for item in self.cadences}
        required = {
            "regia…cosmos…above": tuple("☽☉☾"),
            "breath…throughout": (chr(0x11066),),
            "cantillation…chant": (chr(0x0FC2),),
            "magic…subspace…prosody": ("⟠",),
        }
        for cadence_id, glyphs in required.items():
            item = cadence_by_id.get(cadence_id)
            if item is None or item.glyphs != glyphs:
                raise TranslationMatrixIntegrationError(f"Living Cadence identity moved: {cadence_id}")
            if item.parser_trigger or item.written or item.spoken:
                raise TranslationMatrixIntegrationError(f"Living Cadence entered runtime token grammar: {cadence_id}")
        if len(self.semantic_digest) != 64 or len(self.byte_manifest_digest) != 64:
            raise TranslationMatrixIntegrationError("Translation Matrix contract digests are incomplete")

    @property
    def enoch_count(self) -> int:
        return len(self.enochs)

    @property
    def grammar_operators(self) -> tuple[EnochContract, ...]:
        return tuple(sorted((item for item in self.enochs if item.order is not None), key=lambda item: item.order))

    @property
    def active_grammar_glyphs(self) -> frozenset[str]:
        return frozenset(
            glyph
            for enoch in self.enochs
            if enoch.parser_trigger and enoch.written
            for glyph in enoch.glyphs
        )


@dataclass(frozen=True, slots=True)
class ClosedBearingWord:
    aeon: AeonIdentity
    bearing: GoeticBearing
    bearing_index: int
    word: str
    native_q_bias: str
    sense_fingerprint: str
    proof_digest: str
    closure_digest: str
    source_record_digest: str
    grammatical_offices: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.bearing_index != BEARINGS.index(self.bearing):
            raise TranslationMatrixIntegrationError("closed bearing index moved")
        if not self.word or self.native_q_bias not in {"Q0", "Q1", "Q2", "Q3"}:
            raise TranslationMatrixIntegrationError("closed bearing lacks word or native Q Bias")
        for value in (
            self.sense_fingerprint,
            self.proof_digest,
            self.closure_digest,
            self.source_record_digest,
        ):
            if len(value) != 64:
                raise TranslationMatrixIntegrationError("closed bearing lacks an exact source digest")
        if len(set(self.grammatical_offices)) != len(self.grammatical_offices):
            raise TranslationMatrixIntegrationError("grammatical offices were duplicated")

    @property
    def immutable_key(self) -> tuple[int, str, str, str]:
        return (
            self.aeon.index,
            self.bearing.value,
            self.sense_fingerprint,
            self.proof_digest,
        )


@dataclass(frozen=True, slots=True)
class ClosedEightBearingBody:
    aeon: AeonIdentity
    native_q_bias: str
    bearings: tuple[ClosedBearingWord, ...]
    strict_law: PartialBodyLaw
    body_digest: str

    def __post_init__(self) -> None:
        if self.strict_law is not PARTIAL_BODY_LAW or self.strict_law is not PartialBodyLaw.STRICT:
            raise TranslationMatrixIntegrationError("Translation Matrix received a non-STRICT body")
        if tuple(item.bearing for item in self.bearings) != BEARINGS or len(self.bearings) != 8:
            raise TranslationMatrixIntegrationError("Translation Matrix requires all eight closed bearings")
        if any(item.aeon != self.aeon for item in self.bearings):
            raise TranslationMatrixIntegrationError("assembled body mixed Aeon identities")
        if any(item.native_q_bias != self.native_q_bias for item in self.bearings):
            raise TranslationMatrixIntegrationError("assembled body changed native Q Bias")
        if len({item.proof_digest for item in self.bearings}) != 8:
            raise TranslationMatrixIntegrationError("each bearing must retain its own closure certificate")
        if len(self.body_digest) != 64:
            raise TranslationMatrixIntegrationError("assembled body lacks its exact digest")

    def bearing_word(self, bearing: GoeticBearing) -> ClosedBearingWord:
        return self.bearings[BEARINGS.index(bearing)]


@dataclass(frozen=True, slots=True)
class ChooserSnapshot:
    bodies: tuple[ClosedEightBearingBody, ...]
    source_certificate_count: int
    snapshot_digest: str
    authority_independent: bool = True

    def __post_init__(self) -> None:
        if tuple(body.aeon for body in self.bodies) != AEON_IDENTITIES or len(self.bodies) != AEON_TOTAL:
            raise TranslationMatrixIntegrationError("chooser snapshot must preserve all 156 Aeons")
        if self.source_certificate_count != AEON_TOTAL * 8:
            raise TranslationMatrixIntegrationError("chooser snapshot must preserve all 1,248 certificates")
        if not self.authority_independent or len(self.snapshot_digest) != 64:
            raise TranslationMatrixIntegrationError("chooser snapshot lost its authority-independent witness")

    @property
    def word_count(self) -> int:
        return sum(len(body.bearings) for body in self.bodies)

    def body(self, aeon_index: int) -> ClosedEightBearingBody:
        if not 0 <= aeon_index < AEON_TOTAL:
            raise TranslationMatrixIntegrationError("Aeon index lies outside the 156-body field")
        return self.bodies[aeon_index]


@dataclass(frozen=True, slots=True)
class DomusBearingReference:
    aeon_index: int
    bearing: GoeticBearing
    expected_proof_digest: str
    grammar_before: tuple[str, ...] = ()
    grammar_after: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not 0 <= self.aeon_index < AEON_TOTAL:
            raise TranslationMatrixIntegrationError("Domus use references an unknown Aeon")
        if len(self.expected_proof_digest) != 64:
            raise TranslationMatrixIntegrationError("Domus use lacks the pinned bearing certificate")
        if any(len(glyph) != 1 for glyph in self.grammar_before + self.grammar_after):
            raise TranslationMatrixIntegrationError("Domus grammar references must be exact glyphs")


@dataclass(frozen=True, slots=True)
class DomusUsePlan:
    plan_id: str
    references: tuple[DomusBearingReference, ...]

    def __post_init__(self) -> None:
        if not self.plan_id or not self.references:
            raise TranslationMatrixIntegrationError("Domus use plan requires an identity and at least one bearing")


@dataclass(frozen=True, slots=True)
class SydonicMagicaeUseToken:
    closed_word: ClosedBearingWord
    word: str
    native_q_bias: str
    grammatical_offices: tuple[str, ...]
    grammar_before: tuple[str, ...]
    grammar_after: tuple[str, ...]
    proof_digest: str

    def __post_init__(self) -> None:
        if self.word != self.closed_word.word:
            raise TranslationMatrixIntegrationError("Translation Matrix attempted to alter a closed word")
        if self.native_q_bias != self.closed_word.native_q_bias:
            raise TranslationMatrixIntegrationError("Translation Matrix attempted to alter native Q Bias")
        if self.grammatical_offices != self.closed_word.grammatical_offices:
            raise TranslationMatrixIntegrationError("Translation Matrix attempted to alter the closed grammatical office")
        if self.proof_digest != self.closed_word.proof_digest:
            raise TranslationMatrixIntegrationError("Translation Matrix detached the word from its certificate")


@dataclass(frozen=True, slots=True)
class SydonicMagicaeUse:
    plan: DomusUsePlan
    tokens: tuple[SydonicMagicaeUseToken, ...]
    chooser_snapshot_digest: str
    matrix_semantic_digest: str
    use_digest: str

    def __post_init__(self) -> None:
        if len(self.tokens) != len(self.plan.references):
            raise TranslationMatrixIntegrationError("Domus use lost a bearing reference")
        if any(len(value) != 64 for value in (
            self.chooser_snapshot_digest,
            self.matrix_semantic_digest,
            self.use_digest,
        )):
            raise TranslationMatrixIntegrationError("Domus use lacks exact boundary digests")

    @property
    def words(self) -> tuple[str, ...]:
        return tuple(token.word for token in self.tokens)


@dataclass(frozen=True, slots=True)
class TranslationMatrixIntegrationField:
    chooser_snapshot: ChooserSnapshot
    matrix_contracts: TranslationMatrixContracts
    canonical_uses: tuple[SydonicMagicaeUse, ...]

    def __post_init__(self) -> None:
        if len(self.canonical_uses) != AEON_TOTAL:
            raise TranslationMatrixIntegrationError("Phase 18 requires one post-closure use for every Aeon")
        for body, use in zip(self.chooser_snapshot.bodies, self.canonical_uses, strict=True):
            if use.words != tuple(item.word for item in body.bearings):
                raise TranslationMatrixIntegrationError("canonical Domus use changed the assembled eight")
            if use.chooser_snapshot_digest != self.chooser_snapshot.snapshot_digest:
                raise TranslationMatrixIntegrationError("canonical Domus use detached from chooser snapshot")


def _certificate_by_body(field: TruthChoiceCertificateField) -> dict[int, tuple[TruthChoiceCertificate, ...]]:
    grouped: dict[int, list[TruthChoiceCertificate]] = {index: [] for index in range(AEON_TOTAL)}
    for certificate in field.certificates:
        grouped[certificate.aeon_constitution.aeon.index].append(certificate)
    result: dict[int, tuple[TruthChoiceCertificate, ...]] = {}
    for index in range(AEON_TOTAL):
        certificates = tuple(sorted(grouped[index], key=lambda item: item.bearing_index))
        if len(certificates) != 8 or tuple(item.bearing_index for item in certificates) != tuple(range(8)):
            raise TranslationMatrixIntegrationError("certificate field lost an eight-bearing Aeon body")
        result[index] = certificates
    return result



def _compact_closure_digest(certificate: TruthChoiceCertificate) -> str:
    return _digest((
        certificate.aeon_constitution,
        certificate.relational_geometry_witness,
        certificate.envelope_witness,
        certificate.exact_arithmetic,
        certificate.bearing_index,
        certificate.proof_digest,
    ))


def _compact_source_record_digest(certificate: TruthChoiceCertificate) -> str:
    return _digest((
        certificate.telegraphic_field_admission,
        tuple((current.glyph, current.evidence_digest, current.satisfied) for current in certificate.current_witnesses),
        tuple(sorted(certificate.unique_survivor_set)),
        certificate.proof_digest,
    ))

def _closed_word(certificate: TruthChoiceCertificate) -> ClosedBearingWord:
    closure = certificate.phase15_closure
    offices = tuple(dict.fromkeys(
        unit.operator_office
        for unit in certificate.prosody_witness.units
        if unit.operator_office
    ))
    return ClosedBearingWord(
        aeon=closure.aeon,
        bearing=closure.bearing,
        bearing_index=certificate.bearing_index,
        word=closure.candidate,
        native_q_bias=closure.native_q_bias,
        sense_fingerprint=certificate.candidate_sense_identity.structural_fingerprint,
        proof_digest=certificate.proof_digest,
        closure_digest=_compact_closure_digest(certificate),
        source_record_digest=_compact_source_record_digest(certificate),
        grammatical_offices=offices,
    )


def build_chooser_snapshot(field: TruthChoiceCertificateField) -> ChooserSnapshot:
    """Freeze all closed words without touching Sydonic .aksh authority or Domus grammar."""
    grouped = _certificate_by_body(field)
    bodies: list[ClosedEightBearingBody] = []
    for result in field.source.aeons:
        if result.body is None or not isinstance(result.body, StrictLexicalBody):
            raise TranslationMatrixIntegrationError("Phase 18 cannot integrate a failed or partial Aeon")
        certificates = grouped[result.aeon.index]
        bearings = tuple(_closed_word(certificate) for certificate in certificates)
        body_material = (
            result.aeon,
            result.body.native_q_bias,
            tuple(item.immutable_key for item in bearings),
            result.body.partial_body_law.value,
        )
        bodies.append(ClosedEightBearingBody(
            result.aeon,
            result.body.native_q_bias,
            bearings,
            result.body.partial_body_law,
            _digest(body_material),
        ))
    frozen = tuple(bodies)
    snapshot_digest = _digest(tuple((body.aeon.index, body.body_digest) for body in frozen))
    return ChooserSnapshot(frozen, len(field.certificates), snapshot_digest, True)


def _bool_attribute(values: dict[str, str], name: str, glyph: str) -> bool:
    if name not in values:
        raise TranslationMatrixIntegrationError(
            f"Enochian Understanding {glyph!r} lacks required boolean attribute {name!r}"
        )
    raw = values[name].casefold()
    if raw == "true":
        return True
    if raw == "false":
        return False
    raise TranslationMatrixIntegrationError(
        f"invalid boolean attribute {name!r}={values[name]!r} for {glyph!r}"
    )


def _authority_version(filename: str, text: str) -> str:
    lines = text.splitlines()
    if not lines:
        raise TranslationMatrixIntegrationError(f"empty .aksh authority: {filename}")
    version = attributes(lines[0]).get("version", "")
    if not version:
        raise TranslationMatrixIntegrationError(f"required .aksh version missing: {filename}")
    return version


def _enoch_contracts(text: str) -> tuple[EnochContract, ...]:
    enochs: list[EnochContract] = []
    current: dict[str, str] | None = None
    operation_type = ""
    for line in text.splitlines():
        if line.startswith("⁖enoch "):
            if current is not None:
                raise TranslationMatrixIntegrationError("nested Enochian Understanding declaration")
            current = attributes(line)
            operation_type = ""
            continue
        if current is None:
            continue
        if line.startswith("⁖operation "):
            operation_type = attributes(line).get("type", "")
            continue
        if line == "⁖⋰enoch჻":
            glyph_text = current.get("glyph", "")
            enoch_id = current.get("id", "")
            order_text = current.get("order", "")
            if not glyph_text or not enoch_id or not operation_type:
                raise TranslationMatrixIntegrationError(
                    f"Enochian Understanding declaration is incomplete: {current!r}"
                )
            enochs.append(EnochContract(
                enoch_id=enoch_id,
                glyphs=tuple(glyph_text),
                operation_type=operation_type,
                presence=current.get("presence", "runtime"),
                order=int(order_text) if order_text else None,
                parser_trigger=_bool_attribute(current, "parser_trigger", glyph_text),
                written=_bool_attribute(current, "written", glyph_text),
                spoken=_bool_attribute(current, "spoken", glyph_text),
            ))
            current = None
            operation_type = ""
    if current is not None:
        raise TranslationMatrixIntegrationError("unterminated Enochian Understanding declaration")
    return tuple(enochs)


def _cadence_contracts(text: str) -> tuple[CadenceContract, ...]:
    cadences: list[CadenceContract] = []
    current: dict[str, str] | None = None
    operation_type = ""
    for line in text.splitlines():
        if line.startswith("⁖cadence "):
            if current is not None:
                raise TranslationMatrixIntegrationError("nested Living Cadence declaration")
            current = attributes(line)
            operation_type = ""
            continue
        if current is None:
            continue
        if line.startswith("⁖operation "):
            operation_type = attributes(line).get("type", "")
            continue
        if line == "⁖⋰cadence჻":
            glyph_text = current.get("glyph", "")
            cadence_id = current.get("id", "")
            if not glyph_text or not cadence_id or not operation_type:
                raise TranslationMatrixIntegrationError(
                    f"Living Cadence declaration is incomplete: {current!r}"
                )
            cadences.append(CadenceContract(
                cadence_id=cadence_id,
                glyphs=tuple(glyph_text),
                operation_type=operation_type,
                presence=current.get("presence", "ever⊹present"),
                parser_trigger=_bool_attribute(current, "parser_trigger", glyph_text),
                written=_bool_attribute(current, "written", glyph_text),
                spoken=_bool_attribute(current, "spoken", glyph_text),
            ))
            current = None
            operation_type = ""
    if current is not None:
        raise TranslationMatrixIntegrationError("unterminated Living Cadence declaration")
    return tuple(cadences)


def build_translation_matrix_contracts(aksh_root: str | Path) -> TranslationMatrixContracts:
    """Load the sole current .aksh authority body after chooser closure."""
    root_path = Path(aksh_root).resolve()
    pins: list[MatrixContractPin] = []
    semantic_bodies: list[tuple[str, str]] = []
    understandings = ""
    living_cadences = ""
    for filename in AKSH_AUTHORITY_FILES:
        path = root_path / filename
        if not path.is_file():
            raise TranslationMatrixIntegrationError(f"required post-chooser .aksh contract missing: {filename}")
        data = path.read_bytes()
        text = data.decode("utf-8")
        version = _authority_version(filename, text)
        semantic = _canonical_aksh_digest(text)
        pins.append(MatrixContractPin(
            filename,
            str(path),
            len(data),
            _sha256_bytes(data),
            version,
            semantic,
        ))
        semantic_bodies.append((filename, semantic))
        if filename == "Living_Cadences.aksh":
            living_cadences = text
        if filename == "Enochian…Understandings.aksh":
            understandings = text

    if not living_cadences:
        raise TranslationMatrixIntegrationError("Living Cadences .aksh authority is absent")
    if not understandings:
        raise TranslationMatrixIntegrationError("Enochian Understandings .aksh authority is absent")
    enochs = _enoch_contracts(understandings)
    cadences = _cadence_contracts(living_cadences)
    pin_tuple = tuple(pins)
    semantic_digest = _digest(tuple(semantic_bodies))
    byte_manifest_digest = _digest(tuple(
        (pin.filename, pin.byte_size, pin.sha256)
        for pin in pin_tuple
    ))
    return TranslationMatrixContracts(pin_tuple, enochs, cadences, semantic_digest, byte_manifest_digest)


def _validate_plan_grammar(plan: DomusUsePlan, contracts: TranslationMatrixContracts) -> None:
    active = contracts.active_grammar_glyphs
    for reference in plan.references:
        for glyph in reference.grammar_before + reference.grammar_after:
            if glyph not in active:
                raise TranslationMatrixIntegrationError(
                    f"Domus use requested a non-written or non-triggering grammar glyph: {glyph}"
                )


def apply_translation_matrix(
    snapshot: ChooserSnapshot,
    contracts: TranslationMatrixContracts,
    plan: DomusUsePlan,
) -> SydonicMagicaeUse:
    """Use already-closed words.  The plan can reference slots but cannot supply words."""
    _validate_plan_grammar(plan, contracts)
    tokens: list[SydonicMagicaeUseToken] = []
    for reference in plan.references:
        closed = snapshot.body(reference.aeon_index).bearing_word(reference.bearing)
        if reference.expected_proof_digest != closed.proof_digest:
            raise TranslationMatrixIntegrationError("Domus use reference does not match the closed bearing certificate")
        tokens.append(SydonicMagicaeUseToken(
            closed,
            closed.word,
            closed.native_q_bias,
            closed.grammatical_offices,
            reference.grammar_before,
            reference.grammar_after,
            closed.proof_digest,
        ))
    token_tuple = tuple(tokens)
    material = (
        plan,
        tuple((token.closed_word.immutable_key, token.grammar_before, token.grammar_after) for token in token_tuple),
        snapshot.snapshot_digest,
        contracts.semantic_digest,
    )
    return SydonicMagicaeUse(
        plan,
        token_tuple,
        snapshot.snapshot_digest,
        contracts.semantic_digest,
        _digest(material),
    )


def canonical_body_plan(body: ClosedEightBearingBody) -> DomusUsePlan:
    return DomusUsePlan(
        plan_id=f"canonical-eight:{body.aeon.index}:{body.aeon.key}",
        references=tuple(
            DomusBearingReference(
                body.aeon.index,
                closed.bearing,
                closed.proof_digest,
            )
            for closed in body.bearings
        ),
    )


def replay_translation_matrix_use(
    snapshot: ChooserSnapshot,
    contracts: TranslationMatrixContracts,
    use: SydonicMagicaeUse,
) -> SydonicMagicaeUse:
    replay = apply_translation_matrix(snapshot, contracts, use.plan)
    if replay != use:
        raise TranslationMatrixIntegrationError("Domus use did not reproduce from the assembled eight")
    return replay


def prove_phase18_exit_gate(
    field: TruthChoiceCertificateField,
    aksh_root: str | Path,
) -> TranslationMatrixIntegrationField:
    """Close chooser first, load Matrix second, then replay all 156 canonical uses."""
    snapshot = build_chooser_snapshot(field)
    contracts = build_translation_matrix_contracts(aksh_root)
    uses = tuple(
        apply_translation_matrix(snapshot, contracts, canonical_body_plan(body))
        for body in snapshot.bodies
    )
    result = TranslationMatrixIntegrationField(snapshot, contracts, uses)
    for use in result.canonical_uses:
        replay_translation_matrix_use(snapshot, contracts, use)
    return result
