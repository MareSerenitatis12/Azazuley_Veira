"""Ailalubar reflection and exact rendered witness authority.

Ailalubar performs exactly one textual reflection.  Natural visual order is not
computed here: it is witnessed only after the exact HarfBuzz surface has laid
out and painted the reflected text.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json

from azazuley_veira.config.font_runtime import grimchain_face_for_character


class AilalubarRenderError(RuntimeError):
    pass


def _face_id(character: str) -> str:
    face = grimchain_face_for_character(character)
    return f"{face.family}|{face.file.name}"


def _source_face_runs(face_ids: tuple[str, ...]) -> tuple[tuple[int, int, str], ...]:
    if not face_ids:
        return ()
    runs: list[tuple[int, int, str]] = []
    start = 0
    face_id = face_ids[0]
    for index, next_id in enumerate(face_ids[1:], start=1):
        if next_id != face_id:
            runs.append((start, index, face_id))
            start = index
            face_id = next_id
    runs.append((start, len(face_ids), face_id))
    return tuple(runs)


def _rendering_authority_hash(
    source: str,
    face_ids: tuple[str, ...],
    point_size: float,
    layout_direction: str,
) -> str:
    payload = json.dumps(
        {
            "source_positions": tuple(
                (position, glyph, face_ids[position])
                for position, glyph in enumerate(source)
            ),
            "point_size": point_size,
            "layout_direction": layout_direction,
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


@dataclass(frozen=True, slots=True)
class AilalubarReflection:
    """Prosody and exact physical-font provenance before visual layout exists."""

    source: str
    mirrored_source: str
    source_face_ids: tuple[str, ...]
    source_face_runs: tuple[tuple[int, int, str], ...]
    rendering_authority_sha256: str
    point_size: float
    layout_direction: str = "auto"

    def __post_init__(self) -> None:
        extent = len(self.source)
        if self.mirrored_source != self.source[::-1]:
            raise AilalubarRenderError("Ailalubar must perform exactly one textual reflection")
        if len(self.source_face_ids) != extent:
            raise AilalubarRenderError("Ailalubar font provenance changed source extent")
        rebuilt: list[str] = []
        expected_start = 0
        for start, end, face_id in self.source_face_runs:
            if start != expected_start or end <= start or end > extent or not face_id:
                raise AilalubarRenderError("Ailalubar exact face runs are not a closed source partition")
            rebuilt.extend([face_id] * (end - start))
            expected_start = end
        if expected_start != extent or tuple(rebuilt) != self.source_face_ids:
            raise AilalubarRenderError("Ailalubar exact face runs detached from source positions")
        if self.rendering_authority_sha256 != _rendering_authority_hash(
            self.source,
            self.source_face_ids,
            self.point_size,
            self.layout_direction,
        ):
            raise AilalubarRenderError("Ailalubar exact rendering authority hash does not match reflection")


@dataclass(frozen=True, slots=True)
class AilalubarRenderWitness:
    """Final witness emitted from the same exact layout model that paints Ailalubar."""

    source: str
    mirrored_source: str
    visual_text: str
    visual_source_positions: tuple[int, ...]
    visual_levels: tuple[int, ...]
    visual_mirrored_flags: tuple[bool, ...]
    source_face_ids: tuple[str, ...]
    source_face_runs: tuple[tuple[int, int, str], ...]
    rendering_authority_sha256: str
    point_size: float
    layout_direction: str = "auto"

    def __post_init__(self) -> None:
        extent = len(self.source)
        if self.mirrored_source != self.source[::-1]:
            raise AilalubarRenderError("Ailalubar must perform exactly one textual reflection")
        if len(self.visual_source_positions) != extent:
            raise AilalubarRenderError("Ailalubar Cantillation changed source extent")
        if tuple(sorted(self.visual_source_positions)) != tuple(range(extent)):
            raise AilalubarRenderError("Ailalubar Cantillation changed source identity")
        if self.visual_text != "".join(
            self.source[position] for position in self.visual_source_positions
        ):
            raise AilalubarRenderError("Ailalubar Cantillation detached from source coordinates")
        if len(self.visual_levels) != extent or len(self.visual_mirrored_flags) != extent:
            raise AilalubarRenderError("Ailalubar orientation metadata changed source extent")
        if any(level < 0 for level in self.visual_levels):
            raise AilalubarRenderError("Ailalubar bidi level cannot be negative")
        reflection = AilalubarReflection(
            source=self.source,
            mirrored_source=self.mirrored_source,
            source_face_ids=self.source_face_ids,
            source_face_runs=self.source_face_runs,
            rendering_authority_sha256=self.rendering_authority_sha256,
            point_size=self.point_size,
            layout_direction=self.layout_direction,
        )
        del reflection

    @property
    def right_outward_source_positions(self) -> tuple[int, ...]:
        return self.visual_source_positions

    @property
    def left_outward_source_positions(self) -> tuple[int, ...]:
        return self.visual_source_positions[::-1]


def render_ailalubar(source: str, point_size: float) -> AilalubarReflection:
    """Perform Ailalubar's sole transformation: ``source[::-1]``.

    This function does not calculate visual order and does not alter glyphs.
    Cantillation is created later from the exact surface that actually paints
    ``mirrored_source``.
    """
    if not isinstance(source, str):
        raise TypeError("Ailalubar source must be str")
    mirrored = source[::-1]
    if hasattr(point_size, "pointSizeF"):
        point_size = point_size.pointSizeF()
    point_size = float(point_size)
    if point_size <= 0:
        raise ValueError("Ailalubar point size must be positive")
    source_face_ids = tuple(_face_id(character) for character in source)
    return AilalubarReflection(
        source=source,
        mirrored_source=mirrored,
        source_face_ids=source_face_ids,
        source_face_runs=_source_face_runs(source_face_ids),
        rendering_authority_sha256=_rendering_authority_hash(
            source,
            source_face_ids,
            point_size,
            "auto",
        ),
        point_size=point_size,
    )
