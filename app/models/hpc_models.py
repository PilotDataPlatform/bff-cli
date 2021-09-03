from pydantic import Field, BaseModel
from .base_models import APIResponse


class HPCAuthResponse(APIResponse):
    """
    HPC Auth Response Class
    """
    result: dict = Field({}, example={
            "code": 200,
            "error_msg": "",
            "result": 
                {
                    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                }
        }
    )
