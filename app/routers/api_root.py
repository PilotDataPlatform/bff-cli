from fastapi import APIRouter
from ..config import ConfigClass

router = APIRouter()

## root api, for debuging
@router.get("/")
async def root():
    '''
    For testing if service's up
    '''
    return {"message": "BFF-CLI On, Version: " + ConfigClass.version}
