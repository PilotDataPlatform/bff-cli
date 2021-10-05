from pydantic import BaseModel, Field
from .base_models import APIResponse


class ManifestValidatePost(BaseModel):
    """
    Validate Manifest post model
    """
    manifest_json: dict = Field({}, example={
                "manifest_name": "Manifest1",
                "project_code": "0216",
                "attributes": {"attr1": "a1", "attr2": "test cli upload"},
                "file_path": "/data/vre-storage/0216/raw/testf1"
            }
    )


class ManifestValidateResponse(APIResponse):
    """
    Validate Manifest Response class
    """
    result: dict = Field({}, example={
                    "code": 200,
                    "error_msg": "",
                    "page": 0,
                    "total": 1,
                    "num_of_pages": 1,
                    "result": "Valid"
                }
            )


class ValidateGenerateIDPOST(BaseModel):
    """Validate Generate ID Post model"""
    generate_id: str


class ValidateGenerateIDResponse(APIResponse):
    """
    Validate Generate ID response class
    """
    result: dict = Field({}, example={
            "code": 200,
            "error_msg": "",
            "page": 0,
            "total": 1,
            "num_of_pages": 1,
            "result": "VALID"
        }
    )

class EnvValidatePost(BaseModel):
    """
    Validate Environment post model
    """
    action: str
    environ: str
    zone: str


class EnvValidateResponse(APIResponse):
    """
    Validate Manifest Response class
    """
    result: dict = Field({}, example={
                    "code": 200,
                    "error_msg": "",
                    "page": 0,
                    "total": 1,
                    "num_of_pages": 1,
                    "result": "Valid"
                }
            )
