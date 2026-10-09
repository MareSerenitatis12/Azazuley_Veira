"""Sydonic Magicae engine package."""

from .engine import (
    ENGINE_VERSION, EngineError, SydonicMagicaeEngine, TranslationResult,
    VersionWitness, translate_domus,
)

__all__ = [
    "ENGINE_VERSION", "EngineError", "SydonicMagicaeEngine",
    "TranslationResult", "VersionWitness", "translate_domus",
    "SAVED_TRACE_FORMAT", "load_trace", "save_trace", "SydonicMCPTools",
    "ReleaseSeal", "ReleaseSealer", "SEAL_VERSION",
]

from .saved_trace import SAVED_TRACE_FORMAT, load_trace, save_trace
from .mcp_surface import SydonicMCPTools

from .release_seal import ReleaseSeal, ReleaseSealer, SEAL_VERSION
