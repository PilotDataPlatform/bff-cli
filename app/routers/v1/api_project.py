from fastapi import APIRouter, Depends
from fastapi_utils.cbv import cbv
from ...models.project_models import *
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
        self._logger.info("API list_project".center(80, '-'))
        self._logger.info(f"User request with identity: {self.current_identity}")
        project_list = get_user_projects(user_role, username)
        self._logger.info(f"Getting user projects: {project_list}")
        self._logger.info(f"Number of projects: {len(project_list)}")
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
        self._logger.info("API list_manifest".center(80, '-'))
        self._logger.info(f"User request with identity: {self.current_identity}")
        error = validate_upload_event(data.zone, data.type)
        if error:
            self._logger.error(f"Upload event error: {error}")
            api_response.error_msg = error
            api_response.code = EAPIResponseCode.bad_request
            return api_response.json_response()
        if role == "admin":
            self._logger.info(f"User platform role: {role}")
        else:
            self._logger.info(f"User platform role: {role}")
            project_role, code = get_project_role(user_id, project_code)
            self._logger.info(f"User project role: {project_role}, {code}")
            if data.zone == ConfigClass.CORE_ZONE_LABEL.lower() and project_role == "contributor":
                api_response.error_msg = customized_error_template(ECustomizedError.PERMISSION_DENIED)
                api_response.code = EAPIResponseCode.forbidden
                api_response.result = project_role
                return api_response.json_response()
            elif project_role == 'User not in the project':
                api_response.error_msg = customized_error_template(ECustomizedError.PERMISSION_DENIED)
                api_response.code = EAPIResponseCode.forbidden
                api_response.result = project_role
                return api_response.json_response()
        for file in data.data:
            void_check_file_in_zone(data, file, project_code)
        session_id = request.headers.get("Session-ID")
        result = transfer_to_pre(data, project_code, session_id)

        trans_payload = {
            "current_folder_node": data.current_folder_node,
            "project_code": project_code,
            "operator": data.operator,
            "upload_message": data.upload_message,
            "data": data.data,
            "job_type": data.job_type
        }

        url = select_url_by_zone(data.zone)
        self._logger.info(f"Transfer to pre url: {url}")
        self._logger.info(f"Transfer to pre payload: {trans_payload}")
        self._logger.info(f"Transfer to pre result: {result}")
        self._logger.info(f"Transfer to pre result: {result.status_code}")
        self._logger.info(f"Transfer to pre result: {result.__dict__}")
        if result.status_code == 409:
            api_response.error_msg = result.json()['error_msg']
            api_response.code = EAPIResponseCode.conflict
            return api_response.json_response()
        elif result.status_code != 200:
            api_response.error_msg = "Upload Error: " + result.json()["error_msg"]
            api_response.code = EAPIResponseCode.internal_error
            return api_response.json_response()
        else:
            api_response.result = result.json()["result"]
        return api_response.json_response()

    @router.get("/project/{project_code}/folder", tags=[_API_TAG],
                response_model=GetProjectFolderResponse,
                summary="Get folder in the project")
    @catch_internal(_API_NAMESPACE)
    async def get_project_folder(self, project_code, zone, folder):
        """
        Get folder in project
        """
        api_response = GetProjectFolderResponse()
        try:
            role = self.current_identity["role"]
            user_id = self.current_identity["user_id"]
            user_name = self.current_identity['username']
        except (AttributeError, TypeError):
            return self.current_identity
        self._logger.info("API list_manifest".center(80, '-'))
        self._logger.info(f"User request with identity: {self.current_identity}")
        zone_type = get_zone(zone)
        permission_event = {'user_id': user_id,
                            'username': user_name,
                            'role': role,
                            'project_code': project_code,
                            'zone': zone_type}
        permission = check_permission(permission_event)
        self._logger.info(f"Permission check event: {permission_event}")
        self._logger.info(f"Permission check result: {permission}")
        error_msg = permission.get('error_msg', '')
        if error_msg:
            api_response.error_msg = error_msg
            api_response.code = permission.get('code')
            api_response.result = permission.get('result')
            return api_response.json_response()
        uploader = permission.get('uploader')
        accessing_folder = folder.split('/')[0]
        if uploader and uploader != accessing_folder:
            api_response.error_msg = customized_error_template(ECustomizedError.PERMISSION_DENIED)
            api_response.code = EAPIResponseCode.forbidden
            return api_response.json_response()
        folder_check_event = {
            'namespace': zone_type,
            'display_path': folder,
            'project_code': project_code,
            'folder_name': folder.split('/')[-1],
            'folder_relative_path': '/'.join(folder.split('/')[0:-1])
        }
        response = http_query_node_zone(folder_check_event)
        self._logger.info(f"Folder check event: {folder_check_event}")
        self._logger.info(f"Folder check response: {response.text}")
        if response.status_code != 200:
            error_msg = "Upload Error: " + response.json()["error_msg"]
            response_code = EAPIResponseCode.internal_error
            result = ''
        else:
            res = response.json().get('result')
            if res:
                result = res[0]
                response_code = EAPIResponseCode.success
            else:
                result = res
                response_code = EAPIResponseCode.not_found
                error_msg = 'Folder not exist'
        api_response.result = result
        api_response.code = response_code
        api_response.error_msg = error_msg
        return api_response.json_response()
