from unittest import result
from fastapi import APIRouter, Depends
from fastapi_utils.cbv import cbv
from ...models.file_models import QueryDataInfoResponse, QueryDataInfo, GetProjectFileListResponse
from ...resources.error_handler import catch_internal, customized_error_template, ECustomizedError, EAPIResponseCode
from ...resources.dependencies import jwt_required, has_permission, get_project_role
from ...resources.helpers import batch_query_node_by_geid, verify_list_event, separate_rel_path, get_zone, query_node, query_relation
from ...config import ConfigClass
from logger import LoggerFactory
import httpx

router = APIRouter()
_API_TAG = 'V1 files'
_API_NAMESPACE = "api_files"


@cbv(router)
class APIFile:
    current_identity: dict = Depends(jwt_required)

    def __init__(self):
        self._logger = LoggerFactory(_API_NAMESPACE).get_logger()

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
        geid_list = data.geid
        self._logger.info("API /query/geid".center(80, '-'))
        self._logger.info(f"Received information geid: {geid_list}")
        self._logger.info(f"User request with identity: {self.current_identity}")
        response_list = []
        located_geid, query_result = await batch_query_node_by_geid(geid_list)
        for global_entity_id in geid_list:
            self._logger.info(f'Query geid: {global_entity_id}')
            if global_entity_id not in located_geid:
                status = customized_error_template(ECustomizedError.FILE_NOT_FOUND)
                result = []
                self._logger.info(f'status: {status}')
            elif 'File' not in query_result[global_entity_id].get('labels') and \
                    'Folder' not in query_result[global_entity_id].get('labels'):
                self._logger.info(f'User {user_name} attempt getting node: {query_result[global_entity_id]}')
                status = customized_error_template(ECustomizedError.FILE_FOLDER_ONLY)
                result = []
                self._logger.info(f'status: {status}')
            elif query_result[global_entity_id].get('archived'):
                self._logger.info(f'User {user_name} attempt getting node: {query_result[global_entity_id]}')
                status = customized_error_template(ECustomizedError.FILE_FOLDER_ONLY)
                result = []
                self._logger.info(f'status: {status}')
            else:
                self._logger.info(f'Query result: {query_result[global_entity_id]}')
                project_code = query_result[global_entity_id].get('project_code')
                labels = query_result[global_entity_id].get('labels')
                display_path = query_result[global_entity_id].get('display_path').lstrip('/')
                name_folder = display_path.split('/')[0]
                zone = ConfigClass.CORE_ZONE_LABEL if ConfigClass.CORE_ZONE_LABEL in labels \
                    else ConfigClass.GREEN_ZONE_LABEL
                self._logger.info(f'File zone: {zone}')
                permission = await has_permission(self.current_identity, project_code, "file", zone.lower(), "view")
                if not permission:
                    file_response.error_msg = "Permission denied"
                    file_response.code = EAPIResponseCode.forbidden
                    return file_response.json_response()
                if user_name and user_name != name_folder:
                    self._logger.info(f'User {user_name} attempt getting file: {display_path}')
                    status = customized_error_template(ECustomizedError.PERMISSION_DENIED)
                    result = []
                else:
                    status = 'success'
                    result = [query_result[global_entity_id]]
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
        zone_label = get_zone(zone)
        permission = await has_permission(self.current_identity, project_code, "file", zone, "view")
        self._logger.warn(f"permission: {permission}")
        if not permission:
            file_response.error_msg = "Permission denied"
            file_response.code = EAPIResponseCode.forbidden
            return file_response.json_response()

        username = self.current_identity["username"]
        if username and source_type == 'Container':
            child_attribute = {'project_code': project_code,
                               'uploader': username,
                               'archived': False}
        elif username and source_type == 'Folder':
            child_attribute = {'project_code': project_code,
                               'archived': False}
        else:
            child_attribute = {'project_code': project_code,
                               'archived': False}
        self._logger.info(f"Getting child node attribute: {child_attribute}")
        parent_type = {
                        'folder': 'Folder',
                        'container': 'Container'
                    }.get(source_type.lower(), None)
        rel_path, folder_name = separate_rel_path(folder)
        self._logger.info(f"Getting parent_type: {parent_type}")
        self._logger.info(f"Getting relative_path: {rel_path}")
        self._logger.info(f"Getting folder_name: {folder_name}")
        if parent_type == 'Container':
            parent_attribute = {'code': project_code}
            parent_label = [parent_type]
        else:
            parent_label = [parent_type, zone_label]
            parent_attribute = {'project_code': project_code,
                                'name': folder_name,
                                'folder_relative_path': rel_path}
        if source_type == 'Folder':
            folder_check_event = {
                "query": {
                            "folder_relative_path": '/'.join(folder.split('/')[0:-1]),
                            "display_path": folder,
                            "name": folder.split('/')[-1],
                            "project_code": project_code,
                            "archived": False,
                            "labels": ['Folder', zone_label]}
                    }
            self._logger.info(f"Query node: {folder_check_event}")
            self._logger.info(f"Check folder exist payload: 'zone':{zone}, 'project_code':{project_code}, 'folder_name':{folder_name}, 'rel_path':{rel_path}")
            self._logger.debug(f"username != '': {username != ''}, not rel_path: {not rel_path}, folder != username: {folder != username}")
            self._logger.debug(f"username: {username}, rel_path: {rel_path}, folder: {folder}")
            folder_response = await query_node(folder_check_event)
            res = folder_response.json().get('result')
            self._logger.info(f"Check folder exist response: {code}, '{error_msg}', '{res}'")
            project_role = get_project_role(self.current_identity, project_code)
            self._logger.info(f"Project role: {project_role}")
            if not res:
                file_response.error_msg = 'Folder not exist'
                file_response.code = EAPIResponseCode.forbidden
                self._logger.error(f'Returning error: {EAPIResponseCode.forbidden}, {error_msg}')
                return file_response.json_response()
            if zone_label == ConfigClass.GREEN_ZONE_LABEL and not project_role in ["admin", "platform-admin"]:
                if username and not rel_path and folder_name != username:
                    file_response.error_msg = customized_error_template(ECustomizedError.PERMISSION_DENIED)
                    file_response.code = EAPIResponseCode.forbidden
                    self._logger.error(f'Returning wrong name folder error: {EAPIResponseCode.forbidden}, '
                                    f'{customized_error_template(ECustomizedError.PERMISSION_DENIED)}')
                    return file_response.json_response()
                elif username and rel_path and rel_path.split('/')[0] != username:
                    file_response.error_msg = customized_error_template(ECustomizedError.PERMISSION_DENIED)
                    file_response.code = EAPIResponseCode.forbidden
                    self._logger.error(f'Returning subfolder not in correct name folder error: {EAPIResponseCode.forbidden}, '
                                    f'{customized_error_template(ECustomizedError.PERMISSION_DENIED)}')
                    return file_response.json_response()
        payload = {
            "start_label": parent_label,
            "start_params": parent_attribute,
            "end_label": zone_label,
            "end_params": child_attribute}
        self._logger.info(f"Query relation payload: {payload}")
        query_code, query_result, query_error = await query_relation(payload)
        file_response.result = query_result
        file_response.code = query_code
        file_response.error_msg = query_error
        return file_response.json_response()
