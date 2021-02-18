from fastapi import APIRouter, Depends, Request
from fastapi_utils.cbv import cbv
from ...models.models_data_download import EDataDownloadStatus, PreDataDowanloadPOST, PreDataDowanloadResponse, GetDataDownloadStatusRespon
from ...models.base_models import APIResponse, EAPIResponseCode
from ...models.project_models import ProjectListResponse
from ...commons.logger_services.logger_factory_service import SrvLoggerFactory
from ...resources.error_handler import catch_internal, ECustomizedError, customized_error_template
from ...config import ConfigClass
from ...auth import jwt_required
import jwt
import requests
from ...resources.helpers import get_user_role
import json

router = APIRouter()
_API_TAG = 'v1/project'
_API_NAMESPACE = "api_project_list"

@cbv(router)
class APIProject:
    '''
    API Data Download Class
    '''
    current_identity: dict = Depends(jwt_required)

    def __init__(self):
        self._logger = SrvLoggerFactory(_API_NAMESPACE).get_logger()

    @router.get("/project", tags=[_API_TAG],
                response_model=ProjectListResponse,
                summary="Get project list that user have access to")
    @catch_internal(_API_NAMESPACE)
    async def list_project(self):
        '''
        Get the project list that user have access to
        '''
        api_response = ProjectListResponse()
        jwt_status = self.current_identity
        try:
            username = jwt_status['username']
            user_role = jwt_status['role']
        except (AttributeError, TypeError):
            return jwt_status

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

