from fastapi import FastAPI
from .routers.v1 import api_project, api_manifest, api_validation, api_lineage


def api_registry(app: FastAPI):
    prefix = "/v1"
    app.include_router(api_project.router, prefix=prefix)
    app.include_router(api_manifest.router, prefix=prefix)
    app.include_router(api_validation.router, prefix=prefix)
    app.include_router(api_lineage.router, prefix=prefix)

