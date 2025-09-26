# app/utils/aggregations.py
from __future__ import annotations
from typing import Any, Dict, List
import json

def _stable_key(v: Any) -> str:
    # Ensure we can hash arbitrary JSON-like values for counting
    if isinstance(v, (str, int, float, bool)) or v is None:
        return json.dumps(v)
    try:
        return json.dumps(v, sort_keys=True)
    except TypeError:
        return json.dumps(str(v))

def _emit(rv: Any, counts: Dict[str, int], raw_value: Dict[str, Any], total_ref: List[int]) -> None:
    k = _stable_key(rv)
    counts[k] = counts.get(k, 0) + 1
    raw_value.setdefault(k, rv)
    total_ref[0] += 1

def compute_by_count(items: List[dict], field: str) -> Dict[str, Any]:
    """
    Compute the 'by/{field}/count' payload for a collection of entities.

    Handles metadata shapes:
    - metadata[field] == {"value": ...}
    - metadata[field] == [{"value": ...}, ...]
    - metadata[field] == list of scalars
    - metadata[field] == scalar
    """
    total_ref = [0]  # use list to mutate inside helpers
    missing = 0
    counts: Dict[str, int] = {}
    raw_value: Dict[str, Any] = {}

    for it in items:
        md = it.get("metadata") or {}
        node = md.get(field, None)

        if node is None:
            missing += 1
            continue

        # Case 1: list at top-level (e.g., race: [{"value": "White"}])
        if isinstance(node, list):
            for entry in node:
                # entry may be {"value": ...} or scalar
                if isinstance(entry, dict) and "value" in entry:
                    val = entry.get("value")
                else:
                    val = entry
                if isinstance(val, list):
                    for sub in val:
                        _emit(sub if not isinstance(sub, dict) else sub.get("value", sub),
                              counts, raw_value, total_ref)
                else:
                    _emit(val if not isinstance(val, dict) else val.get("value", val),
                          counts, raw_value, total_ref)
            continue

        # Case 2: dict with "value"
        if isinstance(node, dict):
            val = node.get("value", None)
            if val is None:
                missing += 1
                continue
            if isinstance(val, list):
                for sub in val:
                    _emit(sub if not isinstance(sub, dict) else sub.get("value", sub),
                          counts, raw_value, total_ref)
            else:
                _emit(val if not isinstance(val, dict) else val.get("value", val),
                      counts, raw_value, total_ref)
            continue

        # Case 3: scalar directly
        _emit(node, counts, raw_value, total_ref)

    return {
        "total": total_ref[0],
        "missing": missing,
        "values": [{"value": raw_value[k], "count": counts[k]} for k in sorted(counts.keys())]
    }
