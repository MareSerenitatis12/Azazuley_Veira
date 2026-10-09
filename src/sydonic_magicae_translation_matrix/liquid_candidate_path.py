"""Phase 10 Liquid candidate paths.

Every complete Phase 9 candidate enters one 144-connection Court body governed
by the irreducible typed witness:

    <110_active | 144_total | 34_rest>

Active and resting are horizon offices, not lexical values.  Resting channels
remain valid and present.  The module does not rank, score, sort, or filter
candidate words, and the global candidate field preserves exact cardinality and
input order.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Final, Iterable

from .frequency_projection import CARRIERS
from .triadic_bridge import CandidatePathSeed, triad_A


class LiquidPathError(ValueError):
    """Raised when a candidate violates the Phase 10 Liquid body."""


@dataclass(frozen=True, slots=True, order=True)
class CourtConnection:
    """One of the 12 x 12 valid Court connections."""

    index: int
    governing_aeon: str
    alternating_aeon: str
    valid: bool = True

    def __post_init__(self) -> None:
        if not 0 <= self.index < 144:
            raise LiquidPathError("Court connection index must lie in [0,143]")
        if len(self.governing_aeon) != 1 or len(self.alternating_aeon) != 1:
            raise LiquidPathError("Court connection endpoints must be one Aeon glyph each")
        if not self.valid:
            raise LiquidPathError("all 144 Court connections remain valid")


COURT_CONNECTIONS: Final[tuple[CourtConnection, ...]] = tuple(
    CourtConnection(
        index=(governing_index * 12) + alternating_index,
        governing_aeon=governing.glyph,
        alternating_aeon=alternating.glyph,
    )
    for governing_index, governing in enumerate(CARRIERS)
    for alternating_index, alternating in enumerate(CARRIERS)
)
if len(COURT_CONNECTIONS) != 144 or len(set(COURT_CONNECTIONS)) != 144:
    raise RuntimeError("Phase 10 requires exactly 144 unique valid Court connections")

COURT_CONNECTION_SET: Final[frozenset[CourtConnection]] = frozenset(COURT_CONNECTIONS)
CONNECTION_BY_INDEX: Final[dict[int, CourtConnection]] = {
    connection.index: connection for connection in COURT_CONNECTIONS
}


@dataclass(frozen=True, slots=True)
class LiquidGovernor:
    """The typed connection governor, never reduced to a fraction."""

    active: int = 110
    total: int = 144
    rest: int = 34

    def __post_init__(self) -> None:
        if (self.active, self.total, self.rest) != (110, 144, 34):
            raise LiquidPathError("Liquid governor must remain <110_active|144_total|34_rest>")
        if self.active + self.rest != self.total:
            raise LiquidPathError("Liquid governor counts do not close")

    @property
    def typed_body(self) -> tuple[int, int, int]:
        return (self.active, self.total, self.rest)


LIQUID_GOVERNOR: Final[LiquidGovernor] = LiquidGovernor()


@dataclass(frozen=True, slots=True)
class ActiveGraph:
    """The candidate's active Court graph at one Aeon horizon."""

    court_root: str
    carrier_glyph: str
    vertices: tuple[CourtConnection, ...]
    edges: frozenset[tuple[int, int]]

    def __post_init__(self) -> None:
        if not self.court_root:
            raise LiquidPathError("active graph requires the candidate Court root")
        if len(self.carrier_glyph) != 1:
            raise LiquidPathError("active graph requires one Aeon carrier glyph")
        if len(set(self.vertices)) != len(self.vertices):
            raise LiquidPathError("active graph vertices must be unique")
        indices = {vertex.index for vertex in self.vertices}
        if any(not vertex.valid for vertex in self.vertices):
            raise LiquidPathError("active graph contains an invalid Court connection")
        for left, right in self.edges:
            if left == right or left not in indices or right not in indices:
                raise LiquidPathError("active graph edge leaves its active vertex body")
            if left > right:
                raise LiquidPathError("active graph edges must use canonical endpoint order")
        if len(self.vertices) >= 2 and not self.is_connected:
            raise LiquidPathError("candidate active graph is disconnected")

    @property
    def is_connected(self) -> bool:
        if not self.vertices:
            return False
        if len(self.vertices) == 1:
            return True
        adjacency = {vertex.index: set() for vertex in self.vertices}
        for left, right in self.edges:
            adjacency[left].add(right)
            adjacency[right].add(left)
        start = self.vertices[0].index
        seen = {start}
        frontier = [start]
        while frontier:
            current = frontier.pop()
            for neighbor in adjacency[current] - seen:
                seen.add(neighbor)
                frontier.append(neighbor)
        return len(seen) == len(self.vertices)


@dataclass(frozen=True, slots=True)
class LiquidHorizonWitness:
    """One exact active/resting partition and active graph at horizon h."""

    horizon: int
    governor: LiquidGovernor
    valid_connections: tuple[CourtConnection, ...]
    active_connections: frozenset[CourtConnection]
    resting_connections: frozenset[CourtConnection]
    active_graph: ActiveGraph
    completed: bool

    def __post_init__(self) -> None:
        if not isinstance(self.horizon, int) or self.horizon < 0:
            raise LiquidPathError("horizon must be a nonnegative integer")
        if self.governor != LIQUID_GOVERNOR:
            raise LiquidPathError("horizon changed the typed Liquid governor")
        if self.valid_connections != COURT_CONNECTIONS:
            raise LiquidPathError("horizon must preserve all 144 valid Court connections in order")
        valid_set = frozenset(self.valid_connections)
        if valid_set != COURT_CONNECTION_SET:
            raise LiquidPathError("horizon lost or duplicated a valid Court connection")
        if self.active_connections & self.resting_connections:
            raise LiquidPathError("a Court connection cannot be active and resting at one horizon")
        if self.active_connections | self.resting_connections != valid_set:
            raise LiquidPathError("active and resting sets must partition all 144 valid connections")

        active_count = len(self.active_connections)
        rest_count = len(self.resting_connections)
        if active_count == 144 and rest_count == 0:
            raise LiquidPathError("144-active Whiteout is forbidden")
        if active_count > self.governor.active:
            raise LiquidPathError("active connection body exceeds the 110 governor")
        if rest_count < self.governor.rest:
            raise LiquidPathError("resting contour fell below 34")
        if active_count <= 0:
            raise LiquidPathError("an empty active horizon cannot carry a candidate path")
        if self.completed and (active_count, rest_count) != (
            self.governor.active,
            self.governor.rest,
        ):
            raise LiquidPathError("completed path requires exactly 110 active and 34 resting")

        if frozenset(self.active_graph.vertices) != self.active_connections:
            raise LiquidPathError("active graph vertices differ from the active horizon set")
        if len(self.active_graph.vertices) >= 2 and not self.active_graph.is_connected:
            raise LiquidPathError("active graph does not carry a connected path body")

    @property
    def liquid_witness(self) -> tuple[int, int, int]:
        return (
            len(self.active_connections),
            len(self.valid_connections),
            len(self.resting_connections),
        )


@dataclass(frozen=True, slots=True)
class LiquidCandidatePath:
    """One Phase 9 seed carried through all declared Liquid horizons."""

    seed: CandidatePathSeed
    governor: LiquidGovernor
    horizons: tuple[LiquidHorizonWitness, ...]

    def __post_init__(self) -> None:
        if not triad_A(self.seed):
            raise LiquidPathError("Phase 10 requires a complete Phase 9 candidate seed")
        if self.governor != LIQUID_GOVERNOR:
            raise LiquidPathError("candidate path changed the typed Liquid governor")
        if not self.horizons:
            raise LiquidPathError("candidate path requires at least one horizon")
        if tuple(h.horizon for h in self.horizons) != tuple(range(len(self.horizons))):
            raise LiquidPathError("candidate horizons must be complete and ordered from zero")
        if any(h.governor != self.governor for h in self.horizons):
            raise LiquidPathError("candidate path changed governors between horizons")
        if any(h.active_graph.court_root != self.seed.domain.court_root for h in self.horizons):
            raise LiquidPathError("candidate active graph changed the Court root")
        if any(h.active_graph.carrier_glyph != self.seed.domain.carrier.glyph for h in self.horizons):
            raise LiquidPathError("candidate active graph changed the Aeon carrier")
        if any(h.completed for h in self.horizons[:-1]):
            raise LiquidPathError("only the final declared horizon may close the candidate path")
        if not self.horizons[-1].completed:
            raise LiquidPathError("final candidate horizon lacks a completed Liquid witness")
        if self.horizons[-1].liquid_witness != self.governor.typed_body:
            raise LiquidPathError("final candidate horizon is not the exact Liquid body")

    @property
    def exact_liquid_witness(self) -> tuple[int, int, int]:
        return self.horizons[-1].liquid_witness


@dataclass(frozen=True, slots=True)
class CandidateGlobalField:
    """A cardinality-preserving one-to-one lift into Liquid candidate paths."""

    candidates: tuple[CandidatePathSeed, ...]
    liquid_paths: tuple[LiquidCandidatePath, ...]

    def __post_init__(self) -> None:
        if len(self.candidates) != len(self.liquid_paths):
            raise LiquidPathError("Liquid traversal changed the global candidate count")
        if tuple(path.seed for path in self.liquid_paths) != self.candidates:
            raise LiquidPathError("Liquid traversal reordered, replaced, or filtered candidates")
        if any(path.exact_liquid_witness != LIQUID_GOVERNOR.typed_body for path in self.liquid_paths):
            raise LiquidPathError("global field contains a candidate without exact Liquid witness")

    @property
    def candidate_count(self) -> int:
        return len(self.candidates)



def _active_set(rotation: int, active_count: int = 110) -> frozenset[CourtConnection]:
    """Exact modulo construction A_k = {c_j : (j+k) mod 144 < active_count}."""
    if not isinstance(rotation, int):
        raise LiquidPathError("Liquid rotation must be an integer")
    if not 1 <= active_count <= 144:
        raise LiquidPathError("active count must lie in [1,144]")
    return frozenset(
        connection
        for connection in COURT_CONNECTIONS
        if (connection.index + rotation) % 144 < active_count
    )



def _candidate_rotation(seed: CandidatePathSeed, horizon: int) -> int:
    carrier_index = next(
        index for index, carrier in enumerate(CARRIERS)
        if carrier == seed.domain.carrier
    )
    return (carrier_index * 12 + horizon) % 144



def construct_active_graph(
    seed: CandidatePathSeed,
    active_connections: Iterable[CourtConnection],
) -> ActiveGraph:
    """Build a deterministic connected cycle over the active Court body."""
    vertices = tuple(sorted(set(active_connections), key=lambda connection: connection.index))
    if not vertices:
        raise LiquidPathError("cannot construct an active graph from an empty set")
    edges: set[tuple[int, int]] = set()
    if len(vertices) >= 2:
        for left, right in zip(vertices, vertices[1:]):
            edges.add((left.index, right.index))
        first, last = vertices[0].index, vertices[-1].index
        edges.add((min(first, last), max(first, last)))
    return ActiveGraph(
        court_root=seed.domain.court_root,
        carrier_glyph=seed.domain.carrier.glyph,
        vertices=vertices,
        edges=frozenset(edges),
    )



def build_liquid_horizon(
    seed: CandidatePathSeed,
    horizon: int,
    *,
    active_count: int = 110,
    completed: bool = False,
) -> LiquidHorizonWitness:
    """Construct and validate one horizon without changing candidate identity."""
    if not triad_A(seed):
        raise LiquidPathError("Liquid horizon requires a complete Phase 9 candidate seed")
    rotation = _candidate_rotation(seed, horizon)
    active = _active_set(rotation, active_count)
    resting = COURT_CONNECTION_SET - active
    graph = construct_active_graph(seed, active)
    return LiquidHorizonWitness(
        horizon=horizon,
        governor=LIQUID_GOVERNOR,
        valid_connections=COURT_CONNECTIONS,
        active_connections=active,
        resting_connections=resting,
        active_graph=graph,
        completed=completed,
    )



def run_liquid_candidate_path(
    seed: CandidatePathSeed,
    horizon_count: int,
) -> LiquidCandidatePath:
    """Run one candidate through an exact Liquid body at every horizon."""
    if not isinstance(horizon_count, int) or horizon_count <= 0:
        raise LiquidPathError("horizon_count must be a positive integer")
    horizons = tuple(
        build_liquid_horizon(
            seed,
            horizon,
            active_count=LIQUID_GOVERNOR.active,
            completed=horizon == horizon_count - 1,
        )
        for horizon in range(horizon_count)
    )
    return LiquidCandidatePath(seed, LIQUID_GOVERNOR, horizons)



def prove_phase10_exit_gate(
    candidates: Iterable[CandidatePathSeed],
    horizon_count: int,
) -> CandidateGlobalField:
    """Lift every candidate one-to-one into a complete exact Liquid path."""
    candidate_body = tuple(candidates)
    paths = tuple(run_liquid_candidate_path(seed, horizon_count) for seed in candidate_body)
    return CandidateGlobalField(candidate_body, paths)
