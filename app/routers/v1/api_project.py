from fastapi import APIRouter, Depends, Request
from fastapi_utils.cbv import cbv
from ...models.base_models import EAPIResponseCode
from ...models.project_models import ProjectListResponse, POSTProjectFile, POSTProjectFileResponse
from ...commons.logger_services.logger_factory_service import SrvLoggerFactory
from ...resources.error_handler import catch_internal
from ...auth import jwt_required
from ...resources.helpers import get_user_projects
from app.config import ConfigClass  
import requests


router = APIRouter()
_API_TAG = 'V1 Projects'
_API_NAMESPACE = "api_project_list"


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
            return current_identity
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
        role = self.current_identity["role"]
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
        }
        try:
            result = requests.get(ConfigClass.FILEINFO_HOST + f'/v1/project/{project_code}/file/exist/', params=params)
        except Exception as e:
            api_response.error_msg = f"EntityInfo service  error: {e}"
            api_response.code = EAPIResponseCode.forbidden
            return api_response.json_response()
        if not result.status_code in [200, 404]:
            error_msg = result.json().get("error_msg")
            api_response.error_msg = f"File exist API error: {error_msg}"
            api_response.code = EAPIResponseCode.forbidden
            return api_response.json_response()
        if result.status_code == 404:
            pass
        else:
            api_response.error_msg = "File with that name already exists"
            api_response.code = EAPIResponseCode.conflict
            return api_response.json_response()

        payload = {
            "project_code": project_code,
            "operator": data.operator,
            "operator": data.upload_message,
            "resumable_filename": data.filename,
            #"resumable_dataType": data.type
        }
        headers = {
            "Session-ID": request.headers.get("Session-ID")
        }
        try:
            if data.zone == "vre":
                result = requests.post(ConfigClass.UPLOAD_VRE + "/v1/files/jobs", headers=headers, json=payload)
            else:
                result = requests.post(ConfigClass.UPLOAD_GREENROOM + "/v1/files/jobs", headers=headers, json=payload)
        except Exception as e:
            api_response.error_msg = f"Upload service  error: {e}"
            api_response.code = EAPIResponseCode.forbidden
            return api_response.json_response()
        if result.status_code != 200:
            api_response.error_msg = "Upload Error: " + result.json()["error_msg"]
            api_response.code = EAPIResponseCode.internal_error
            return api_response.json_response()
        api_response.result = result.json()["result"]
        return api_response.json_response()


