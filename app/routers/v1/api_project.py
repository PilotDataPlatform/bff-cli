from fastapi import APIRouter, Depends, Request
from fastapi_utils.cbv import cbv
from ...models.base_models import EAPIResponseCode
from ...models.project_models import ProjectListResponse, POSTProjectFile, POSTProjectFileResponse, GetProjectRoleResponse
from ...commons.logger_services.logger_factory_service import SrvLoggerFactory
from ...resources.error_handler import catch_internal
from ...resources.dependencies import get_project_role, jwt_required
from ...resources.helpers import *
from app.config import ConfigClass  
import requests


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
        api_response = POSTProjectFileResponse()
        try:
            role = self.current_identity["role"]
            user_id = self.current_identity["user_id"]
        except (AttributeError, TypeError):
            return self.current_identity
        if not data.zone in ["vrecore", "greenroom"]:
            api_response.error_msg = "Invalid Zone"
            api_response.code = EAPIResponseCode.bad_request
            return api_response.json_response()

        if not data.type in ["raw", "processed"]:
            api_response.error_msg = "Invalid Type"
            api_response.code = EAPIResponseCode.bad_request
            return api_response.json_response()

        if role != "admin":
            # Check user belongs to dataset
            payload = {
                "start_label": "User",
                "end_label": "Dataset",
                "start_params": {
                    "id": int(self.current_identity["user_id"])
                },
                "end_params": {
                    "code": project_code,
                },
            }
            try:
                result = requests.post(ConfigClass.NEO4J_SERVICE + 'relations/query', json=payload)
            except Exception as e:
                api_response.error_msg = f"Neo4J error: {e}"
                api_response.code = EAPIResponseCode.forbidden
                return api_response.json_response()
            result = result.json()
            if len(result) < 1:
                api_response.error_msg = "User doesn't belong to project"
                api_response.code = EAPIResponseCode.forbidden
                return api_response.json_response()

        params = {
            "type": data.type,
            "zone": data.zone,
            "filename": data.filename,
            "job_type": data.job_type
        }
        try:
            result = requests.get(ConfigClass.FILEINFO_HOST + f'/v1/project/{project_code}/file/exist/', params=params)
            result = result.json()
        except Exception as e:
            api_response.error_msg = f"EntityInfo service  error: {e}"
            api_response.code = EAPIResponseCode.forbidden
            return api_response.json_response()
        if result['code'] in [404, 200]:
            pass
        else:
            api_response.error_msg = "File with that name already exists"
            api_response.code = EAPIResponseCode.conflict
            api_response.result = result
            return api_response.json_response()

        payload = {
            "project_code": project_code,
            "operator": data.operator,
            "upload_message": data.upload_message,
            "data": data.data,
            "job_type": data.job_type
        }
        headers = {
            "Session-ID": request.headers.get("Session-ID")
        }
        try:
            if data.zone == "vrecore":
                # Start permission check fail contributor
                if role != "admin":
                    project_role, code = get_project_role(user_id, project_code)
                    if code != EAPIResponseCode.success:
                        api_response.error_msg = project_role
                        api_response.code = code
                        return api_response.json_response()
                    elif project_role == "contributor":
                        api_response.error_msg = customized_error_template(ECustomizedError.PERMISSION_DENIED)
                        api_response.code = EAPIResponseCode.forbidden
                        api_response.result = project_role
                        return api_response.json_response()

                result = requests.post(ConfigClass.UPLOAD_VRE + "/v1/files/jobs", headers=headers, json=payload)
            else:
                result = requests.post(ConfigClass.UPLOAD_GREENROOM + "/v1/files/jobs", headers=headers, json=payload)
        except Exception as e:
            api_response.error_msg = f"Upload service  error: {e}"
            api_response.code = EAPIResponseCode.forbidden
            return api_response.json_response()
        if result.status_code == 409:
            api_response.error_msg = result.json()['error_msg']
            api_response.code = EAPIResponseCode.conflict
            api_response.result = result.text
            return api_response.json_response()
        elif result.status_code != 200:
            api_response.error_msg = "Upload Error: " + result.json()["error_msg"]
            api_response.code = EAPIResponseCode.internal_error
            return api_response.json_response()
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
