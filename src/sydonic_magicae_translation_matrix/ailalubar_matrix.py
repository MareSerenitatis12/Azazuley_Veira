"""Ailalubar reflective matrix for Sydonic Magicae.

This module consumes a completed visual-mirror witness.  It does not import Qt
or Azazuley.  The finite GrimChain remains the only real source extent; the
visual mirror supplies the parity ordering used only when Aeternum enters an
imaginary reflected block.
"""
from __future__ import annotations

from dataclasses import dataclass

from .engine import EngineError, SydonicMagicaeEngine, TranslationResult
from .models import DomusFrame, ReflectedGlyphToken


class AilalubarMatrixError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class AilalubarMirrorWitness:
    """Translation-only witness of finite source identity and Cantillation order."""

    source: str
    mirrored_source: str
    visual_text: str
    visual_source_positions: tuple[int, ...]

    def __post_init__(self) -> None:
        extent = len(self.source)
        if self.mirrored_source != self.source[::-1]:
            raise AilalubarMatrixError("Ailalubar witness is not the exact reflected GrimChain")
        if len(self.visual_source_positions) != extent:
            raise AilalubarMatrixError("Ailalubar witness changed the selected depth")
        if tuple(sorted(self.visual_source_positions)) != tuple(range(extent)):
            raise AilalubarMatrixError("Ailalubar witness changed finite source identity")
        if self.visual_text != "".join(self.source[position] for position in self.visual_source_positions):
            raise AilalubarMatrixError("Ailalubar visual text detached from its source positions")

    @property
    def right_outward_source_positions(self) -> tuple[int, ...]:
        return self.visual_source_positions

    @property
    def left_outward_source_positions(self) -> tuple[int, ...]:
        return self.visual_source_positions[::-1]


@dataclass(frozen=True, slots=True)
class AilalubarAeternumMatrix:
    witness: AilalubarMirrorWitness

    def cantillation_position(self, virtual_position: int) -> int:
        """Return the active Cantillation-sequence index for Aeternum traversal."""
        extent = len(self.witness.visual_text)
        if extent == 0:
            raise AilalubarMatrixError("Aeternum Cantillation matrix requires a non-empty body")
        _block, offset = divmod(virtual_position, extent)
        return offset

    def prosody_position(self, cantillation_position: int) -> int:
        """Map one Cantillation index back to immutable original-source provenance."""
        if cantillation_position < 0 or cantillation_position >= len(self.witness.visual_source_positions):
            raise IndexError("Cantillation position outside Ailalubar witness")
        return self.witness.visual_source_positions[cantillation_position]

    def token(self, frame: DomusFrame, virtual_position: int) -> ReflectedGlyphToken:
        if frame.source != self.witness.visual_text:
            raise AilalubarMatrixError("Ailalubar Cantillation frame differs from the completed render witness")
        extent = len(frame.tokens)
        cantillation_position = self.cantillation_position(virtual_position)
        token = frame.tokens[cantillation_position]
        return ReflectedGlyphToken(
            value=token.value,
            mirror_position=virtual_position % extent,
            source_position=cantillation_position,
            prosody_position=self.prosody_position(cantillation_position),
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
            raise AilalubarMatrixError("Ailalubar pair reorder changed source identity")
        try:
            slots = sorted((
                causal_body_order.index(left_position),
                causal_body_order.index(right_position),
            ))
        except ValueError as exc:
            raise AilalubarMatrixError("Ailalubar pair lost a finite source body") from exc
        causal_body_order[slots[0]] = order[0]
        causal_body_order[slots[1]] = order[1]

    @staticmethod
    def reorder_corridor(
        causal_body_order: list[int],
        source_positions: tuple[int, ...],
        returned_positions: tuple[int, ...],
    ) -> None:
        if set(source_positions) != set(returned_positions):
            raise AilalubarMatrixError("Ailalubar corridor changed finite source identity")
        try:
            slots = sorted(causal_body_order.index(position) for position in source_positions)
        except ValueError as exc:
            raise AilalubarMatrixError("Ailalubar corridor lost a finite source body") from exc
        for slot, position in zip(slots, returned_positions, strict=True):
            causal_body_order[slot] = position


@dataclass(frozen=True, slots=True)
class AilalubarTranslation:
    result: TranslationResult
    mirror_witness: AilalubarMirrorWitness

    @property
    def translation(self) -> str:
        return self.result.translation


def translate_domus_with_ailalubar(
    engine: SydonicMagicaeEngine,
    *,
    mirror_witness: AilalubarMirrorWitness,
    target_language: str = "en",
    output_style: str = "telegraphic",
    include_trace: bool = True,
) -> AilalubarTranslation:
    """Translate completed Ailalubar Cantillation while preserving Prosody provenance."""
    if target_language != "en":
        raise EngineError(f"unsupported target language: {target_language!r}")
    if output_style not in {"telegraphic", "plain"}:
        raise EngineError(f"unsupported output style: {output_style!r}")

    # Translation executes on the completed rendered Cantillation sequence.
    # Original Prosody remains attached provenance only.
    frame = DomusFrame(
        source=mirror_witness.visual_text,
        tokens=engine.lexer.lex(mirror_witness.visual_text),
        prosody_source=mirror_witness.source,
    )
    matrix = AilalubarAeternumMatrix(mirror_witness)
    try:
        result = engine.translate_domus_with_execution(
            domus_string=mirror_witness.visual_text,
            target_language=target_language,
            output_style=output_style,
            include_trace=include_trace,
            aeternum_token=lambda virtual_position: matrix.token(frame, virtual_position),
            aeternum_pair_reorder=matrix.reorder_pair,
            aeternum_corridor_reorder=matrix.reorder_corridor,
            parsed_frame=frame,
        )
    except Exception as exc:
        if isinstance(exc, (TypeError, EngineError, AilalubarMatrixError)):
            raise
        raise EngineError(
            f"Sydonic Ailalubar pipeline stopped at explicit failure: {exc.__class__.__name__}: {exc}"
        ) from exc
    return AilalubarTranslation(result=result, mirror_witness=mirror_witness)
