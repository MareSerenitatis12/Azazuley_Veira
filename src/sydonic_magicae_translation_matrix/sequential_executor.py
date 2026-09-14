"""Pattern-driven execution of one exact Sydonic Magicae Aeonic line.

Every visible code point is preserved. Ordinary lexical bodies resolve through
SeeD Body and maximal consecutive Enochian grammar runs execute in written order.
"""
from __future__ import annotations

from dataclasses import replace

from .zero_and_one import (
    AXIOMYR_GLYPH, SHADOW_LOCUS, ZERO_MIDDLE_GLYPH, TRIPARTITE_AXIOMYR,
    ZeroAndOneEvent, ZeroAndOneTrace, ZeroAndOneMachine,
)
from .local_grammar import (
    SUBSTRATE, CATALYST, RELIC, OUROBORIC, SPATIAL_ABSOLUTE, PHANTASMAGORIA_GLYPH,
    LocalGrammarError, LocalGrammarEvent,
    PhantasmagoriaTransmutation, LocalGrammarTrace, OuroboricState, RecognitionRequest,
    ResolvedBody, AeternumBearingEncounter, AeternumBearingPath,
)
from .models import DomusFrame
from .frequency_projection import CARRIER_BY_GLYPH

try:
    from ._sydonic_kernel import walk_aeternum as _compiled_walk_aeternum
except ImportError as exc:
    raise RuntimeError("Sydonic requires the compiled Aeternum index kernel") from exc

OFFICE_BEARINGS = {
    RELIC: "relic",
    CATALYST: "catalyst",
    SUBSTRATE: "substrate",
    SPATIAL_ABSOLUTE: "spatial_absolute",
    "🜔": "temporal_absolute",
    "🜕": "terminal_state",
    "🜖": "adversarial",
    "🜗": "recursive_identity",
}
VISIBLE_GRAMMARS = frozenset(set(OFFICE_BEARINGS) | {OUROBORIC, PHANTASMAGORIA_GLYPH})

class SequentialDomusExecutor:
    """Execute the complete Aeonic line by lexical bodies and grammar stacks."""

    def __init__(self, zero_and_one_machine: ZeroAndOneMachine) -> None:
        self.machine = zero_and_one_machine

    def _resolve_office(self, body: ResolvedBody, office: str) -> object:
        resolver = self.machine.resolver
        owner = getattr(resolver, "__self__", None)
        if owner is None or not hasattr(owner, "resolve_office"):
            raise LocalGrammarError(f"authored {office} resolver is unavailable for {body.glyph!r}")
        return owner.resolve_office(body.glyph, office)

    def _resolve_special(self, glyph: str) -> object:
        resolver = self.machine.resolver
        owner = getattr(resolver, "__self__", None)
        if owner is None or not hasattr(owner, "resolve_special"):
            raise LocalGrammarError(f"authored Axiomyr/Shadow special resolver is unavailable for {glyph!r}")
        return owner.resolve_special(glyph)

    def execute_frame(
        self,
        frame: DomusFrame,
        *,
        aeternum_token=None,
        aeternum_pair_reorder=None,
        aeternum_corridor_reorder=None,
    ) -> tuple[ZeroAndOneTrace, LocalGrammarTrace]:
        aeternum_token = frame.aeternum_token if aeternum_token is None else aeternum_token
        aeternum_period_source_positions: tuple[int, ...] | None = None
        zero_and_one_events: list[ZeroAndOneEvent] = []
        grammar_events: list[LocalGrammarEvent] = []
        source_body_order: list[int] = []
        causal_body_order: list[int] = []
        bodies: dict[int, ResolvedBody] = {}
        recognitions: list[RecognitionRequest] = []
        loops: list[OuroboricState] = []
        transmutations: list[PhantasmagoriaTransmutation] = []
        aeternum_bearing_paths: list[AeternumBearingPath] = []

        pending_ouroborose: tuple[tuple[int, ...], int, tuple[tuple[int, str], ...], tuple[int, ...], int] | None = None
        active_loop: tuple[tuple[int, ...], int, tuple[tuple[int, str], ...], tuple[int, ...], int, int, int] | None = None
        pending_transmutation: tuple[tuple[int, ...], int, list[int]] | None = None

        tokens = frame.tokens
        i = 0
        semantic_source = frame.source if frame.prosody_source is None else frame.prosody_source
        shadow_ostensive = semantic_source == ZERO_MIDDLE_GLYPH
        axiomyr_ostensive = semantic_source == TRIPARTITE_AXIOMYR

        # Resolve the one finite real center before grammar attaches to it.  This does
        # not change source/causal order; it only makes the same real bodies available
        # when a boundary operator reaches them through the Aeternum mirror field.
        for source_token in tokens:
            if source_token.value in self.machine.ordinary_lexical_glyphs:
                bodies[source_token.position] = ResolvedBody(
                    source_token.position,
                    source_token.value,
                    self.machine.resolver(source_token.value),
                )
            elif source_token.value == SHADOW_LOCUS and shadow_ostensive:
                bodies[source_token.position] = ResolvedBody(
                    source_token.position, source_token.value, self._resolve_special(source_token.value),
                )
            elif source_token.value == AXIOMYR_GLYPH and axiomyr_ostensive:
                bodies[source_token.position] = ResolvedBody(
                    source_token.position, source_token.value, self._resolve_special(source_token.value),
                )

        # Causal order starts as the exact real speaking-body order of the immutable
        # center.  The scanner's source_body_order below remains a separate record of
        # visited source positions.  Aeternum may therefore resolve topology against a
        # real body before the scanner reaches its code point without creating a body.
        causal_body_order[:] = sorted(bodies)

        def source_bearing(source_position: int) -> str | None:
            """Return the authored bearing/law carried by one finite source position."""
            token = tokens[source_position]
            glyph = token.value
            if glyph in OFFICE_BEARINGS:
                return OFFICE_BEARINGS[glyph]
            if glyph == OUROBORIC:
                return "ouroborose_loop"
            if glyph == PHANTASMAGORIA_GLYPH:
                return "phantasmagoria"
            if source_position in bodies:
                if token.kind == "lexical":
                    return "seed_identity"
                if token.value in {SHADOW_LOCUS, AXIOMYR_GLYPH}:
                    return None
            return None

        def bearing_context(
            position: int, count: int, step: int, *, purpose: str
        ) -> tuple[tuple[int, int], ...]:
            """Traverse the complete Aeternum field until the center's obligation closes.

            Every encountered glyph is retained as a bearing-only witness.  Reflected
            glyphs are never translated as a second utterance and never become new source
            extent.  The return value contains only the speaking-body encounters needed by
            the center law, while ``aeternum_bearing_paths`` preserves every intervening
            Enoch and its unchanged authored bearing.
            """
            if count < 0 or step not in {-1, 1}:
                raise ValueError("invalid Aeternum bearing-context request")
            if count == 0:
                return ()
            if not bodies:
                raise LocalGrammarError("Aeternum center has no speaking body for this utterance obligation")
            nonlocal aeternum_period_source_positions
            if aeternum_period_source_positions is None:
                period_length = 2 * len(tokens)
                aeternum_period_source_positions = tuple(
                    aeternum_token(virtual_position).source_position
                    for virtual_position in range(period_length)
                )

            out: list[tuple[int, int]] = []
            encounters: list[AeternumBearingEncounter] = []
            start_virtual_position = position + step
            # Every 2N virtual positions repeat the exact finite source identities.
            # Python materializes that one authored period once; the compiled kernel
            # performs only the repeated integer walk and speaking-body mask checks.
            limit = 2 * len(tokens) * (count + 1)
            speaking_mask = bytes(
                1 if source_position in bodies else 0
                for source_position in range(len(tokens))
            )
            visited_source_positions, completed = _compiled_walk_aeternum(
                aeternum_period_source_positions,
                speaking_mask,
                start_virtual_position,
                step,
                count,
                limit,
            )
            for offset, source_position in enumerate(visited_source_positions):
                virtual_position = start_virtual_position + step * offset
                source_token = tokens[source_position]
                speaking = source_position in bodies
                encounters.append(AeternumBearingEncounter(
                    virtual_position=virtual_position,
                    source_position=source_position,
                    glyph=source_token.value,
                    token_kind=source_token.kind,
                    bearing=source_bearing(source_position),
                    imaginary=not (0 <= virtual_position < len(tokens)),
                    speaking_body=speaking,
                    bearing_only=True,
                ))
                if speaking:
                    out.append((source_position, virtual_position))
            if completed:
                aeternum_bearing_paths.append(AeternumBearingPath(
                    purpose=purpose,
                    origin_position=position,
                    step=step,
                    required_speaking_bodies=count,
                    speaking_body_source_positions=tuple(pos for pos, _ in out),
                    encounters=tuple(encounters),
                    completed=True,
                ))
                return tuple(out)
            raise LocalGrammarError("Aeternum mirror failed to close a speaking-body context")

        # Compatibility name retained deliberately: callers still request lexical context,
        # but the implementation now proves the full glyph-by-glyph bearing traversal.
        def lexical_context(
            position: int, count: int, step: int, *, purpose: str = "grammar-context"
        ) -> tuple[tuple[int, int], ...]:
            return bearing_context(position, count, step, purpose=purpose)

        # A center made solely of visible Enochian grammar is lawful information, energy,
        # and magic, but it has no lexical speaking body and therefore utters nothing.
        # Its mirror remains present as bearing-only structure; it is not translated into
        # a second sentence and may not fabricate a lexical vessel.
        if tokens and not bodies and all(token.value in VISIBLE_GRAMMARS for token in tokens):
            stack_positions = tuple(token.position for token in tokens)
            for token in tokens:
                action = "transmutation-gate-unuttered" if token.value == PHANTASMAGORIA_GLYPH else "grammar-lawful-unuttered"
                zero_and_one_events.append(ZeroAndOneEvent(
                    token.position, token.value, token.kind, action, False,
                ))
                grammar_events.append(LocalGrammarEvent(
                    token.position, token.value, "enochian-bearing-unuttered", (),
                    {"stack_positions": stack_positions},
                ))
            period_encounters = tuple(
                AeternumBearingEncounter(
                    virtual_position=virtual_position,
                    source_position=aeternum_token(virtual_position).source_position,
                    glyph=aeternum_token(virtual_position).value,
                    token_kind=aeternum_token(virtual_position).kind,
                    bearing=source_bearing(aeternum_token(virtual_position).source_position),
                    imaginary=not (0 <= virtual_position < len(tokens)),
                    speaking_body=False,
                    bearing_only=True,
                )
                for virtual_position in range(-len(tokens), len(tokens))
            )
            aeternum_bearing_paths.append(AeternumBearingPath(
                purpose="lawful-unuttered-enochian-field",
                origin_position=0,
                step=1,
                required_speaking_bodies=0,
                speaking_body_source_positions=(),
                encounters=period_encounters,
                completed=True,
            ))
            zero_and_one = ZeroAndOneTrace(tuple(zero_and_one_events))
            self.machine._validate_trace(frame.tokens, zero_and_one)
            local = LocalGrammarTrace(
                (), (), tuple(grammar_events), (), (), (), tuple(aeternum_bearing_paths),
            )
            return zero_and_one, local

        def register_body(token, resolution: object, event_name: str) -> None:
            zero_and_one_events.append(ZeroAndOneEvent(
                token.position, token.value, token.kind, event_name, True, resolution,
            ))
            body = bodies.get(token.position)
            if body is None:
                body = ResolvedBody(token.position, token.value, resolution)
                bodies[token.position] = body
            if token.position not in source_body_order:
                source_body_order.append(token.position)
            if token.position not in causal_body_order:
                causal_body_order.append(token.position)

        def apply_bearing(
            operator_position: int,
            operator_glyph: str,
            target_position: int,
            *,
            depth: int,
            stack_positions: tuple[int, ...],
            direction: str = "backward",
            scope: str = "grammar-stack-pattern",
        ) -> None:
            bearing = OFFICE_BEARINGS[operator_glyph]
            target = bodies[target_position]
            request = RecognitionRequest(
                operator_position=operator_position,
                operator_glyph=operator_glyph,
                target_position=target.position,
                target_glyph=target.glyph,
                bearing=bearing,
                direction=direction,
                scope=scope,
                retrocausal_depth=depth,
                stack_positions=stack_positions,
            )
            recognitions.append(request)
            office_resolution = self._resolve_office(target, bearing)
            bodies[target.position] = replace(
                target,
                recognition=bearing,
                office_resolutions=target.office_resolutions + (office_resolution,),
            )
            grammar_events.append(LocalGrammarEvent(
                operator_position,
                operator_glyph,
                "compound-retrocausal-bearing",
                (target.position,),
                request,
            ))

        def apply_echo_recursive(operator_position: int, target_position: int, stack_positions: tuple[int, ...]) -> None:
            target = bodies[target_position]
            request = RecognitionRequest(
                operator_position=operator_position,
                operator_glyph=OUROBORIC,
                target_position=target.position,
                target_glyph=target.glyph,
                bearing="recursive_identity",
                direction="ouroborose-echo",
                scope="ouroborose-loop",
                retrocausal_depth=0,
                stack_positions=stack_positions,
            )
            recognitions.append(request)
            office_resolution = self._resolve_office(target, "recursive_identity")
            bodies[target.position] = replace(
                target,
                recognition="recursive_identity",
                office_resolutions=target.office_resolutions + (office_resolution,),
            )
            grammar_events.append(LocalGrammarEvent(
                operator_position, OUROBORIC, "ouroborose-echo-recursive",
                (target.position,), request,
            ))

        def set_causal_pair(left_position: int, right_position: int, order: tuple[int, int]) -> None:
            if left_position == right_position:
                return
            if aeternum_pair_reorder is not None:
                aeternum_pair_reorder(causal_body_order, left_position, right_position, order)
                return
            if left_position not in causal_body_order or right_position not in causal_body_order:
                raise LocalGrammarError("⚶ Ouroborose Loop lost a lexical body")
            li = causal_body_order.index(left_position)
            ri = causal_body_order.index(right_position)
            if abs(ri - li) != 1:
                raise LocalGrammarError("⚶ Ouroborose Loop requires adjacent lexical bodies")
            lo, hi = sorted((li, ri))
            causal_body_order[lo:hi + 1] = list(order)

        def finalize_transmutation(
            operator_positions: tuple[int, ...],
            first_position: int,
            following_positions: tuple[int, ...] | list[int],
        ) -> None:
            vessel_positions = (first_position, *tuple(following_positions))
            if len(vessel_positions) != len(operator_positions) + 1:
                raise LocalGrammarError("ཪ corridor did not close over exactly K+1 Real vessels")
            if any(position not in bodies for position in vessel_positions):
                raise LocalGrammarError("ཪ corridor lost one of its Real vessels")
            vessels = tuple(bodies[position] for position in vessel_positions)

            # A reflected encounter points to the same finite real source body, so its
            # already-selected Phantasmagoria office resolution is reused exactly.
            resolution_by_real_position: dict[int, object] = {}
            office_resolutions_list: list[object] = []
            for body in vessels:
                resolution = resolution_by_real_position.get(body.position)
                if resolution is None:
                    resolution = self._resolve_office(body, "phantasmagoria")
                    resolution_by_real_position[body.position] = resolution
                office_resolutions_list.append(resolution)
            office_resolutions = tuple(office_resolutions_list)

            carrier = CARRIER_BY_GLYPH["⚝"]
            if carrier.name != "AHN" or carrier.structural_hz != 432 or carrier.parity_hz != 417:
                raise LocalGrammarError("ཪ cannot open: AHN 432 / i417 witness is not exact")

            returned_order = vessel_positions[1:] + vessel_positions[:1]
            # The mirror introduces imaginary encounters but no second real source
            # extent.  Therefore causal permutation is applied once per unique real
            # source body, in returned encounter order.
            unique_source = tuple(dict.fromkeys(vessel_positions))
            unique_return = tuple(dict.fromkeys(returned_order))
            if len(unique_source) > 1:
                if aeternum_corridor_reorder is not None:
                    aeternum_corridor_reorder(causal_body_order, unique_source, unique_return)
                else:
                    try:
                        indexes = tuple(causal_body_order.index(position) for position in unique_source)
                    except ValueError as exc:
                        raise LocalGrammarError("ཪ corridor lost one of its causal vessels") from exc
                    ordered_indexes = sorted(indexes)
                    if ordered_indexes != list(range(ordered_indexes[0], ordered_indexes[0] + len(ordered_indexes))):
                        raise LocalGrammarError("ཪ corridor requires adjacent causal Real vessels")
                    causal_body_order[ordered_indexes[0]:ordered_indexes[-1] + 1] = list(unique_return)

            state = PhantasmagoriaTransmutation(
                operator_positions=operator_positions,
                vessels=vessels,
                office_resolutions=office_resolutions,
                source_vessel_order=vessel_positions,
                returned_order=returned_order,
                gate_boundary="i417",
                carrier_glyph=carrier.glyph,
                carrier_name=carrier.name,
                structural_hz=str(carrier.structural_hz),
                imaginary_parity_hz=str(carrier.parity_hz),
            )
            transmutations.append(state)
            grammar_events.append(LocalGrammarEvent(
                operator_positions[-1], PHANTASMAGORIA_GLYPH, "phantasmagoria-transmutation",
                vessel_positions, state,
            ))

        def finalize_loop(
            loop_data: tuple[tuple[int, ...], int, tuple[tuple[int, str], ...], tuple[int, ...], int, int, int],
            right_offices: tuple[tuple[int, str], ...],
        ) -> None:
            (
                operator_positions, left_position, left_offices, loop_stack_positions,
                right_position, left_virtual, right_virtual,
            ) = loop_data
            if not operator_positions:
                raise LocalGrammarError("⚶ Ouroborose Loop has no written turn")
            left = bodies[left_position]
            right = bodies[right_position]
            n = len(operator_positions)
            # Current public GrimChain contains only the manifested spoken center.
            # The old House wrapper positions are gone: a true left-edge contact is
            # the Loop's real left lexical body at source position 0, and a true
            # right-edge contact is the complete B/R side reaching the last source
            # position. The mirror-echo algorithm below is otherwise preserved.
            # Preserve the original mirror-echo algorithm, but anchor its old
            # Court-adjacent trigger to the current public GrimChain itself.
            # A mirror edge is the immediate A ⚶... B form at a real source edge;
            # L/R office material remains part of the ordinary loop topology.
            crossed_left_mirror = left_virtual < 0
            crossed_right_mirror = right_virtual >= len(tokens)
            leading_echo = (
                crossed_left_mirror
                or (not crossed_right_mirror and left_position == 0)
            ) and not left_offices
            trailing_echo = (
                crossed_right_mirror
                or (not crossed_left_mirror and right_position == len(tokens) - 1)
            ) and not right_offices
            left_glyphs = tuple(g for _, g in left_offices)
            right_glyphs = tuple(g for _, g in right_offices)
            mirror_positions: tuple[int, ...] = ()
            mirror_source_positions: tuple[int, ...] = ()
            mirror_glyphs: tuple[str, ...] = ()

            def reflected_continuation(start_virtual: int, turns: int, step: int) -> tuple[tuple[int, ...], tuple[int, ...], tuple[str, ...]]:
                reflected = tuple(
                    aeternum_token(start_virtual + step * offset)
                    for offset in range(max(0, turns))
                )
                return (
                    tuple(token.mirror_position for token in reflected),
                    tuple(token.source_position for token in reflected),
                    tuple(token.value for token in reflected),
                )

            if leading_echo:
                # The root Court is already the real left lexical glyph at source position 1.
                # It uses the ordinary lexical/office resolver; only the Loop topology is special.
                set_causal_pair(left_position, right_position, (right_position, left_position))
                apply_echo_recursive(operator_positions[0], left_position, loop_stack_positions)
                for pos, glyph in right_offices:
                    apply_bearing(pos, glyph, left_position, depth=0, stack_positions=loop_stack_positions,
                                  direction="ouroborose-echo", scope="ouroborose-loop")
                mirror_start = left_virtual if left_virtual < 0 else -1
                mirror_turns = n if left_virtual < 0 else n - 1
                mirror_positions, mirror_source_positions, mirror_glyphs = reflected_continuation(
                    mirror_start, mirror_turns, -1,
                )
                topology_parts: list[str] = [right.glyph, OUROBORIC, left.glyph]
                for glyph in mirror_glyphs:
                    topology_parts.extend((OUROBORIC, glyph))
                topology = tuple(topology_parts)
                echo_position = left_position
            elif trailing_echo:
                # The alternating Court is already the ordinary right lexical glyph in the public line.
                if left_offices:
                    apply_echo_recursive(operator_positions[-1], right_position, loop_stack_positions)
                for pos, glyph in left_offices:
                    apply_bearing(pos, glyph, right_position, depth=0, stack_positions=loop_stack_positions,
                                  direction="ouroborose-echo", scope="ouroborose-loop")
                for pos, glyph in right_offices:
                    apply_bearing(pos, glyph, right_position, depth=0, stack_positions=loop_stack_positions,
                                  direction="ouroborose-echo", scope="ouroborose-loop")
                mirror_start = right_virtual if right_virtual >= len(tokens) else len(tokens)
                mirror_turns = n if right_virtual >= len(tokens) else n - 1
                mirror_positions, mirror_source_positions, mirror_glyphs = reflected_continuation(
                    mirror_start, mirror_turns, 1,
                )
                topology_parts = [left.glyph, *left_glyphs, OUROBORIC, right.glyph]
                for glyph in mirror_glyphs:
                    topology_parts.extend((OUROBORIC, glyph))
                topology = tuple(topology_parts)
                echo_position = right_position
            elif n == 1:
                for pos, glyph in left_offices:
                    apply_bearing(pos, glyph, right_position, depth=0, stack_positions=loop_stack_positions,
                                  direction="ouroborose-loop", scope="ouroborose-loop")
                for pos, glyph in right_offices:
                    apply_bearing(pos, glyph, right_position, depth=0, stack_positions=loop_stack_positions,
                                  direction="ouroborose-loop", scope="ouroborose-loop")
                topology = (left.glyph, right.glyph, OUROBORIC, *left_glyphs, *right_glyphs)
                echo_position = None
            elif n == 2:
                set_causal_pair(left_position, right_position, (right_position, left_position))
                for pos, glyph in right_offices:
                    apply_bearing(pos, glyph, left_position, depth=0, stack_positions=loop_stack_positions,
                                  direction="ouroborose-loop", scope="ouroborose-loop")
                for pos, glyph in left_offices:
                    apply_bearing(pos, glyph, left_position, depth=0, stack_positions=loop_stack_positions,
                                  direction="ouroborose-loop", scope="ouroborose-loop")
                topology = (right.glyph, OUROBORIC, left.glyph, *right_glyphs, OUROBORIC, *left_glyphs)
                echo_position = None
            else:
                # Three turns open all four authored topology blocks. Further turns continue the
                # same Loop by rotating those blocks; no turn is discarded and no ceiling exists.
                blocks: list[tuple[str, object, tuple[tuple[int, str], ...]]] = [
                    ("lex", right_position, ()),
                    ("office", right_position, right_offices),
                    ("office", left_position, left_offices),
                    ("lex", left_position, ()),
                ]
                if n > 3:
                    k = (n - 3) % 4
                    blocks = blocks[k:] + blocks[:k]
                lexical_order = tuple(int(value) for kind, value, _ in blocks if kind == "lex")
                if lexical_order != (left_position, right_position):
                    set_causal_pair(left_position, right_position, lexical_order)
                last_lex = None
                for kind, value, office_block in blocks:
                    if kind == "lex":
                        last_lex = int(value)
                        continue
                    if not office_block:
                        continue
                    if last_lex is None:
                        for prior_kind, prior_value, _ in reversed(blocks):
                            if prior_kind == "lex":
                                last_lex = int(prior_value)
                                break
                    if last_lex is None:
                        raise LocalGrammarError("⚶ Ouroborose Loop has no lexical owner")
                    for pos, glyph in office_block:
                        apply_bearing(pos, glyph, last_lex, depth=0, stack_positions=loop_stack_positions,
                                      direction="ouroborose-loop", scope="ouroborose-loop")
                flat: list[str] = []
                for bi, (kind, value, office_block) in enumerate(blocks):
                    if bi:
                        flat.append(OUROBORIC)
                    if kind == "lex":
                        flat.append(bodies[int(value)].glyph)
                    else:
                        flat.extend(g for _, g in office_block)
                flat.extend(OUROBORIC for _ in range(max(0, n - 3)))
                topology = tuple(flat)
                echo_position = None

            state = OuroboricState(
                operator_positions=operator_positions,
                winding_count=n,
                left=bodies[left_position],
                right=bodies[right_position],
                source_order=(left_position, *operator_positions, right_position),
                left_office_glyphs=left_glyphs,
                left_office_positions=tuple(pos for pos, _ in left_offices),
                right_office_glyphs=right_glyphs,
                right_office_positions=tuple(pos for pos, _ in right_offices),
                resolved_topology=topology,
                leading_echo=leading_echo,
                trailing_echo=trailing_echo,
                echo_position=echo_position,
                mirror_positions=mirror_positions,
                mirror_source_positions=mirror_source_positions,
                mirror_glyphs=mirror_glyphs,
                mirror_token_kinds=(),
                mirror_resolved_bearings=(),
                imaginary_reflection=bool(mirror_positions),
                bearing_preserved_in_reflection=True,
            )
            loops.append(state)
            grammar_events.append(LocalGrammarEvent(
                operator_positions[0], OUROBORIC, "ouroborose-loop",
                (left_position, right_position), state,
            ))

        while i < len(tokens):
            token = tokens[i]
            glyph = token.value

            if glyph == SHADOW_LOCUS:
                if shadow_ostensive:
                    register_body(token, bodies[token.position].lexical_resolution, glyph)
                else:
                    zero_and_one_events.append(ZeroAndOneEvent(
                        token.position, glyph, token.kind, glyph, False,
                    ))
                i += 1
                continue

            if glyph == AXIOMYR_GLYPH:
                if not axiomyr_ostensive:
                    raise LocalGrammarError("Axiomyr is only valid in the canonical depth-one body ☽᳀☾")
                register_body(token, bodies[token.position].lexical_resolution, glyph)
                i += 1
                continue

            if glyph in self.machine.ordinary_lexical_glyphs:
                resolution = bodies[token.position].lexical_resolution
                register_body(token, resolution, "lexical-resolution")

                if pending_transmutation is not None:
                    op_positions, first_position, following_positions = pending_transmutation
                    following_positions.append(token.position)
                    if len(following_positions) == len(op_positions):
                        finalize_transmutation(op_positions, first_position, following_positions)
                        pending_transmutation = None

                if pending_ouroborose is not None:
                    op_positions, left_position, left_offices, loop_stack_positions, left_virtual = pending_ouroborose
                    active_loop = (
                        op_positions, left_position, left_offices, loop_stack_positions,
                        token.position, left_virtual, token.position,
                    )
                    pending_ouroborose = None

                i += 1
                continue

            if active_loop is not None and glyph not in VISIBLE_GRAMMARS:
                finalize_loop(active_loop, ())
                active_loop = None

            if glyph not in VISIBLE_GRAMMARS:
                raise LocalGrammarError(
                    f"grammar glyph {glyph!r} at position {token.position} has no executable law"
                )

            j = i
            stack = []
            while j < len(tokens) and tokens[j].value in VISIBLE_GRAMMARS:
                stack.append(tokens[j])
                j += 1
            stack_positions = tuple(t.position for t in stack)
            stack_glyphs = tuple(t.value for t in stack)
            source_history_before_stack = tuple(source_body_order)

            for gt in stack:
                action = "transmutation-gate" if gt.value == PHANTASMAGORIA_GLYPH else "grammar-executed"
                local_action = "transmutation-gate" if gt.value == PHANTASMAGORIA_GLYPH else "grammar-stack-member"
                zero_and_one_events.append(ZeroAndOneEvent(
                    gt.position, gt.value, gt.kind, action, False,
                ))
                grammar_events.append(LocalGrammarEvent(
                    gt.position, gt.value, local_action, (),
                    {"stack_positions": stack_positions},
                ))

            transmutation_tokens = [gt for gt in stack if gt.value == PHANTASMAGORIA_GLYPH]
            if transmutation_tokens:
                first_key = transmutation_tokens[0]
                first_context = lexical_context(first_key.position, 1, -1, purpose="phantasmagoria-preceding-vessel")
                if pending_transmutation is not None:
                    raise LocalGrammarError("ཪ encountered before the prior Transmutation Corridor completed")
                pending_transmutation = (
                    tuple(gt.position for gt in transmutation_tokens),
                    first_context[0][0],
                    [],
                )

            reversal_tokens = [gt for gt in stack if gt.value == OUROBORIC]
            bearing_tokens = [gt for gt in stack if gt.value in OFFICE_BEARINGS]

            if active_loop is not None:
                if reversal_tokens or transmutation_tokens:
                    finalize_loop(active_loop, ())
                    active_loop = None
                elif bearing_tokens and len(bearing_tokens) == len(stack):
                    finalize_loop(active_loop, tuple((gt.position, gt.value) for gt in bearing_tokens))
                    active_loop = None
                    bearing_tokens = []

            if reversal_tokens:
                # A maximal Enoch stack may contain more than one separate ⚶ run.
                # Each consecutive run is one winding.  Separating Enochs keep their
                # own laws; they do not silently merge two windings or invalidate one.
                reversal_runs: list[tuple[int, int, tuple[object, ...]]] = []
                k = 0
                while k < len(stack):
                    if stack[k].value != OUROBORIC:
                        k += 1
                        continue
                    start = k
                    run: list[object] = []
                    while k < len(stack) and stack[k].value == OUROBORIC:
                        run.append(stack[k])
                        k += 1
                    reversal_runs.append((start, k, tuple(run)))

                claimed_office_positions: set[int] = set()
                for run_index, (start, end, reversal_run) in enumerate(reversal_runs):
                    left_start = start
                    while left_start > 0 and stack[left_start - 1].value in OFFICE_BEARINGS:
                        left_start -= 1
                    left_offices = tuple(
                        (gt.position, gt.value) for gt in stack[left_start:start]
                    )
                    claimed_office_positions.update(pos for pos, _ in left_offices)
                    left_position, left_virtual = lexical_context(stack[start].position, 1, -1, purpose="ouroborose-left-body")[0]
                    loop_positions = tuple(gt.position for gt in stack[left_start:end])
                    operator_positions = tuple(gt.position for gt in reversal_run)

                    is_last_run = run_index == len(reversal_runs) - 1
                    if is_last_run:
                        if pending_ouroborose is not None:
                            raise LocalGrammarError(
                                "⚶ Ouroborose Loop reached a new turn-run before its following lexical body"
                            )
                        pending_ouroborose = (
                            operator_positions,
                            left_position,
                            left_offices,
                            loop_positions,
                            left_virtual,
                        )
                    else:
                        right_position, right_virtual = lexical_context(stack[end - 1].position, 1, 1, purpose="ouroborose-right-body")[0]
                        finalize_loop((
                            operator_positions,
                            left_position,
                            left_offices,
                            loop_positions,
                            right_position,
                            left_virtual,
                            right_virtual,
                        ), ())

                bearing_tokens = [
                    gt for gt in bearing_tokens if gt.position not in claimed_office_positions
                ]

            if bearing_tokens:
                bearing_count = len(bearing_tokens)
                context = lexical_context(bearing_tokens[0].position, bearing_count, -1, purpose="office-retrocausal-bearing")
                for index, gt in enumerate(bearing_tokens):
                    depth = bearing_count - 1 - index
                    target_position, target_virtual = context[depth]
                    apply_bearing(
                        gt.position, gt.value, target_position,
                        depth=depth, stack_positions=stack_positions,
                        direction=("aeternum-left-reflection" if target_virtual < 0 else "backward"),
                    )

            grammar_events.append(LocalGrammarEvent(
                stack[-1].position, "".join(stack_glyphs), "compound-grammar-stack",
                tuple(source_history_before_stack),
                {"stack_positions": stack_positions, "stack_length": len(stack)},
            ))
            i = j

        if pending_transmutation is not None:
            op_positions, first_position, following_positions = pending_transmutation
            needed = len(op_positions) - len(following_positions)
            reflected_following = lexical_context(len(tokens) - 1, needed, 1, purpose="phantasmagoria-following-vessels")
            following_positions.extend(position for position, _virtual in reflected_following)
            finalize_transmutation(op_positions, first_position, following_positions)
            pending_transmutation = None
        if pending_ouroborose is not None:
            op_positions, left_position, left_offices, loop_stack_positions, left_virtual = pending_ouroborose
            right_position, right_virtual = lexical_context(len(tokens) - 1, 1, 1, purpose="ouroborose-following-body")[0]
            active_loop = (
                op_positions, left_position, left_offices, loop_stack_positions,
                right_position, left_virtual, right_virtual,
            )
            pending_ouroborose = None
        if active_loop is not None:
            finalize_loop(active_loop, ())
            active_loop = None

        recognition_by_operator: dict[int, RecognitionRequest] = {
            request.operator_position: request for request in recognitions
        }
        transmutation_positions = {position for state in transmutations for position in state.operator_positions}
        transmuted_vessel_resolution: dict[int, object] = {
            body.position: resolution
            for state in transmutations
            for body, resolution in zip(state.vessels, state.office_resolutions)
        }
        loop_positions = {position for loop in loops for position in loop.operator_positions}
        token_by_position = {token.position: token for token in tokens}

        def resolved_reflection_bearing(source_position: int) -> str | None:
            token = token_by_position[source_position]
            request = recognition_by_operator.get(source_position)
            if request is not None:
                return request.bearing
            if source_position in transmutation_positions or source_position in transmuted_vessel_resolution:
                return "phantasmagoria"
            if source_position in loop_positions:
                return "ouroborose_loop"
            if token.kind == "lexical":
                return "seed_identity"
            if token.value in {SHADOW_LOCUS, AXIOMYR_GLYPH}:
                return None
            raise LocalGrammarError(
                f"reflected grammar at source position {source_position} lacks its resolved original law"
            )

        reflected_loops: list[OuroboricState] = []
        for loop in loops:
            kinds = tuple(token_by_position[pos].kind for pos in loop.mirror_source_positions)
            bearings = tuple(resolved_reflection_bearing(pos) for pos in loop.mirror_source_positions)
            mirror_corridor = frame.mirror_corridor_period() if loop.imaginary_reflection else ()
            def ostensive_provenance(source_position: int) -> tuple[str | None, str | None, str | None]:
                resolution = transmuted_vessel_resolution.get(source_position)
                if resolution is None:
                    return (None, None, None)
                return (
                    getattr(resolution, "ostensive_variant"),
                    getattr(resolution, "resolved_body"),
                    getattr(resolution, "source_authority"),
                )

            mirror_ostensive = tuple(ostensive_provenance(pos) for pos in loop.mirror_source_positions)
            corridor_ostensive = tuple(ostensive_provenance(token.source_position) for token in mirror_corridor)
            reflected_loops.append(replace(
                loop,
                mirror_token_kinds=kinds,
                mirror_resolved_bearings=bearings,
                mirror_ostensive_variants=tuple(item[0] for item in mirror_ostensive),
                mirror_ostensive_bodies=tuple(item[1] for item in mirror_ostensive),
                mirror_ostensive_authorities=tuple(item[2] for item in mirror_ostensive),
                mirror_corridor_glyphs=tuple(token.value for token in mirror_corridor),
                mirror_corridor_source_positions=tuple(token.source_position for token in mirror_corridor),
                mirror_corridor_resolved_bearings=tuple(
                    resolved_reflection_bearing(token.source_position) for token in mirror_corridor
                ),
                mirror_corridor_ostensive_variants=tuple(item[0] for item in corridor_ostensive),
                mirror_corridor_ostensive_bodies=tuple(item[1] for item in corridor_ostensive),
                mirror_corridor_ostensive_authorities=tuple(item[2] for item in corridor_ostensive),
            ))
        loops = reflected_loops
        loops = [replace(loop, left=bodies[loop.left.position], right=bodies[loop.right.position]) for loop in loops]
        transmutations = [replace(state, vessels=tuple(bodies[body.position] for body in state.vessels)) for state in transmutations]

        zero_and_one = ZeroAndOneTrace(tuple(zero_and_one_events))
        self.machine._validate_trace(frame.tokens, zero_and_one)
        local = LocalGrammarTrace(
            tuple(bodies[pos] for pos in source_body_order),
            tuple(causal_body_order),
            tuple(grammar_events), tuple(recognitions), tuple(loops), tuple(transmutations),
            tuple(aeternum_bearing_paths),
        )
        return zero_and_one, local
