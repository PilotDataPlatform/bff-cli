from pydantic import Field, BaseModel
from .base_models import APIResponse


class GetProjectFileList(BaseModel):
    project_code: str
    zone: str
    folder: str
    source_type: str


class GetProjectFileListResponse(APIResponse):
    result: dict = Field({}, example={
        "code": 200,
        "error_msg": "",
        "page": 0,
        "total": 1,
        "num_of_pages": 1,
        "result": [
            {
                "id": 6127,
                "labels": [
                    "File",
                    "Greenroom"
                ],
                "global_entity_id": "baee1ca0-37a5-4c9b-afcb-1b2d4b2447aa-1621348460",
                "project_code": "may511",
                "operator": "jzhang33",
                "file_size": 1048576,
                "tags": [],
                "list_priority": 20,
                "archived": 'false',
                "path": "/data/vre-storage/may511/raw/folders1",
                "time_lastmodified": "2021-05-18T14:34:21",
                "process_pipeline": "",
                "uploader": "jzhang33",
                "parent_folder_geid": "c1c3766f-36bd-42db-8ca5-9040726cbc03-1620764271",
                "name": "Testdateiäöüßs2",
                "time_created": "2021-05-18T14:34:21",
                "guid": "4e06b8c5-8235-476e-b818-1ea5b0f0043c",
                "full_path": "/data/vre-storage/may511/raw/folders1/Testdateiäöüßs2",
                "generate_id": "undefined"
            },
            {
                "id": 2842,
                "labels": [
                    "Greenroom",
                    "Folder"
                ],
                "folder_level": 1,
                "global_entity_id": "7a71ed22-9cd0-465e-a18e-b66fda2c4e04-1620764271",
                "list_priority": 10,
                "folder_relative_path": "folders1",
                "time_lastmodified": "2021-05-11T20:17:51",
                "uploader": "jzhang33",
                "name": "fodlers",
                "time_created": "2021-05-11T20:17:51",
                "project_code": "may511",
                "tags": []
            }
        ]
    }
    )
