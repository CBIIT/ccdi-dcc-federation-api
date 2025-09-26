from __future__ import annotations
from fastapi import FastAPI
from app.routers.subject import router as subject_router
from app.routers.sample import router as sample_router
from app.routers.file import router as file_router
from app.routers.namespace import router as namespace_router
from app.routers.organization import router as organization_router
from app.routers.metadata import router as metadata_router
from app.routers.experimental_subject_diagnosis import router as experimental_subject_diagnosis_router
from app.routers.experimental_sample_diagnosis import router as experimental_sample_diagnosis_router
# imports (add this next to your other router imports)
from app.routers.root import router as root_route

app = FastAPI(title="CCDI Data Federation: Participating Nodes API — FastAPI Server")

app.include_router(subject_router)
app.include_router(sample_router)
app.include_router(file_router)
app.include_router(namespace_router)
app.include_router(organization_router)
app.include_router(metadata_router)
app.include_router(experimental_subject_diagnosis_router)
app.include_router(experimental_sample_diagnosis_router)
# after app = FastAPI(...), include the router (with your other include_router calls)
app.include_router(root_router)

# Serve the original swagger.yaml as the OpenAPI schema (so docs show all params/enums)
import yaml
from functools import lru_cache
@lru_cache()
def custom_openapi():
    with open('/mnt/data/ccdi_server_final/app/openapi/swagger.yaml', "r") as f:
        return yaml.safe_load(f)
app.openapi = custom_openapi
