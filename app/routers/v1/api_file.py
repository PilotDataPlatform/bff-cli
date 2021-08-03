from fastapi import APIRouter, Depends
from fastapi_utils.cbv import cbv
from fastapi.responses import JSONResponse
from ...models.file_models import *
from ...commons.logger_services.logger_factory_service import SrvLoggerFactory
from ...resources.error_handler import catch_internal
from ...resources.dependencies import *
from ...resources.helpers import *
from ...service_logger.logger_factory_service import SrvLoggerFactory


router = APIRouter()
_API_TAG = 'V1 files'
_API_NAMESPACE = "api_files"


@cbv(router)
class APIProject:
    current_identity: dict = Depends(jwt_required)

    def __init__(self):
        self._logger = SrvLoggerFactory(_API_NAMESPACE).get_logger()

    @router.post("/query/geid", tags=[_API_TAG],
                response_model=QueryDataInfoResponse,
                summary="Query file/folder information by geid")
    @catch_internal(_API_NAMESPACE)
    async def query_file_folders_by_geid(self, data: QueryDataInfo):
        """
        Get file/folder information by geid
        """
        file_response = QueryDataInfoResponse()
        try:
            role = self.current_identity["role"]
            user_id = self.current_identity["user_id"]
            user_name = self.current_identity['username']
        except (AttributeError, TypeError):
            return self.current_identity
        geid = data.geid
        self._logger.info("API /query/geid".center(80, '-'))
        self._logger.info(f"Received information geid: {geid}")
        self._logger.info(f"User request with identity: {self.current_identity}")
        response_list = []
        for global_entity_id in geid: 
            self._logger.info(f'Query geid: {global_entity_id}')
            res = get_node_by_geid(global_entity_id)
            if not res:
                status = customized_error_template(ECustomizedError.FILE_NOT_FOUND)
                result = []
                self._logger.info(f'status: {status}')
            elif 'File' not in res[0].get('labels') and 'Folder' not in res[0].get('labels'):
                self._logger.info(f'User {user_name} attempt getting node: {res}')
                status = customized_error_template(ECustomizedError.FILE_FOLDER_ONLY)
                result = []
                self._logger.info(f'status: {status}')
            elif res[0].get('archived'):
                self._logger.info(f'User {user_name} attempt getting node: {res}')
                status = customized_error_template(ECustomizedError.FILE_FOLDER_ONLY)
                result = []
                self._logger.info(f'status: {status}')
            else:
                self._logger.info(f'Query result: {res}')
                project_code = res[0].get('project_code')
                labels = res[0].get('labels')
                display_path = res[0].get('display_path').lstrip('/')
                name_folder = display_path.split('/')[0]
                zone = 'VRECore' if 'VRECore' in labels else 'Greenroom'
                self._logger.info(f'File zone: {zone}')
                permission_event = {'user_id': user_id,
                                    'username': user_name,
                                    'role': role,
                                    'project_code': project_code,
                                    'zone': zone}
                permission = check_permission(permission_event)
                self._logger.info(f"Permission check event: {permission_event}")
                self._logger.info(f"Permission check result: {permission}")
                error_msg = permission.get('error_msg', '')
                uploader = permission.get('uploader')
                if error_msg:
                    status = error_msg
                    result = []
                elif uploader and uploader != name_folder:
                    self._logger.info(f'User {user_name} attempt getting file: {display_path}')
                    status = customized_error_template(ECustomizedError.PERMISSION_DENIED)
                    result = []
                else:
                    status = 'success'
                    result = res
                self._logger.info(f'file result: {result}')
            response_list.append({'status': status, 'result': result, 'geid': global_entity_id})
        self._logger.info(f'Query file/folder result: {response_list}')
        file_response.result = response_list
        file_response.code = EAPIResponseCode.success
        return file_response.json_response()


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
        self._logger.info("API file_list_query".center(80, '-'))
        self._logger.info(f"Received information project_code: {project_code}, zone: {zone}, "
                          f"folder: {folder}, source_type: {source_type}")
        self._logger.info(f"User request with identity: {self.current_identity}")
        self._logger.info(f"Verified list event: {code}, {error_msg}")
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
        self._logger.info(f"Permission check event: {permission_event}")
        self._logger.info(f"Permission check result: {permission}")
        error_msg = permission.get('error_msg', '')
        if error_msg:
            file_response.error_msg = error_msg
            file_response.code = permission.get('code')
            file_response.result = permission.get('result')
            return file_response.json_response()
        uploader = permission.get('uploader')
        if uploader and source_type == 'Container':
            child_attribute = {'project_code': project_code,
                               'uploader': user_name,
                               'archived': False}
        elif uploader and source_type == 'Folder':
            child_attribute = {'project_code': project_code,
                               'archived': False}
        else:
            child_attribute = {'project_code': project_code,
                               'archived': False}
        self._logger.info(f"Getting child node attribute: {child_attribute}")
        parent_label = get_parent_label(source_type)
        rel_path, folder_name = separate_rel_path(folder)
        self._logger.info(f"Getting parent_label: {parent_label}")
        self._logger.info(f"Getting relative_path: {rel_path}")
        self._logger.info(f"Getting folder_name: {folder_name}")
        if parent_label == 'Container':
            parent_attribute = {'code': project_code}
        else:
            parent_attribute = {'project_code': project_code,
                                'name': folder_name,
                                'folder_relative_path': rel_path}
        if source_type == 'Folder':
            code, error_msg = check_folder_exist(zone, project_code, folder)
            self._logger.info(f"Check folder exist payload: 'zone':{zone}, 'project_code':{project_code}, 'folder_name':{folder_name}, 'rel_path':{rel_path}")
            self._logger.info(f"Check folder exist response: {code}, {error_msg}")
            self._logger.debug(
                f"uploader != '': {uploader != ''}, not rel_path: {not rel_path}, folder != uploader: {folder != uploader}")
            self._logger.debug(f"uploader: {uploader}, rel_path: {rel_path}, folder: {folder}")
            if error_msg:
                file_response.error_msg = error_msg
                file_response.code = EAPIResponseCode.forbidden
                self._logger.error(f'Returning error: {EAPIResponseCode.forbidden}, {error_msg}')
                return file_response.json_response()
            elif uploader and not rel_path and folder_name != uploader:
                file_response.error_msg = customized_error_template(ECustomizedError.PERMISSION_DENIED)
                file_response.code = EAPIResponseCode.forbidden
                self._logger.error(f'Returning wrong name folder error: {EAPIResponseCode.forbidden}, '
                                   f'{customized_error_template(ECustomizedError.PERMISSION_DENIED)}')
                return file_response.json_response()
            elif uploader and rel_path and rel_path.split('/')[0] != uploader:
                file_response.error_msg = customized_error_template(ECustomizedError.PERMISSION_DENIED)
                file_response.code = EAPIResponseCode.forbidden
                self._logger.error(f'Returning subfolder not in correct name folder error: {EAPIResponseCode.forbidden}, '
                                   f'{customized_error_template(ECustomizedError.PERMISSION_DENIED)}')
                return file_response.json_response()
        zone_label = [zone_type]
        url = ConfigClass.NEO4J_SERVICE + "relations/query"
        payload = {"start_label": parent_label,
                   "start_params": parent_attribute,
                   "end_label": zone_label,
                   "end_params": child_attribute}
        self._logger.info(f"Query file/folder payload: {payload}")
        self._logger.info(f"Query file/folder API: {url}")
        try:
            res = requests.post(url, json=payload)
            res = res.json()
            query_result = []
            for f in res:
                query_result.append(f.get('end_node'))
            file_response.result = query_result
            file_response.code = EAPIResponseCode.success
            return file_response.json_response()
        except Exception as e:
            self._logger.error(f"Error query files: {str(e)}")
            file_response.error_msg = str(e)
            file_response.code = EAPIResponseCode.internal_error
            return file_response.json_response()


@cbv(router)
class APIProject:
    current_identity: dict = Depends(jwt_required)

    def __init__(self):
        self._logger = SrvLoggerFactory(_API_NAMESPACE).get_logger()

    @router.post("/files/download/pre", tags=[_API_TAG],
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
        self._logger.info("API forward_donwload_pre".center(80, '-'))
        self._logger.info(f"User request with identity: {self.current_identity}")
        zone = get_zone(data.zone)
        permission_event = {'user_id': user_id,
                            'username': user_name,
                            'role': role,
                            'project_code': data.project_code,
                            'zone': zone}
        permission = check_permission(permission_event)
        error_msg = permission.get('error_msg', '')
        self._logger.info(f"Permission check event: {permission_event}")
        self._logger.info(f"Permission check result: {permission}")
        if error_msg:
            self._logger.info(f"Permission check error: {error_msg}")
            download_response.error_msg = error_msg
            download_response.code = permission.get('code')
            download_response.result = permission.get('result')
            return download_response.json_response()
        limited_file_access = permission.get('uploader', '')
        if limited_file_access:
            try:
                payload = {"query": {
                    "global_entity_id": data.files[0].get('geid'),
                    "project_code": data.project_code,
                    "labels": [zone]
                }
                }
                self._logger.info(f"File query payload: {payload}")
                self._logger.info(f"File query API: {ConfigClass.NEO4J_SERVICE_v2 + 'nodes/query'}")
                file_res = requests.post(ConfigClass.NEO4J_SERVICE_v2 + 'nodes/query', json=payload)
                self._logger.info(f"File query result: {file_res.text}")
                file_info = file_res.json().get('result')[0]
                owner = file_info.get('uploader')
                if owner != permission.get('uploader'):
                    download_response.error_msg = customized_error_template(ECustomizedError.PERMISSION_DENIED)
                    download_response.code = EAPIResponseCode.forbidden
                    download_response.result = f"{permission.get('uploader')} No permission to access file {file_info}"
                    return download_response.json_response()
            except Exception as e:
                download_response.error_msg = 'File may not exist in the given project (geid does not match project code)'
                download_response.code = EAPIResponseCode.bad_request
                download_response.result = str(e)
                return download_response.json_response()
        if zone == 'VRECore':
            url = ConfigClass.url_download_vrecore
        else:
            url = ConfigClass.url_download_greenroom
        payload = {'files': data.files,
                   'operator': data.operator,
                   'project_code': data.project_code,
                   'session_id': data.session_id}
        self._logger.info(f"Download requests payload: {payload}")
        self._logger.info(f"Download requests API: {url}")
        pre_res = requests.post(url, json=payload)
        return JSONResponse(content=pre_res.json(), status_code=pre_res.status_code)
