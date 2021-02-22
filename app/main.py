from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import ConfigClass
from .api_registry import api_registry

app = FastAPI(
    title="BFF VRECLI",
    description="BFF For VRECLI",
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

# API registry
# v1
api_registry(app)


