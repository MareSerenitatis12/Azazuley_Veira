"""Rendering and return audit over one complete Aeonic line."""
from __future__ import annotations
from dataclasses import asdict, dataclass
import hashlib, json
from .engine import TranslationResult

AUDIT_VERSION="aeonic-line-return-audit-v1"

class ReturnAuditError(RuntimeError): pass

@dataclass(frozen=True, slots=True)
class WordReturnRecord:
    output_index:int
    text:str
    kind:str
    source_position:int|None
    source_glyph:str|None
    source_body_id:str|None
    grammatical_bearing:str|None
    clothing_role:str|None
    traceable:bool
    adds_source_meaning:bool

@dataclass(frozen=True, slots=True)
class ReturnAudit:
    audit_version:str
    translation:str
    source_string:str
    trace_sha256:str
    content_words:tuple[WordReturnRecord,...]
    support_words:tuple[WordReturnRecord,...]
    absent_words:tuple[WordReturnRecord,...]
    exact_source:bool
    dependency_preserved:bool
    return_preserved:bool
    untraceable_content_words:tuple[str,...]
    status:str
    def to_json(self)->str:
        return json.dumps(asdict(self),ensure_ascii=False,sort_keys=True,separators=(",",":"))
    @property
    def sha256(self)->str:
        return hashlib.sha256(self.to_json().encode()).hexdigest()

def audit_translation(result:TranslationResult)->ReturnAudit:
    trace=result.semantic_trace
    if trace is None: raise ReturnAuditError("semantic trace required for return audit")
    content=[]; support=[]; absent=[]
    source_positions={t.source_position for t in trace.rendering_input.tokens if t.resolved_state_body is not None}
    for i,w in enumerate(result.rendering.final_words):
        if w.kind=="content":
            ok=w.source_position in source_positions and w.source_glyph is not None and w.source_body_id is not None
            content.append(WordReturnRecord(i,w.text,w.kind,w.source_position,w.source_glyph,w.source_body_id,w.grammatical_bearing,w.clothing_role,ok,True))
        elif w.kind=="clothing":
            ok=w.clothing_role is not None and w.source_position is None and w.source_glyph is None and w.source_body_id is None
            support.append(WordReturnRecord(i,w.text,w.kind,None,None,None,None,w.clothing_role,ok,False))
        elif w.kind=="absent-word":
            ok=w.text=="𑁦" and w.source_glyph=="𑁦"
            absent.append(WordReturnRecord(i,w.text,w.kind,w.source_position,w.source_glyph,None,None,None,ok,False))
    bad=tuple(r.text for r in content if not r.traceable)
    exact_source=trace.source_string==trace.rendering_input.source==trace.parsed_frame.source
    dependency=all(r.traceable for r in content) and all(r.traceable for r in support) and all(r.traceable for r in absent)
    status="PASS" if not bad and exact_source and dependency else "FAIL"
    audit=ReturnAudit(AUDIT_VERSION,result.translation,trace.source_string,trace.sha256,tuple(content),tuple(support),tuple(absent),exact_source,dependency,dependency and exact_source,bad,status)
    if status!="PASS": raise ReturnAuditError(audit.to_json())
    return audit
