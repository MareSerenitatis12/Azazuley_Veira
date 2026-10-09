"""Exact source-stable Sydonic support for Orobouros Tail ⟲.

Orobouros Tail ⟲ does not rewrite the finite Real GrimChain. Its written positions activate
the already-existing Aeternum relation and remain distinct temporal seams.
Their positions and separations are preserved exactly; no universal stride,
sign, cancellation, destination, mirror count, or replacement string is
assigned here.
"""
from __future__ import annotations

from dataclasses import dataclass

from .models import DomusFrame, ReflectedGlyphToken

TEMPORAL_OPERATOR_GLYPH = "⟲"


class TemporalOperatorError(RuntimeError):
    """Raised when the written temporal geometry is structurally inconsistent."""


@dataclass(frozen=True, slots=True)
class TemporalSeam:
    position: int
    previous_position: int | None
    next_position: int | None
    distance_from_previous: int | None
    intervening_from_previous: int | None


@dataclass(frozen=True, slots=True)
class TemporalGeometry:
    source: str
    operator_positions: tuple[int, ...]
    seams: tuple[TemporalSeam, ...]

    def __post_init__(self) -> None:
        if tuple(sorted(self.operator_positions)) != self.operator_positions:
            raise TemporalOperatorError("⟲ positions must remain in written source order")
        if len(set(self.operator_positions)) != len(self.operator_positions):
            raise TemporalOperatorError("each written ⟲ position must remain distinct")


@dataclass(frozen=True, slots=True)
class AeternumAddressWitness:
    virtual_position: int
    source_position: int
    glyph: str
    kind: str
    imaginary: bool


@dataclass(frozen=True, slots=True)
class TemporalCrossing:
    operator_position: int
    entrance_virtual_position: int
    mirror_virtual_position: int
    source_position: int
    temporal_parsecs: int


@dataclass(frozen=True, slots=True)
class TailTransformation:
    operator_position: int
    run_positions: tuple[int, ...]
    start: int
    stop: int
    before_positions: tuple[int, ...]
    after_positions: tuple[int, ...]
    crossing: TemporalCrossing


@dataclass(frozen=True, slots=True)
class TailResolution:
    source_positions: tuple[int, ...]
    execution_positions: tuple[int, ...]
    transformations: tuple[TailTransformation, ...]
    completed: bool = True


def resolve_tail(frame: DomusFrame) -> TailResolution:
    """Resolve written Tail runs before the other Enochians execute.

    Each adjacent Tail performs one turn of the same window. A separated run
    ends that window; the next run continues after the processed seam, over
    the body produced by the previous run. Source coordinates never change.
    """
    source = tuple(token.position for token in frame.tokens)
    if source != tuple(range(len(frame.tokens))):
        raise TemporalOperatorError("Tail requires exact contiguous source coordinates")
    runs: list[list[int]] = []
    for position in temporal_operator_positions(frame):
        if runs and position == runs[-1][-1] + 1:
            runs[-1].append(position)
        else:
            runs.append([position])
    order = list(source)
    transformations: list[TailTransformation] = []
    start = 0
    for index, run in enumerate(runs):
        stop = min(order.index(pos) for pos in runs[index + 1]) if index + 1 < len(runs) else len(order)
        for operator_position in run:
            before = tuple(order[start:stop])
            after = tuple(reversed(before))
            order[start:stop] = after
            transformations.append(TailTransformation(
                operator_position, tuple(run), start, stop, before, after,
                temporal_crossing(frame, operator_position),
            ))
        start = max(order.index(pos) for pos in run) + 1
    result = TailResolution(source, tuple(order), tuple(transformations))
    validate_tail_resolution(frame, result)
    return result


def validate_tail_resolution(frame: DomusFrame, resolution: TailResolution) -> None:
    """Replay every turn; matching final order alone cannot prove execution."""
    source = tuple(token.position for token in frame.tokens)
    if source != tuple(range(len(frame.tokens))) or frame.to_source() != frame.source:
        raise TemporalOperatorError("Tail source identity does not round-trip exactly")
    if not resolution.completed or resolution.source_positions != source:
        raise TemporalOperatorError("Tail resolution is incomplete or belongs to another source")
    if tuple(step.operator_position for step in resolution.transformations) != temporal_operator_positions(frame):
        raise TemporalOperatorError("every written Tail must execute exactly once in written order")
    runs: list[list[int]] = []
    for position in temporal_operator_positions(frame):
        if runs and position == runs[-1][-1] + 1:
            runs[-1].append(position)
        else:
            runs.append([position])
    run_index_by_position = {position: index for index, run in enumerate(runs) for position in run}
    order = list(source)
    start = 0
    for step in resolution.transformations:
        index = run_index_by_position[step.operator_position]
        run = runs[index]
        stop = min(order.index(pos) for pos in runs[index + 1]) if index + 1 < len(runs) else len(order)
        if step.run_positions != tuple(run) or (step.start, step.stop) != (start, stop):
            raise TemporalOperatorError("Tail transformation changed its adjacent or staggered boundaries")
        if not 0 <= step.start < step.stop <= len(order):
            raise TemporalOperatorError("Tail transformation has invalid traversal boundaries")
        if step.operator_position not in step.before_positions:
            raise TemporalOperatorError("Tail transformation lost its operator identity")
        if tuple(order[step.start:step.stop]) != step.before_positions:
            raise TemporalOperatorError("Tail transformation does not continue the preceding state")
        if step.after_positions != tuple(reversed(step.before_positions)):
            raise TemporalOperatorError("Tail transformation did not complete its turn")
        if step.crossing != temporal_crossing(frame, step.operator_position):
            raise TemporalOperatorError("Tail crossing lost its source address or distance")
        order[step.start:step.stop] = step.after_positions
        if step.operator_position == run[-1]:
            start = max(order.index(pos) for pos in run) + 1
    if tuple(order) != resolution.execution_positions:
        raise TemporalOperatorError("Tail execution order does not match its completed transformations")


def tail_resolution_from_dict(data: dict) -> TailResolution:
    return TailResolution(
        tuple(data["source_positions"]), tuple(data["execution_positions"]),
        tuple(TailTransformation(
            operator_position=item["operator_position"],
            run_positions=tuple(item["run_positions"]), start=item["start"], stop=item["stop"],
            before_positions=tuple(item["before_positions"]),
            after_positions=tuple(item["after_positions"]),
            crossing=TemporalCrossing(**item["crossing"]),
        ) for item in data["transformations"]),
        bool(data["completed"]),
    )


def temporal_crossing(frame: DomusFrame, operator_position: int) -> TemporalCrossing:
    """Resolve the written Orobouros Tail ⟲ position to its first reflected Aeternum manifestation."""
    if not isinstance(operator_position, int):
        raise TypeError("operator_position must be int")
    extent = len(frame.tokens)
    if operator_position < 0 or operator_position >= extent:
        raise TemporalOperatorError("⟲ position lies outside the finite Real GrimChain")
    token = frame.tokens[operator_position]
    if token.position != operator_position or token.value != TEMPORAL_OPERATOR_GLYPH:
        raise TemporalOperatorError(f"source position {operator_position} is not a written ⟲")

    mirror_virtual_position = 2 * extent - 1 - operator_position
    mirror_token = frame.aeternum_token(mirror_virtual_position)
    if mirror_token.source_position != operator_position:
        raise TemporalOperatorError("Aeternum mirror did not preserve the written ⟲ source position")

    return TemporalCrossing(
        operator_position=operator_position,
        entrance_virtual_position=operator_position,
        mirror_virtual_position=mirror_virtual_position,
        source_position=operator_position,
        temporal_parsecs=abs(mirror_virtual_position - operator_position),
    )


def temporal_crossings(frame: DomusFrame) -> tuple[TemporalCrossing, ...]:
    """Resolve every written ⟲ independently against the same immutable Real frame."""
    return tuple(
        temporal_crossing(frame, position)
        for position in temporal_operator_positions(frame)
    )


def temporal_operator_positions(frame: DomusFrame) -> tuple[int, ...]:
    """Return every exact written ⟲ position without changing the source."""
    return tuple(
        token.position
        for token in frame.tokens
        if token.value == TEMPORAL_OPERATOR_GLYPH
    )


def temporal_geometry(frame: DomusFrame) -> TemporalGeometry:
    """Describe every written ⟲ and the exact source-coordinate geometry between them."""
    positions = temporal_operator_positions(frame)
    seams: list[TemporalSeam] = []
    for index, position in enumerate(positions):
        previous_position = positions[index - 1] if index else None
        next_position = positions[index + 1] if index + 1 < len(positions) else None
        distance = None if previous_position is None else position - previous_position
        intervening = None if distance is None else distance - 1
        seams.append(
            TemporalSeam(
                position=position,
                previous_position=previous_position,
                next_position=next_position,
                distance_from_previous=distance,
                intervening_from_previous=intervening,
            )
        )
    return TemporalGeometry(
        source=frame.source,
        operator_positions=positions,
        seams=tuple(seams),
    )


def aeternum_address(frame: DomusFrame, virtual_position: int) -> AeternumAddressWitness:
    """Resolve one existing Aeternum coordinate back to the same finite Real source."""
    if not isinstance(virtual_position, int):
        raise TypeError("virtual_position must be int")
    token: ReflectedGlyphToken = frame.aeternum_token(virtual_position)
    return AeternumAddressWitness(
        virtual_position=virtual_position,
        source_position=token.source_position,
        glyph=token.value,
        kind=token.kind,
        imaginary=token.imaginary,
    )


def aeternum_period(frame: DomusFrame) -> tuple[AeternumAddressWitness, ...]:
    """Return one exact 2N Aeternum period for the unchanged finite source."""
    extent = len(frame.tokens)
    if extent == 0:
        return ()
    return tuple(aeternum_address(frame, v) for v in range(2 * extent))
