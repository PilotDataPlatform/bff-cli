from fastapi import APIRouter, Depends
from fastapi_utils.cbv import cbv
from ...models.file_models import QueryDataInfoResponse, QueryDataInfo, GetProjectFileListResponse
from ...resources.error_handler import catch_internal, customized_error_template, ECustomizedError, EAPIResponseCode
from ...resources.dependencies import jwt_required, has_permission, get_project_role
from ...resources.helpers import batch_query_node_by_geid, get_zone, query_node, separate_rel_path
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
        self._logger.info("API file_list_query".center(80, '-'))
        file_response = GetProjectFileListResponse()
        username = self.current_identity["username"]
        zone = get_zone(zone)
        project_role = get_project_role(self.current_identity, project_code)
        rel_path, folder_name = separate_rel_path(folder)
        self._logger.info(f"Getting relative_path: {rel_path}")
        self._logger.info(f"Getting folder_name: {folder_name}")
        self._logger.info(f"Getting rel_path.split('/')[0]: {rel_path.split('/')[0]}")
        self._logger.info(f"Getting username: {username}")
        self._logger.info(f"Getting zone: {zone}")
        self._logger.info(f"Getting zone: {type(zone)}")
        self._logger.info(f"Getting role: {not project_role in ['admin', 'platform-admin']}")
        self._logger.info(f"Getting zone: {zone == 0}")
        self._logger.info(f"Getting project_role: {project_role}")
        self._logger.info(f"Getting username and rel_path and rel_path.split('/')[0] != username: {username and rel_path and rel_path.split('/')[0] != username}")
        self._logger.info(f'project_role in ["admin", "platform-admin"]: {project_role in ["admin", "platform-admin"]}')
        if zone == 0 and not project_role in ["admin", "platform-admin"]:
            if username and not rel_path and folder_name != username:
                self._logger.info(f"should return at 113")
                file_response.error_msg = customized_error_template(ECustomizedError.PERMISSION_DENIED)
                file_response.code = EAPIResponseCode.forbidden
                self._logger.error(f'Returning wrong name folder error: {EAPIResponseCode.forbidden}, '
                                f'{customized_error_template(ECustomizedError.PERMISSION_DENIED)}')
                return file_response.json_response()
            elif username and rel_path and rel_path.split('/')[0] != username:
                self._logger.info(f"should return at 116")
                file_response.error_msg = customized_error_template(ECustomizedError.PERMISSION_DENIED)
                file_response.code = EAPIResponseCode.forbidden
                self._logger.error(f'Returning subfolder not in correct name folder error: {EAPIResponseCode.forbidden}, '
                                f'{customized_error_template(ECustomizedError.PERMISSION_DENIED)}')
                return file_response.json_response()
            else:
                self._logger.info(f"Getting username: {username}, project_role: {project_role}, rel_path: {rel_path}, foldername: {folder_name}")



        params = {
                    'container_code': project_code,
                    'container_type': source_type.lower(),
                    'parent_path': folder,
                    'recursive': False,
                    'zone': zone,
                    'archived': False
                }
        self._logger.info(f"Query node payload: {params}")
        folder_info = await query_node(params)
        self._logger.info(f'folder_info: {folder_info}')
        response = folder_info.json()
        self._logger.info(f'folder_response: {response}')
        if response.get('code') != 200:
            error_msg = "Error Getting Folder: " + response.get("error_msg")
            response_code = EAPIResponseCode.internal_error
            result = []
            file_response.result = result
            file_response.code = response_code
            file_response.error_msg = error_msg
            return file_response.json_response()
        else:
            result = response.get('result')
            if result:
                result = result
                code = EAPIResponseCode.success
                error_msg = response.get('error_msg')
            else:
                result = []
                code = EAPIResponseCode.forbidden
                error_msg = 'Folder not exist'
            file_response.result = result
            file_response.code = code
            file_response.error_msg = error_msg
            return file_response.json_response()
