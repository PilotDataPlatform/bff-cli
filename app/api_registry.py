from fastapi import FastAPI
from .routers import api_root
from .routers.v1 import api_data_download, api_project, api_manifest


def api_registry(app: FastAPI):
    app.include_router(api_root.router)
    app.include_router(api_data_download.router, prefix="/v1")
    app.include_router(api_project.router, prefix="/v1")
    app.include_router(api_manifest.router, prefix="/v1")
