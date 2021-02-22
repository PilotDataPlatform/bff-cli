from pydantic import BaseModel, Field
from .base_models import APIResponse


class ManifestListResponse(APIResponse):
    """
    Manifest list response class
    """
    result: dict = Field({}, example={
            "code": 200,
            "error_msg": "",
            "page": 0,
            "total": 1,
            "num_of_pages": 1,
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
                "manifest_name": "Manifest1",
                "project_code": "0216",
                "attributes": {"attr1": "a1", "attr2": "test cli upload"},
                "file_path": "/data/vre-storage/0216/raw/testf1"
            }
    )


class ManifestAttachResponse(APIResponse):
    """
    Attach Manifest response class
    """
    result: dict = Field({}, example={
            "code": 200,
            "error_msg": "",
            "page": 0,
            "total": 1,
            "num_of_pages": 1,
            "result": [
                {
                    "id": 690,
                    "labels": [
                        "File",
                        "Raw",
                        "Greenroom"
                    ],
                    "global_entity_id": "file_data-11f0d2b4-7163-11eb-8428-be498ca98c54-1613595588",
                    "operator": "",
                    "file_size": 1048576,
                    "tags": [
                        "tag"
                    ],
                    "archived": 'false',
                    "path": "/data/vre-storage/0216/raw",
                    "time_lastmodified": "2021-02-19T19:06:06",
                    "uploader": "admin",
                    "process_pipeline": "",
                    "name": "testf1",
                    "time_created": "2021-02-17T20:59:48",
                    "guid": "6afa671d-f093-446c-a5a2-a495adcf29a5",
                    "full_path": "/data/vre-storage/0216/raw/testf1",
                    "generate_id": "undefined",
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
                "page": 0,
                "total": 1,
                "num_of_pages": 1,
                "result": {
                    "name": "Manifest1",
                    "project_code": "0216",
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




