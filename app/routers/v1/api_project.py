from fastapi import APIRouter, Depends
from ...models.base_models import EAPIResponseCode
from ...models.project_models import ProjectListResponse
from ...commons.logger_services.logger_factory_service import SrvLoggerFactory
from ...resources.error_handler import catch_internal
from ...auth import jwt_required
from fastapi_utils.cbv import cbv
from ...resources.helpers import query_node_has_relation_for_user, query__node_has_relation_with_admin


router = APIRouter()
_API_TAG = 'v1/projects'
_API_NAMESPACE = "api_project_list"


@cbv(router)
class APIProject:

    def __init__(self):
        self._logger = SrvLoggerFactory(_API_NAMESPACE).get_logger()

    @router.get("/projects", tags=[_API_TAG],
                response_model=ProjectListResponse,
                summary="Get project list that user have access to")
    @catch_internal(_API_NAMESPACE)
    async def list_project(self, current_identity: dict = Depends(jwt_required)):
        '''
        Get the project list that user have access to
        '''
        api_response = ProjectListResponse()
        try:
            username = current_identity['username']
            user_role = current_identity['role']
        except (AttributeError, TypeError):
            return current_identity
        projects_list = []
        if user_role == "admin":
            project_candidate = query__node_has_relation_with_admin()
        else:
            project_candidate = query_node_has_relation_for_user(username)
        for p in project_candidate:
            if p['labels'] == ['Dataset']:
                res_projects = {'name': p.get('name'),
                                'code': p.get('code')}
                projects_list.append(res_projects)
        api_response.result = projects_list
        api_response.code = EAPIResponseCode.success
        return api_response.json_response()
