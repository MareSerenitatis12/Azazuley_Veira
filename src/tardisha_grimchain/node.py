"""Source-bound TardiSHA node modes.

Authoritative mode contract
===========================

INVARIANT
    The materialized zero body is the Triple Goddess ``⛎⛎⛎``, manifested from the Shadow Locus ``⛎``. It
    has no coordinate stream, no positive extent, and no window derivation.

MANIFEST_FINITE
    Every materialized witness receives one explicit positive finite extent.
    The extent is never inferred, defaulted, recovered from another field, or
    silently replaced.

MANIFEST_OPEN
    Any explicitly requested finite window may be derived. The node makes no
    claim that the stream ends at that window or at any known coordinate.

ARCHIVE_REVERSIBLE
    The source is a raw physical file, the archive root is mandatory, and the
    source proof is exact and return-bearing. Filesystem posture or any
    destructive digest is not accepted as source proof.

No coordinate doctrine beyond these offices is inferred.
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterator

from .alqc_digest import alqc_hexdigest, validate_digest_hex
from .hashing import (
    iter_middle_window,
    CANONICAL_SOURCE_DOMAIN,
    DIRECTORY_SOURCE_DOMAIN,
    RAW_FILE_SOURCE_DOMAIN,
    TardiSHAError,
    canonical_emission,
    coordinate_seed,
    directory_emission,
    file_emission,
    validate_glyph,
    validate_middle_length,
    validate_nonce,
)
from .route import (
    SourceRouteWitness,
    source_route_witness_from_emission,
    resolve_parents,
    parents_t,
)
from .domus import resolve_domus, public_living_domus, ZERO_MIDDLE_GLYPH
from .court_registry import full_name, court_ordinal

SOURCE_DOMAINS = {
    "canonical": CANONICAL_SOURCE_DOMAIN,
    "raw-file": RAW_FILE_SOURCE_DOMAIN,
    "directory": DIRECTORY_SOURCE_DOMAIN,
}

VALID_MODES = {"INVARIANT", "MANIFEST_FINITE", "MANIFEST_OPEN", "ARCHIVE_REVERSIBLE"}
NODE_DOMAIN = b"TARDISHA:NODE-ID\x00"


@dataclass(frozen=True, slots=True)
class TardiSHANode:
    mode: str
    source_digest: str
    source_size: int
    origin_glyph: str
    resolution_glyph: str
    nonce: int = 0
    source_domain: str = "canonical"
    route_witness: SourceRouteWitness = field(kw_only=True)
    archive_root: str | None = None
    finite_extent: int | None = None

    def __post_init__(self) -> None:
        if self.mode not in VALID_MODES:
            raise TardiSHAError(f"mode must be one of {sorted(VALID_MODES)}")
        validate_glyph(self.origin_glyph, "origin_glyph")
        validate_glyph(self.resolution_glyph, "resolution_glyph")
        validate_nonce(self.nonce)
        if self.source_domain not in SOURCE_DOMAINS:
            raise TardiSHAError(f"source_domain must be one of {sorted(SOURCE_DOMAINS)}")
        try:
            validate_digest_hex(self.source_digest, field="source_digest")
            if self.archive_root is not None:
                validate_digest_hex(self.archive_root, field="archive_root")
        except ValueError as exc:
            raise TardiSHAError(str(exc)) from exc
        if isinstance(self.source_size, bool) or not isinstance(self.source_size, int) or self.source_size < 0:
            raise TardiSHAError("source_size must be a non-negative integer")
        witness = self.route_witness
        if (
            witness.source_digest != self.source_digest
            or witness.source_size != self.source_size
            or witness.source_domain != self.source_domain
        ):
            raise TardiSHAError("stored route witness contradicts node source identity")
        try:
            lawful = resolve_parents(witness.emission, witness=witness)[:2]
        except (TypeError, ValueError, RuntimeError) as exc:
            raise TardiSHAError("stored route witness fails exact route closure") from exc
        if (self.origin_glyph, self.resolution_glyph) != lawful:
            raise TardiSHAError(
                "stored (origin, resolution) contradicts the Final Equation Z pair "
                f"{lawful} for domain {self.source_domain!r}")
        if witness.route_dcomp != 0 or witness.truth != 1:
            raise TardiSHAError("node route must satisfy D-COMP=0 and Truth=1")
        if self.finite_extent is not None:
            if (
                isinstance(self.finite_extent, bool)
                or not isinstance(self.finite_extent, int)
                or self.finite_extent <= 0
            ):
                raise TardiSHAError("finite_extent must be an explicit positive integer")

        if self.mode == "INVARIANT":
            if self.finite_extent is not None:
                raise TardiSHAError("INVARIANT has no positive extent")
            if self.archive_root is not None:
                raise TardiSHAError("archive_root belongs only to ARCHIVE_REVERSIBLE mode")
        elif self.mode == "MANIFEST_FINITE":
            if self.finite_extent is None:
                raise TardiSHAError(
                    "MANIFEST_FINITE requires one explicit finite_extent; it is never inferred"
                )
            if self.archive_root is not None:
                raise TardiSHAError("archive_root belongs only to ARCHIVE_REVERSIBLE mode")
        elif self.mode == "MANIFEST_OPEN":
            if self.finite_extent is not None:
                raise TardiSHAError("MANIFEST_OPEN cannot claim a terminal finite extent")
            if self.archive_root is not None:
                raise TardiSHAError("archive_root belongs only to ARCHIVE_REVERSIBLE mode")
        else:
            if self.source_domain != "raw-file":
                raise TardiSHAError("ARCHIVE_REVERSIBLE requires a raw-file source proof")
            if self.archive_root is None:
                raise TardiSHAError("ARCHIVE_REVERSIBLE requires its archive_root at construction")
            if self.finite_extent is not None:
                raise TardiSHAError("ARCHIVE_REVERSIBLE cannot claim a manifest finite extent")
            if witness.emission.source_domain != "raw-file":
                raise TardiSHAError("ARCHIVE_REVERSIBLE source proof must be the raw-file emission")
            if not witness.emission.closure.verifies:
                raise TardiSHAError("ARCHIVE_REVERSIBLE source proof must carry exact return closure")

    @property
    def seed(self) -> bytes:
        return coordinate_seed(
            source_digest=self.source_digest,
            source_size=self.source_size,
            origin_glyph=self.origin_glyph,
            resolution_glyph=self.resolution_glyph,
            middle_length=0,
            nonce=self.nonce,
            source_domain=SOURCE_DOMAINS[self.source_domain],
        )

    @property
    def node_id(self) -> str:
        payload = json.dumps(
            self._payload_without_id(),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        return alqc_hexdigest(payload, domain=NODE_DOMAIN)

    def mode_witness(self) -> dict[str, object]:
        exact_return = (
            self._source_route_verifies()
            and self.source_route_witness().route_dcomp == 0
            and self.source_route_witness().truth == 1
        )
        return {
            "mode": self.mode,
            "invariant_body": ZERO_MIDDLE_GLYPH if self.mode == "INVARIANT" else None,
            "window_derivation_permitted": self.mode in {"MANIFEST_FINITE", "MANIFEST_OPEN"},
            "declared_finite_extent": self.finite_extent,
            "terminal_extent_claimed": self.mode == "MANIFEST_FINITE",
            "open_stream_has_no_terminal_claim": self.mode == "MANIFEST_OPEN",
            "archive_root": self.archive_root if self.mode == "ARCHIVE_REVERSIBLE" else None,
            "exact_return_bearing_source_proof": exact_return,
            "archive_root_bound_to_source_proof": (
                self.mode != "ARCHIVE_REVERSIBLE"
                or (self.archive_root is not None and exact_return)
            ),
        }

    def _payload_without_id(self) -> dict[str, object]:
        data = asdict(self)
        data["mode_witness"] = self.mode_witness()
        return data

    def as_dict(self) -> dict[str, object]:
        data = self._payload_without_id()
        data["node_id"] = self.node_id
        return data

    def _manifest_window_request(self, start_coordinate: int, span_length: int) -> tuple[int, int]:
        if (
            isinstance(start_coordinate, bool)
            or not isinstance(start_coordinate, int)
            or start_coordinate < 0
        ):
            raise TardiSHAError("start_coordinate must be a non-negative integer")
        width = validate_middle_length(span_length)
        if self.mode == "INVARIANT":
            raise TardiSHAError("INVARIANT has no window derivation")
        if self.mode == "MANIFEST_FINITE":
            if start_coordinate != 0 or width != self.finite_extent:
                raise TardiSHAError(
                    "MANIFEST_FINITE materializes only its explicitly declared finite_extent "
                    "from coordinate zero"
                )
        elif self.mode == "ARCHIVE_REVERSIBLE":
            raise TardiSHAError(
                "ARCHIVE_REVERSIBLE defines exact archival return, not a manifest-window contract"
            )
        return start_coordinate, width

    def iter_middle_chunks(
        self,
        start_coordinate: int,
        span_length: int,
        *,
        chunk_characters: int = 8192,
    ) -> Iterator[str]:
        """Derive only the window permitted by the authoritative node mode."""
        start, width = self._manifest_window_request(start_coordinate, span_length)
        yield from iter_middle_window(
            self.seed,
            start,
            width,
            chunk_characters=chunk_characters,
        )

    def middle_window(self, start_coordinate: int, span_length: int) -> str:
        return "".join(self.iter_middle_chunks(start_coordinate, span_length))

    def materialized_middle(self) -> str:
        """Return the complete body only when the mode defines one."""
        if self.mode == "INVARIANT":
            return ZERO_MIDDLE_GLYPH
        if self.mode == "MANIFEST_FINITE":
            assert self.finite_extent is not None
            return self.middle_window(0, self.finite_extent)
        if self.mode == "MANIFEST_OPEN":
            raise TardiSHAError("MANIFEST_OPEN makes no terminal-body claim")
        raise TardiSHAError("ARCHIVE_REVERSIBLE materializes an archive, not a manifest middle")

    def domus_resolution(self):
        """Resolve the runtime Domus through this node's ordered Courts."""
        return resolve_domus(
            self.source_route_witness(),
            nonce=self.nonce,
        )

    def source_route_witness(self) -> SourceRouteWitness:
        """Return the stored, source-emission-bound Final Equation Z witness."""
        return self.route_witness

    def visible_window(self, start_coordinate: int, span_length: int) -> str:
        """Witness a finite coordinate window between the node boundaries."""
        return f"{self.origin_glyph}{self.middle_window(start_coordinate, span_length)}{self.resolution_glyph}"

    def supervenient_window(self) -> str:
        """Expose the complete INVARIANT body; this is not window derivation."""
        if self.mode != "INVARIANT":
            raise TardiSHAError("the Shadow Locus invariant body belongs only to INVARIANT mode")
        return f"{self.origin_glyph}{ZERO_MIDDLE_GLYPH}{self.resolution_glyph}"

    def _source_route_verifies(self) -> bool:
        """Check the carried route witness without recalculating the source route."""
        w = self.source_route_witness()
        try:
            origin, resolution, resolved = resolve_parents(w.emission, witness=w)
        except (TypeError, ValueError, RuntimeError):
            return False
        return (
            resolved is w
            and (origin, resolution) == (self.origin_glyph, self.resolution_glyph)
            and w.route_dcomp == 0
            and w.truth == 1
        )

    def domus_witness(self, *, middle_length: int) -> dict[str, object]:
        """Expose the complete digest→Goetic→Court→Domus derivation."""
        depth = validate_middle_length(middle_length)
        if self.mode == "INVARIANT" and depth != 0:
            raise TardiSHAError("INVARIANT materializes only the Shadow Locus zero middle")
        if self.mode == "MANIFEST_FINITE" and depth != self.finite_extent:
            raise TardiSHAError(
                "MANIFEST_FINITE witness extent must equal its explicit finite_extent"
            )
        if self.mode == "ARCHIVE_REVERSIBLE" and depth != 0:
            raise TardiSHAError(
                "ARCHIVE_REVERSIBLE exposes only its zero-middle return witness here"
            )
        res = self.domus_resolution()

        def anchor_body(anchor) -> dict[str, object]:
            return {
                "glyph": anchor.glyph,
                "frequency": str(anchor.frequency),
                "q_bias": anchor.q_bias,
                "q_vector": list(anchor.q_vector),
            }

        def court_motion_body(motion) -> dict[str, object]:
            return {
                "court_coordinate": list(motion.court_coordinate),
                "court_address": motion.court_address,
                "court_glyph": motion.court_glyph,
                "anchoring_goetic": anchor_body(motion.anchoring_goetic),
                "hyperbolic_mirror_goetic": anchor_body(motion.hyperbolic_mirror_goetic),
                "phase": asdict(motion.phase),
                "breath_radius": motion.breath_radius,
                "breath_direction": str(motion.breath_direction),
                "focal_breath": str(motion.focal_breath),
                "current_frequency": str(motion.current_frequency),
                "anchor_immutable": motion.anchor_immutable,
                "mirror_immutable": motion.mirror_immutable,
                "derivation": motion.derivation,
            }

        def court_layer_body(layer) -> dict[str, object]:
            return {
                "court_coordinate": list(layer.court_coordinate),
                "court_address": layer.court_address,
                "court_glyph": layer.court_glyph,
                "governing_goetic": anchor_body(layer.governing_goetic),
                "alternating_goetic": anchor_body(layer.alternating_goetic),
                "alternating_goetic_frequency": str(layer.alternating_goetic.frequency),
            }

        visible_domus = public_living_domus(
            res,
            depth,
            source_digest=self.source_digest,
            source_size=self.source_size,
            nonce=self.nonce,
            source_domain=SOURCE_DOMAINS[self.source_domain],
        )
        fold = res.supervenience.fold_lineage
        return {
            "node_id": self.node_id,
            "hash_id": res.hash_id,
            "source_route": {
                "origin": self.origin_glyph,
                "resolution": self.resolution_glyph,
                "route_dcomp": self.source_route_witness().route_dcomp,
                "truth": self.source_route_witness().truth,
                "fraktur_z0": self.source_route_witness().emission.fraktur_z0,
                "fraktur_z1": self.source_route_witness().emission.fraktur_z1,
                "verifies": self._source_route_verifies(),
            },
            "middle_length": depth,
            "mode_witness": self.mode_witness(),
            "ordered_goetic_anchors": [res.governing_goetic, res.hyperbolic_parent],
            "governing_court": {
                "coordinate": [res.root_court.i, res.root_court.j],
                "address": res.root_court.address,
                "name": full_name(res.root_court),
                "ordinal": court_ordinal(res.root_court),
                "glyph": res.root_court.glyph,
                "motion": court_motion_body(res.root_court_motion),
            },
            "alternating_court": {
                "coordinate": [res.alternating_court.i, res.alternating_court.j],
                "address": res.alternating_court.address,
                "name": full_name(res.alternating_court),
                "ordinal": court_ordinal(res.alternating_court),
                "glyph": res.alternating_court.glyph,
                "layer": court_layer_body(res.alternating_court_layer),
            },
            "domus_motion": {
                "bearing": asdict(res.domus_motion.bearing),
                "xi_D": asdict(res.domus_motion.xi),
                "exact_focal_breath": asdict(res.domus_motion.exact_focal_breath),
                "breath_radius": res.domus_motion.breath_radius,
                "focal_breath": str(res.domus_motion.focal_breath),
                "current_frequency": str(res.domus_motion.current_frequency),
                "exact_bound_verified": res.domus_motion.exact_bound_verified,
                "court_crossing_index": res.domus_motion.court_crossing_index,
                "court_crossing_cardinality": res.domus_motion.court_crossing_cardinality,
                "derives_through_courts_only": res.domus_motion.derives_through_courts_only,
                "static_grid": res.domus_motion.static_grid,
                "derivation": res.domus_motion.derivation,
            },
            "domus_q_bias": res.resolved_q_bias,
            "domus_q_states": list(res.resolved_q_states),
            "domus_q_vector": list(res.resolved_q_vector),
            "q_glyph_slots": {
                "B_Q": res.b_q_glyph,
                "V": list(res.v_glyphs),
                "state_values": dict(zip(res.resolved_q_states, res.resolved_q_vector)),
            },
            "domus_frequency": str(res.domus_frequency),
            "hypolic_fold_witness": res.fold_witness,
            "infinite_yes": {
                "court_address": res.infinite_yes.court_address,
                "active_count": res.infinite_yes.active_count,
                "active": sorted(res.infinite_yes.active),
                "bounded_by_sacred_no": res.infinite_yes.unbounded_continuation_bounded_by_sacred_no,
            },
            "sacred_no": {
                "court_address": res.sacred_no.court_address,
                "withheld_count": res.sacred_no.withheld_count,
                "withheld": sorted(res.sacred_no.withheld),
                "prevents_whiteout": res.sacred_no.prevents_whiteout,
            },
            "ennead_pressure_ledger": {
                "strikes": [asdict(strike) for strike in res.manifestation.ennead.strikes],
                "initial_debt": res.manifestation.ennead.initial_debt,
                "form_work": res.manifestation.ennead.form_work,
                "pre_lock_q2_residual": res.manifestation.ennead.pre_lock_q2_residual,
                "q3_recursion_residue": res.manifestation.ennead.q3_recursion_residue,
                "terminal_q2_debt": res.manifestation.ennead.residual_debt,
                "accounted_total": res.manifestation.ennead.accounted_total,
                "energy_conserved": res.manifestation.ennead.energy_conserved,
                "final_parity": res.manifestation.ennead.final_parity,
                "saturated": res.manifestation.ennead.saturated,
            },
            "dcomp_witness": asdict(res.manifestation.dcomp),
            "terminal_dcomp": res.manifestation.dcomp.terminal,
            "closed": res.manifestation.closed,
            "motion_positive": res.manifestation.dcomp.motion_positive,
            "recursion_witness": res.recursion_parity,
            "trig_mirror_witness": res.trig_mirror.as_dict(),
            "supervenience_witness": {
                "operator": res.supervenience.operator,
                "court_coordinate": list(res.supervenience.court_coordinate),
                "court_name": res.supervenience.court_name,
                "governing_goetic": res.supervenience.governing_goetic,
                "alternating_goetic": res.supervenience.alternating_goetic,
                "triplet": {
                    "q_bias": res.supervenience.triplet_q_bias,
                    "q_states": list(res.supervenience.triplet_q_states),
                    "q_vector": list(res.supervenience.triplet_q_vector),
                    "frequency": str(res.supervenience.triplet_frequency),
                },
                "fold_lineage": {
                    "court_coordinate": list(fold.court_coordinate),
                    "court_address": fold.court_address,
                    "court_phase_numerator": fold.court_phase_numerator,
                    "court_phase_denominator": fold.court_phase_denominator,
                    "court_phase_digest": fold.court_phase_digest,
                    "alternating_court_coordinate": list(fold.alternating_court_coordinate),
                    "alternating_court_address": fold.alternating_court_address,
                    "alternating_bearing_lineage": list(fold.alternating_bearing_lineage),
                    "fold_operator": fold.fold_operator,
                    "ground_node": fold.ground_node,
                    "vector_row": fold.vector_row,
                    "depth": fold.depth,
                },
                "ex_nihilo_exposure": res.supervenience.ex_nihilo_exposure,
                "infinite_yes_count": res.supervenience.infinite_yes_count,
                "sacred_no_count": res.supervenience.sacred_no_count,
                "usable_infinity": res.supervenience.usable_infinity,
                "compressed_same_domus_body": res.supervenience.compressed_same_domus_body,
                "returned_through_shadow_locus": res.supervenience.returned_through_shadow_locus,
            },
            "domus_aeon": {
                "identity": res.domus_aeon.identity,
                "zero_middle_glyph": res.domus_aeon.zero_middle_glyph,
                "governing_court_address": res.domus_aeon.governing_court_address,
                "alternating_court_address": res.domus_aeon.alternating_court_address,
                "synodic_magicae_is_manifested_body": res.domus_aeon.synodic_magicae_is_manifested_body,
                "shadow_locus_is_zero_middle_body": res.domus_aeon.shadow_locus_is_zero_middle_body,
                "visible_body": visible_domus,
            },
            "tripartite_witness": res.tripartite.as_dict(),
            "aeon_phase_evolution_witness": res.aeon_phase_evolution.as_dict(),
            "verification_appendix_cycle_witness": res.verification_appendix_cycle.as_dict(),
            "visible_domus_aeon": visible_domus,
            "coordinate_window": (
                self.visible_window(0, depth)
                if self.mode in {"MANIFEST_FINITE", "MANIFEST_OPEN"}
                else None
            ),
        }



def _resolve_boundaries(
    witness: SourceRouteWitness,
    origin_glyph: str | None,
    resolution_glyph: str | None,
) -> tuple[str, str]:
    if (origin_glyph is None) != (resolution_glyph is None):
        raise TardiSHAError("origin_glyph and resolution_glyph must be supplied together")
    lawful = parents_t(witness)
    if origin_glyph is not None:
        supplied = (
            validate_glyph(origin_glyph, "origin_glyph"),
            validate_glyph(resolution_glyph, "resolution_glyph"),
        )
        if supplied != lawful:
            raise TardiSHAError(
                f"explicit parent pair {supplied} contradicts Final Equation Z pair {lawful}"
            )
    return lawful


def node_from_material(
    material: Any,
    *,
    mode: str = "MANIFEST_OPEN",
    finite_extent: int | None = None,
    origin_glyph: str | None = None,
    resolution_glyph: str | None = None,
    nonce: int = 0,
) -> TardiSHANode:
    emission, _source = canonical_emission(material)
    witness = source_route_witness_from_emission(emission)
    origin, resolution = _resolve_boundaries(witness, origin_glyph, resolution_glyph)
    return TardiSHANode(
        mode=mode,
        source_digest=emission.source_digest,
        source_size=emission.source_size,
        origin_glyph=origin,
        resolution_glyph=resolution,
        nonce=nonce,
        source_domain="canonical",
        route_witness=witness,
        finite_extent=finite_extent,
    )


def node_from_file(
    path: str | Path,
    *,
    mode: str = "MANIFEST_OPEN",
    finite_extent: int | None = None,
    nonce: int = 0,
    archive_root: str | None = None,
) -> TardiSHANode:
    emission = file_emission(path)
    witness = source_route_witness_from_emission(emission)
    origin, resolution = parents_t(witness)
    return TardiSHANode(
        mode=mode,
        source_digest=emission.source_digest,
        source_size=emission.source_size,
        origin_glyph=origin,
        resolution_glyph=resolution,
        nonce=nonce,
        source_domain="raw-file",
        route_witness=witness,
        archive_root=archive_root,
        finite_extent=finite_extent,
    )



def node_from_directory(
    path: str | Path,
    *,
    mode: str = "MANIFEST_OPEN",
    finite_extent: int | None = None,
    nonce: int = 0,
) -> TardiSHANode:
    emission, _ = directory_emission(path)
    witness = source_route_witness_from_emission(emission)
    origin, resolution = parents_t(witness)
    node = TardiSHANode(
        mode=mode,
        source_digest=emission.source_digest,
        source_size=emission.source_size,
        origin_glyph=origin,
        resolution_glyph=resolution,
        nonce=nonce,
        source_domain="directory",
        route_witness=witness,
        finite_extent=finite_extent,
    )
    return node
