from fastapi import FastAPI
from .routers import api_root
from .routers.v1 import api_file, api_project, api_manifest, api_validation, \
                        api_lineage, api_forward_entity_info, api_dataset, \
                            api_hpc, api_kg


def api_registry(app: FastAPI):
    prefix = "/v1"
    app.include_router(api_root.router)
    app.include_router(api_project.router, prefix=prefix)
    app.include_router(api_manifest.router, prefix=prefix)
    app.include_router(api_validation.router, prefix=prefix)
    app.include_router(api_lineage.router, prefix=prefix)
    app.include_router(api_forward_entity_info.router, prefix=prefix)
    app.include_router(api_file.router, prefix=prefix)
    app.include_router(api_dataset.router, prefix=prefix)
    app.include_router(api_hpc.router, prefix=prefix)
    app.include_router(api_kg.router, prefix=prefix)
