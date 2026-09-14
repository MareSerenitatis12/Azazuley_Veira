"""Stable saved-trace envelope for Sydonic Magicae public surfaces."""
from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path

from .trace import DomusTrace

SAVED_TRACE_FORMAT = "sydonic-aeonic-line-trace-v1"

class SavedTraceError(RuntimeError):
    pass

@dataclass(frozen=True, slots=True)
class SavedTraceEnvelope:
    format: str
    trace_sha256: str
    trace: DomusTrace

    def to_json(self) -> str:
        payload = {
            "format": self.format,
            "trace_sha256": self.trace_sha256,
            "trace": self.trace.to_dict(),
        }
        return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))

    @classmethod
    def from_json(cls, payload: str) -> "SavedTraceEnvelope":
        raw = json.loads(payload)
        if raw.get("format") != SAVED_TRACE_FORMAT:
            raise SavedTraceError(f"unsupported saved trace format: {raw.get('format')!r}")
        trace_json = json.dumps(raw.get("trace"), ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        trace = DomusTrace.from_json(trace_json)
        expected = raw.get("trace_sha256")
        if trace.sha256 != expected:
            raise SavedTraceError("saved trace checksum mismatch")
        return cls(SAVED_TRACE_FORMAT, trace.sha256, trace)


def save_trace(trace: DomusTrace, path: str | Path) -> Path:
    target = Path(path)
    envelope = SavedTraceEnvelope(SAVED_TRACE_FORMAT, trace.sha256, trace)
    target.write_text(envelope.to_json() + "\n", encoding="utf-8")
    return target


def load_trace(path: str | Path) -> DomusTrace:
    return SavedTraceEnvelope.from_json(Path(path).read_text(encoding="utf-8")).trace
