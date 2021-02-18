from fastapi import APIRouter, Depends, Request
from fastapi_utils.cbv import cbv
from ...models.models_data_download import EDataDownloadStatus, PreDataDowanloadPOST, PreDataDowanloadResponse, GetDataDownloadStatusRespon
from ...models.base_models import APIResponse, EAPIResponseCode
from ...models.project_models import ProjectListResponse
from ...commons.logger_services.logger_factory_service import SrvLoggerFactory
from ...config import ConfigClass
import os
import time
import requests
import jwt
import requests

router = APIRouter()

@cbv(router)
class FiledataMeta:
    def __init__(self):
        self._logger = SrvLoggerFactory('api_file_meta').get_logger()

@cbv(router)
class APIProject:
    '''
    API Data Download Class
    '''

    def __init__(self):
        self._logger = SrvLoggerFactory('api_file_meta').get_logger()

    @router.get("/project", response_model=ProjectListResponse,
                summary="Get project list that user have access to")
    async def list_project(self, request: Request):
        '''
        Get the project list that user have access to
        '''
        api_response = ProjectListResponse()
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
        api_response.result = res.json()
        api_response.code = EAPIResponseCode.success
        return api_response.json_response()

