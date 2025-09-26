from __future__ import annotations
from fastapi import APIRouter, Request, Response
from typing import Any, Optional
import json, os
from app.utils.pagination import paginate, build_link_header
from app.utils.filtering import apply_filters
# router = APIRouter(prefix="/subject-diagnosis", tags=["Experimental"])
router = APIRouter(prefix="/api/v1/subject-diagnosis", tags=["Experimental"])
DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "subjects.json")
def _load() -> list[dict]:
    with open(DATA_PATH, "r") as f: return json.load(f)
@router.get("")
def index(request: Request, response: Response, page: Optional[int] = 1, per_page: Optional[int] = 100) -> Any:
    items = apply_filters(_load(), dict(request.query_params))
    sliced, total = paginate(items, page or 1, per_page or 100)
    response.headers["link"] = build_link_header(str(request.url).split('?')[0], page or 1, per_page or 100, total, dict(request.query_params))
    return {"summary": {"counts": {"current": len(sliced), "all": total}}, "data": sliced}
