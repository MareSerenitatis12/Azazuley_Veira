"""Transport-neutral MCP operation surface.

Every operation delegates to the same validator, resolver, auditor, and engine used
by the Python API and CLI. No grammar law is duplicated here.
"""
from __future__ import annotations

from dataclasses import asdict
import json
from typing import Any

from .corpus_audit import CorpusAuditor
from .english_renderer import SydonicSpokenVoice
from .engine import SydonicMagicaeEngine

class SydonicMCPTools:
    def __init__(self) -> None:
        self.engine = SydonicMagicaeEngine(house_voice=SydonicSpokenVoice())

    def parse_domus(self, domus_string: str) -> dict[str, Any]:
        return asdict(self.engine.parse_domus(domus_string))

    def resolve_sydonic_glyph(self, glyph: str) -> dict[str, Any]:
        return asdict(self.engine.lexical_resolver.resolve(glyph))

    def translate_domus(self, domus_string: str, target_language: str = "en", output_style: str = "telegraphic", include_trace: bool = True) -> dict[str, Any]:
        result = self.engine.translate_domus(
            domus_string=domus_string,
            target_language=target_language,
            output_style=output_style,
            include_trace=include_trace,
        )
        return json.loads(result.to_json())

    def trace_domus(self, domus_string: str) -> dict[str, Any]:
        result = self.engine.translate_domus(
            domus_string=domus_string,
            target_language="en",
            output_style="telegraphic",
            include_trace=True,
        )
        if result.semantic_trace is None:
            raise RuntimeError("engine returned no trace")
        return result.semantic_trace.to_dict()

    def validate_sydonic_corpus(self) -> dict[str, Any]:
        return json.loads(CorpusAuditor(self.engine.lexical_resolver).run().to_json())


def operation_schemas() -> dict[str, dict[str, Any]]:
    return {
        "parse_domus": {"required": ["domus_string"]},
        "resolve_sydonic_glyph": {"required": ["glyph"]},
        "translate_domus": {"required": ["domus_string"], "optional": ["target_language", "output_style", "include_trace"]},
        "trace_domus": {"required": ["domus_string"]},
        "validate_sydonic_corpus": {"required": []},
    }
