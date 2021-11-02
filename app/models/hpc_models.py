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

class HPCJobSubmitPost(BaseModel):
    """
    Submit HPC Job post model
    """
    host: str
    username: str
    token: str
    job_info: dict


class HPCJobResponse(APIResponse):
    """
    HPC Job Response Class
    """
    result: dict = Field({}, example={
            "code": 200,
            "error_msg": "",
            "result": 
                {
                    "t": "e",
                }
        }
    )

class HPCJobInfoGet(BaseModel):
    """
    Get HPC Job info model
    """
    job_id: str
    host: str
    username: str
    token: str


class HPCJobInfoResponse(APIResponse):
    """
    HPC Job Response Class
    """
    result: dict = Field({}, example={
            "code": 200,
            "error_msg": "",
            "result": 
                {
                    "t": "e",
                }
        }
    )
