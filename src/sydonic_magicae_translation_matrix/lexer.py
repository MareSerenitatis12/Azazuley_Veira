"""Exact code-point lexer for completed Sydonic Magicae Domus strings."""
from __future__ import annotations
from pathlib import Path
from .models import GlyphToken
from .aksh_reader import read_enochian_inventory

class GlyphLexError(ValueError):
    def __init__(self, position: int, value: str, expected: str = "known exact glyph") -> None:
        self.position = position
        self.value = value
        self.expected = expected
        shown = f"U+{ord(value):04X}" if value else "end of input"
        super().__init__(f"glyph lex failure at code-point position {position}: {shown}; expected {expected}")

class ExactGlyphLexer:
    def __init__(self, lexical_glyphs: tuple[str, ...], understandings: str | Path) -> None:
        self.understandings = Path(understandings)
        lexical = tuple(lexical_glyphs)
        grammar, non_runtime_enochs = read_enochian_inventory(self.understandings)
        invalid = [x for x in lexical + grammar + non_runtime_enochs if len(x) != 1]
        if invalid:
            raise ValueError(f"inventory contains non-single-code-point glyphs: {invalid!r}")
        self.lexical_glyphs = frozenset(lexical)
        self.grammar_glyphs = frozenset(grammar)
        self.non_runtime_enoch_glyphs = frozenset(non_runtime_enochs)
        self.known = self.lexical_glyphs | self.grammar_glyphs | {"⛎", "᳀"}

    def classify(self, value: str) -> str:
        if value in self.grammar_glyphs:
            return "grammar"
        if value in self.lexical_glyphs:
            return "lexical"
        if value in {"⛎", "᳀"}:
            return value
        raise KeyError(value)

    def lex(self, source: str) -> tuple[GlyphToken, ...]:
        if not isinstance(source, str):
            raise TypeError("source must be str")
        out: list[GlyphToken] = []
        for position, value in enumerate(source):
            if value not in self.known:
                raise GlyphLexError(position, value)
            out.append(GlyphToken(value=value, position=position, kind=self.classify(value)))
        return tuple(out)
