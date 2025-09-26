# app/utils/cypher_filters.py
from __future__ import annotations
from typing import Any, Dict, Mapping, Tuple, List

# Build a Cypher WHERE clause and parameter map from query params.
# - AND across different fields
# - Exact, case-sensitive equality
# - OR within list-typed values in the DB
# - Supports dynamic harmonized keys: metadata.<param>[.value]
# - Supports dynamic unharmonized keys: metadata.unharmonized.<path>
#
# Excludes pagination keys (page, per_page).
#
# Returns: (where_clause: str ("" or "WHERE ..."), params: dict)
def build_where_and_params_from_qp(qp: Mapping[str, Any]) -> Tuple[str, Dict[str, Any]]:
    filters: Dict[str, Any] = {}
    uh_filters: List[Tuple[str, Any]] = []  # (path, value)

    for k, v in qp.items():
        if k in ("page", "per_page"):
            continue
        if v is None or v == "":
            continue
        if k.startswith("metadata.unharmonized."):
            path = k.split(".", 2)[2] if "." in k else ""
            if path:
                uh_filters.append((path, v))
        else:
            # harmonized field: treat as metadata[k] or metadata[k].value
            filters[k] = v

    where_parts: List[str] = []
    params: Dict[str, Any] = {}

    if filters:
        # For each k in $filters:
        #   if n.metadata[k] is a dict with .value -> compare against that
        #   if it's a list -> membership
        #   otherwise -> equality
        params["filters"] = filters
        where_parts.append(
            """
            ALL(k IN keys($filters) WHERE
              CASE
                WHEN n.metadata[k] IS NULL THEN false
                WHEN (n.metadata[k]).value IS NOT NULL THEN
                  CASE
                    WHEN (n.metadata[k]).value IS LIST THEN $filters[k] IN (n.metadata[k]).value
                    ELSE (n.metadata[k]).value = $filters[k]
                  END
                ELSE
                  CASE
                    WHEN (n.metadata[k]) IS LIST THEN $filters[k] IN (n.metadata[k])
                    ELSE (n.metadata[k]) = $filters[k]
                  END
              END
            )
            """.strip()
        )

    for idx, (path, value) in enumerate(uh_filters):
        key_param = f"uh{idx}_parts"
        val_param = f"uh{idx}_value"
        params[key_param] = path.split(".")
        params[val_param] = value
        # reduce() walks nested maps: reduce(m = n.metadata.unharmonized, p IN $parts | m[p])
        where_parts.append(
            f"""
            CASE
              WHEN reduce(m = n.metadata.unharmonized, p IN ${key_param} | m[p]) IS NULL THEN false
              ELSE
                CASE
                  WHEN reduce(m = n.metadata.unharmonized, p IN ${key_param} | m[p]) IS LIST
                    THEN ${val_param} IN reduce(m = n.metadata.unharmonized, p IN ${key_param} | m[p])
                  ELSE reduce(m = n.metadata.unharmonized, p IN ${key_param} | m[p]) = ${val_param}
                END
            END
            """.strip()
        )

    if not where_parts:
        return "", {}
    return "WHERE " + " AND ".join(f"({p})" for p in where_parts), params


def page_params(qp: Mapping[str, Any]) -> Dict[str, int]:
    # Default per_page = 100 (as requested)
    try:
        per = int(qp.get("per_page", 100))
    except Exception:
        per = 100
    try:
        page = int(qp.get("page", 1))
    except Exception:
        page = 1
    if page < 1:
        page = 1
    if per < 1:
        per = 100
    return {"limit": per, "skip": (page - 1) * per, "page": page, "per_page": per}
