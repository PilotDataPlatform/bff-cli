from fastapi import FastAPI
from .routers import api_root
from .routers.v1 import api_data_download

def api_registry(app: FastAPI):
    app.include_router(api_root.router)
    app.include_router(api_data_download.router, prefix="/v1")