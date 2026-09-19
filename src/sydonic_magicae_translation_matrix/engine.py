"""Explicit end-to-end Sydonic Magicae translation engine."""
from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
from typing import Callable, Literal

from .zero_and_one import ZeroAndOneMachine
from .cadence import grimchain_azulation
from .lexer import ExactGlyphLexer
from .models import DomusFrame
from tardisha_grimchain.domus import parse_public_living_domus
from .english_renderer import EnglishRealizer, EnglishRendering, HouseVoiceRealizer
from .lexical_resolver import LexicalResolver
from .implementation_reconciliation import PACKAGE_AKSH_ROOT, require_package_aksh_authority
from .sequential_executor import SequentialDomusExecutor
from .trace import DomusTrace, DomusTraceBuilder

ENGINE_VERSION = "absolute-fidelity-phase2-v1"
TargetLanguage = Literal["en"]
OutputStyle = Literal["telegraphic", "plain"]
AKSH_ROOT = PACKAGE_AKSH_ROOT
DEFAULT_UNDERSTANDINGS = AKSH_ROOT / "Enochian…Understandings.aksh"


class EngineError(RuntimeError):
    """Raised when the explicit pipeline cannot lawfully complete."""


@dataclass(frozen=True, slots=True)
class VersionWitness:
    engine: str
    renderer: str
    trace: str
    semantic_lexicon: str
    lexical_authorities_aksh: tuple[tuple[str, str], ...]
    understandings_aksh: str
    source_sha256: str
    trace_sha256: str


@dataclass(frozen=True, slots=True)
class TranslationResult:
    translation: str
    semantic_trace: DomusTrace | None
    version_witness: VersionWitness
    rendering: EnglishRendering

    def to_json(self) -> str:
        payload = {
            "translation": self.translation,
            "semantic_trace": None if self.semantic_trace is None else self.semantic_trace.to_dict(),
            "version_witness": asdict(self.version_witness),
            "rendering": asdict(self.rendering),
        }
        return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


@dataclass(frozen=True, slots=True)
class GrimChainUnfoldWitness:
    requested_depth: int
    final_depth: int
    additional_depth: int
    final_chain: str
    first_speaking_body_position: int


class SydonicMagicaeEngine:
    """Join TardiSHA validation, exact glyph lexing, lexical projection, grammar, trace, and renderer."""

    version = ENGINE_VERSION

    def __init__(
        self,
        *,
        house_voice: HouseVoiceRealizer | None = None,
    ) -> None:
        require_package_aksh_authority()
        self.understandings = DEFAULT_UNDERSTANDINGS
        self.lexical_resolver = LexicalResolver(AKSH_ROOT)
        self.lexer = ExactGlyphLexer(self.lexical_resolver.glyph_order, self.understandings)
        self.zero_and_one = ZeroAndOneMachine(
            self.lexical_resolver.lexical_glyphs,
            self.lexical_resolver.resolve,
        )
        self.sequential = SequentialDomusExecutor(self.zero_and_one)
        self.trace_builder = DomusTraceBuilder(self.lexical_resolver, self.understandings)
        self.english = EnglishRealizer(house_voice=house_voice)

    def parse_domus(self, domus_string: str) -> DomusFrame:
        parse_public_living_domus(domus_string)
        domus_string = grimchain_azulation(domus_string)
        return DomusFrame(source=domus_string, tokens=self.lexer.lex(domus_string))

    def resolve_grimchain_unfold(
        self,
        requested_depth: int,
        chain_at_depth: Callable[[int], str],
    ) -> GrimChainUnfoldWitness:
        """Resolve the first same-identity depth containing a Real speaking body."""
        depth = requested_depth
        previous_chain: str | None = None
        while True:
            chain = chain_at_depth(depth)
            if depth > 1 and len(chain) != depth:
                raise EngineError("GrimChain continuation changed the requested manifest depth")
            if previous_chain is not None and not chain.startswith(previous_chain):
                raise EngineError("GrimChain continuation changed the witnessed prefix")
            frame = self.parse_domus(chain)
            if depth <= 1:
                speaking_position = next((token.position for token in frame.tokens if token.kind != "grammar"), 0)
                return GrimChainUnfoldWitness(requested_depth, depth, depth - requested_depth, chain, speaking_position)
            speaking_position = next((token.position for token in frame.tokens if token.kind != "grammar"), None)
            if speaking_position is not None:
                return GrimChainUnfoldWitness(requested_depth, depth, depth - requested_depth, chain, speaking_position)
            previous_chain = chain
            depth += 1

    def _complete_translation(
        self,
        *,
        domus_string: str,
        frame: DomusFrame,
        zero_and_one,
        local,
        output_style: str,
        include_trace: bool,
    ) -> TranslationResult:
        trace = self.trace_builder.build(frame, zero_and_one, local)
        rendering = self.english.render(trace, style=output_style)
        witness = VersionWitness(
            engine=self.version,
            renderer=rendering.renderer_version,
            trace=trace.trace_version,
            semantic_lexicon=trace.semantic_lexicon_version,
            lexical_authorities_aksh=trace.authority_versions.lexical_authorities,
            understandings_aksh=trace.authority_versions.understandings,
            source_sha256=hashlib.sha256(domus_string.encode("utf-8")).hexdigest(),
            trace_sha256=trace.sha256,
        )
        return TranslationResult(
            translation=rendering.final_text,
            semantic_trace=trace if include_trace else None,
            version_witness=witness,
            rendering=rendering,
        )

    def translate_domus_with_execution(
        self,
        *,
        domus_string: str,
        target_language: str = "en",
        output_style: str = "telegraphic",
        include_trace: bool = True,
        aeternum_token=None,
        aeternum_pair_reorder=None,
        aeternum_corridor_reorder=None,
        parsed_frame: DomusFrame | None = None,
    ) -> TranslationResult:
        """Public translation entry point with explicit Aeternum traversal adapters."""
        if target_language != "en":
            raise EngineError(f"unsupported target language: {target_language!r}")
        if output_style not in {"telegraphic", "plain"}:
            raise EngineError(f"unsupported output style: {output_style!r}")
        if not isinstance(domus_string, str):
            raise TypeError("domus_string must be str")
        try:
            if parsed_frame is None:
                frame = self.parse_domus(domus_string)
            else:
                if parsed_frame.source != domus_string:
                    raise EngineError("provided Domus frame does not match translation string")
                frame = parsed_frame
            zero_and_one, local = self.sequential.execute_frame(
                frame,
                aeternum_token=aeternum_token,
                aeternum_pair_reorder=aeternum_pair_reorder,
                aeternum_corridor_reorder=aeternum_corridor_reorder,
            )
            return self._complete_translation(
                domus_string=domus_string,
                frame=frame,
                zero_and_one=zero_and_one,
                local=local,
                output_style=output_style,
                include_trace=include_trace,
            )
        except Exception as exc:
            if isinstance(exc, (TypeError, EngineError)):
                raise
            raise EngineError(
                f"Sydonic Magicae pipeline stopped at explicit failure: {exc.__class__.__name__}: {exc}"
            ) from exc

    def translate_domus(
        self,
        *,
        domus_string: str,
        target_language: str = "en",
        output_style: str = "telegraphic",
        include_trace: bool = True,
    ) -> TranslationResult:
        return self.translate_domus_with_execution(
            domus_string=domus_string,
            target_language=target_language,
            output_style=output_style,
            include_trace=include_trace,
        )


def translate_domus(
    *,
    domus_string: str,
    target_language: str = "en",
    output_style: str = "telegraphic",
    include_trace: bool = True,
    house_voice: HouseVoiceRealizer | None = None,
) -> TranslationResult:
    """Public one-call engine entry point using the current package .aksh authorities."""
    return SydonicMagicaeEngine(
        house_voice=house_voice,
    ).translate_domus(
        domus_string=domus_string,
        target_language=target_language,
        output_style=output_style,
        include_trace=include_trace,
    )
