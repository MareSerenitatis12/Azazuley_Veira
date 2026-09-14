"""Pure ALQC Aeternum Mirror mathematics.

Mirror Math preserves Parliament operator position while exchanging the
Manifest/Reflect Golden bearing. This module performs no filesystem, suffix,
serialization, PDF, Manifest, cache, or recursive return work.

Vāhana means vehicle or carrier in Sanskrit. A completed emission, Mirror derivation,
or route witness may be carried as invocation-local Vāhana on its way to becoming
permanent history; it is temporary working state and is never persisted as cache.
"""
from __future__ import annotations

from .canon import court_load
from .source_emission import (
    ALPHA,
    BETA,
    GoldenGoeticDerivation,
    SourceEmission,
    resolve_bearing,
)


def derive_goetics(emission: SourceEmission) -> GoldenGoeticDerivation:
    if not emission.closure.verifies:
        raise RuntimeError("source emission does not carry D-COMP=0 / Truth=1")
    first = resolve_bearing(
        weights=emission.structural_weights,
        body="Goetic structural amplitude",
        phase=emission.fraktur_z0,
        bearing=ALPHA,
        cadence_symbol="𝔃₀",
        cadence_index=0,
        traversal="Manifest / forward bearing",
    )
    last = resolve_bearing(
        weights=emission.operational_weights,
        body="Parliament operational phase",
        phase=emission.fraktur_z1,
        bearing=BETA,
        cadence_symbol="𝔃₁",
        cadence_index=1,
        traversal="Reflect / conjugate bearing with append-only cadence",
    )
    if first.operator_order != last.operator_order:
        raise RuntimeError("Mirror Math illegally reversed the Parliament procession")
    court = court_load(first.seat.goetic, last.seat.goetic)
    reciprocal = court_load(last.seat.goetic, first.seat.goetic)
    return GoldenGoeticDerivation(emission, first, last, court, reciprocal)




def _render_self(
    emission: SourceEmission,
    depth: int,
    *,
    nonce: int,
    route_witness,
) -> str:
    """Return the compressed GrimChain posture from one completed Aeternum Mirror route."""
    from .route import resolve_parents
    from .domus import resolve_domus, public_living_domus

    _g_i, _g_j, witness = resolve_parents(emission, witness=route_witness)
    res = resolve_domus(witness, nonce=nonce)
    return public_living_domus(
        res,
        depth,
        source_digest=emission.source_digest,
        source_size=emission.source_size,
        source_domain=emission.source_domain,
        nonce=nonce,
    )


def verify_derivation(derivation: GoldenGoeticDerivation) -> bool:
    try:
        expected = derive_goetics(derivation.emission)
    except (TypeError, ValueError, RuntimeError):
        return False
    return (
        derivation == expected
        and derivation.same_operator_order
        and derivation.first.interval_verifies
        and derivation.last.interval_verifies
        and derivation.route_dcomp == 0
        and derivation.truth == 1
    )
