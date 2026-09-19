"""Azazuley boundary to the bundled Sydonic Magicae stack."""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import secrets

from sydonic_magicae_translation_matrix.engine import (
    EngineError,
    SydonicMagicaeEngine,
    TranslationResult,
)
from sydonic_magicae_translation_matrix.lexical_resolver import ApprovedLexicalEntry
from sydonic_magicae_translation_matrix.english_renderer import SydonicSpokenVoice
from sydonic_magicae_translation_matrix.models import DomusFrame, ReflectedGlyphToken
from azazuley_veira.ailalubar_render import AilalubarRenderWitness

BREATH_SEPARATOR = "𑁦"
OSTENSIVE_PARAGRAPH_PREFIXES = tuple("בגדכפרתךםןףץ")
OSTENSIVE_UTTERANCE_SEPARATOR = ""
OSTENSIVE_PARAGRAPH_SEPARATOR = "\n"
_SYDONIC_ENGINE = SydonicMagicaeEngine(house_voice=SydonicSpokenVoice())



def qt_utf16_units(text: str) -> int:
    return len(text.encode("utf-16-le")) // 2


@dataclass(frozen=True, slots=True)
class PresentationSpan:
    qt_start: int
    qt_end: int
    source_glyph: str
    source_position: int
    source_authority: str
    rendered_text: str
    font_family: str
    semantic_role: str

    def __post_init__(self) -> None:
        if self.qt_start < 0 or self.qt_end < self.qt_start:
            raise ValueError((self.qt_start, self.qt_end))
        if self.qt_end - self.qt_start != qt_utf16_units(self.rendered_text):
            raise ValueError("presentation span extent does not match rendered UTF-16 text")


@dataclass(frozen=True, slots=True)
class DefinitionField:
    label: str
    value: str
    semantic_role: str
    qt_value_start: int
    qt_value_end: int


@dataclass(frozen=True, slots=True)
class DefinitionEntryPresentation:
    source_glyph: str
    source_position: int
    source_authority: str
    fields: tuple[DefinitionField, ...]


@dataclass(frozen=True, slots=True)
class DefinitionPresentation:
    text: str
    entries: tuple[DefinitionEntryPresentation, ...]
    lexical_spans: tuple[PresentationSpan, ...]


@dataclass(frozen=True, slots=True)
class LeySyffEntryPresentation:
    source_glyph: str
    source_position: int
    source_authority: str
    lemma: str
    payload: str
    lemma_span: PresentationSpan
    payload_span: PresentationSpan | None


@dataclass(frozen=True, slots=True)
class LeySyffPresentation:
    text: str
    entries: tuple[LeySyffEntryPresentation, ...]
    spans: tuple[PresentationSpan, ...]


@dataclass(frozen=True, slots=True)
class SourceBodyIdentity:
    source_authority: str
    glyph: str
    ostensive_variant: str | None = None


@dataclass(frozen=True, slots=True)
class ResolvedRenderWord:
    text: str
    source_position: int
    source_glyph: str
    source_body_id: str
    identity: SourceBodyIdentity
    entry: ApprovedLexicalEntry


def select_ostensive_utterances(
    words: tuple[ResolvedRenderWord, ...],
    *,
    randbelow=secrets.randbelow,
) -> tuple[str, ...]:
    """Select complete authored ostensive utterances without rewriting them."""
    utterances: list[str] = []
    for word in words:
        entry = word.entry
        if entry.authored_office == "phantasmagoria":
            variants = entry.ostensive_variants
            utterances.append(variants[randbelow(3)])
            continue
        utterances.append(entry.ostensive)
    return tuple(utterances)

def project_ostensive_paragraphs(
    utterances: tuple[str, ...],
    *,
    randbelow=secrets.randbelow,
) -> str:
    """Group complete ostensive utterances into presentation-only paragraphs."""
    paragraphs: list[str] = []
    position = 0
    while position < len(utterances):
        paragraph_size = randbelow(6) + 1
        paragraph_utterances = utterances[position:position + paragraph_size]
        prefix = OSTENSIVE_PARAGRAPH_PREFIXES[randbelow(len(OSTENSIVE_PARAGRAPH_PREFIXES))]
        paragraphs.append(
            prefix + OSTENSIVE_UTTERANCE_SEPARATOR.join(paragraph_utterances)
        )
        position += len(paragraph_utterances)
    return OSTENSIVE_PARAGRAPH_SEPARATOR.join(paragraphs)


def project_ostensive_presentations(
    words: tuple[ResolvedRenderWord, ...],
    *,
    randbelow=secrets.randbelow,
) -> tuple[LeySyffPresentation, LeySyffPresentation]:
    """Project LeySyff and FfysYel using only the injected presentation randomness."""
    leysyff_utterances = select_ostensive_utterances(words, randbelow=randbelow)
    leysyff_text = project_ostensive_paragraphs(leysyff_utterances, randbelow=randbelow)
    ffysyel_words = tuple(reversed(words))
    ffysyel_utterances = select_ostensive_utterances(ffysyel_words, randbelow=randbelow)
    ffysyel_text = project_ostensive_paragraphs(ffysyel_utterances, randbelow=randbelow)
    return (
        LeySyffPresentation(leysyff_text, (), ()),
        LeySyffPresentation(ffysyel_text, (), ()),
    )

@dataclass(frozen=True, slots=True)
class SydonicRenderTransaction:
    chain: str
    mirror_witness: AilalubarRenderWitness
    result: TranslationResult
    resolved_words: tuple[ResolvedRenderWord, ...]
    azalalia_runs: tuple[PresentationSpan, ...]
    ailalaza_runs: tuple[PresentationSpan, ...]
    definition: DefinitionPresentation
    leysyff: LeySyffPresentation
    ffysyel: LeySyffPresentation

    @property
    def azalalia_body(self) -> str:
        return BREATH_SEPARATOR.join(word.entry.authored_lemma for word in self.resolved_words)


    @property
    def ailalaza_body(self) -> str:
        return BREATH_SEPARATOR.join(word.entry.authored_lemma for word in reversed(self.resolved_words))

    @property
    def glossolalia_body(self) -> str:
        return BREATH_SEPARATOR.join(word.entry.pronunciation for word in self.resolved_words)

    @property
    def ailalossolg_body(self) -> str:
        return BREATH_SEPARATOR.join(word.entry.pronunciation for word in reversed(self.resolved_words))

    @property
    def definition_body(self) -> str:
        return self.definition.text

    @property
    def definition_runs(self) -> tuple[PresentationSpan, ...]:
        return self.definition.lexical_spans

    @property
    def leysyff_body(self) -> str:
        return self.leysyff.text

    @property
    def leysyff_runs(self) -> tuple[PresentationSpan, ...]:
        return self.leysyff.spans
    @property
    def ffysyel_body(self) -> str:
        return self.ffysyel.text

    @property
    def ffysyel_runs(self) -> tuple[PresentationSpan, ...]:
        return self.ffysyel.spans


    @property
    def trace_sha256(self) -> str:
        trace = self.result.semantic_trace
        if trace is None:
            raise EngineError("Azazuley render transaction requires a semantic trace")
        return trace.sha256


def parse_source_body_id(source_body_id: str, grammatical_bearing: str | None) -> SourceBodyIdentity:
    """Parse one renderer source-body ID in one canonical place."""
    if grammatical_bearing == "phantasmagoria":
        source_authority, glyph, ostensive_field = source_body_id.rsplit(":", 2)
        if ostensive_field not in {"ostensiveI", "ostensiveII", "ostensiveIII"}:
            raise EngineError(f"invalid Phantasmagoria Ostensive provenance: {source_body_id!r}")
        return SourceBodyIdentity(source_authority, glyph, ostensive_field.removeprefix("ostensive"))
    source_authority, glyph = source_body_id.rsplit(":", 1)
    return SourceBodyIdentity(source_authority, glyph)


def _resolved_words(
    engine: SydonicMagicaeEngine,
    result: TranslationResult,
    visual_source_positions: tuple[int, ...],
) -> tuple[ResolvedRenderWord, ...]:
    words: list[ResolvedRenderWord] = []
    for word in result.rendering.final_words:
        if (
            word.kind != "content"
            or word.source_position is None
            or word.source_body_id is None
            or word.source_glyph is None
        ):
            continue
        identity = parse_source_body_id(word.source_body_id, word.grammatical_bearing)
        entry = engine.lexical_resolver.entry_from_authority(word.source_glyph, identity.source_authority)
        try:
            prosody_position = visual_source_positions[word.source_position]
        except IndexError as exc:
            raise EngineError(
                f"Sydonic Cantillation position has no Prosody provenance: {word.source_position}"
            ) from exc
        words.append(ResolvedRenderWord(
            text=word.text,
            source_position=prosody_position,
            source_glyph=word.source_glyph,
            source_body_id=word.source_body_id,
            identity=identity,
            entry=entry,
        ))
    return tuple(words)




class _AilalubarSydonicAdapter:
    """Azuzaley-owned adapter from Ailalubar presentation order to Sydonic's generic execution API."""

    def __init__(self, witness: AilalubarRenderWitness, frame: DomusFrame) -> None:
        if frame.source != witness.visual_text:
            raise ValueError("Sydonic frame differs from the completed Ailalubar presentation")
        self.witness = witness
        self.frame = frame

    def token(self, virtual_position: int) -> ReflectedGlyphToken:
        extent = len(self.frame.tokens)
        if extent == 0:
            raise ValueError("Ailalubar traversal requires a non-empty rendered body")
        position = self.frame.aeternum_source_position(virtual_position)
        token = self.frame.tokens[position]
        return ReflectedGlyphToken(
            value=token.value,
            mirror_position=position,
            source_position=position,
            prosody_position=self.witness.visual_source_positions[position],
            kind=token.kind,
            imaginary=not (0 <= virtual_position < extent),
        )

    @staticmethod
    def reorder_pair(
        causal_body_order: list[int],
        left_position: int,
        right_position: int,
        order: tuple[int, int],
    ) -> None:
        if left_position == right_position:
            return
        if set(order) != {left_position, right_position}:
            raise ValueError("Ailalubar pair reorder changed source identity")
        try:
            slots = sorted((
                causal_body_order.index(left_position),
                causal_body_order.index(right_position),
            ))
        except ValueError as exc:
            raise ValueError("Ailalubar pair lost a finite source body") from exc
        causal_body_order[slots[0]] = order[0]
        causal_body_order[slots[1]] = order[1]

    @staticmethod
    def reorder_corridor(
        causal_body_order: list[int],
        source_positions: tuple[int, ...],
        returned_positions: tuple[int, ...],
    ) -> None:
        if set(source_positions) != set(returned_positions):
            raise ValueError("Ailalubar corridor changed finite source identity")
        try:
            slots = sorted(causal_body_order.index(position) for position in source_positions)
        except ValueError as exc:
            raise ValueError("Ailalubar corridor lost a finite source body") from exc
        for slot, position in zip(slots, returned_positions, strict=True):
            causal_body_order[slot] = position


def _written_projection_runs(words: tuple[ResolvedRenderWord, ...]) -> tuple[PresentationSpan, ...]:
    runs: list[PresentationSpan] = []
    offset = 0
    for index, word in enumerate(words):
        if index:
            offset += qt_utf16_units(BREATH_SEPARATOR)
        lemma = word.entry.authored_lemma
        start = offset
        offset += qt_utf16_units(lemma)
        runs.append(PresentationSpan(
            start, offset, word.source_glyph, word.source_position,
            word.identity.source_authority, lemma, word.entry.font, "authored_lexical",
        ))
    return tuple(runs)


@lru_cache(maxsize=32)
def render_transaction(witness: AilalubarRenderWitness) -> SydonicRenderTransaction:
    """Translate the completed Azuzaley Ailalubar presentation through Sydonic's generic matrix API."""
    engine = _SYDONIC_ENGINE
    frame = DomusFrame(
        source=witness.visual_text,
        tokens=engine.lexer.lex(witness.visual_text),
        prosody_source=witness.source,
    )
    adapter = _AilalubarSydonicAdapter(witness, frame)
    result = engine.translate_domus_with_execution(
        domus_string=witness.visual_text,
        target_language="en",
        output_style="telegraphic",
        include_trace=True,
        aeternum_token=adapter.token,
        aeternum_pair_reorder=adapter.reorder_pair,
        aeternum_corridor_reorder=adapter.reorder_corridor,
        parsed_frame=frame,
    )
    resolved = _resolved_words(engine, result, witness.visual_source_positions)

    azalalia_runs = _written_projection_runs(resolved)
    ailalaza_runs = _written_projection_runs(tuple(reversed(resolved)))

    definition_parts: list[str] = []
    definition_runs: list[PresentationSpan] = []
    definition_entries: list[DefinitionEntryPresentation] = []
    definition_offset = 0
    field_specs = (
        ("Word", "authored_lexical"),
        ("Origin Language", "prose"),
        ("Pronunciation", "prose"),
        ("Cadence", "prose"),
        ("Non-Ostensive", "prose"),
        ("Ostensive", "prose"),
        ("LeySyff", "prose"),
        ("GrimChain", "grimchain"),
    )
    for index, word in enumerate(resolved):
        if index:
            separator = "\n\n"
            definition_parts.append(separator)
            definition_offset += qt_utf16_units(separator)
        entry = word.entry
        values = (
            entry.authored_lemma,
            entry.origin_language,
            entry.pronunciation,
            entry.cadence,
            entry.non_ostensive,
            entry.ostensive,
            entry.leysyff,
            entry.grimchain,
        )
        fields: list[DefinitionField] = []
        for line_index, ((label, role), body) in enumerate(zip(field_specs, values, strict=True)):
            if line_index:
                definition_parts.append("\n")
                definition_offset += qt_utf16_units("\n")
            prefix = f"{label}: "
            definition_parts.append(prefix)
            definition_offset += qt_utf16_units(prefix)
            start = definition_offset
            definition_parts.append(body)
            definition_offset += qt_utf16_units(body)
            fields.append(DefinitionField(label, body, role, start, definition_offset))
            if role == "authored_lexical":
                definition_runs.append(PresentationSpan(
                    start, definition_offset, word.source_glyph, word.source_position,
                    word.identity.source_authority, body, entry.font, "definition_word",
                ))
        definition_entries.append(DefinitionEntryPresentation(
            word.source_glyph, word.source_position, word.identity.source_authority, tuple(fields)
        ))
    definition_body = "".join(definition_parts)
    definition = DefinitionPresentation(definition_body, tuple(definition_entries), tuple(definition_runs))

    leysyff, ffysyel = project_ostensive_presentations(resolved)


    return SydonicRenderTransaction(
        chain=witness.source,
        mirror_witness=witness,
        result=result,
        resolved_words=resolved,
        azalalia_runs=azalalia_runs,
        ailalaza_runs=ailalaza_runs,
        definition=definition,
        leysyff=leysyff,
        ffysyel=ffysyel,
    )










