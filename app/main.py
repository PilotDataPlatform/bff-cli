from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
# os.environ['env'] = 'test'
from .config import ConfigClass
from .api_registry import api_registry


def create_app():
    """
    create app function
    """
    app = FastAPI(
        title="BFF VRECLI",
        description="BFF for vrecli",
        docs_url="/v1/api-doc",
        version=ConfigClass.version
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins="*",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    api_registry(app)
    return app
