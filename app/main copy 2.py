from __future__ import annotations

import importlib
import inspect
import pkgutil
from pathlib import Path
from typing import Any

from fastapi import FastAPI, APIRouter

app = FastAPI(title="CCDI Data Federation: Participating Nodes API — FastAPI Server")

# --- Dynamically include every APIRouter under app.routers.* ---
def _include_routers(app: FastAPI) -> None:
    import app.routers as routers_pkg  # raises if routers package missing
    pkg_path = Path(routers_pkg.__file__).parent

    for modinfo in pkgutil.iter_modules([str(pkg_path)]):
        mod_name = f"{routers_pkg.__name__}.{modinfo.name}"
        module = importlib.import_module(mod_name)
        # include any APIRouter objects exported by the module
        for _, obj in inspect.getmembers(module):
            if isinstance(obj, APIRouter):
                app.include_router(obj)

_include_routers(app)

# --- Serve YOUR swagger.yaml verbatim at /openapi.json (with a safe fallback) ---
import yaml
from functools import lru_cache
from fastapi.openapi.utils import get_openapi

@lru_cache()
def custom_openapi() -> dict[str, Any]:
    spec_path = Path(__file__).parent / "openapi" / "swagger.yaml"
    try:
        with spec_path.open("r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception:
        # Fallback to generated OpenAPI so /docs never 500s
        return get_openapi(
            title=app.title,
            version="0.1.0",
            routes=app.routes,
        )
# Always send Access-Control-Allow-Origin: *
@app.middleware("http")
async def add_cors_header(request, call_next):
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response

app.openapi = custom_openapi  # use spec-driven docs (or safe fallback)
"""
Automatically loads every APIRouter defined in any module under app/routers/ (so you don’t need root_router imports—no more NameError).

Serves your app/openapi/swagger.yaml directly as /openapi.json so Swagger UI shows all query parameters and enum values exactly as in your spec.

If the YAML can’t be read, it falls back to FastAPI’s generated schema so the docs don’t break.
"""

