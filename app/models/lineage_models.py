from enum import Enum
from pydantic import BaseModel, Field
from .base_models import APIResponse


class LineageCreatePost(BaseModel):
    project_code: str
    input_geid: str
    output_geid: str
    pipeline_name: str
    description: str


class LineageCreateResponse(APIResponse):
    """
    Validate Manifest Response class
    """
    result: dict = Field({}, example={
        "message": "Succeed"
    }
    )
