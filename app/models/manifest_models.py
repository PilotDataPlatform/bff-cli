from enum import Enum
from pydantic import BaseModel, Field
from .base_models import APIResponse

### Manifest ###


class ManifestListParams(BaseModel):
    '''
    Manifest list params model
    '''
    pass


class ManifestListResponse(APIResponse):
    '''
    Manifest list response class
    '''
    result: dict = Field({}, example={
    "code": 200,
    "error_msg": "",
    "page": 0,
    "total": 1,
    "num_of_pages": 1,
    "result": {
        "Manifest1": [
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
        ],
        "Manifest2": [
            {
                "name": "a1",
                "type": "multiple_choice",
                "optional": 'true',
                "value": "1,2,3"
            }
        ]
    }
}
    )
