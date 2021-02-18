from enum import Enum
from pydantic import BaseModel, Field
from .base_models import APIResponse

### PreDataDowanload ###


class ProjectListParams(BaseModel):
    '''
    Pre download payload model
    '''
    pass


class ProjectListResponse(APIResponse):
    '''
    Pre download response class
    '''
    result: dict = Field({})
