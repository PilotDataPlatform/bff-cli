from pydantic import Field
from pydantic import BaseModel
from .base_models import APIResponse


class ManifestListResponse(APIResponse):
    """
    Manifest list response class
    """
    result: dict = Field({}, example={
            "code": 200,
            "error_msg": "",
            "result": [
                {
                    "manifest_name": "Manifest1",
                    "id": 270,
                    "attributes": [
                        {
                            "name": "attr1",
                            "type": "multiple_choice",
                            "optional": 'false',
                            "value": "a1,a2"
                        },
                        {
                            "name": "attr2",
                            "type": "text",
                            "optional": 'true',
                            "value": 'null'
                        }
                    ]
                },
                {
                    "manifest_name": "Manifest2",
                    "id": 280,
                    "attributes": [
                        {
                            "name": "a1",
                            "type": "multiple_choice",
                            "optional": 'true',
                            "value": "1,2,3"
                        }
                    ]
                }
            ]
        }
    )


class ManifestAttachPost(BaseModel):
    """
    Attach Manifest post model
    """
    manifest_json: dict = Field({}, example={
        "manifest_json": {
            "manifest_name": "Manifest1",
            "project_code": "sampleproject",
            "attributes": {"attr1": "a1", "attr2": "asdf", "attr3": "t1"},
            "file_name": "file1"
        }
    }
    )


class ManifestAttachResponse(APIResponse):
    """
    Attach Manifest response class
    """
    result: dict = Field({}, example={
            "code": 200,
            "error_msg": "",
            "result": [
                {
                    "id": 690,
                    "labels": [
                        "File",
                        "Greenroom"
                    ],
                    "global_entity_id": "file_data-11f0d2b4-7163...",
                    "operator": "",
                    "file_size": 1048576,
                    "tags": [
                        "tag"
                    ],
                    "archived": 'false',
                    "path": "/data/core-storage/sampleproject/raw",
                    "time_lastmodified": "2021-02-19T19:06:06",
                    "uploader": "admin",
                    "process_pipeline": "",
                    "name": "testf1",
                    "time_created": "2021-02-17T20:59:48",
                    "guid": "6afa671d-f093-446c-a5a2-a495adcf29a5",
                    "full_path": "/data/core-storage/sampleproject/raw/testf1",
                    "dcm_id": "undefined",
                    "manifest_id": 270,
                    "attr_attr1": "a1",
                    "attr_attr2": "test cli upload"
                }
            ]
        }
    )


class ManifestExportParam(BaseModel):
    project_code: str
    manifest_name: str


class ManifestExportResponse(APIResponse):
    """
    Validate Manifest Response class
    """
    result: dict = Field({}, example={
                "code": 200,
                "error_msg": "",
                "result": {
                    "name": "Manifest1",
                    "project_code": "sampleproject",
                    "attributes": [
                        {
                            "name": "attr1",
                            "type": "multiple_choice",
                            "optional": "false",
                            "value": "a1,a2"
                        },
                        {
                            "name": "attr2",
                            "type": "text",
                            "optional": "true",
                            "value": "null"
                        }
                    ]
                }
            }
        )
