from enum import Enum
from pydantic import BaseModel, Field
from .base_models import APIResponse

### Manifest ###


class ManifestListParams(BaseModel):
    '''
    Manifest list params model
    '''
    pass


class ManifestListResponse(APIResponse):
    '''
    Manifest list response class
    '''
    result: dict = Field({}, example={
            "code": 200,
            "error_msg": "",
            "page": 0,
            "total": 1,
            "num_of_pages": 1,
            "result": [
                {
                    "name": "GENERATE TEST",
                    "code": "generate"
                },
                {
                    "name": "Indoc Test Project",
                    "code": "indoctestproject"
                }
            ]
        }
    )
