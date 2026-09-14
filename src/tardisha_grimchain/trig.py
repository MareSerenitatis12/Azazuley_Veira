"""Typed Axiom TRIG Mirror and completion witness.

TRIG carries the ordered Q1→Q3 materialization and Q3→Q1 committed return.
Every completion claim is rederived from exact Court, lineage, parity, resonance,
and D-COMP bodies. Float images never replace the exact frequencies.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from decimal import Decimal
import json
from math import isfinite
from typing import Final, Sequence

from .alqc_digest import alqc_hexdigest, validate_digest_hex
from .aeon_layers import court_layer, derive_court_motion, derive_domus_motion, normalize_source_domain
from .canon import FrequencyAnchor, GLYPH_BODY, law
from .court_registry import court_record
from .manifestation import close_boundary
from .qstate_glyphs import Q_STATES, derive_domus_q_body
from .source_emission import SourceEmission, Q5Fraction, resolve_court_bearing, validate_court_bearing_lineage
from .mirror_math import derive_goetics

TRIG_GLYPH: Final[str] = "⌬"
TRIG_NAME: Final[str] = "TRIG"
TRIG_FREQUENCY: Final[FrequencyAnchor] = law(TRIG_GLYPH).frequency
TRIG_Q_BIAS: Final[str] = "Q3"
TRIG_Q_VECTOR: Final[tuple[int, int, int, int]] = (1, 1, 3, 2)

PARITY_OPERATOR: Final[str] = "𝔓"
BOUND_TENSOR_OPERATOR: Final[str] = "T_Bound"
COMMITMENT_OPERATOR: Final[str] = "✡"
COMMITMENT_FREQUENCY: Final[FrequencyAnchor] = law(COMMITMENT_OPERATOR).frequency
RESONANCE_OPERATOR: Final[str] = "❄"
RESONANCE_FREQUENCY: Final[FrequencyAnchor] = law(RESONANCE_OPERATOR).frequency

GLOBAL_SHADOW_PARITY: Final[tuple[str, str]] = ("Q2", "Q3")
FORWARD_MIRROR_MAP: Final[tuple[str, str]] = ("Q1", "Q3")
RETURN_COMMITMENT_MAP: Final[tuple[str, str]] = ("Q3", "Q1")
TRIG_CYCLE_DOMAIN: Final[bytes] = b"TARDISHA:TRIG-MIRROR-CYCLE\x00"

_RETURN_OBLIGATION: Final[str] = (
    "Preserve the Q2↔Q3 Shadow parity ledger; materialize Q1→Q3 through "
    "the Bound Tensor and Klein parity; return Q3→Q1 through ✡ commitment "
    "and ❄ resonance without erasing lineage; let ⌬ seal only when the complete "
    "one-turn return closes at D-COMP zero."
)


@dataclass(frozen=True, slots=True)
class ExactDomusFrequency:
    """Immutable Goetic anchor plus exact Q(√5) Domus focal breath."""

    anchor_glyph: str
    anchor_frequency: FrequencyAnchor
    focal_breath: Q5Fraction

    @property
    def image(self) -> complex:
        return complex(self.anchor_frequency) + complex(self.focal_breath.value, 0.0)


def _frequency_body(value: FrequencyAnchor) -> dict[str, str | None]:
    if not isinstance(value, FrequencyAnchor):
        raise TypeError("frequency must be one exact FrequencyAnchor")
    return {
        "structural_hz": str(value.structural_hz),
        "parity_hz": None if value.parity_hz is None else str(value.parity_hz),
    }


def _domus_frequency_body(value: ExactDomusFrequency) -> dict[str, object]:
    if not isinstance(value, ExactDomusFrequency):
        raise TypeError("domus frequency must be one ExactDomusFrequency")
    return {
        "anchor_glyph": value.anchor_glyph,
        "anchor_frequency": _frequency_body(value.anchor_frequency),
        "focal_breath": {
            "a": value.focal_breath.a,
            "b": value.focal_breath.b,
            "denominator": value.focal_breath.denominator,
        },
    }


def exact_domus_frequency_from_bearing(
    alternating_court_address: int,
    alternating_court_bearing: Sequence[int],
) -> ExactDomusFrequency:
    if isinstance(alternating_court_address, bool) or not isinstance(alternating_court_address, int) or not 0 <= alternating_court_address < 144:
        raise ValueError("alternating Court address must be an exact integer in [0,143]")
    lineage = validate_court_bearing_lineage(alternating_court_bearing)
    if lineage[0] != alternating_court_address:
        raise ValueError("alternating Court bearing address does not match Court D")
    rec = court_record(alternating_court_address)
    anchor_glyph = GLYPH_BODY[rec.j]
    xi = Q5Fraction(lineage[11], lineage[12], lineage[13])
    return ExactDomusFrequency(
        anchor_glyph=anchor_glyph,
        anchor_frequency=law(anchor_glyph).frequency,
        focal_breath=xi.times_phi_squared(),
    )


def _exact_float(value: object, field: str) -> float:
    if type(value) is not float:
        raise TypeError(f"{field} must be one exact float image")
    if not isfinite(value):
        raise ValueError(f"{field} must be finite")
    return value


def _require_boolean(value: object, field: str) -> bool:
    if type(value) is not bool:
        raise TypeError(f"{field} must be one exact Boolean witness")
    return value


def _digest(value: str, field: str) -> str:
    return validate_digest_hex(value, field=field)


def _display(value: object) -> object:
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, tuple):
        return [_display(item) for item in value]
    if isinstance(value, list):
        return [_display(item) for item in value]
    if isinstance(value, dict):
        return {key: _display(item) for key, item in value.items()}
    return value


@dataclass(frozen=True, slots=True)
class TrigMirrorWitness:
    operator_glyph: str
    operator_name: str
    structural_frequency: FrequencyAnchor
    operator_q_bias: str
    operator_q_vector: tuple[int, int, int, int]

    parity_operator: str
    bound_tensor_operator: str
    commitment_operator: str
    commitment_frequency: FrequencyAnchor
    resonance_operator: str
    resonance_frequency: FrequencyAnchor

    global_shadow_parity: tuple[str, str]
    forward_mirror_map: tuple[str, str]
    return_commitment_map: tuple[str, str]

    source_digest: str
    source_size: int
    source_domain: str
    nonce: int
    governing_court_address: int
    alternating_court_address: int
    governing_court_phase_digest: str
    alternating_court_bearing: tuple[int, ...]
    domus_frequency: ExactDomusFrequency
    domus_body_commitment: str

    q_states: tuple[str, str, str, str]
    q_vector_values: tuple[int, int, int, int]
    q1_truth_value: int
    q3_recursion_value: int
    q3_recursion_gain: float
    final_shadow_parity: str

    bound_tensor_witnessed: bool
    court_rooted: bool
    derives_through_courts_only: bool
    global_shadow_parity_preserved: bool
    mirror_materialization_typed: bool
    commitment_return_typed: bool
    resonance_lock_witnessed: bool
    lineage_preserved: bool

    terminal_dcomp: float
    one_turn_return_closed: bool
    completion_reached: bool
    return_obligation: str
    classical_hodge_computation: bool
    derivation: str
    cycle_digest: str

    def as_dict(self) -> dict[str, object]:
        return _display(asdict(self))  # type: ignore[return-value]


def _payload(witness: TrigMirrorWitness) -> bytes:
    body = {
        "operator": {
            "glyph": witness.operator_glyph,
            "name": witness.operator_name,
            "frequency": _frequency_body(witness.structural_frequency),
            "q_bias": witness.operator_q_bias,
            "q_vector": list(witness.operator_q_vector),
        },
        "operators": {
            "parity": witness.parity_operator,
            "bound_tensor": witness.bound_tensor_operator,
            "commitment": witness.commitment_operator,
            "commitment_frequency": _frequency_body(witness.commitment_frequency),
            "resonance": witness.resonance_operator,
            "resonance_frequency": _frequency_body(witness.resonance_frequency),
        },
        "maps": {
            "global_shadow_parity": list(witness.global_shadow_parity),
            "forward_mirror": list(witness.forward_mirror_map),
            "return_commitment": list(witness.return_commitment_map),
        },
        "source": {
            "digest": witness.source_digest,
            "size": witness.source_size,
            "domain": witness.source_domain,
            "nonce": witness.nonce,
        },
        "court_domus": {
            "governing_court": witness.governing_court_address,
            "alternating_court": witness.alternating_court_address,
            "governing_phase": witness.governing_court_phase_digest,
            "alternating_court_bearing": list(witness.alternating_court_bearing),
            "domus_frequency": _domus_frequency_body(witness.domus_frequency),
            "body_commitment": witness.domus_body_commitment,
        },
        "q_body": {
            "states": list(witness.q_states),
            "values": list(witness.q_vector_values),
            "q1_truth_value": witness.q1_truth_value,
            "q3_recursion_value": witness.q3_recursion_value,
            "q3_recursion_gain": witness.q3_recursion_gain.hex(),
            "final_shadow_parity": witness.final_shadow_parity,
        },
        "typing": {
            "bound_tensor_witnessed": witness.bound_tensor_witnessed,
            "court_rooted": witness.court_rooted,
            "derives_through_courts_only": witness.derives_through_courts_only,
            "global_shadow_parity_preserved": witness.global_shadow_parity_preserved,
            "mirror_materialization_typed": witness.mirror_materialization_typed,
            "commitment_return_typed": witness.commitment_return_typed,
            "resonance_lock_witnessed": witness.resonance_lock_witnessed,
            "lineage_preserved": witness.lineage_preserved,
        },
        "return": {
            "terminal_dcomp": witness.terminal_dcomp.hex(),
            "one_turn_return_closed": witness.one_turn_return_closed,
            "completion_reached": witness.completion_reached,
            "obligation": witness.return_obligation,
        },
        "scope": {
            "classical_hodge_computation": witness.classical_hodge_computation,
            "derivation": witness.derivation,
        },
    }
    return json.dumps(body, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def derive_trig_mirror(
    *,
    source_digest: str,
    source_size: int,
    source_domain: str | bytes,
    nonce: int,
    governing_court_address: int,
    alternating_court_address: int,
    governing_court_phase_digest: str,
    alternating_court_bearing: Sequence[int],
    domus_frequency: complex,
    domus_body_commitment: str,
    q_states: Sequence[str],
    q_vector_values: Sequence[int],
    q3_recursion_gain: float,
    final_shadow_parity: str,
    bound_tensor_witnessed: bool,
    derives_through_courts_only: bool,
    resonance_lock_witnessed: bool,
    lineage_preserved: bool,
    terminal_dcomp: float,
    one_turn_return_closed: bool,
) -> TrigMirrorWitness:
    trig = law(TRIG_GLYPH)
    if trig.frequency != TRIG_FREQUENCY or trig.q_bias != TRIG_Q_BIAS or trig.q_vector != TRIG_Q_VECTOR:
        raise RuntimeError("the immutable TRIG Goetic body has changed")

    digest = _digest(source_digest, "source_digest")
    body_commitment = _digest(domus_body_commitment, "domus_body_commitment")
    governing_phase = _digest(governing_court_phase_digest, "governing_court_phase_digest")
    bearing_lineage = validate_court_bearing_lineage(alternating_court_bearing)
    domain = normalize_source_domain(source_domain).decode("ascii").rstrip("\x00")

    if isinstance(source_size, bool) or not isinstance(source_size, int) or source_size < 0:
        raise ValueError("source_size must be a non-negative integer")
    if isinstance(nonce, bool) or not isinstance(nonce, int) or not 0 <= nonce < 2**64:
        raise ValueError("nonce must be an integer in [0,2^64)")
    for field, address in (("governing_court_address", governing_court_address), ("alternating_court_address", alternating_court_address)):
        if isinstance(address, bool) or not isinstance(address, int) or not 0 <= address < 144:
            raise ValueError(f"{field} must be an exact integer in [0,143]")
    if bearing_lineage[0] != alternating_court_address:
        raise ValueError("alternating Court bearing address does not match Court D")

    if not isinstance(q_states, (tuple, list)) or any(type(value) is not str for value in q_states):
        raise TypeError("q_states must be a list or tuple of exact strings")
    states = tuple(q_states)
    if states != Q_STATES:
        raise ValueError("TRIG requires the fixed Q0/Q1/Q2/Q3 state slots")
    if not isinstance(q_vector_values, (tuple, list)):
        raise TypeError("q_vector_values must be a list or tuple")
    values = tuple(q_vector_values)
    if len(values) != 4 or any(isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= 3 for value in values):
        raise ValueError("TRIG Q-vector values must be four exact integers in [0,3]")
    if type(final_shadow_parity) is not str:
        raise TypeError("final_shadow_parity must be one exact string")

    recursion_gain = _exact_float(q3_recursion_gain, "q3_recursion_gain")
    terminal = _exact_float(terminal_dcomp, "terminal_dcomp")
    if recursion_gain < 0.0 or terminal < 0.0:
        raise ValueError("q3_recursion_gain and terminal_dcomp must be non-negative")
    bound = _require_boolean(bound_tensor_witnessed, "bound_tensor_witnessed")
    court_derivation = _require_boolean(derives_through_courts_only, "derives_through_courts_only")
    resonance_lock = _require_boolean(resonance_lock_witnessed, "resonance_lock_witnessed")
    lineage = _require_boolean(lineage_preserved, "lineage_preserved")
    one_turn = _require_boolean(one_turn_return_closed, "one_turn_return_closed")

    if type(domus_frequency) is not complex:
        raise TypeError("domus_frequency must be the exact complex image supplied by Domus")
    exact_frequency = exact_domus_frequency_from_bearing(alternating_court_address, bearing_lineage)
    if domus_frequency != exact_frequency.image:
        raise ValueError("domus_frequency image does not return from its exact Court anchor and Q(√5) breath")

    court_rooted = court_derivation
    shadow_parity_preserved = final_shadow_parity == "Q3"
    mirror_typed = bound and court_rooted and values[1] > 0 and (values[3] > 0 or recursion_gain > 0.0)
    return_typed = resonance_lock and lineage and values[1] > 0 and shadow_parity_preserved
    completion = mirror_typed and return_typed and shadow_parity_preserved and one_turn and terminal == 0.0

    derivation = (
        "Q1 --𝔓[T_Bound]--> Q3 --✡/❄--> Q1; "
        "Q2↔Q3 remains the separate Shadow parity law; "
        f"⌬ completion={'reached' if completion else 'owed'} from the complete return body."
    )

    provisional = TrigMirrorWitness(
        operator_glyph=TRIG_GLYPH,
        operator_name=TRIG_NAME,
        structural_frequency=TRIG_FREQUENCY,
        operator_q_bias=TRIG_Q_BIAS,
        operator_q_vector=TRIG_Q_VECTOR,
        parity_operator=PARITY_OPERATOR,
        bound_tensor_operator=BOUND_TENSOR_OPERATOR,
        commitment_operator=COMMITMENT_OPERATOR,
        commitment_frequency=COMMITMENT_FREQUENCY,
        resonance_operator=RESONANCE_OPERATOR,
        resonance_frequency=RESONANCE_FREQUENCY,
        global_shadow_parity=GLOBAL_SHADOW_PARITY,
        forward_mirror_map=FORWARD_MIRROR_MAP,
        return_commitment_map=RETURN_COMMITMENT_MAP,
        source_digest=digest,
        source_size=source_size,
        source_domain=domain,
        nonce=nonce,
        governing_court_address=governing_court_address,
        alternating_court_address=alternating_court_address,
        governing_court_phase_digest=governing_phase,
        alternating_court_bearing=bearing_lineage,
        domus_frequency=exact_frequency,
        domus_body_commitment=body_commitment,
        q_states=states,  # type: ignore[arg-type]
        q_vector_values=values,  # type: ignore[arg-type]
        q1_truth_value=values[1],
        q3_recursion_value=values[3],
        q3_recursion_gain=recursion_gain,
        final_shadow_parity=final_shadow_parity,
        bound_tensor_witnessed=bound,
        court_rooted=court_rooted,
        derives_through_courts_only=court_derivation,
        global_shadow_parity_preserved=shadow_parity_preserved,
        mirror_materialization_typed=mirror_typed,
        commitment_return_typed=return_typed,
        resonance_lock_witnessed=resonance_lock,
        lineage_preserved=lineage,
        terminal_dcomp=terminal,
        one_turn_return_closed=one_turn,
        completion_reached=completion,
        return_obligation=_RETURN_OBLIGATION,
        classical_hodge_computation=False,
        derivation=derivation,
        cycle_digest="0" * 64,
    )
    cycle_digest = alqc_hexdigest(_payload(provisional), domain=TRIG_CYCLE_DOMAIN)
    return TrigMirrorWitness(**{**asdict(provisional), "domus_frequency": exact_frequency, "structural_frequency": TRIG_FREQUENCY, "commitment_frequency": COMMITMENT_FREQUENCY, "resonance_frequency": RESONANCE_FREQUENCY, "cycle_digest": cycle_digest})


def verify_trig_mirror(witness: TrigMirrorWitness, emission: SourceEmission) -> bool:
    """Rederive TRIG from the complete source emission and exact Court bodies."""
    try:
        if not isinstance(emission, SourceEmission):
            return False
        domain = normalize_source_domain(emission.source_domain).decode("ascii").rstrip("\x00")
        if (
            witness.source_digest != emission.source_digest
            or witness.source_size != emission.source_size
            or witness.source_domain != domain
        ):
            return False

        source_derivation = derive_goetics(emission)
        governing = court_record(source_derivation.court_address)
        alternating_bearing = resolve_court_bearing(emission)
        alternating = alternating_bearing.court
        if (
            witness.governing_court_address != governing.address
            or witness.alternating_court_address != alternating.address
        ):
            return False

        governing_layer = court_layer(governing)
        alternating_layer = court_layer(alternating)
        governing_motion = derive_court_motion(
            governing,
            source_digest=emission.source_digest,
            source_size=emission.source_size,
            source_domain=emission.source_domain,
            nonce=witness.nonce,
        )
        domus_motion = derive_domus_motion(
            governing_layer,
            alternating_layer,
            bearing=alternating_bearing,
        )
        q_body = derive_domus_q_body(
            governing_layer.governing_goetic.q_bias,
            governing_layer.governing_goetic.q_vector,
        )
        manifestation = close_boundary(
            governing_layer.governing_goetic.q_vector,
            alternating_layer.governing_goetic.q_vector,
            court=governing.address,
        )

        expected = derive_trig_mirror(
            source_digest=emission.source_digest,
            source_size=emission.source_size,
            source_domain=emission.source_domain,
            nonce=witness.nonce,
            governing_court_address=governing.address,
            alternating_court_address=alternating.address,
            governing_court_phase_digest=governing_motion.phase.digest,
            alternating_court_bearing=alternating_bearing.lineage,
            domus_frequency=domus_motion.current_frequency,
            domus_body_commitment=witness.domus_body_commitment,
            q_states=q_body.q_states,
            q_vector_values=q_body.q_vector,
            q3_recursion_gain=manifestation.dcomp.q3_recursion_gain,
            final_shadow_parity=manifestation.ennead.final_parity,
            bound_tensor_witnessed=True,
            derives_through_courts_only=domus_motion.derives_through_courts_only,
            resonance_lock_witnessed=manifestation.ennead.strikes[-1].phase_locked,
            lineage_preserved=True,
            terminal_dcomp=manifestation.dcomp.terminal,
            one_turn_return_closed=manifestation.dcomp.closed,
        )
    except (AttributeError, IndexError, TypeError, ValueError, RuntimeError):
        return False
    return witness == expected
