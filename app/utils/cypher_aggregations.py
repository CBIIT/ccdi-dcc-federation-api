# app/utils/cypher_aggregations.py
from __future__ import annotations
from typing import Any, Dict, List

from app.db.memgraph import run as mg_run

def by_count(label: str, field: str, where: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compute by/{field}/count in the database via Cypher.

    Normalizes shapes:
      - metadata[field]        == scalar or list
      - metadata[field].value  == scalar or list
      - list entries may be scalars or {value: ...}
    """
    q_values = f"""
    MATCH (n:{label}) {where}
    WITH n.metadata[$field] AS node
    WITH CASE WHEN node IS NULL THEN [] WHEN node IS LIST THEN node ELSE [node] END AS entries
    UNWIND entries AS entry
    WITH CASE WHEN entry IS MAP AND entry.value IS NOT NULL THEN entry.value ELSE entry END AS val
    WITH CASE WHEN val IS LIST THEN val ELSE [val] END AS vals
    UNWIND vals AS v
    WITH CASE WHEN v IS MAP AND v.value IS NOT NULL THEN v.value ELSE v END AS value
    RETURN value, count(*) AS count
    ORDER BY value
    """

    q_missing = f"""
    MATCH (n:{label}) {where}
    RETURN sum(CASE WHEN n.metadata[$field] IS NULL THEN 1 ELSE 0 END) AS missing
    """

    p = dict(params); p["field"] = field
    rows = mg_run(q_values, p)
    miss = mg_run(q_missing, p)

    values = [{"value": r["value"], "count": r["count"]} for r in rows]
    total = sum(r["count"] for r in rows)
    missing = miss[0]["missing"] if miss else 0

    return {"total": total, "missing": missing, "values": values}
