from pydantic import Field
from pydantic import BaseModel
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
