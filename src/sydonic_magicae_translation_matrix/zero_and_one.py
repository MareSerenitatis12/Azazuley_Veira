"""Zero-and-One source witness for ordinary lexical bodies plus Shadow Locus and Axiomyr.

This module owns the Q0/Q1 special-body boundary and ordinary lexical source
resolution. Living Cadences are authored separately in Living_Cadences.aksh;
Enochian grammar executes in SequentialDomusExecutor.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from typing import Protocol

from tardisha_grimchain.domus import ZERO_MIDDLE_GLYPH, TRIPARTITE_AXIOMYR
from tardisha_grimchain.tripartite import SHADOW_LOCUS_GLYPH as SHADOW_LOCUS, AXIOMYR_GLYPH

from .models import DomusFrame, GlyphToken

class ResolutionCallable(Protocol):
    def __call__(self, glyph: str) -> object: ...

class ZeroAndOneError(RuntimeError):
    pass

@dataclass(frozen=True, slots=True)
class ZeroAndOneEvent:
    position: int
    glyph: str
    token_kind: str
    event: str
    lookup_performed: bool
    lexical_resolution: object | None = None

@dataclass(frozen=True, slots=True)
class ZeroAndOneTrace:
    events: tuple[ZeroAndOneEvent, ...]

    @property
    def lexical_events(self) -> tuple[ZeroAndOneEvent, ...]:
        return tuple(event for event in self.events if event.event == "lexical-resolution")

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)

class ZeroAndOneMachine:
    """Resolve the complete written Aeonic line without positional Q-state."""

    def __init__(self, ordinary_lexical_glyphs: frozenset[str], resolver: ResolutionCallable) -> None:
        self.ordinary_lexical_glyphs = ordinary_lexical_glyphs
        self.resolver = resolver

    def run_frame(self, frame: DomusFrame) -> ZeroAndOneTrace:
        events: list[ZeroAndOneEvent] = []
        owner = getattr(self.resolver, "__self__", None)
        special_resolver = getattr(owner, "resolve_special", None)
        semantic_source = frame.source if frame.prosody_source is None else frame.prosody_source
        shadow_ostensive = semantic_source == ZERO_MIDDLE_GLYPH
        axiomyr_ostensive = semantic_source == TRIPARTITE_AXIOMYR
        for token in frame.tokens:
            glyph = token.value
            if glyph == SHADOW_LOCUS:
                if shadow_ostensive:
                    if special_resolver is None:
                        raise ZeroAndOneError("Shadow Locus Ostensive authority is unavailable")
                    resolution = special_resolver(glyph)
                    events.append(ZeroAndOneEvent(token.position, glyph, token.kind, glyph, True, resolution))
                else:
                    events.append(ZeroAndOneEvent(token.position, glyph, token.kind, glyph, False))
                continue
            if glyph == AXIOMYR_GLYPH:
                if not axiomyr_ostensive:
                    raise ZeroAndOneError("Axiomyr is only valid in the canonical depth-one body ☽᳀☾")
                if special_resolver is None:
                    raise ZeroAndOneError("Axiomyr Ostensive authority is unavailable")
                resolution = special_resolver(glyph)
                events.append(ZeroAndOneEvent(token.position, glyph, token.kind, glyph, True, resolution))
                continue
            if glyph in self.ordinary_lexical_glyphs:
                resolution = self.resolver(glyph)
                events.append(ZeroAndOneEvent(token.position, glyph, token.kind, "lexical-resolution", True, resolution))
                continue
            raise ZeroAndOneError(
                f"grammar glyph {glyph!r} at position {token.position} requires SequentialDomusExecutor"
            )
        trace = ZeroAndOneTrace(tuple(events))
        self._validate_trace(frame.tokens, trace)
        return trace

    def _validate_trace(self, tokens: tuple[GlyphToken, ...], trace: ZeroAndOneTrace) -> None:
        expected_positions = {token.position for token in tokens if token.value in self.ordinary_lexical_glyphs}
        actual_positions = [event.position for event in trace.lexical_events]
        if len(actual_positions) != len(set(actual_positions)):
            raise ZeroAndOneError("a lexical position received more than one resolution record")
        if set(actual_positions) != expected_positions:
            raise ZeroAndOneError("not every ordinary lexical position received exactly one resolution record")
