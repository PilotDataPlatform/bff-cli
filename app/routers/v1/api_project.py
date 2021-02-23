from fastapi import APIRouter, Depends
from ...models.base_models import EAPIResponseCode
from ...models.project_models import ProjectListResponse
from ...commons.logger_services.logger_factory_service import SrvLoggerFactory
from ...resources.error_handler import catch_internal
from ...auth import jwt_required
from fastapi_utils.cbv import cbv
from ...resources.helpers import get_user_projects


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
        project_list = get_user_projects(user_role, username)
        api_response.result = project_list
        api_response.code = EAPIResponseCode.success
        return api_response.json_response()
