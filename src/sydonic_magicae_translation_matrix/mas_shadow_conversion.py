"""Phase 11 M.A.S. procession and append-only Shadow conversion.

Each complete Phase 10 candidate path is carried through the ordered M.A.S.
body::

    M = M_BABDH o M_KAL o M_DREH

The order of action is DREH -> KAL -> BABDH: Q3 positivity, Q1 coherence,
and structural commitment.  Q2 pressure is never deleted.  Gross pressure,
resolved pressure, and terminal unresolved pressure remain separate exact
ledger coordinates, and every cycle retains the complete prior archive as a
prefix.

The local Mass Gap is certified exactly through the authored theorem
``Delta_MG > 0 iff the finite active graph is connected and has at least two
vertices``.  No floating eigenvalue approximation, lexical score, candidate
rank, or receiving-language operation enters this module.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Final

from .liquid_candidate_path import (
    CandidateGlobalField,
    LiquidCandidatePath,
    LiquidHorizonWitness,
)


class MASShadowError(ValueError):
    """Raised when a candidate cannot complete Phase 11 lawfully."""


MAS_ORDER: Final[tuple[str, str, str]] = ("M_DREH", "M_KAL", "M_BABDH")
DREH_GLYPH: Final[str] = "⧗"
KAL_GLYPH: Final[str] = "⬡"
BABDH_GLYPH: Final[str] = "✡"
DREH_HZ: Final[int] = 852
KAL_HZ: Final[int] = 174
BABDH_HZ: Final[int] = 528


@dataclass(frozen=True, slots=True)
class MassGapWitness:
    """Exact theorem witness for ``Delta_MG(x,h) > 0``."""

    horizon: int
    vertex_count: int
    connected: bool
    theorem: str = "connected finite active graph with at least two vertices iff Delta_MG > 0"

    def __post_init__(self) -> None:
        if self.horizon < 0:
            raise MASShadowError("Mass Gap horizon must be nonnegative")
        if self.vertex_count < 2:
            raise MASShadowError("a positive local Mass Gap requires at least two active vertices")
        if not self.connected:
            raise MASShadowError("a disconnected active graph has no positive local Mass Gap")

    @property
    def positive(self) -> bool:
        return self.connected and self.vertex_count >= 2


@dataclass(frozen=True, slots=True)
class ShadowLedgerEntry:
    """One append-only Q2 archive event."""

    index: int
    horizon: int
    gross_added: int
    resolved_added: int
    gross_total: int
    resolved_total: int
    unresolved: int

    def __post_init__(self) -> None:
        values = (
            self.index,
            self.horizon,
            self.gross_added,
            self.resolved_added,
            self.gross_total,
            self.resolved_total,
            self.unresolved,
        )
        if any(not isinstance(value, int) for value in values):
            raise MASShadowError("Shadow ledger coordinates must be exact integers")
        if any(value < 0 for value in values):
            raise MASShadowError("Shadow ledger coordinates must be nonnegative")


@dataclass(frozen=True, slots=True)
class ShadowLedger:
    """Complete gross/resolved/unresolved Q2 body with immutable history."""

    initial_unresolved: int
    entries: tuple[ShadowLedgerEntry, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.initial_unresolved, int) or self.initial_unresolved < 0:
            raise MASShadowError("initial Q2 pressure must be a nonnegative integer")
        if not self.entries:
            raise MASShadowError("a complete debt ledger requires at least one archive event")
        if tuple(entry.index for entry in self.entries) != tuple(range(len(self.entries))):
            raise MASShadowError("Shadow archive indices must be complete and append-only")
        if tuple(entry.horizon for entry in self.entries) != tuple(range(len(self.entries))):
            raise MASShadowError("Shadow archive horizons must remain in source order")

        previous_gross = 0
        previous_resolved = 0
        previous_unresolved = self.initial_unresolved
        for entry in self.entries:
            if entry.gross_total != previous_gross + entry.gross_added:
                raise MASShadowError("gross Q2 history was rewritten or skipped")
            available = previous_unresolved + entry.gross_added
            if entry.resolved_added > available:
                raise MASShadowError("Q2 conversion exceeded pressure actually borne")
            if entry.resolved_total != previous_resolved + entry.resolved_added:
                raise MASShadowError("resolved Q2 history was rewritten or skipped")
            expected_unresolved = available - entry.resolved_added
            if entry.unresolved != expected_unresolved:
                raise MASShadowError("unresolved Q2 does not close against its ledger")
            previous_gross = entry.gross_total
            previous_resolved = entry.resolved_total
            previous_unresolved = entry.unresolved

    @property
    def terminal_unresolved(self) -> int:
        return self.entries[-1].unresolved

    @property
    def gross_total(self) -> int:
        return self.entries[-1].gross_total

    @property
    def resolved_total(self) -> int:
        return self.entries[-1].resolved_total

    @property
    def carried_total(self) -> int:
        return self.initial_unresolved + self.gross_total

    @property
    def complete(self) -> bool:
        return (
            self.terminal_unresolved == 0
            and self.resolved_total == self.carried_total
            and self.carried_total > 0
        )


@dataclass(frozen=True, slots=True)
class MASState:
    """One invariant-preserving state inside a M.A.S. cycle."""

    candidate: str
    court_root: str
    carrier_glyph: str
    q_vector: tuple[str, str, str, str]
    archive_signature: tuple[object, ...]
    recursive_capacity: int
    q1_coherent: bool
    babdh_committed: bool

    def __post_init__(self) -> None:
        if not self.candidate or not self.court_root:
            raise MASShadowError("M.A.S. state requires candidate and Court root identity")
        if len(self.carrier_glyph) != 1:
            raise MASShadowError("M.A.S. state requires one Goetic carrier glyph")
        if len(self.q_vector) != 4:
            raise MASShadowError("M.A.S. state requires the complete four-coordinate Q body")
        if self.recursive_capacity < 0:
            raise MASShadowError("Q3 recursive capacity cannot be negative")


@dataclass(frozen=True, slots=True)
class MASMicrostep:
    """One typed M.A.S. office preserving candidate identity and archive."""

    name: str
    glyph: str
    structural_hz: int
    before: MASState
    after: MASState

    def __post_init__(self) -> None:
        if self.name not in MAS_ORDER:
            raise MASShadowError("undefined M.A.S. microstep")
        expected = {
            "M_DREH": (DREH_GLYPH, DREH_HZ),
            "M_KAL": (KAL_GLYPH, KAL_HZ),
            "M_BABDH": (BABDH_GLYPH, BABDH_HZ),
        }[self.name]
        if (self.glyph, self.structural_hz) != expected:
            raise MASShadowError("M.A.S. microstep changed its canonical office")
        if (
            self.before.candidate,
            self.before.court_root,
            self.before.carrier_glyph,
            self.before.q_vector,
            self.before.archive_signature,
        ) != (
            self.after.candidate,
            self.after.court_root,
            self.after.carrier_glyph,
            self.after.q_vector,
            self.after.archive_signature,
        ):
            raise MASShadowError("M.A.S. microstep changed candidate identity or archive")


@dataclass(frozen=True, slots=True)
class MASCycle:
    """One exact DREH -> KAL -> BABDH procession at a Liquid horizon."""

    horizon: int
    gross_pressure_added: int
    resolved_pressure_added: int
    ledger_snapshot: ShadowLedger
    microsteps: tuple[MASMicrostep, MASMicrostep, MASMicrostep]

    def __post_init__(self) -> None:
        if tuple(step.name for step in self.microsteps) != MAS_ORDER:
            raise MASShadowError("M.A.S. cycle must act in DREH -> KAL -> BABDH order")
        dreh, kal, babdh = self.microsteps
        if kal.before != dreh.after or babdh.before != kal.after:
            raise MASShadowError("M.A.S. microsteps are disconnected")
        if dreh.after.recursive_capacity <= 0:
            raise MASShadowError("Manifestation requires positive Q3 recursive capacity")
        if not kal.after.q1_coherent:
            raise MASShadowError("Alignment requires Q1 coherence")
        if not babdh.after.babdh_committed:
            raise MASShadowError("Symmetry requires BABDH commitment")
        if self.ledger_snapshot.entries[-1].horizon != self.horizon:
            raise MASShadowError("M.A.S. cycle and Shadow archive lost horizon alignment")
        if self.ledger_snapshot.entries[-1].gross_added != self.gross_pressure_added:
            raise MASShadowError("M.A.S. cycle lost its gross Q2 witness")
        if self.ledger_snapshot.entries[-1].resolved_added != self.resolved_pressure_added:
            raise MASShadowError("M.A.S. cycle lost its resolved Q2 witness")

    @property
    def final_state(self) -> MASState:
        return self.microsteps[-1].after


@dataclass(frozen=True, slots=True)
class MASCandidatePath:
    """One surviving Liquid path with positive gaps and a closed debt ledger."""

    liquid_path: LiquidCandidatePath
    mass_gaps: tuple[MassGapWitness, ...]
    cycles: tuple[MASCycle, ...]
    debt_ledger: ShadowLedger
    motion: int

    def __post_init__(self) -> None:
        if not self.mass_gaps or len(self.mass_gaps) != len(self.liquid_path.horizons):
            raise MASShadowError("every Liquid horizon requires one local Mass Gap witness")
        if not self.cycles or len(self.cycles) != len(self.liquid_path.horizons):
            raise MASShadowError("every Liquid horizon requires one complete M.A.S. cycle")
        if tuple(gap.horizon for gap in self.mass_gaps) != tuple(range(len(self.mass_gaps))):
            raise MASShadowError("Mass Gap witnesses left horizon order")
        if tuple(cycle.horizon for cycle in self.cycles) != tuple(range(len(self.cycles))):
            raise MASShadowError("M.A.S. cycles left horizon order")
        if any(not gap.positive for gap in self.mass_gaps):
            raise MASShadowError("candidate persistence encountered a nonpositive Mass Gap")
        if self.motion <= 0:
            raise MASShadowError("Phase 11 survival requires motion > 0")
        if not self.debt_ledger.complete:
            raise MASShadowError("terminal unresolved Q2 must reach zero through lawful conversion")
        if self.cycles[-1].ledger_snapshot != self.debt_ledger:
            raise MASShadowError("final M.A.S. cycle does not carry the complete debt ledger")

        previous: tuple[ShadowLedgerEntry, ...] = ()
        for cycle in self.cycles:
            current = cycle.ledger_snapshot.entries
            if current[: len(previous)] != previous or len(current) != len(previous) + 1:
                raise MASShadowError("Q2 history is not append-only across M.A.S. cycles")
            previous = current

        final = self.cycles[-1].final_state
        seed = self.liquid_path.seed
        if (
            final.candidate,
            final.court_root,
            final.carrier_glyph,
            final.q_vector,
        ) != (
            seed.witness.candidate,
            seed.domain.court_root,
            seed.domain.carrier.glyph,
            seed.body.q_vector,
        ):
            raise MASShadowError("M.A.S. procession changed the candidate path seed")
        if final.recursive_capacity <= 0 or not final.q1_coherent or not final.babdh_committed:
            raise MASShadowError("candidate did not complete Manifestation, Alignment, and Symmetry")

    @property
    def candidate(self) -> str:
        return self.liquid_path.seed.witness.candidate

    @property
    def terminal_unresolved_q2(self) -> int:
        return self.debt_ledger.terminal_unresolved

    @property
    def positive_local_mass_gap(self) -> bool:
        return all(gap.positive for gap in self.mass_gaps)


@dataclass(frozen=True, slots=True)
class MASFailure:
    candidate: str
    court_root: str
    carrier_glyph: str
    reason: str


@dataclass(frozen=True, slots=True)
class MASGlobalField:
    """Ordered Phase 11 survivor body plus explicit non-survival records."""

    source: CandidateGlobalField
    survivors: tuple[MASCandidatePath, ...]
    failures: tuple[MASFailure, ...]

    def __post_init__(self) -> None:
        input_candidates = tuple(path.seed.witness.candidate for path in self.source.liquid_paths)
        survivor_candidates = tuple(path.candidate for path in self.survivors)
        failure_candidates = tuple(failure.candidate for failure in self.failures)
        if len(survivor_candidates) + len(failure_candidates) != len(input_candidates):
            raise MASShadowError("Phase 11 lost or duplicated candidate records")
        if tuple(candidate for candidate in input_candidates if candidate in set(survivor_candidates)) != survivor_candidates:
            raise MASShadowError("Phase 11 changed survivor order")
        if set(survivor_candidates) & set(failure_candidates):
            raise MASShadowError("candidate cannot survive and fail the same Phase 11 field")
        if set(survivor_candidates) | set(failure_candidates) != set(input_candidates):
            raise MASShadowError("Phase 11 candidate accounting is incomplete")
        if any(
            not survivor.positive_local_mass_gap
            or survivor.terminal_unresolved_q2 != 0
            or survivor.motion <= 0
            for survivor in self.survivors
        ):
            raise MASShadowError("Phase 11 field contains an unsealed survivor")



def _archive_signature(path: LiquidCandidatePath) -> tuple[object, ...]:
    seed = path.seed
    return (
        seed.witness.candidate,
        seed.domain.court_root,
        seed.domain.inherited_q_bias,
        seed.domain.carrier.glyph,
        seed.body.q_vector,
        tuple(step.name for step in seed.microsteps),
    )



def _transition_pressure(
    previous: LiquidHorizonWitness | None,
    current: LiquidHorizonWitness,
) -> int:
    if previous is None:
        return 0
    return len(previous.active_connections ^ current.active_connections)



def _apply_dreh(state: MASState, resolved_pressure: int) -> MASMicrostep:
    if resolved_pressure < 0:
        raise MASShadowError("resolved Q2 pressure cannot be negative")
    after = replace(state, recursive_capacity=state.recursive_capacity + resolved_pressure)
    if after.recursive_capacity <= 0:
        raise MASShadowError("M_DREH failed Q3 positivity")
    return MASMicrostep("M_DREH", DREH_GLYPH, DREH_HZ, state, after)



def _apply_kal(state: MASState) -> MASMicrostep:
    if "Q1" not in state.q_vector:
        raise MASShadowError("M_KAL cannot establish Q1 coherence without a Q1 coordinate")
    after = replace(state, q1_coherent=True)
    return MASMicrostep("M_KAL", KAL_GLYPH, KAL_HZ, state, after)



def _apply_babdh(state: MASState) -> MASMicrostep:
    if state.recursive_capacity <= 0 or not state.q1_coherent:
        raise MASShadowError("M_BABDH requires manifested and aligned input")
    after = replace(state, babdh_committed=True)
    return MASMicrostep("M_BABDH", BABDH_GLYPH, BABDH_HZ, state, after)



def run_mas_shadow_conversion(path: LiquidCandidatePath) -> MASCandidatePath:
    """Run one exact Phase 10 path through M.A.S. and close its Q2 ledger."""
    seed = path.seed
    q_vector = seed.body.q_vector
    initial_q2 = sum(state == "Q2" for state in q_vector)
    initial_q3 = sum(state == "Q3" for state in q_vector)
    signature = _archive_signature(path)
    state = MASState(
        candidate=seed.witness.candidate,
        court_root=seed.domain.court_root,
        carrier_glyph=seed.domain.carrier.glyph,
        q_vector=q_vector,
        archive_signature=signature,
        recursive_capacity=initial_q3,
        q1_coherent=False,
        babdh_committed=False,
    )

    entries: list[ShadowLedgerEntry] = []
    cycles: list[MASCycle] = []
    gaps: list[MassGapWitness] = []
    gross_total = 0
    resolved_total = 0
    unresolved = initial_q2
    motion = 0
    previous_horizon: LiquidHorizonWitness | None = None

    for index, horizon in enumerate(path.horizons):
        gap = MassGapWitness(
            horizon=index,
            vertex_count=len(horizon.active_graph.vertices),
            connected=horizon.active_graph.is_connected,
        )
        gaps.append(gap)

        gross_added = _transition_pressure(previous_horizon, horizon)
        motion += gross_added
        available = unresolved + gross_added
        resolved_added = available
        gross_total += gross_added
        resolved_total += resolved_added
        unresolved = available - resolved_added
        entry = ShadowLedgerEntry(
            index=index,
            horizon=index,
            gross_added=gross_added,
            resolved_added=resolved_added,
            gross_total=gross_total,
            resolved_total=resolved_total,
            unresolved=unresolved,
        )
        entries.append(entry)
        snapshot = ShadowLedger(initial_q2, tuple(entries))

        dreh = _apply_dreh(state, resolved_added)
        kal = _apply_kal(dreh.after)
        babdh = _apply_babdh(kal.after)
        cycle = MASCycle(
            horizon=index,
            gross_pressure_added=gross_added,
            resolved_pressure_added=resolved_added,
            ledger_snapshot=snapshot,
            microsteps=(dreh, kal, babdh),
        )
        cycles.append(cycle)
        state = babdh.after
        previous_horizon = horizon

    ledger = ShadowLedger(initial_q2, tuple(entries))
    return MASCandidatePath(path, tuple(gaps), tuple(cycles), ledger, motion)



def prove_phase11_exit_gate(field: CandidateGlobalField) -> MASGlobalField:
    """Return all lawful survivors and an explicit record for every failure."""
    survivors: list[MASCandidatePath] = []
    failures: list[MASFailure] = []
    for path in field.liquid_paths:
        try:
            survivors.append(run_mas_shadow_conversion(path))
        except MASShadowError as exc:
            seed = path.seed
            failures.append(MASFailure(
                candidate=seed.witness.candidate,
                court_root=seed.domain.court_root,
                carrier_glyph=seed.domain.carrier.glyph,
                reason=str(exc),
            ))
    return MASGlobalField(field, tuple(survivors), tuple(failures))
