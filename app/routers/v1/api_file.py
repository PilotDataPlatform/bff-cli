from fastapi import APIRouter, Depends
from fastapi_utils.cbv import cbv
from ...models.file_models import *
from ...commons.logger_services.logger_factory_service import SrvLoggerFactory
from ...resources.error_handler import catch_internal
from ...resources.dependencies import *
from ...resources.helpers import *


router = APIRouter()
_API_TAG = 'V1 files'
_API_NAMESPACE = "api_files"


@cbv(router)
class APIProject:
    current_identity: dict = Depends(jwt_required)

    def __init__(self):
        self._logger = SrvLoggerFactory(_API_NAMESPACE).get_logger()

    @router.get("/{project_code}/files/query", tags=[_API_TAG],
                response_model=GetProjectFileListResponse,
                summary="Get files and folders in the project/folder")
    @catch_internal(_API_NAMESPACE)
    async def get_file_folders(self, project_code, zone, folder, source_type):
        """
        List files and folders in project
        """
        file_response = GetProjectFileListResponse()
        try:
            role = self.current_identity["role"]
            user_id = self.current_identity["user_id"]
            user_name = self.current_identity['username']
        except (AttributeError, TypeError):
            return self.current_identity
        code, error_msg = verify_list_event(source_type, folder)
        if error_msg:
            file_response.error_msg = error_msg
            file_response.code = code
            return file_response.json_response()
        project_role, code = get_project_role(user_id, project_code)
        if role == "admin" and code != EAPIResponseCode.not_found:
            project_role = 'admin'
        elif project_role == 'User not in the project':
            file_response.error_msg = customized_error_template(ECustomizedError.PERMISSION_DENIED)
            file_response.code = code
            file_response.result = project_role
            return file_response.json_response()
        elif code == EAPIResponseCode.not_found:
            file_response.error_msg = customized_error_template(ECustomizedError.PROJECT_NOT_FOUND)
            file_response.code = code
            return file_response.json_response()
        zone_type = get_zone(zone)
        parent_label = get_parent_label(source_type)
        rel_path, folder_name = separate_rel_path(folder)
        if parent_label == 'Dataset':
            parent_attribute = {'code': project_code}
        else:
            parent_attribute = {'project_code': project_code,
                                'name': folder_name,
                                'folder_relative_path': rel_path}
        if project_role != 'admin' and zone_type == 'Greenroom':
            child_attribute = {'project_code': project_code,
                               'uploader': user_name}
        elif project_role != 'contributor' and zone_type == 'VRECore':
            child_attribute = {'project_code': project_code}
        elif project_role == 'admin':
            child_attribute = {'project_code': project_code}
        else:
            file_response.code = EAPIResponseCode.forbidden
            file_response.error_msg = 'Permission Denied'
            return file_response.json_response()
        if source_type == 'Folder':
            code, error_msg = check_folder_exist(zone, project_code, folder_name, rel_path)
            if error_msg:
                file_response.error_msg = error_msg
                file_response.code = code
                return file_response.json_response()
        zone_label = [zone_type]
        url = ConfigClass.NEO4J_SERVICE + "relations/query"
        payload = {"start_label": parent_label,
                   "start_params": parent_attribute,
                   "end_label": zone_label,
                   "end_params": child_attribute}
        res = requests.post(url, json=payload)
        res = res.json()
        query_result = []
        for f in res:
            query_result.append(f.get('end_node'))
        file_response.result = query_result
        file_response.code = EAPIResponseCode.success
        return file_response.json_response()
