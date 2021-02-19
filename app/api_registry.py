from fastapi import FastAPI
from .routers import api_root
from .routers.v1 import api_project, api_manifest, api_generate_id_validation


def api_registry(app: FastAPI):
    prefix = "/v1"
    app.include_router(api_root.router)
    app.include_router(api_project.router, prefix=prefix)
    app.include_router(api_manifest.router, prefix=prefix)
    app.include_router(api_generate_id_validation.router, prefix=prefix)
