import os
import time
from fastapi import APIRouter, BackgroundTasks, Request
from fastapi_utils import cbv
from fastapi.responses import FileResponse
from ...config import ConfigClass
import jwt
import time
import requests
import aiohttp


router = APIRouter()

_API_TAG = 'v1/project'
_API_NAMESPACE = "api_project"

@cbv.cbv(router)
class APIProject:
    '''
    API Data Download Class
    '''

    def __init__(self):
        pass

    @router.get("/project", summary="Get project list that user have access to")
    async def list_project(self, request: Request):
        '''
        Get the project list that user have access to
        '''
        access_token = request.headers.get('authorization').split(' ')[1]
        decoded = jwt.decode(access_token, verify=False)
        username = decoded.get('preferred_username')
        exp = decoded.get('exp')
        #if time.time() - exp > 0:
        #    return {'result': '', 'error_msg':'token expired', 'error_code': 401}
        url = ConfigClass.NEO4J_SERVICE + "relations/query"
        data = {'is_all': 'true'}

        res = requests.post(
            url=url,
            json=data,
        )
        return res
