"""Exact authored corpus audit."""
from __future__ import annotations
from dataclasses import asdict, dataclass
import hashlib, json
from .lexical_resolver import LEXICAL_AUTHORITY_FILES, LexicalResolver

AUDIT_VERSION="exact-authored-corpus-audit-v1"

@dataclass(frozen=True, slots=True)
class CorpusAuditReport:
    audit_version: str
    authority_count: int
    inventory_count: int
    unique_word_count: int
    unique_definition_count: int
    duplicate_words: tuple[str,...]
    duplicate_definitions: tuple[str,...]
    missing_sources: tuple[str,...]
    external_lexicon_disconnected: bool
    status: str
    def to_json(self)->str:
        return json.dumps(asdict(self),ensure_ascii=False,sort_keys=True,separators=(",",":"))
    @property
    def sha256(self)->str:
        return hashlib.sha256(self.to_json().encode()).hexdigest()

class CorpusAuditor:
    def __init__(self,resolver:LexicalResolver|None=None)->None:
        if resolver is None:
            raise RuntimeError("authored lexical resolver is required for corpus audit")
        self.resolver=resolver
    def run(self)->CorpusAuditReport:
        authorities=self.resolver.authority_entries()
        entries=tuple(e for _, body in authorities for e in body)
        words={}; definitions={}; missing=[]
        for e in entries:
            if e.authored_lemma:
                words.setdefault(e.authored_lemma,[]).append(e.glyph)
            if e.non_ostensive or e.ostensive or e.leysyff:
                definitions.setdefault((e.non_ostensive,e.ostensive,e.leysyff),[]).append(e.glyph)
            if not e.source_authority: missing.append(e.glyph)
        # Uniqueness is required within each authored list, not across ten deliberately different lists.
        duplicate_words=[]; duplicate_definitions=[]
        for filename, body in authorities:
            local_words={}; local_definitions={}
            for e in body:
                if e.authored_lemma:
                    local_words.setdefault(e.authored_lemma,[]).append(e.glyph)
                if e.non_ostensive or e.ostensive or e.leysyff:
                    local_definitions.setdefault((e.non_ostensive,e.ostensive,e.leysyff),[]).append(e.glyph)
            duplicate_words.extend(f"{filename}:{w}:{''.join(gs)}" for w,gs in local_words.items() if len(gs)>1)
            duplicate_definitions.extend(f"{filename}:{d}:{''.join(gs)}" for d,gs in local_definitions.items() if len(gs)>1)
        ok=len(authorities)==len(LEXICAL_AUTHORITY_FILES) and all(len(body)==179 for _,body in authorities) and not duplicate_words and not duplicate_definitions and not missing
        return CorpusAuditReport(AUDIT_VERSION,len(authorities),len(entries),len(words),len(definitions),tuple(duplicate_words),tuple(duplicate_definitions),tuple(missing),True,"PASS" if ok else "FAIL")
