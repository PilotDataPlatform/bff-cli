from pydantic import Field, BaseModel
from .base_models import APIResponse


class ProjectListResponse(APIResponse):
    """
    Project list response class
    """
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


class POSTProjectFileResponse(APIResponse):
    result: dict = Field({}, example={
            "code": 200,
            "error_msg": "",
            "page": 0,
            "total": 1,
            "num_of_pages": 1,
            "result": {}
        }
    )


class POSTProjectFile(BaseModel):
    operator: str
    #resumable_datatype: str
    upload_message: str
    type: str
    zone: str
    filename: str


class GetProjectRoleResponse(APIResponse):
    result: dict = Field({}, example={
            "code": 200,
            "error_msg": "",
            "page": 0,
            "total": 1,
            "num_of_pages": 1,
            "result": "role"
        }
    )