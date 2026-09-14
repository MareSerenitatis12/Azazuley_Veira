"""Command-line surface for the Sydonic Magicae engine."""
from __future__ import annotations

import argparse
from dataclasses import asdict
import json
import sys

from .corpus_audit import CorpusAuditor
from .engine import EngineError, SydonicMagicaeEngine
from .implementation_reconciliation import AKSH_AUTHORITY_FILES, require_package_aksh_authority
from .saved_trace import save_trace
from .english_renderer import SydonicSpokenVoice
from .aksh_reader import read_lexicon, attributes


def _json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)


def _engine(args: argparse.Namespace) -> SydonicMagicaeEngine:
    return SydonicMagicaeEngine(house_voice=SydonicSpokenVoice())


def _entries_for_chain(engine: SydonicMagicaeEngine, chain: str):
    result = engine.translate_domus(
        domus_string=chain,
        target_language="en",
        output_style="telegraphic",
        include_trace=True,
    )
    entries = []
    for word in result.rendering.final_words:
        if word.kind != "content" or word.source_body_id is None:
            continue
        if word.grammatical_bearing == "phantasmagoria":
            source_authority, glyph, ostensive_field = word.source_body_id.rsplit(":", 2)
            if ostensive_field not in {"ostensiveI", "ostensiveII", "ostensiveIII"}:
                raise EngineError(f"invalid Phantasmagoria Ostensive provenance: {word.source_body_id!r}")
        else:
            source_authority, glyph = word.source_body_id.rsplit(":", 1)
        entries.append(engine.lexical_resolver.entry_from_authority(glyph, source_authority))
    return tuple(entries)

def _defined_body(entry) -> str:
    return "\n".join((
        f"Word: {entry.authored_lemma}",
        f"Origin Language: {entry.origin_language}",
        f"Pronunciation: {entry.pronunciation}",
        f"Cadence: {entry.cadence}",
        f"Non-Ostensive: {entry.non_ostensive}",
        f"Ostensive: {entry.ostensive}",
        f"LeySyff: {entry.leysyff}",
        f"GrimChain: {entry.grimchain}",
    ))

def _define_chain(engine: SydonicMagicaeEngine, chain: str) -> str:
    return "\n\n".join(_defined_body(entry) for entry in _entries_for_chain(engine, chain))

def _leysyff_chain(engine: SydonicMagicaeEngine, chain: str) -> str:
    return "\n".join(f"{entry.authored_lemma} ⋮{entry.leysyff}⋮" for entry in _entries_for_chain(engine, chain))

def _spoken_runs(engine: SydonicMagicaeEngine, chain: str) -> str:
    """Return the exact spoken runs from one translation.

    Run text comes from the renderer rather than the lexical lemma so a literal
    Phantasmagoria vessel reports its selected authored Ostensive body exactly.
    """
    result = engine.translate_domus(
        domus_string=chain,
        target_language="en",
        output_style="telegraphic",
        include_trace=True,
    )
    runs = []
    for word in result.rendering.final_words:
        if word.kind != "content" or word.source_body_id is None:
            continue
        if word.grammatical_bearing == "phantasmagoria":
            source_authority, glyph, ostensive_field = word.source_body_id.rsplit(":", 2)
            if ostensive_field not in {"ostensiveI", "ostensiveII", "ostensiveIII"}:
                raise EngineError(f"invalid Phantasmagoria Ostensive provenance: {word.source_body_id!r}")
        else:
            source_authority, glyph = word.source_body_id.rsplit(":", 1)
        entry = engine.lexical_resolver.entry_from_authority(glyph, source_authority)
        runs.append({
            "word": word.text,
            "origin_language": entry.origin_language,
            "font": entry.font,
            "source_authority": source_authority,
        })
    return _json(tuple(runs))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="sydonic")
    parser.add_argument("--version", action="version", version="23.0.7")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("validate-aksh")
    resolve = sub.add_parser("resolve-glyph")
    resolve.add_argument("glyph")
    parse = sub.add_parser("parse-domus")
    parse.add_argument("string")
    translate = sub.add_parser("translate")
    translate.add_argument("string")
    translate.add_argument("--to", default="en")
    translate.add_argument("--style", default="plain", choices=("telegraphic", "plain"))
    translate.add_argument("--trace", action="store_true")
    translate.add_argument("--json", action="store_true", help="emit the complete machine-readable result")
    translate.add_argument("--save-trace")
    define = sub.add_parser("define")
    define.add_argument("string")
    leysyff = sub.add_parser("leysyff")
    leysyff.add_argument("string")
    spoken_runs = sub.add_parser("spoken-runs")
    spoken_runs.add_argument("string")
    sub.add_parser("audit-corpus")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "validate-aksh":
            paths = require_package_aksh_authority()
            versions = {}
            for path in paths:
                if path.name in {"Living_Cadences.aksh", "Enochian…Understandings.aksh"}:
                    lines = path.read_text(encoding="utf-8").splitlines()
                    version = attributes(lines[0]).get("version", "") if lines else ""
                else:
                    version = read_lexicon(path).header.get("version", "")
                if not version:
                    raise EngineError(f"required .aksh version attribute missing: {path.name}")
                versions[path.name] = version
            print(_json({"valid": True, "authorities": versions, "count": len(AKSH_AUTHORITY_FILES)}))
            return 0
        engine = _engine(args)
        if args.command == "resolve-glyph":
            print(_json(asdict(engine.lexical_resolver.resolve(args.glyph))))
            return 0
        if args.command == "parse-domus":
            print(_json(asdict(engine.parse_domus(args.string))))
            return 0
        if args.command == "define":
            print(_define_chain(engine, args.string))
            return 0
        if args.command == "leysyff":
            print(_leysyff_chain(engine, args.string))
            return 0
        if args.command == "spoken-runs":
            print(_spoken_runs(engine, args.string))
            return 0
        if args.command == "translate":
            result = engine.translate_domus(
                domus_string=args.string,
                target_language=args.to,
                output_style=args.style,
                include_trace=args.trace or bool(args.save_trace),
            )
            if args.save_trace:
                if result.semantic_trace is None:
                    raise EngineError("trace requested for saving but engine returned none")
                save_trace(result.semantic_trace, args.save_trace)
            print(result.to_json() if args.json or args.trace else result.translation)
            return 0
        if args.command == "audit-corpus":
            print(CorpusAuditor(engine.lexical_resolver).run().to_json())
            return 0
    except Exception as exc:
        print(_json({"error": exc.__class__.__name__, "message": str(exc)}), file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
