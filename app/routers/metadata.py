from __future__ import annotations
from fastapi import APIRouter
from typing import Any
from app.models.entities import FieldDescriptions
# router = APIRouter(prefix="/metadata/fields", tags=["Metadata"])
router = APIRouter(prefix="/api/v1/metadata/fields", tags=["Metadata"])
@router.get("/subject", response_model=FieldDescriptions)
def subject_fields() -> Any: return {"fields": [{"harmonized": True, "path": "metadata.sex", "wiki_url": None}]}
@router.get("/sample", response_model=FieldDescriptions)
def sample_fields() -> Any: return {"fields": [{"harmonized": True, "path": "metadata.diagnosis", "wiki_url": None}]}
@router.get("/file", response_model=FieldDescriptions)
def file_fields() -> Any: return {"fields": [{"harmonized": True, "path": "metadata.type", "wiki_url": None}]}
