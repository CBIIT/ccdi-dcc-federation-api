from __future__ import annotations
from fastapi import APIRouter
from typing import Any, List
import json, os
from app.models.entities import Organization
#router = APIRouter(prefix="/organization", tags=["Organization"])
router = APIRouter(prefix="/api/v1/organization", tags=["Organization"])
DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "organizations.json")
def _load() -> list[dict]:
    with open(DATA_PATH, "r") as f: return json.load(f)
@router.get("", response_model=List[Organization])
def index() -> Any: return _load()
@router.get("/{name}", response_model=Organization)
def show(name: str) -> Any:
    for it in _load():
        if it.get("identifier")==name: return it
    return {"identifier": name, "metadata": {}}
