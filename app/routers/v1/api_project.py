from fastapi import APIRouter, Depends
from fastapi_utils.cbv import cbv
from ...models.project_models import ProjectListResponse, POSTProjectFile, POSTProjectFileResponse, GetProjectRoleResponse
from ...commons.logger_services.logger_factory_service import SrvLoggerFactory
from ...resources.error_handler import catch_internal
from ...resources.dependencies import *
from ...resources.helpers import *


router = APIRouter()
_API_TAG = 'V1 Projects'
_API_NAMESPACE = "api_project"


@cbv(router)
class APIProject:
    current_identity: dict = Depends(jwt_required)

    def __init__(self):
        self._logger = SrvLoggerFactory(_API_NAMESPACE).get_logger()

    @router.get("/projects", tags=[_API_TAG],
                response_model=ProjectListResponse,
                summary="Get project list that user have access to")
    @catch_internal(_API_NAMESPACE)
    async def list_project(self):
        '''
        Get the project list that user have access to
        '''
        api_response = ProjectListResponse()
        try:
            username = self.current_identity['username']
            user_role = self.current_identity['role']
        except (AttributeError, TypeError):
            return self.current_identity
        project_list = get_user_projects(user_role, username)
        api_response.result = project_list
        api_response.code = EAPIResponseCode.success
        return api_response.json_response()

    @router.post("/project/{project_code}/files",
                 response_model=POSTProjectFileResponse,
                 summary="pre upload file to the target zone", tags=["V1 Files"])
    @catch_internal(_API_NAMESPACE)
    async def project_file_preupload(self, project_code, request: Request, data: POSTProjectFile):
        """
        PRE upload and check existence of file in project
        """
        api_response = POSTProjectFileResponse()
        try:
            role = self.current_identity["role"]
            user_id = self.current_identity["user_id"]
        except (AttributeError, TypeError):
            return self.current_identity
        error = validate_upload_event(data.zone, data.type)
        if error:
            api_response.error_msg = error
            api_response.code = EAPIResponseCode.bad_request
            return api_response.json_response()
        if role == "admin":
            project_role = 'admin'
        else:
            project_role, code = get_project_role(user_id, project_code)
        void_check_file_in_zone(data, project_code)
        session_id = request.headers.get("Session-ID")
        result = transfer_to_pre(data, project_code, project_role, session_id)
        if result.status_code == 409:
            api_response.error_msg = result.json()['error_msg']
            api_response.code = EAPIResponseCode.conflict
            api_response.result = result.text
            return api_response.json_response()
        elif result.status_code != 200:
            api_response.error_msg = "Upload Error: " + result.json()["error_msg"]
            api_response.code = EAPIResponseCode.internal_error
            return api_response.json_response()
        else:
            api_response.result = result.json()["result"]
        return api_response.json_response()

    @router.get("/project/{project_code}/role", tags=[_API_TAG],
                response_model=GetProjectRoleResponse,
                summary="Get user's project role")
    @catch_internal(_API_NAMESPACE)
    async def get_user_project_role(self, project_code):
        """
        Get user's role in the project
        """
        api_response = GetProjectRoleResponse()
        try:
            user_id = self.current_identity['user_id']
        except (AttributeError, TypeError):
            return self.current_identity
        project = get_dataset_node(project_code)
        if not project:
            api_response.error_msg = customized_error_template(ECustomizedError.PROJECT_NOT_FOUND)
            api_response.code = EAPIResponseCode.not_found
            return api_response.json_response()
        project_id = project.get("id")
        role_check_result = get_user_role(user_id, project_id)
        if role_check_result:
            role = role_check_result.get("r").get('type')
            api_response.result = role
            api_response.code = EAPIResponseCode.success
            return api_response.json_response()
        else:
            api_response.error_msg = customized_error_template(ECustomizedError.USER_NOT_IN_PROJECT)
            api_response.code = EAPIResponseCode.not_found
            return api_response.json_response()
