from __future__ import annotations
from fastapi import APIRouter, Request, Response
from typing import Any, Optional
import json, os
from app.utils.pagination import paginate, build_link_header
from app.utils.filtering import apply_filters
from app.models.entities import SubjectPage, Subject, ByCountSubjectResults
from app.utils.aggregations import compute_by_count
from app.db.memgraph import run as mg_run
from app.utils.cypher_filters import build_where_and_params_from_qp, page_params
from fastapi import HTTPException
from app.utils.cypher_aggregations import by_count as mg_by_count
from app.utils.cypher_filters import build_where_and_params_from_qp

#router = APIRouter(prefix="/subject", tags=["Subject"])
router = APIRouter(prefix="/api/v1/subject", tags=["Subject"])

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "subjects.json")
def _load() -> list[dict]:
    with open(DATA_PATH, "r") as f: return json.load(f)
# add these imports alongside existing ones
def _loadDb() -> list[dict]:
    rows = mg_run("MATCH (n:Subject) RETURN n AS node")
    return [r["node"] for r in rows]

@router.get("", response_model=SubjectPage)
def index(request: Request, response: Response, page: Optional[int] = 1, per_page: Optional[int] = 100) -> Any:
    items = apply_filters(_load(), dict(request.query_params))
    sliced, total = paginate(items, page or 1, per_page or 100)
    response.headers["link"] = build_link_header(str(request.url).split('?')[0], page or 1, per_page or 100, total, dict(request.query_params))
    return {"summary": {"counts": {"current": len(sliced), "all": total}}, "data": sliced}

@router.get("/by/{field}/count", response_model=ByCountSubjectResults)
def by_count(field: str) -> Any:
    return compute_by_count(_load(), field)

# detail route: raise 404 instead of returning a dummy entity
@router.get("/{organization}/{namespace}/{name}", response_model=Subject)

# detail route: raise 404 instead of returning a dummy entity
@router.get("/{organization}/{namespace}/{name}", response_model=Subject)
def show(organization: str, namespace: str, name: str) -> Any:
    for it in _load():
        ident = it.get("id", {}); ns = ident.get("namespace", {})
        if ns.get("organization") == organization and ns.get("name") == namespace and ident.get("name") == name:
            return it
    raise HTTPException(status_code=404, detail="Subject not found")
''' From DB
@router.get("/by/{field}/count", response_model=ByCountSubjectResults)
@router.get("/by/{field}/count", response_model=ByCountSubjectResults)
def by_count(field: str, request: Request) -> Any:
    qp = dict(request.query_params)
    where, params = build_where_and_params_from_qp(qp)
    return mg_by_count("Subject", field, where, params)

@router.get("", response_model=SubjectPage)
def index(request: Request, response: Response, page: Optional[int] = None, per_page: Optional[int] = None) -> Any:
    qp = dict(request.query_params)
    # Build WHERE and params from qp
    where, where_params = build_where_and_params_from_qp(qp)
    # Pagination defaults to per_page=100 if not provided
    pp = page_params(qp)
    params = {**where_params, "skip": pp["skip"], "limit": pp["limit"]}

    # Count all matching
    cnt = mg_run(f"MATCH (n:Subject) {where} RETURN count(n) AS total", params)
    total = cnt[0]["total"] if cnt else 0

    # Page of entities
    rows = mg_run(f"MATCH (n:Subject) {where} RETURN n AS node SKIP $skip LIMIT $limit", params)
    items = [r["node"] for r in rows]

    # Link header
    response.headers["link"] = build_link_header(
        str(request.url).split("?")[0], pp["page"], pp["per_page"], total, dict(request.query_params)
    )
    return {"summary": {"counts": {"current": len(items), "all": total}}, "data": items}

@router.get("/{organization}/{namespace}/{name}", response_model=Subject)
def show(organization: str, namespace: str, name: str) -> Any:
    rows = mg_run(
        """
        MATCH (n:Subject)
        WHERE n.id.name = $name
          AND n.id.namespace.organization = $org
          AND n.id.namespace.name = $ns
        RETURN n AS node
        LIMIT 1
        """,
        {"name": name, "org": organization, "ns": namespace},
    )
    if rows:
        return rows[0]["node"]
    raise HTTPException(status_code=404, detail="Subject not found")
'''
@router.get("/summary")
def summary() -> Any:
    return {"counts": {"total": len(_load())}}
