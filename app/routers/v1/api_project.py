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
from ...resources.helpers import get_user_role


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
        if time.time() - exp > 0:
            api_response.error_msg = "token expired"
            api_response.code = EAPIResponseCode.forbidden
            return api_response.json_response()
        user_role = get_user_role(username, api_response)
        projects_list = []
        if user_role == "admin":
            url = ConfigClass.NEO4J_SERVICE + "nodes/Dataset/query"
            data = {'is_all': 'true'}
            res = requests.post(
                url=url,
                json=data,
            )
            project = res.json()
        else:
            url = ConfigClass.NEO4J_SERVICE + "relations/query"
            data = {'start_params': {'name': username}}
            res = requests.post(
                url=url,
                json=data,
            )
            res = res.json()
            project = []
            for i in res:
                project.append(i['end_node'])
        for p in project:
            if p['labels'] == ['Dataset']:
                res_projects = {'name': p.get('name'),
                                'code': p.get('code')}
                projects_list.append(res_projects)
        api_response.result = projects_list
        api_response.code = EAPIResponseCode.success
        return api_response.json_response()

