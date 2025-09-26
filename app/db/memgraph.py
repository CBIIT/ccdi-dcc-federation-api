from __future__ import annotations

import os
from typing import Any, Dict, List

from fastapi import HTTPException
from neo4j import GraphDatabase, basic_auth
from neo4j.graph import Node, Relationship, Path


def _env(name: str, default: str | None = None) -> str | None:
    """Read config from Linux-style environment variables with sensible aliases."""
    v = os.getenv(name)
    if v is not None:
        return v

    # Aliases commonly seen in Memgraph/Neo4j setups (e.g., mgconsole envs)
    aliases: Dict[str, List[str]] = {
        "MEMGRAPH_URI": ["MG_URI", "NEO4J_URI"],
        "MEMGRAPH_HOST": ["MG_HOST"],
        "MEMGRAPH_PORT": ["MG_PORT"],
        "MEMGRAPH_USER": ["MG_USER", "MG_USERNAME", "NEO4J_USER"],
        "MEMGRAPH_PASSWORD": ["MG_PASSWORD", "MG_PASS", "NEO4J_PASSWORD"],
        "MEMGRAPH_ENCRYPTED": ["MG_ENCRYPTED"],
    }
    for alias in aliases.get(name, []):
        av = os.getenv(alias)
        if av is not None:
            return av
    return default


def _build_uri() -> str:
    # Prefer full URI if provided; otherwise compose from host/port.
    uri = _env("MEMGRAPH_URI")
    if uri:
        return uri
    host = _env("MEMGRAPH_HOST", "localhost")
    port = _env("MEMGRAPH_PORT", "7687")
    scheme = "bolt"
    return f"{scheme}://{host}:{port}"


_MEMGRAPH_URI = _build_uri()
_MEMGRAPH_USER = _env("MEMGRAPH_USER", "memgraph")
_MEMGRAPH_PASSWORD = _env("MEMGRAPH_PASSWORD", "memgraph")
_ENCRYPTED = (_env("MEMGRAPH_ENCRYPTED", "false") or "false").strip().lower() in {"1", "true", "yes", "on"}

_driver = GraphDatabase.driver(
    _MEMGRAPH_URI,
    auth=basic_auth(_MEMGRAPH_USER, _MEMGRAPH_PASSWORD),
    encrypted=_ENCRYPTED,
)


def _to_python(v: Any) -> Any:
    if isinstance(v, Node):
        return {k: _to_python(v[k]) for k in v.keys()}
    if isinstance(v, Relationship):
        return {k: _to_python(v[k]) for k in v.keys()}
    if isinstance(v, Path):
        return [_to_python(n) for n in v.nodes]
    if isinstance(v, list):
        return [_to_python(x) for x in v]
    if isinstance(v, dict):
        return {k: _to_python(val) for k, val in v.items()}
    return v


def run(cypher: str, params: Dict[str, Any] | None = None) -> List[Dict[str, Any]]:
    try:
        with _driver.session() as session:
            result = session.run(cypher, **(params or {}))
            rows: List[Dict[str, Any]] = []
            for rec in result:
                row: Dict[str, Any] = {k: _to_python(v) for k, v in rec.items()}
                rows.append(row)
            return rows
    except Exception as e:
        # Bubble up as 503; global handler formats per responses.Errors
        raise HTTPException(status_code=503, detail=f"Memgraph unavailable: {e}")
