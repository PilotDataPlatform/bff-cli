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


class POSTDownloadFile(BaseModel):
    files: list
    operator: str
    project_code: str
    session_id: str
    zone: str


class POSTDownloadFileResponse(APIResponse):
    result: dict = Field({}, example={
        "code": 200,
        "error_msg": "",
        "page": 0,
        "total": 1,
        "num_of_pages": 1,
        "result": {
            "session_id": "downloadtest",
            "job_id": "data-download-1621521355",
            "geid": "6c890078-1596-44a5-b695-1a9a1b1d974a-1621347776",
            "source": "/data/vre-storage/may511/raw/contributor_file_a",
            "action": "data_download",
            "status": "READY_FOR_DOWNLOADING",
            "project_code": "may511",
            "operator": "jzhang33",
            "progress": 0,
            "payload": {
                "hash_code": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJnZWlkIjoiNmM4OTAwNzgtMTU5Ni00NGE1LWI2OTUtMWE5YTFiMWQ5NzRhLTE2MjEzNDc3NzYiLCJmdWxsX3BhdGgiOiIvZGF0YS92cmUtc3RvcmFnZS9tYXk1MTEvcmF3L2NvbnRyaWJ1dG9yX2ZpbGVfYSIsImlzc3VlciI6IlNFUlZJQ0UgREFUQSBET1dOTE9BRCIsIm9wZXJhdG9yIjoianpoYW5nMzMiLCJzZXNzaW9uX2lkIjoiZG93bmxvYWR0ZXN0Iiwiam9iX2lkIjoiZGF0YS1kb3dubG9hZC0xNjIxNTIxMzU1IiwicHJvamVjdF9jb2RlIjoibWF5NTExIiwiaWF0IjoxNjIxNTIxMzU1LCJleHAiOjE2MjE1MjE2NTV9.t0pMGdvZ-KDgDBi2Q7rpOlwJerd7g6PLxnDPEx80QjA",
                "files": [
                    "/data/vre-storage/may511/raw/contributor_file_a"
                ],
                "zone": "greenroom",
                "frontend_zone": "Green Room"
            },
            "update_timestamp": "1621521356"
        }
    })

class QueryDataInfo(BaseModel):
    geid: list


class QueryDataInfoResponse(APIResponse):
    result: dict = Field({}, example={
        "code": 200,
        "error_msg": "",
        "page": 0,
        "total": 1,
        "num_of_pages": 1,
        "result": {
            "session_id": "downloadtest",
            "job_id": "data-download-1621521355",
            "geid": "6c890078-1596-44a5-b695-1a9a1b1d974a-1621347776",
            "source": "/data/vre-storage/may511/raw/contributor_file_a",
            "action": "data_download",
            "status": "READY_FOR_DOWNLOADING",
            "project_code": "may511",
            "operator": "jzhang33",
            "progress": 0,
            "payload": {
                "hash_code": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJnZWlkIjoiNmM4OTAwNzgtMTU5Ni00NGE1LWI2OTUtMWE5YTFiMWQ5NzRhLTE2MjEzNDc3NzYiLCJmdWxsX3BhdGgiOiIvZGF0YS92cmUtc3RvcmFnZS9tYXk1MTEvcmF3L2NvbnRyaWJ1dG9yX2ZpbGVfYSIsImlzc3VlciI6IlNFUlZJQ0UgREFUQSBET1dOTE9BRCIsIm9wZXJhdG9yIjoianpoYW5nMzMiLCJzZXNzaW9uX2lkIjoiZG93bmxvYWR0ZXN0Iiwiam9iX2lkIjoiZGF0YS1kb3dubG9hZC0xNjIxNTIxMzU1IiwicHJvamVjdF9jb2RlIjoibWF5NTExIiwiaWF0IjoxNjIxNTIxMzU1LCJleHAiOjE2MjE1MjE2NTV9.t0pMGdvZ-KDgDBi2Q7rpOlwJerd7g6PLxnDPEx80QjA",
                "files": [
                    "/data/vre-storage/may511/raw/contributor_file_a"
                ],
                "zone": "greenroom",
                "frontend_zone": "Green Room"
            },
            "update_timestamp": "1621521356"
        }
    })
