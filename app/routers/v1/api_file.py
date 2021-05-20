from fastapi import APIRouter, Depends
from fastapi_utils.cbv import cbv
from fastapi.responses import JSONResponse
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
        zone_type = get_zone(zone)
        permission_event = {'user_id': user_id,
                            'username': user_name,
                            'role': role,
                            'project_code': project_code,
                            'zone': zone}
        permission = check_permission(permission_event)
        error_msg = permission.get('error_msg', '')
        if error_msg:
            file_response.error_msg = error_msg
            file_response.code = permission.get('code')
            file_response.result = permission.get('result')
            return file_response.json_response()
        uploader = permission.get('uploader')
        if uploader:
            child_attribute = {'project_code': project_code,
                               'uploader': user_name}
        else:
            child_attribute = {'project_code': project_code}
        parent_label = get_parent_label(source_type)
        rel_path, folder_name = separate_rel_path(folder)
        if parent_label == 'Dataset':
            parent_attribute = {'code': project_code}
        else:
            parent_attribute = {'project_code': project_code,
                                'name': folder_name,
                                'folder_relative_path': rel_path}
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


@cbv(router)
class APIProject:
    current_identity: dict = Depends(jwt_required)

    def __init__(self):
        self._logger = SrvLoggerFactory(_API_NAMESPACE).get_logger()

    @router.post("/files/download/pre/", tags=[_API_TAG],
                 response_model=POSTDownloadFileResponse,
                 summary="Permission check for downloading")
    @catch_internal(_API_NAMESPACE)
    async def forward_download_pre(self, data: POSTDownloadFile):
        """
        List files and folders in project
        """
        download_response = POSTDownloadFileResponse()
        try:
            role = self.current_identity["role"]
            user_id = self.current_identity["user_id"]
            user_name = self.current_identity['username']
        except (AttributeError, TypeError):
            return self.current_identity
        permission_event = {'user_id': user_id,
                            'username': user_name,
                            'role': role,
                            'project_code': data.project_code,
                            'zone': data.zone}
        permission = check_permission(permission_event)
        error_msg = permission.get('error_msg', '')
        if error_msg:
            download_response.error_msg = error_msg
            download_response.code = permission.get('code')
            download_response.result = permission.get('result')
            return download_response.json_response()
        limited_file_access = permission.get('uploader', '')
        if limited_file_access:
            try:
                payload = {"global_entity_id": data.files[0].get('geid'),
                           "project_code": data.project_code}
                file_res = requests.post(ConfigClass.NEO4J_SERVICE + 'nodes/File/query', json=payload)
                file_info = file_res.json()[0]
                owner = file_info.get('uploader')
                if owner != permission.get('uploader'):
                    download_response.error_msg = customized_error_template(ECustomizedError.PERMISSION_DENIED)
                    download_response.code = EAPIResponseCode.forbidden
                    download_response.result = 'No permission to access file'
                    return download_response.json_response()
            except Exception as e:
                download_response.error_msg = customized_error_template(ECustomizedError.INTERNAL)
                download_response.code = EAPIResponseCode.internal_error
                download_response.result = str(e)
                return download_response.json_response()
        if data.zone == 'vrecore':
            url = ConfigClass.url_download_vrecore
        else:
            url = ConfigClass.url_download_greenroom
        payload = {'files': data.files,
                   'operator': data.operator,
                   'project_code': data.project_code,
                   'session_id': data.session_id}
        pre_res = requests.post(url, json=payload)
        return JSONResponse(content=pre_res.json(), status_code=pre_res.status_code)
