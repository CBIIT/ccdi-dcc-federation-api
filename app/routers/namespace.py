from __future__ import annotations
from fastapi import APIRouter
from typing import Any, List
import json, os
from app.models.entities import Namespace
# router = APIRouter(prefix="/namespace", tags=["Namespace"])
router = APIRouter(prefix="/api/v1/namespace", tags=["Namespace"])
DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "namespaces.json")
def _load() -> list[dict]:
    with open(DATA_PATH, "r") as f: return json.load(f)
@router.get("", response_model=List[Namespace])
def index() -> Any: return _load()
@router.get("/{organization}/{namespace}", response_model=Namespace)
def show(organization: str, namespace: str) -> Any:
    for it in _load():
        ident = it.get("id", {})
        if ident.get("organization")==organization and ident.get("name")==namespace: return it
    return {"id": {"organization": organization, "name": namespace}, "metadata": {}}
