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
    job_type: str
    upload_message: str
    type: str
    zone: str
    filename: str
    generate_id: str
    current_folder_node: str
    data: list


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


class GetProjectFolder(BaseModel):
    project_code: str
    zone: str
    folder: str
    relative_path: str


class GetProjectFolderResponse(APIResponse):
    result: dict = Field({}, example={
        "code": 200,
        "error_msg": "",
        "page": 0,
        "total": 1,
        "num_of_pages": 1,
        "result": {
            "id": 1552,
            "labels": [
                "Greenroom",
                "Folder"
            ],
            "global_entity_id": "bc8b4239-b22a-47dd-9d23-36ade331ebbf-1620685109",
            "folder_level": 1,
            "list_priority": 10,
            "folder_relative_path": "cli_folder_test23",
            "time_lastmodified": "2021-05-10T22:18:29",
            "uploader": "admin",
            "name": "folder_test",
            "time_created": "2021-05-10T22:18:29",
            "project_code": "may10",
            "tags": []
        }
    }
    )
