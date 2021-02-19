from pydantic import BaseModel, Field
from .base_models import APIResponse

### Validate Generate ID ###


class ValidateGenerateIDPOST(BaseModel):
    '''
    Validate Generate ID Post model
    '''
    generate_id: str


class ValidateGenerateIDResponse(APIResponse):
    '''
    Validate Generate ID response class
    '''
    result: dict = Field({}, example={
            "code": 200,
            "error_msg": "",
            "page": 0,
            "total": 1,
            "num_of_pages": 1,
            "result": "VALID"
        }
    )




