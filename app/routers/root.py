from __future__ import annotations

import json
from pathlib import Path

from fastapi import APIRouter, HTTPException

router = APIRouter(tags=["Root"])

# Expect the file at: app/data/API-root.json
DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "API-root.json"

@router.get("/", summary="API root JSON")
def api_root():
    try:
        with DATA_PATH.open("r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail=f"Missing file: {DATA_PATH}")
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Invalid JSON in API-root.json")
