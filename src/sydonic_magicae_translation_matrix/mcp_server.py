"""Minimal dependency-free MCP stdio server for Sydonic Magicae."""
from __future__ import annotations

import json
import sys
from typing import Any

from .mcp_surface import SydonicMCPTools, operation_schemas

SERVER_NAME = "sydonic-magicae"
SERVER_VERSION = "phase15-mcp-v1"

def _tools() -> list[dict[str, Any]]:
    descriptions = {
        "parse_domus": "Validate and tokenize one exact completed Aeonic line.",
        "resolve_sydonic_glyph": "Resolve one ordinary glyph directly through SeeD Body.",
        "translate_domus": "Translate one completed Domus through the shared engine.",
        "trace_domus": "Return the deterministic semantic trace for one completed Domus.",
        "validate_sydonic_corpus": "Audit SeeD Body and every authored office projection on the shared 179-glyph body.",
    }
    schemas = operation_schemas()
    properties = {
        "domus_string": {"type": "string"},
        "glyph": {"type": "string", "minLength": 1, "maxLength": 1},
        "target_language": {"type": "string", "default": "en"},
        "output_style": {"type": "string", "enum": ["telegraphic", "plain"], "default": "telegraphic"},
        "include_trace": {"type": "boolean", "default": True},
    }
    out=[]
    for name,spec in schemas.items():
        keys=spec.get("required",[])+spec.get("optional",[])
        out.append({"name":name,"description":descriptions[name],"inputSchema":{"type":"object","properties":{k:properties[k] for k in keys},"required":spec.get("required",[]),"additionalProperties":False}})
    return out

def _response(req_id: Any, result: Any = None, error: dict[str, Any] | None = None) -> dict[str, Any]:
    body={"jsonrpc":"2.0","id":req_id}
    if error is not None: body["error"]=error
    else: body["result"]=result
    return body

def dispatch(tools: SydonicMCPTools, request: dict[str, Any]) -> dict[str, Any] | None:
    method=request.get("method")
    req_id=request.get("id")
    if method == "notifications/initialized": return None
    if method == "initialize":
        return _response(req_id,{"protocolVersion":request.get("params",{}).get("protocolVersion","2025-06-18"),"capabilities":{"tools":{}},"serverInfo":{"name":SERVER_NAME,"version":SERVER_VERSION}})
    if method == "tools/list": return _response(req_id,{"tools":_tools()})
    if method == "tools/call":
        params=request.get("params") or {}
        name=params.get("name")
        arguments=params.get("arguments") or {}
        if not hasattr(tools,name): return _response(req_id,error={"code":-32601,"message":f"unknown tool: {name}"})
        try:
            value=getattr(tools,name)(**arguments)
            return _response(req_id,{"content":[{"type":"text","text":json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(",",":"))}],"structuredContent":value,"isError":False})
        except Exception as exc:
            return _response(req_id,{"content":[{"type":"text","text":f"{exc.__class__.__name__}: {exc}"}],"isError":True})
    return _response(req_id,error={"code":-32601,"message":f"method not found: {method}"})

def main() -> int:
    tools=SydonicMCPTools()
    for line in sys.stdin:
        if not line.strip(): continue
        try:
            request=json.loads(line)
            response=dispatch(tools,request)
        except Exception as exc:
            response=_response(None,error={"code":-32700,"message":f"{exc.__class__.__name__}: {exc}"})
        if response is not None:
            sys.stdout.write(json.dumps(response,ensure_ascii=False,separators=(",",":"))+"\n")
            sys.stdout.flush()
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
