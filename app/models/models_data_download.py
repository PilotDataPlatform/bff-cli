from enum import Enum
from pydantic import BaseModel, Field
from .base_models import APIResponse

### PreDataDowanload ###


class PreDataDowanloadPOST(BaseModel):
    '''
    Pre download payload model
    '''
    files: list
    project_code: str
    operator: str
    session_id: str


class PreDataDowanloadResponse(APIResponse):
    '''
    Pre download response class
    '''
    result: dict = Field({}, example={
        "code": 200,
        "error_msg": "",
        "page": 0,
        "total": 1,
        "num_of_pages": 1,
        "result": {
            "session_id": "unique_session_id",
            "job_id": "data-download-1613507376",
            "source": "./test_project/workdir/test_project_zipped_1613507376.zip",
            "action": "data_download",
            "status": "ZIPPING",
            "project_code": "test_project",
            "operator": "zhengyang",
            "progress": 0,
            "payload": {
                "hash_code": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJmdWxsX3BhdGgiOiIuL3Rlc3RfcHJvamVjdC93b3JrZGlyL3Rlc3RfcHJvamVjdF96aXBwZWRfMTYxMzUwNzM3Ni56aXAiLCJpc3N1ZXIiOiJTRVJWSUNFIERBVEEgRE9XTkxPQUQgIiwib3BlcmF0b3IiOiJ6aGVuZ3lhbmciLCJzZXNzaW9uX2lkIjoidW5pcXVlX3Nlc3Npb25faWQiLCJqb2JfaWQiOiJkYXRhLWRvd25sb2FkLTE2MTM1MDczNzYiLCJwcm9qZWN0X2NvZGUiOiJ0ZXN0X3Byb2plY3QiLCJpYXQiOjE2MTM1MDczNzYsImV4cCI6MTYxMzUwNzY3Nn0.ipzWy6y79QxRGhQQ_VWIk-Lz8Iv8zU7JHGF3ZBoNt-g"
            },
            "update_timestamp": "1613507376"
        }
    }
    )


class GetDataDownloadStatusRespon(APIResponse):
    '''
    Get data download status
    '''
    result: dict = Field({}, example={
        "code": 200,
        "error_msg": "",
        "page": 0,
        "total": 1,
        "num_of_pages": 1,
        "result": {
            "session_id": "unique_session_id",
            "job_id": "data-download-1613507376",
            "source": "./test_project/workdir/test_project_zipped_1613507376.zip",
            "action": "data_download",
            "status": "READY_FOR_DOWNLOADING",
            "project_code": "test_project",
            "operator": "zhengyang",
            "progress": 0,
            "payload": {
                "hash_code": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJmdWxsX3BhdGgiOiIuL3Rlc3RfcHJvamVjdC93b3JrZGlyL3Rlc3RfcHJvamVjdF96aXBwZWRfMTYxMzUwNzM3Ni56aXAiLCJpc3N1ZXIiOiJTRVJWSUNFIERBVEEgRE9XTkxPQUQgIiwib3BlcmF0b3IiOiJ6aGVuZ3lhbmciLCJzZXNzaW9uX2lkIjoidW5pcXVlX3Nlc3Npb25faWQiLCJqb2JfaWQiOiJkYXRhLWRvd25sb2FkLTE2MTM1MDczNzYiLCJwcm9qZWN0X2NvZGUiOiJ0ZXN0X3Byb2plY3QiLCJpYXQiOjE2MTM1MDczNzYsImV4cCI6MTYxMzUwNzY3Nn0.ipzWy6y79QxRGhQQ_VWIk-Lz8Iv8zU7JHGF3ZBoNt-g"
            },
            "update_timestamp": "1613507385"
        }
    })


class EDataDownloadStatus(Enum):
    INIT = 0
    CANCELLED = 1
    ZIPPING = 3
    READY_FOR_DOWNLOADING = 5
