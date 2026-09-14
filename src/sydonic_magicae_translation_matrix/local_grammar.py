"""Local grammar declarations used by the single-pass Domus executor.

This module defines operator payloads and trace records. Execution occurs only
inside SequentialDomusExecutor so grammar cannot be deferred into a second pass.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from typing import Literal



RecognitionKind = Literal["relic", "catalyst", "substrate", "spatial_absolute", "temporal_absolute", "terminal_state", "adversarial", "recursive_identity"]

PHANTASMAGORIA_GLYPH = "ཪ"
RELIC = "🜛"
CATALYST = "🜚"
SUBSTRATE = "߷"
SPATIAL_ABSOLUTE = "☍"
TEMPORAL_ABSOLUTE = "🜔"
TERMINAL_STATE = "🜕"
ADVERSARIAL = "🜖"
RECURSIVE_IDENTITY = "🜗"
OUROBORIC = "⚶"

RECOGNITION_GLYPHS: dict[str, RecognitionKind] = {
    RELIC: "relic",
    CATALYST: "catalyst",
    SUBSTRATE: "substrate",
    SPATIAL_ABSOLUTE: "spatial_absolute",
    TEMPORAL_ABSOLUTE: "temporal_absolute",
    TERMINAL_STATE: "terminal_state",
    ADVERSARIAL: "adversarial",
    RECURSIVE_IDENTITY: "recursive_identity",
}


class LocalGrammarError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class ResolvedBody:
    position: int
    glyph: str
    lexical_resolution: object | None
    office_resolutions: tuple[object, ...] = ()
    recognition: RecognitionKind | None = None


@dataclass(frozen=True, slots=True)
class RecognitionRequest:
    operator_position: int
    operator_glyph: str
    target_position: int
    target_glyph: str
    bearing: RecognitionKind
    direction: str = "backward"
    scope: str = "pattern-derived-lexical-body"
    retrocausal_depth: int | None = None
    stack_positions: tuple[int, ...] = ()
    source_reordered: bool = False
    surface_form_selected: bool = True


@dataclass(frozen=True, slots=True)
class PhantasmagoriaTransmutation:
    operator_positions: tuple[int, ...]
    vessels: tuple[ResolvedBody, ...]
    office_resolutions: tuple[object, ...]
    source_vessel_order: tuple[int, ...]
    returned_order: tuple[int, ...]
    gate_boundary: str
    carrier_glyph: str
    carrier_name: str
    structural_hz: str
    imaginary_parity_hz: str
    traversal: tuple[str, str, str, str] = ("Real", "Imaginary", "Real", "Imaginary")
    hand: str = "ཪ"
    chord: str = "Wellspring"
    prosodical_subspace: str = "Prosodical Subspace"

    def __post_init__(self) -> None:
        if not self.operator_positions:
            raise LocalGrammarError("ཪ transmutation requires at least one Key")
        if len(self.vessels) != len(self.operator_positions) + 1:
            raise LocalGrammarError("ཪ corridor requires one more Real vessel than Keys")
        if len(self.office_resolutions) != len(self.vessels):
            raise LocalGrammarError("ཪ every vessel must resolve through the Phantasmagoria office")
        positions = tuple(body.position for body in self.vessels)
        if self.source_vessel_order != positions:
            raise LocalGrammarError("ཪ source vessel order changed")
        expected_return = positions[1:] + positions[:1]
        if self.returned_order != expected_return:
            raise LocalGrammarError("ཪ corridor must pass the first vessel through every following vessel")
        if self.gate_boundary != "i417":
            raise LocalGrammarError("ཪ must open the Wellspring at the i417 boundary")
        if self.carrier_glyph != "⚝" or self.carrier_name != "AHN":
            raise LocalGrammarError("ཪ i417 gate must be witnessed by AHN")
        if self.structural_hz != "432" or self.imaginary_parity_hz != "417":
            raise LocalGrammarError("ཪ AHN witness changed its 432 / i417 channels")
        if self.traversal != ("Real", "Imaginary", "Real", "Imaginary"):
            raise LocalGrammarError("ཪ traversal must remain RI RI RI RI")
        for body, resolution in zip(self.vessels, self.office_resolutions):
            if getattr(resolution, "source_glyph", None) != body.glyph:
                raise LocalGrammarError("ཪ transmutation changed vessel glyph identity")
            if getattr(resolution, "authored_office", None) != "phantasmagoria":
                raise LocalGrammarError("ཪ vessel resolution must come from the authored Phantasmagoria office")
            if getattr(resolution, "ostensive_variant", None) not in {"I", "II", "III"}:
                raise LocalGrammarError("ཪ Phantasmagoria must select authored Ostensive I, II, or III")


@dataclass(frozen=True, slots=True)
class OuroboricState:
    operator_positions: tuple[int, ...]
    winding_count: int
    left: ResolvedBody
    right: ResolvedBody
    source_order: tuple[int, ...]
    left_office_glyphs: tuple[str, ...]
    left_office_positions: tuple[int, ...]
    right_office_glyphs: tuple[str, ...]
    right_office_positions: tuple[int, ...]
    resolved_topology: tuple[str, ...]
    leading_echo: bool = False
    trailing_echo: bool = False
    echo_position: int | None = None
    mirror_positions: tuple[int, ...] = ()
    mirror_source_positions: tuple[int, ...] = ()
    mirror_glyphs: tuple[str, ...] = ()
    mirror_token_kinds: tuple[str, ...] = ()
    mirror_resolved_bearings: tuple[str | None, ...] = ()
    mirror_ostensive_variants: tuple[str | None, ...] = ()
    mirror_ostensive_bodies: tuple[str | None, ...] = ()
    mirror_ostensive_authorities: tuple[str | None, ...] = ()
    mirror_corridor_glyphs: tuple[str, ...] = ()
    mirror_corridor_source_positions: tuple[int, ...] = ()
    mirror_corridor_resolved_bearings: tuple[str | None, ...] = ()
    mirror_corridor_ostensive_variants: tuple[str | None, ...] = ()
    mirror_corridor_ostensive_bodies: tuple[str | None, ...] = ()
    mirror_corridor_ostensive_authorities: tuple[str | None, ...] = ()
    imaginary_reflection: bool = False
    bearing_preserved_in_reflection: bool = True
    derived_glyph: str | None = None


@dataclass(frozen=True, slots=True)
class LocalGrammarEvent:
    position: int
    glyph: str
    event: str
    target_positions: tuple[int, ...]
    payload: object | None = None


@dataclass(frozen=True, slots=True)
class AeternumBearingEncounter:
    virtual_position: int
    source_position: int
    glyph: str
    token_kind: str
    bearing: str | None
    imaginary: bool
    speaking_body: bool
    bearing_only: bool = True


@dataclass(frozen=True, slots=True)
class AeternumBearingPath:
    purpose: str
    origin_position: int
    step: int
    required_speaking_bodies: int
    speaking_body_source_positions: tuple[int, ...]
    encounters: tuple[AeternumBearingEncounter, ...]
    completed: bool = True


@dataclass(frozen=True, slots=True)
class LocalGrammarTrace:
    bodies: tuple[ResolvedBody, ...]
    causal_body_order: tuple[int, ...]
    events: tuple[LocalGrammarEvent, ...]
    recognitions: tuple[RecognitionRequest, ...]
    ouroboric_states: tuple[OuroboricState, ...]
    transmutations: tuple[PhantasmagoriaTransmutation, ...]
    aeternum_bearing_paths: tuple[AeternumBearingPath, ...] = ()

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)


