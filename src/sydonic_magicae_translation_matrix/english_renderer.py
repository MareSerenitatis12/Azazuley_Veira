"""Phase 11 receiving-language realization from an invariant DomusTrace.

English is downstream clothing. It may realize traced semantic bodies and add
marked function words, but it may not rewrite source lineage or turn structural
presence into vocabulary.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from typing import Literal, Protocol

from .trace import DomusTrace, LexicalUtteranceTrace, RenderingToken

RENDERER_VERSION = "sydonic-office-resolution-v2"

Bearing = Literal["relic", "catalyst", "substrate", "spatial_absolute", "temporal_absolute", "terminal_state", "adversarial", "recursive_identity"]
WordKind = Literal["content", "clothing"]


class RealizationError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class EnglishWord:
    text: str
    kind: WordKind
    source_position: int | None
    source_glyph: str | None
    source_body_id: str | None
    grammatical_bearing: str | None
    clothing_role: str | None = None


@dataclass(frozen=True, slots=True)
class EnglishRendering:
    renderer_version: str
    trace_sha256: str
    style: str
    telegraphic_words: tuple[EnglishWord, ...]
    telegraphic_text: str
    clothing_words: tuple[EnglishWord, ...]
    final_words: tuple[EnglishWord, ...]
    final_text: str
    house_voice_applied: bool
    house_voice_notes: tuple[str, ...]

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False, sort_keys=True, separators=(",", ":"))


class HouseVoiceRealizer(Protocol):
    version: str
    def apply(self, trace: DomusTrace, words: tuple[EnglishWord, ...]) -> tuple[tuple[EnglishWord, ...], tuple[str, ...]]: ...


class SydonicSpokenVoice:
    """Emit the renderer's uttered Aeonic order as the spoken Sydonic form."""

    version = "sydonic-spoken-house-v1"

    def apply(self, trace: DomusTrace, words: tuple[EnglishWord, ...]) -> tuple[tuple[EnglishWord, ...], tuple[str, ...]]:
        return words, ("sydonic translate emits the uttered Aeonic order",)


class EnglishRealizer:
    """Deterministic two-stage English realization with reverse audit."""

    version = RENDERER_VERSION

    def __init__(self, store: object | None = None, house_voice: HouseVoiceRealizer | None = None) -> None:
        if store is not None:
            raise RealizationError("external lexical stores are not accepted by the authored renderer")
        self.store = None
        self.house_voice = house_voice

    def render(self, trace: DomusTrace, *, style: str = "plain") -> EnglishRendering:
        if style not in {"telegraphic", "plain"}:
            raise RealizationError(f"unsupported named style: {style!r}")
        telegraphic = self._telegraphic(trace)
        if self.house_voice is None:
            raise RealizationError("authored HouseVoiceRealizer is required at the House Voice boundary")
        voiced, voice_notes = self.house_voice.apply(trace, telegraphic)
        voice_applied = True
        self._audit_words(voiced, trace)
        clothing: tuple[EnglishWord, ...] = ()
        final = voiced
        if style == "plain":
            clothing, final = self._clothe(voiced)
        result = EnglishRendering(
            renderer_version=self.version,
            trace_sha256=trace.sha256,
            style=style,
            telegraphic_words=voiced,
            telegraphic_text=self._join(voiced),
            clothing_words=clothing,
            final_words=final,
            final_text=self._join(final),
            house_voice_applied=voice_applied,
            house_voice_notes=voice_notes,
        )
        self.reverse_audit(trace, result)
        return result

    def _telegraphic(self, trace: DomusTrace) -> tuple[EnglishWord, ...]:
        out: list[EnglishWord] = []
        tokens = tuple(trace.rendering_input.tokens)

        ostensive_by_position: dict[int, tuple[str, str, str, str]] = {}
        for state in trace.transmutation_traces:
            for position, glyph, body, variant, authority in zip(
                state.vessel_positions,
                state.vessel_glyphs,
                state.ostensive_bodies,
                state.ostensive_variants,
                state.ostensive_authorities,
            ):
                provenance = (glyph, body, variant, authority)
                prior = ostensive_by_position.get(position)
                if prior is not None and prior != provenance:
                    raise RealizationError(
                        "one real lexical vessel received two distinct Phantasmagoria Ostensive selections"
                    )
                # Aeternum may encounter the same finite real vessel more than once.
                # The mirror carries the already-selected Ostensive exactly and does not
                # select a second variant for the same finite real source body.
                ostensive_by_position[position] = provenance

        def emit(token: RenderingToken) -> None:
            if token.preserved_without_lookup:
                return
            ostensive = ostensive_by_position.get(token.source_position)
            if ostensive is not None:
                glyph, body, variant, authority = ostensive
                if glyph != token.glyph:
                    raise RealizationError("ཪ Phantasmagoria provenance changed vessel glyph identity")
                out.append(EnglishWord(
                    text=body,
                    kind="content",
                    source_position=token.source_position,
                    source_glyph=token.glyph,
                    source_body_id=f"{authority}:{token.glyph}:ostensive{variant}",
                    grammatical_bearing="phantasmagoria",
                ))
                return
            if not token.utterances:
                raise RealizationError(
                    f"spoken lexical token {token.glyph!r} at position {token.source_position} lacks authored utterances"
                )
            for utterance in token.utterances:
                out.append(self._realize_utterance(token, utterance))

        for token in tokens:
            emit(token)
        return tuple(out)

    def _realize_utterance(self, token: RenderingToken, utterance: LexicalUtteranceTrace) -> EnglishWord:
        bearing = utterance.grammatical_bearing
        if bearing not in {None, "relic", "catalyst", "substrate", "spatial_absolute", "temporal_absolute", "terminal_state", "adversarial", "recursive_identity"}:
            raise RealizationError(f"unsupported grammatical bearing {bearing!r} for {token.glyph!r}")
        return EnglishWord(
            text=utterance.resolved_state_body,
            kind="content",
            source_position=token.source_position,
            source_glyph=token.glyph,
            source_body_id=f"{utterance.source_authority}:{token.glyph}",
            grammatical_bearing=bearing,
        )

    def _clothe(self, words: tuple[EnglishWord, ...]) -> tuple[tuple[EnglishWord, ...], tuple[EnglishWord, ...]]:
        return (), words

    @staticmethod
    def _join(words: tuple[EnglishWord, ...]) -> str:
        return " ".join(word.text for word in words)

    def reverse_audit(self, trace: DomusTrace, rendering: EnglishRendering) -> None:
        self._audit_words(rendering.final_words, trace)
        content_positions = {
            token.source_position for token in trace.rendering_input.tokens
            if token.utterances
        }
        for word in rendering.final_words:
            if word.kind == "content":
                if word.source_position not in content_positions:
                    raise RealizationError(f"content word lacks traced source body: {word.text!r}")
                if word.source_glyph is None or word.source_body_id is None:
                    raise RealizationError(f"content word has incomplete reverse audit: {word.text!r}")
            elif word.kind == "clothing":
                if word.clothing_role is None:
                    raise RealizationError(f"English support word is not marked as clothing: {word.text!r}")
                if word.source_position is not None or word.source_glyph is not None:
                    raise RealizationError("receiving-language clothing falsely claims a source lexeme")

    @staticmethod
    def _audit_words(words: tuple[EnglishWord, ...], trace: DomusTrace) -> None:
        source_positions = {token.source_position for token in trace.token_traces}
        for word in words:
            if word.kind == "content" and (word.source_position is None or word.source_position not in source_positions):
                raise RealizationError("content word provenance is outside the Aeonic line")
