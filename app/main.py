from __future__ import annotations

import importlib
import inspect
import pkgutil
from pathlib import Path
from typing import Any, Mapping
import json
import structlog, logging, time
from fastapi import Request

logging.basicConfig(level=logging.INFO)
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.dict_tracebacks,
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
    cache_logger_on_first_use=True,
)
log = structlog.get_logger()

from fastapi import FastAPI, APIRouter
from fastapi import HTTPException
from fastapi.responses import JSONResponse

logging.basicConfig(level=logging.INFO)

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

def _redact_query(q: Mapping[str, str]) -> dict:
    s = dict(q)
    for k in ("token", "auth", "password", "apikey", "api_key", "authorization"):
        if k in s:
            s[k] = "***"
    return s

def _redact_query(q: Mapping[str, str]) -> dict:
    s = dict(q)
    for k in ("token", "auth", "password", "apikey", "api_key", "authorization"):
        if k in s:
            s[k] = "***"
    return s

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    status = None

    # Build access-line string like Uvicorn's, but emit it in JSON
    client = getattr(request, "client", None)
    host = getattr(client, "host", None) if client else None
    port = getattr(client, "port", None) if client else None
    http_version = request.scope.get("http_version", "1.1")
    path_qs = request.url.path + (("?" + request.url.query) if request.url.query else "")
    access_line = f'{host}:{port} - "{request.method} {path_qs} HTTP/{http_version}"'

    try:
        response = await call_next(request)
        status = response.status_code
        return response
    except Exception:
        status = status or 500
        log.exception(
            "request_error",
            access=access_line,
            method=request.method,
            path=request.url.path,
            url=str(request.url),
            query=_redact_query(request.query_params),
            remote_addr=host,
            remote_port=port,
            http_version=http_version,
            status=status,
        )
        raise
    finally:
        duration_ms = int((time.perf_counter() - start) * 1000)
        log.info(
            "request",
            access=access_line,              # <= classic access string, now inside JSON
            method=request.method,
            path=request.url.path,
            url=str(request.url),
            query=_redact_query(request.query_params),
            remote_addr=host,
            remote_port=port,
            http_version=http_version,
            status=status,
            duration_ms=duration_ms,
        )

app.openapi = custom_openapi  # use spec-driven docs (or safe fallback)

@app.exception_handler(HTTPException)
async def json_http_exception_handler(request, exc: HTTPException):
    # Format per components/schemas/responses.Errors
    # (errors: [{message, code, status}])
    code = "not_found" if exc.status_code == 404 else "http_error"
    payload = {
        "errors": [{
            "message": exc.detail or "Error",
            "code": code,
            "status": exc.status_code
        }]
    }
    return JSONResponse(status_code=exc.status_code, content=payload, media_type="application/json")

"""
Automatically loads every APIRouter defined in any module under app/routers/ (so you don’t need root_router imports—no more NameError).

Serves your app/openapi/swagger.yaml directly as /openapi.json so Swagger UI shows all query parameters and enum values exactly as in your spec.

If the YAML can’t be read, it falls back to FastAPI’s generated schema so the docs don’t break.
"""

