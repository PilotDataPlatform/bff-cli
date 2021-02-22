from enum import Enum
from pydantic import BaseModel, Field
from .base_models import APIResponse


class LineageCreatePost(BaseModel):
    project_code: str
    filename: str


class LineageCreateResponse(APIResponse):
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