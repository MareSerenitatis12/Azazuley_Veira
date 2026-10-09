"""Standalone hypothetical physical movement of the written GrimChain.

Only the original chain and Sydonic's Enochian execution records participate.
No mirror renderer, spoken-word projection, or translation presentation is used.
"""
from dataclasses import dataclass
from functools import lru_cache

from sydonic_magicae_translation_matrix.models import DomusFrame


def office_name(office):
    return 'SeeD' if office == 'seed_identity' else office.replace('_', ' ').title() + ' Office'


@dataclass(frozen=True, slots=True)
class PathStep:
    label: str
    operators: str
    targets: str
    before_body: str
    body: str
    explanation: str
    before_offices: tuple[str, ...] = ()
    offices: tuple[str, ...] = ()
    whole_traversal: bool = True
    after_targets: str = ''


@dataclass(frozen=True, slots=True)
class PathOut:
    source: str
    steps: tuple[PathStep, ...]
    final_body: str
    final_offices: tuple[str, ...] = ()
    capture_error: str | None = None


@dataclass(frozen=True, slots=True)
class _Glyph:
    text: str
    origin: int


def _replace_related(body, positions, replacement):
    indexes = [i for i, glyph in enumerate(body) if glyph.origin in positions]
    if not indexes:
        raise ValueError('Transformation has no affected glyphs')
    first = indexes[0]
    selected = set(indexes)
    # Unaffected glyphs, including resolved Tail seams, retain their order.
    return [*body[:first], *replacement, *(glyph for i, glyph in enumerate(body[first:], first) if i not in selected)]


def _build_path(source, engine):
    """Execute the original source once and project physical glyph movement.

    Identity coordinates are private bookkeeping for stable glyph ownership.
    The public path consists only of glyph states, Enochians, and Offices.
    """
    frame = DomusFrame(source=source, tokens=engine.lexer.lex(source))
    _zero, local = engine.sequential.execute_frame(frame)
    original = {token.position: _Glyph(token.value, token.position) for token in frame.tokens}
    body = list(original.values())
    steps = []
    assigned = {}
    head_offices = {}
    inherited = {
        resolved.position: [office_name(resolved.lexical_resolution.authored_office)]
        for resolved in local.bodies if resolved.lexical_resolution is not None
    }

    def text(glyphs):
        return ''.join(glyph.text for glyph in glyphs)

    def roles(positions):
        return tuple(dict.fromkeys(role for position in positions for role in inherited.get(position, ())))

    def source_text(positions):
        return ''.join(original[position].text for position in positions)

    for event in local.events:
        payload = event.payload
        before = text(body)
        if event.event == 'orobouros-tail-transformation':
            actual = tuple(glyph.origin for glyph in body[payload.start:payload.stop])
            if actual != payload.before_positions:
                raise ValueError('Tail movement differs from its recorded traversal')
            targets = text(body[payload.start:payload.stop])
            before_roles = roles(payload.before_positions)
            body[payload.start:payload.stop] = [original[p] for p in payload.after_positions]
            operators = original[payload.operator_position].text
            label = 'Orobouros Tail'
            explanation = 'Tail reverses this window of the GrimChain.'
            affected = payload.after_positions
            after_targets = text(body[payload.start:payload.stop])
        elif event.event in {'compound-retrocausal-bearing', 'orobouros-head-echo-recursive'}:
            # These are the Head's internal Office assignments; its authored
            # topology records their physical arrangement as one Head step.
            target = payload.target_position
            before_roles = roles((target,))
            if payload.scope == 'orobouros-head':
                head_offices.setdefault(target, []).append(office_name(payload.bearing))
                continue
            inherited.setdefault(target, []).append(office_name(payload.bearing))
            operator = payload.operator_position
            moving = next(glyph for glyph in body if glyph.origin == operator)
            targets = original[target].text
            remaining = [glyph for glyph in body if glyph.origin != operator]
            at = next(i for i, glyph in enumerate(remaining) if glyph.origin == target) + 1
            # Keep previous inherited Offices with this body, in their order.
            previous_offices = assigned.setdefault(target, set())
            while at < len(remaining) and remaining[at].origin in previous_offices:
                at += 1
            body = [*remaining[:at], moving, *remaining[at:]]
            previous_offices.add(operator)
            operators = moving.text
            label = payload.bearing.replace('_', ' ').title()
            explanation = 'This body inherits ' + office_name(payload.bearing) + '.'
            affected = (target,)
            after_targets = targets
        elif event.event == 'orobouros-head':
            participating = {
                payload.left.position, payload.right.position, *payload.operator_positions, *payload.source_order,
                *payload.left_office_positions, *payload.right_office_positions,
            }
            targets = source_text((payload.left.position, payload.right.position))
            before_roles = roles((payload.left.position, payload.right.position))
            for position, offices in head_offices.items():
                inherited.setdefault(position, []).extend(offices)
            head_offices.clear()
            available = {}
            for glyph in body:
                if glyph.origin in participating:
                    available.setdefault(glyph.text, []).append(glyph)
            replacement = []
            for glyph in payload.resolved_topology:
                queue = available.get(glyph, [])
                if queue:
                    replacement.append(queue.pop(0))
                else:
                    # Authored Head mirror echoes can repeat a source glyph.
                    origin = next((p for p in payload.mirror_source_positions if original[p].text == glyph), None)
                    if origin is None:
                        origin = next(p for p in participating if original[p].text == glyph)
                    replacement.append(_Glyph(glyph, origin))
            body = _replace_related(body, participating, replacement)
            operators = source_text(payload.operator_positions)
            label = 'Orobouros Head'
            explanation = f'Head rearranges these bodies and Offices through {payload.winding_count} turns.'
            if payload.leading_echo or payload.trailing_echo:
                explanation += ' Its recorded arrangement includes a body echo.'
            affected = (payload.left.position, payload.right.position)
            after_targets = text(replacement)
        elif event.event == 'phantasmagoria-transmutation':
            participating = {*payload.source_vessel_order, *payload.operator_positions}
            participating.update(operator for position in payload.source_vessel_order for operator in assigned.get(position, ()))
            targets = source_text(payload.source_vessel_order)
            before_roles = roles(payload.source_vessel_order)
            replacement = []
            for index, position in enumerate(payload.returned_order):
                replacement.append(original[position])
                replacement.extend(glyph for glyph in body if glyph.origin in assigned.get(position, ()))
                if index < len(payload.operator_positions):
                    replacement.append(original[payload.operator_positions[index]])
                inherited[position] = ['Phantasmagoria Office']
            body = _replace_related(body, participating, replacement)
            operators = source_text(payload.operator_positions)
            label = 'Phantasmagoria'
            explanation = 'Phantasmagoria moves the vessels into their returned order.'
            affected = payload.returned_order
            after_targets = source_text(payload.returned_order)
        else:
            continue
        steps.append(PathStep(label, operators, targets, before, text(body), explanation, before_roles, roles(affected), label == 'Orobouros Tail', after_targets))

    return PathOut(source, tuple(steps), text(body), roles(glyph.origin for glyph in body))


@lru_cache(maxsize=32)
def build_path(source, engine):
    """Keep this independent view from changing ordinary translation outcomes."""
    try:
        if engine.lexical_resolver.living_mirror_entries(source):
            return PathOut(source, (), source)
        return _build_path(source, engine)
    except Exception as exc:
        return PathOut(source, (), source, capture_error=str(exc))
