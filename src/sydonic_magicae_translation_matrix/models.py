"""Immutable structural records for one exact Sydonic Magicae Aeonic line."""
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class GlyphToken:
    value: str
    position: int
    kind: str

    def __post_init__(self) -> None:
        if len(self.value) != 1:
            raise ValueError("GlyphToken.value must be exactly one Unicode code point")

@dataclass(frozen=True, slots=True)
class ReflectedGlyphToken:
    value: str
    mirror_position: int
    source_position: int
    kind: str
    imaginary: bool = True
    prosody_position: int | None = None

    def __post_init__(self) -> None:
        if len(self.value) != 1:
            raise ValueError("ReflectedGlyphToken.value must be exactly one Unicode code point")

@dataclass(frozen=True, slots=True)
class DomusFrame:
    source: str
    tokens: tuple[GlyphToken, ...]
    prosody_source: str | None = None

    def to_source(self) -> str:
        return "".join(token.value for token in self.tokens)

    """
    They do not move their feet, it only changes their bearing,
    It is simply reflected again, as the dancer laughs at the scribe.
    Left, Right, Bow
    """
    def mirror_source(self) -> str:
        return self.source[::-1]

    def mirror_tokens(self) -> tuple[ReflectedGlyphToken, ...]:
        size = len(self.tokens)
        return tuple(
            ReflectedGlyphToken(
                value=token.value,
                mirror_position=size - 1 - token.position,
                source_position=token.position,
                kind=token.kind,
            )
            for token in reversed(self.tokens)
        )

    def reflected_source_position(self, mirror_position: int) -> int:
        if mirror_position < 0 or mirror_position >= len(self.tokens):
            raise IndexError("mirror position outside reflected utterance")
        return len(self.tokens) - 1 - mirror_position

    def mirror_corridor_period(self) -> tuple[ReflectedGlyphToken, ...]:
        """Return one Aeternum period: reflected utterance then original utterance.

        For a real center ``ABCD`` this is ``DCBAABCD``.  Repeating that period
        outward on either side yields the ordinary real-world mirror field around
        the immutable center: ``... ABCD | DCBA | ABCD | DCBA ...``.  The repeated
        images are imaginary traversal only; ``source_position`` always points
        back into the one finite real GrimChain.
        """
        reflected = self.mirror_tokens()
        original = tuple(
            ReflectedGlyphToken(
                value=token.value,
                mirror_position=token.position,
                source_position=token.position,
                kind=token.kind,
            )
            for token in self.tokens
        )
        return reflected + original

    def aeternum_source_position(self, virtual_position: int) -> int:
        """Map an integer mirror-field position onto the finite real center.

        Real positions are ``0..N-1``.  Negative and >=N positions are imaginary
        mirror positions.  With center ``ABCD`` the spatial field around it is
        ``DCBA | ABCD | DCBA`` for virtual positions ``-4..7``.
        """
        extent = len(self.tokens)
        if extent == 0:
            raise ValueError("Aeternum mirror requires a non-empty original utterance")
        phase = virtual_position % (2 * extent)
        return phase if phase < extent else (2 * extent - 1 - phase)

    def aeternum_is_reflected(self, virtual_position: int) -> bool:
        """Whether a virtual position lies in a reflected mirror block."""
        extent = len(self.tokens)
        if extent == 0:
            raise ValueError("Aeternum mirror requires a non-empty original utterance")
        return (virtual_position // extent) % 2 != 0

    def aeternum_token(self, virtual_position: int) -> ReflectedGlyphToken:
        """Return the imaginary token at one position in the infinite mirror field."""
        extent = len(self.tokens)
        source_position = self.aeternum_source_position(virtual_position)
        token = self.tokens[source_position]
        return ReflectedGlyphToken(
            value=token.value,
            mirror_position=virtual_position % extent,
            source_position=source_position,
            kind=token.kind,
            imaginary=not (0 <= virtual_position < extent),
        )

    def mirror_walk(
        self,
        source_position: int,
        count: int,
        step: int,
    ) -> tuple[ReflectedGlyphToken, ...]:
        """Walk outward from a real source position through the Aeternum field.

        ``step`` is the traversal bearing in the spatial field.  Crossing a mirror
        changes which way source positions are encountered; it does not rewrite
        the source or alter an already-resolved grammatical bearing.
        """
        if count < 0:
            raise ValueError("mirror walk count must be non-negative")
        if step not in {-1, 1}:
            raise ValueError("mirror walk step must be -1 or 1")
        extent = len(self.tokens)
        if extent == 0:
            raise ValueError("mirror walk requires the resolved original utterance")
        if source_position < 0 or source_position >= extent:
            raise IndexError("source position outside original utterance")
        start = source_position + step
        return tuple(
            self.aeternum_token(start + step * offset)
            for offset in range(count)
        )
