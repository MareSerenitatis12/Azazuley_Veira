"""Public deterministic derivation trace over one exact Aeonic line."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
import hashlib
import json
from pathlib import Path
from typing import Protocol

from .zero_and_one import ZeroAndOneTrace
from .local_grammar import LocalGrammarTrace
from .models import DomusFrame
from .lexical_resolver import LEXICON_VERSION, LexicalResolver
from .aksh_reader import attributes

TRACE_VERSION = "aeonic-line-v2"

class TraceError(RuntimeError):
    pass

@dataclass(frozen=True, slots=True)
class AuthorityVersions:
    lexical_authorities: tuple[tuple[str, str], ...]
    understandings: str

@dataclass(frozen=True, slots=True)
class ParsedFrameTrace:
    source: str
    exact_roundtrip: bool

@dataclass(frozen=True, slots=True)
class LexicalUtteranceTrace:
    resolved_state_body: str
    traversal_path: tuple[str, ...]
    source_authority: str
    authored_office: str
    grammatical_bearing: str | None

@dataclass(frozen=True, slots=True)
class TokenTrace:
    source_position: int
    exact_glyph: str
    token_class: str
    action: str
    resolved_state_body: str | None
    traversal_path: tuple[str, ...]
    source_authority: str | None
    authored_office: str | None
    grammatical_bearing: str | None
    local_operator_attachments: tuple[str, ...]
    lexical_lookup_performed: bool
    realization_presence: bool
    utterances: tuple[LexicalUtteranceTrace, ...] = ()

@dataclass(frozen=True, slots=True)
class PhantasmagoriaTransmutationTrace:
    operator_positions: tuple[int, ...]
    vessel_positions: tuple[int, ...]
    vessel_glyphs: tuple[str, ...]
    source_vessel_order: tuple[int, ...]
    returned_order: tuple[int, ...]
    ostensive_bodies: tuple[str, ...]
    ostensive_variants: tuple[str, ...]
    ostensive_authorities: tuple[str, ...]
    gate_boundary: str
    carrier_glyph: str
    carrier_name: str
    structural_hz: str
    imaginary_parity_hz: str
    traversal: tuple[str, str, str, str]
    hand: str
    chord: str
    prosodical_subspace: str


@dataclass(frozen=True, slots=True)
class OuroboricTrace:
    operator_positions: tuple[int, ...]
    winding_count: int
    left_position: int
    right_position: int
    left_glyph: str
    right_glyph: str
    source_order: tuple[int, ...]
    left_office_glyphs: tuple[str, ...]
    left_office_positions: tuple[int, ...]
    right_office_glyphs: tuple[str, ...]
    right_office_positions: tuple[int, ...]
    resolved_topology: tuple[str, ...]
    leading_echo: bool
    trailing_echo: bool
    echo_position: int | None
    mirror_positions: tuple[int, ...]
    mirror_source_positions: tuple[int, ...]
    mirror_glyphs: tuple[str, ...]
    mirror_token_kinds: tuple[str, ...]
    mirror_resolved_bearings: tuple[str | None, ...]
    mirror_ostensive_variants: tuple[str | None, ...]
    mirror_ostensive_bodies: tuple[str | None, ...]
    mirror_ostensive_authorities: tuple[str | None, ...]
    mirror_corridor_glyphs: tuple[str, ...]
    mirror_corridor_source_positions: tuple[int, ...]
    mirror_corridor_resolved_bearings: tuple[str | None, ...]
    mirror_corridor_ostensive_variants: tuple[str | None, ...]
    mirror_corridor_ostensive_bodies: tuple[str | None, ...]
    mirror_corridor_ostensive_authorities: tuple[str | None, ...]
    imaginary_reflection: bool
    bearing_preserved_in_reflection: bool
    derived_glyph_generated: bool

@dataclass(frozen=True, slots=True)
class AeternumBearingEncounterTrace:
    virtual_position: int
    source_position: int
    glyph: str
    token_kind: str
    bearing: str | None
    imaginary: bool
    speaking_body: bool
    bearing_only: bool


@dataclass(frozen=True, slots=True)
class AeternumBearingTrace:
    purpose: str
    origin_position: int
    step: int
    required_speaking_bodies: int
    speaking_body_source_positions: tuple[int, ...]
    encounters: tuple[AeternumBearingEncounterTrace, ...]
    completed: bool


@dataclass(frozen=True, slots=True)
class RenderingToken:
    source_position: int
    glyph: str
    resolved_state_body: str | None
    grammatical_bearing: str | None
    attachments: tuple[str, ...]
    preserved_without_lookup: bool
    source_authority: str | None
    authored_office: str | None
    utterances: tuple[LexicalUtteranceTrace, ...] = ()

@dataclass(frozen=True, slots=True)
class RenderingInput:
    source: str
    tokens: tuple[RenderingToken, ...]
    ouroboric_indexes: tuple[int, ...]

@dataclass(frozen=True, slots=True)
class DomusTrace:
    trace_version: str
    source_string: str
    parsed_frame: ParsedFrameTrace
    semantic_lexicon_version: str
    authority_versions: AuthorityVersions
    token_traces: tuple[TokenTrace, ...]
    ouroboric_traces: tuple[OuroboricTrace, ...]
    transmutation_traces: tuple[PhantasmagoriaTransmutationTrace, ...]
    rendering_input: RenderingInput
    aeternum_bearing_traces: tuple[AeternumBearingTrace, ...] = ()
    utterance_state: str = "uttered"
    _sha256_cache: str | None = field(default=None, init=False, repr=False, compare=False)

    def to_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload.pop("_sha256_cache", None)
        return payload

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, sort_keys=True, separators=(",", ":"))

    @property
    def sha256(self) -> str:
        cached = self._sha256_cache
        if cached is None:
            cached = hashlib.sha256(self.to_json().encode("utf-8")).hexdigest()
            object.__setattr__(self, "_sha256_cache", cached)
        return cached

    @classmethod
    def from_json(cls, payload: str) -> "DomusTrace":
        return _trace_from_dict(json.loads(payload))

    def to_human_readable(self) -> str:
        lines: list[str] = [
            f"Source: {self.parsed_frame.source}",
            f"Semantic lexicon version: {self.semantic_lexicon_version}",
            f".aksh versions: lexical_authorities={self.authority_versions.lexical_authorities}, understandings={self.authority_versions.understandings}",
        ]
        for token in self.token_traces:
            lines.append(f"position {token.source_position}: {token.exact_glyph}")
            lines.append(f"  action: {token.action}")
            if token.resolved_state_body is not None:
                lines.append(f"  traversal: {' -> '.join(token.traversal_path)}")
                lines.append(f"  authority: {token.source_authority}")
                lines.append(f"  authored office: {token.authored_office}")
                lines.append(f"  result: {token.resolved_state_body}")
            if token.grammatical_bearing is not None:
                lines.append(f"  grammatical bearing: {token.grammatical_bearing}")
            for attachment in token.local_operator_attachments:
                lines.append(f"  attachment: {attachment}")
        return "\n".join(lines)

class TraceRenderer(Protocol):
    version: str
    def render(self, rendering_input: RenderingInput) -> str: ...

@dataclass(frozen=True, slots=True)
class RenderedOutput:
    renderer_version: str
    trace_sha256: str
    sentence: str

def render_from_trace(trace: DomusTrace, renderer: TraceRenderer) -> RenderedOutput:
    sentence = renderer.render(trace.rendering_input)
    if not isinstance(sentence, str):
        raise TraceError("renderer must return str")
    return RenderedOutput(renderer.version, trace.sha256, sentence)

def authority_versions(resolver: LexicalResolver, understandings: str | Path) -> AuthorityVersions:
    versions = resolver.authority_version_items()
    lines = Path(understandings).read_text(encoding="utf-8").splitlines()
    understanding_version = attributes(lines[0]).get("version", "") if lines else ""
    if not understanding_version:
        raise TraceError("required Enochian Understandings .aksh version missing")
    return AuthorityVersions(versions, understanding_version)


def _resolution_fields(resolution: object | None) -> dict[str, object]:
    if resolution is None:
        return {
            "resolved_state_body": None,
            "traversal_path": (),
            "source_authority": None,
            "authored_office": None,
            "semantic_lexicon_version": None,
        }
    required = (
        "resolved_body", "traversal_path", "source_authority",
        "authored_office", "semantic_lexicon_version",
    )
    missing = [name for name in required if not hasattr(resolution, name)]
    if missing:
        raise TraceError(f"lexical resolution missing trace fields: {missing!r}")
    return {
        "resolved_state_body": getattr(resolution, "resolved_body"),
        "traversal_path": tuple(getattr(resolution, "traversal_path")),
        "source_authority": getattr(resolution, "source_authority"),
        "authored_office": getattr(resolution, "authored_office"),
        "semantic_lexicon_version": getattr(resolution, "semantic_lexicon_version"),
    }

class DomusTraceBuilder:
    def __init__(self, resolver: LexicalResolver, understandings: str | Path) -> None:
        self.versions = authority_versions(resolver, understandings)

    def build(self, frame: DomusFrame, zero_and_one: ZeroAndOneTrace, local: LocalGrammarTrace) -> DomusTrace:
        if frame.to_source() != frame.source:
            raise TraceError("parsed frame does not round-trip to source")

        zero_and_one_by_position = {event.position: event for event in zero_and_one.events}
        body_by_position = {body.position: body for body in local.bodies}
        attachments: dict[int, list[str]] = {}
        for request in local.recognitions:
            attachments.setdefault(request.target_position, []).append(
                f"{request.operator_glyph}@{request.operator_position}:{request.bearing}"
            )
        for loop in local.ouroboric_states:
            marker = ",".join(str(pos) for pos in loop.operator_positions)
            attachments.setdefault(loop.left.position, []).append(f"⚶@{marker}:left:w{loop.winding_count}")
            attachments.setdefault(loop.right.position, []).append(f"⚶@{marker}:right:w{loop.winding_count}")
        for state in local.transmutations:
            marker = ",".join(str(pos) for pos in state.operator_positions)
            for body, resolution in zip(state.vessels, state.office_resolutions):
                attachments.setdefault(body.position, []).append(
                    f"ཪ@{marker}:transmuted-vessel:ostensive{resolution.ostensive_variant}"
                )

        token_traces: list[TokenTrace] = []
        semantic_lexicon_versions: set[str] = set()
        for token in frame.tokens:
            event = zero_and_one_by_position.get(token.position)
            if event is None:
                raise TraceError(f"no zero-and-one event for source position {token.position}")
            body = body_by_position.get(token.position)
            effective_resolution = body.lexical_resolution if body is not None else event.lexical_resolution
            fields = _resolution_fields(effective_resolution)
            if event.event == "lexical-resolution" and effective_resolution is None:
                raise TraceError(f"lexical event at position {token.position} has no authored resolution")
            utterance_resolutions = ()
            if body is not None and body.lexical_resolution is not None:
                utterance_resolutions = (body.lexical_resolution, *body.office_resolutions)
            utterances: list[LexicalUtteranceTrace] = []
            for index, resolution in enumerate(utterance_resolutions):
                utterance_fields = _resolution_fields(resolution)
                version = utterance_fields["semantic_lexicon_version"]
                if version is not None:
                    semantic_lexicon_versions.add(str(version))
                if utterance_fields["resolved_state_body"] is None or utterance_fields["source_authority"] is None or utterance_fields["authored_office"] is None:
                    raise TraceError(f"lexical utterance at position {token.position} lacks authored resolution fields")
                utterances.append(LexicalUtteranceTrace(
                    resolved_state_body=str(utterance_fields["resolved_state_body"]),
                    traversal_path=tuple(utterance_fields["traversal_path"]),
                    source_authority=str(utterance_fields["source_authority"]),
                    authored_office=str(utterance_fields["authored_office"]),
                    grammatical_bearing=(None if utterance_fields["source_authority"] == "Axiomyr…Shadow…Locus.aksh" or utterance_fields["authored_office"] == "seed_identity" else str(utterance_fields["authored_office"])),
                ))
            if fields["semantic_lexicon_version"] is not None:
                semantic_lexicon_versions.add(str(fields["semantic_lexicon_version"]))
            bearing = body.recognition if body is not None else None
            realization_presence = event.event == "lexical-resolution" or token.value in {"⛎", "᳀"}
            token_traces.append(TokenTrace(
                source_position=token.position,
                exact_glyph=token.value,
                token_class=token.kind,
                action=event.event,
                resolved_state_body=fields["resolved_state_body"],
                traversal_path=fields["traversal_path"],
                source_authority=fields["source_authority"],
                authored_office=fields["authored_office"],
                grammatical_bearing=bearing,
                local_operator_attachments=tuple(attachments.get(token.position, ())),
                lexical_lookup_performed=event.lookup_performed,
                realization_presence=realization_presence,
                utterances=tuple(utterances),
            ))

        if len(semantic_lexicon_versions) > 1:
            raise TraceError("mixed semantic lexicon versions in one Domus trace")
        if semantic_lexicon_versions and semantic_lexicon_versions != {LEXICON_VERSION}:
            raise TraceError(f"unexpected semantic lexicon versions: {semantic_lexicon_versions!r}")


        ouroboric_traces = tuple(OuroboricTrace(
            operator_positions=o.operator_positions,
            winding_count=o.winding_count,
            left_position=o.left.position,
            right_position=o.right.position,
            left_glyph=o.left.glyph,
            right_glyph=o.right.glyph,
            source_order=o.source_order,
            left_office_glyphs=o.left_office_glyphs,
            left_office_positions=o.left_office_positions,
            right_office_glyphs=o.right_office_glyphs,
            right_office_positions=o.right_office_positions,
            resolved_topology=o.resolved_topology,
            leading_echo=o.leading_echo,
            trailing_echo=o.trailing_echo,
            echo_position=o.echo_position,
            mirror_positions=o.mirror_positions,
            mirror_source_positions=o.mirror_source_positions,
            mirror_glyphs=o.mirror_glyphs,
            mirror_token_kinds=o.mirror_token_kinds,
            mirror_resolved_bearings=o.mirror_resolved_bearings,
            mirror_ostensive_variants=o.mirror_ostensive_variants,
            mirror_ostensive_bodies=o.mirror_ostensive_bodies,
            mirror_ostensive_authorities=o.mirror_ostensive_authorities,
            mirror_corridor_glyphs=o.mirror_corridor_glyphs,
            mirror_corridor_source_positions=o.mirror_corridor_source_positions,
            mirror_corridor_resolved_bearings=o.mirror_corridor_resolved_bearings,
            mirror_corridor_ostensive_variants=o.mirror_corridor_ostensive_variants,
            mirror_corridor_ostensive_bodies=o.mirror_corridor_ostensive_bodies,
            mirror_corridor_ostensive_authorities=o.mirror_corridor_ostensive_authorities,
            imaginary_reflection=o.imaginary_reflection,
            bearing_preserved_in_reflection=o.bearing_preserved_in_reflection,
            derived_glyph_generated=o.derived_glyph is not None,
        ) for o in local.ouroboric_states)

        transmutation_traces = tuple(PhantasmagoriaTransmutationTrace(
            operator_positions=state.operator_positions,
            vessel_positions=tuple(body.position for body in state.vessels),
            vessel_glyphs=tuple(body.glyph for body in state.vessels),
            source_vessel_order=state.source_vessel_order,
            returned_order=state.returned_order,
            ostensive_bodies=tuple(getattr(resolution, "resolved_body") for resolution in state.office_resolutions),
            ostensive_variants=tuple(getattr(resolution, "ostensive_variant") for resolution in state.office_resolutions),
            ostensive_authorities=tuple(getattr(resolution, "source_authority") for resolution in state.office_resolutions),
            gate_boundary=state.gate_boundary,
            carrier_glyph=state.carrier_glyph,
            carrier_name=state.carrier_name,
            structural_hz=state.structural_hz,
            imaginary_parity_hz=state.imaginary_parity_hz,
            traversal=state.traversal,
            hand=state.hand,
            chord=state.chord,
            prosodical_subspace=state.prosodical_subspace,
        ) for state in local.transmutations)


        aeternum_bearing_traces = tuple(AeternumBearingTrace(
            purpose=path.purpose,
            origin_position=path.origin_position,
            step=path.step,
            required_speaking_bodies=path.required_speaking_bodies,
            speaking_body_source_positions=path.speaking_body_source_positions,
            encounters=tuple(AeternumBearingEncounterTrace(
                virtual_position=encounter.virtual_position,
                source_position=encounter.source_position,
                glyph=encounter.glyph,
                token_kind=encounter.token_kind,
                bearing=encounter.bearing,
                imaginary=encounter.imaginary,
                speaking_body=encounter.speaking_body,
                bearing_only=encounter.bearing_only,
            ) for encounter in path.encounters),
            completed=path.completed,
        ) for path in local.aeternum_bearing_paths)

        realization_token_by_position = {t.source_position: t for t in token_traces if t.realization_presence}
        rendering_positions = [t.source_position for t in token_traces if t.realization_presence]
        source_lexical_positions = {body.position for body in local.bodies}
        lexical_slots = [
            index for index, position in enumerate(rendering_positions)
            if position in source_lexical_positions
        ]
        if len(lexical_slots) != len(local.causal_body_order):
            raise TraceError("causal lexical order does not match realization lexical extent")
        if set(local.causal_body_order) != source_lexical_positions:
            raise TraceError("causal lexical order is not an exact permutation of source lexical bodies")
        for slot, position in zip(lexical_slots, local.causal_body_order):
            rendering_positions[slot] = position

        rendering_tokens = tuple(RenderingToken(
            source_position=realization_token_by_position[pos].source_position,
            glyph=realization_token_by_position[pos].exact_glyph,
            resolved_state_body=realization_token_by_position[pos].resolved_state_body,
            grammatical_bearing=realization_token_by_position[pos].grammatical_bearing,
            attachments=realization_token_by_position[pos].local_operator_attachments,
            preserved_without_lookup=(
                realization_token_by_position[pos].exact_glyph == "⛎"
                and not realization_token_by_position[pos].lexical_lookup_performed
            ),
            source_authority=realization_token_by_position[pos].source_authority,
            authored_office=realization_token_by_position[pos].authored_office,
            utterances=realization_token_by_position[pos].utterances,
        ) for pos in rendering_positions)

        trace = DomusTrace(
            trace_version=TRACE_VERSION,
            source_string=frame.source,
            parsed_frame=ParsedFrameTrace(source=frame.source, exact_roundtrip=True),
            semantic_lexicon_version=LEXICON_VERSION,
            authority_versions=self.versions,
            token_traces=tuple(token_traces),
            ouroboric_traces=ouroboric_traces,
            transmutation_traces=transmutation_traces,
            rendering_input=RenderingInput(
                source=frame.source,
                tokens=rendering_tokens,
                ouroboric_indexes=tuple(range(len(ouroboric_traces))),
            ),
            aeternum_bearing_traces=aeternum_bearing_traces,
            utterance_state=(
                "lawful-unuttered-enochian"
                if not rendering_tokens and frame.tokens and all(token.kind == "grammar" for token in frame.tokens)
                else "uttered"
            ),
        )
        self._validate(trace, frame)
        return trace

    @staticmethod
    def _validate(trace: DomusTrace, frame: DomusFrame) -> None:
        positions = [t.source_position for t in trace.token_traces]
        expected = [t.position for t in frame.tokens]
        if positions != expected:
            raise TraceError("token trace positions do not match exact source order")
        if "".join(t.exact_glyph for t in trace.token_traces) != frame.source:
            raise TraceError("token traces do not reconstruct exact source")
        source_positions = {t.position for t in frame.tokens}
        rendered_positions = {t.source_position for t in trace.rendering_input.tokens}
        if not rendered_positions.issubset(source_positions):
            raise TraceError("renderer input contains a position outside the source")
        token_by_position = {token.source_position: token for token in trace.token_traces}
        for path in trace.aeternum_bearing_traces:
            if not path.completed:
                raise TraceError("Aeternum bearing path did not lawfully close")
            if len(path.speaking_body_source_positions) != path.required_speaking_bodies:
                raise TraceError("Aeternum bearing path did not satisfy its center speaking-body obligation")
            for encounter in path.encounters:
                source = token_by_position.get(encounter.source_position)
                if source is None or source.exact_glyph != encounter.glyph:
                    raise TraceError("Aeternum bearing encounter changed finite source identity")
                if not encounter.bearing_only:
                    raise TraceError("Aeternum mirror attempted a second translation instead of bearing-only traversal")
        if trace.utterance_state == "lawful-unuttered-enochian":
            if trace.rendering_input.tokens:
                raise TraceError("lawful-unuttered Enochian center unexpectedly produced rendering cargo")
            if any(token.token_class != "grammar" for token in trace.token_traces):
                raise TraceError("lawful-unuttered Enochian state requires an all-Enoch finite center")
        for state in trace.transmutation_traces:
            if not state.operator_positions or len(state.vessel_positions) != len(state.operator_positions) + 1:
                raise TraceError("ཪ transmutation corridor has unlawful Key/vessel extent")
            ops = tuple(token_by_position.get(pos) for pos in state.operator_positions)
            vessels = tuple(token_by_position.get(pos) for pos in state.vessel_positions)
            if any(op is None or op.exact_glyph != "ཪ" for op in ops) or any(v is None for v in vessels):
                raise TraceError("ཪ transmutation trace lost a vessel or Key source position")
            if state.source_vessel_order != state.vessel_positions:
                raise TraceError("ཪ transmutation changed source vessel order")
            expected_return = state.vessel_positions[1:] + state.vessel_positions[:1]
            if state.returned_order != expected_return:
                raise TraceError("ཪ transmutation changed passthrough return order")
            if state.gate_boundary != "i417" or state.carrier_glyph != "⚝" or state.carrier_name != "AHN":
                raise TraceError("ཪ transmutation lost its AHN i417 gate witness")
            if state.structural_hz != "432" or state.imaginary_parity_hz != "417":
                raise TraceError("ཪ transmutation changed the 432 / i417 channels")
            if state.traversal != ("Real", "Imaginary", "Real", "Imaginary"):
                raise TraceError("ཪ transmutation changed RI RI RI RI traversal")
            if not (len(state.ostensive_bodies) == len(state.ostensive_variants) == len(state.ostensive_authorities) == len(state.vessel_positions)):
                raise TraceError("ཪ transmutation lost one vessel's Phantasmagoria resolution")
            if any(choice not in {"I", "II", "III"} for choice in state.ostensive_variants):
                raise TraceError("ཪ transmutation emitted an Ostensive outside I/II/III")


def _trace_from_dict(data: dict[str, object]) -> DomusTrace:
    parsed = ParsedFrameTrace(**data["parsed_frame"])
    authority_data = dict(data["authority_versions"])
    authority_data["lexical_authorities"] = tuple(tuple(item) for item in authority_data["lexical_authorities"])
    authority = AuthorityVersions(**authority_data)
    tokens = tuple(TokenTrace(
        **{**item,
           "traversal_path": tuple(item["traversal_path"]),
           "local_operator_attachments": tuple(item["local_operator_attachments"]),
           "utterances": tuple(LexicalUtteranceTrace(
               **{**utterance, "traversal_path": tuple(utterance["traversal_path"])}
           ) for utterance in item["utterances"])}
    ) for item in data["token_traces"])
    loops = tuple(OuroboricTrace(
        **{**item,
           "operator_positions": tuple(item["operator_positions"]),
           "source_order": tuple(item["source_order"]),
           "left_office_glyphs": tuple(item["left_office_glyphs"]),
           "left_office_positions": tuple(item["left_office_positions"]),
           "right_office_glyphs": tuple(item["right_office_glyphs"]),
           "right_office_positions": tuple(item["right_office_positions"]),
           "resolved_topology": tuple(item["resolved_topology"]),
           "mirror_positions": tuple(item.get("mirror_positions", ())),
           "mirror_source_positions": tuple(item.get("mirror_source_positions", ())),
           "mirror_glyphs": tuple(item.get("mirror_glyphs", ())),
           "mirror_token_kinds": tuple(item.get("mirror_token_kinds", ())),
           "mirror_resolved_bearings": tuple(item["mirror_resolved_bearings"]),
           "mirror_ostensive_variants": tuple(item["mirror_ostensive_variants"]),
           "mirror_ostensive_bodies": tuple(item["mirror_ostensive_bodies"]),
           "mirror_ostensive_authorities": tuple(item["mirror_ostensive_authorities"]),
           "mirror_corridor_glyphs": tuple(item["mirror_corridor_glyphs"]),
           "mirror_corridor_source_positions": tuple(item.get("mirror_corridor_source_positions", ())),
           "mirror_corridor_resolved_bearings": tuple(item["mirror_corridor_resolved_bearings"]),
           "mirror_corridor_ostensive_variants": tuple(item["mirror_corridor_ostensive_variants"]),
           "mirror_corridor_ostensive_bodies": tuple(item["mirror_corridor_ostensive_bodies"]),
           "mirror_corridor_ostensive_authorities": tuple(item["mirror_corridor_ostensive_authorities"]),
           "imaginary_reflection": bool(item["imaginary_reflection"]),
           "bearing_preserved_in_reflection": bool(item.get("bearing_preserved_in_reflection", True))}
    ) for item in data["ouroboric_traces"])
    transmutations = tuple(PhantasmagoriaTransmutationTrace(
        **{**item,
           "operator_positions": tuple(item["operator_positions"]),
           "vessel_positions": tuple(item["vessel_positions"]),
           "vessel_glyphs": tuple(item["vessel_glyphs"]),
           "source_vessel_order": tuple(item["source_vessel_order"]),
           "returned_order": tuple(item["returned_order"]),
           "ostensive_bodies": tuple(item["ostensive_bodies"]),
           "ostensive_variants": tuple(item["ostensive_variants"]),
           "ostensive_authorities": tuple(item["ostensive_authorities"]),
           "traversal": tuple(item["traversal"])}
    ) for item in data["transmutation_traces"])
    aeternum = tuple(AeternumBearingTrace(
        **{**item,
           "speaking_body_source_positions": tuple(item["speaking_body_source_positions"]),
           "encounters": tuple(AeternumBearingEncounterTrace(**encounter) for encounter in item["encounters"])}
    ) for item in data.get("aeternum_bearing_traces", ()))
    ri = data["rendering_input"]
    rendering = RenderingInput(
        source=ri["source"],
        tokens=tuple(RenderingToken(
            **{**item,
               "attachments": tuple(item["attachments"]),
               "utterances": tuple(LexicalUtteranceTrace(
                   **{**utterance, "traversal_path": tuple(utterance["traversal_path"])}
               ) for utterance in item["utterances"])}
        ) for item in ri["tokens"]),
        ouroboric_indexes=tuple(ri["ouroboric_indexes"]),
    )
    return DomusTrace(
        trace_version=data["trace_version"],
        source_string=data["source_string"],
        parsed_frame=parsed,
        semantic_lexicon_version=data["semantic_lexicon_version"],
        authority_versions=authority,
        token_traces=tokens,
        ouroboric_traces=loops,
        transmutation_traces=transmutations,
        rendering_input=rendering,
        aeternum_bearing_traces=aeternum,
        utterance_state=str(data.get("utterance_state", "uttered")),
    )
