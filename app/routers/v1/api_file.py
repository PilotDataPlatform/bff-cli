# Copyright (C) 2022 Indoc Research
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from common import LoggerFactory
from fastapi import APIRouter
from fastapi import Depends
from fastapi_utils.cbv import cbv

from ...models.file_models import GetProjectFileListResponse
from ...models.file_models import QueryDataInfo
from ...models.file_models import QueryDataInfoResponse
from ...resources.dependencies import get_project_role
from ...resources.dependencies import has_permission
from ...resources.dependencies import jwt_required
from ...resources.error_handler import EAPIResponseCode
from ...resources.error_handler import ECustomizedError
from ...resources.error_handler import catch_internal
from ...resources.error_handler import customized_error_template
from ...resources.helpers import batch_query_node_by_geid
from ...resources.helpers import get_zone
from ...resources.helpers import query_file_folder
from ...resources.helpers import separate_rel_path

router = APIRouter()
_API_TAG = 'V1 files'
_API_NAMESPACE = 'api_files'


@cbv(router)
class APIFile:
    current_identity: dict = Depends(jwt_required)

    def __init__(self):
        self._logger = LoggerFactory(_API_NAMESPACE).get_logger()

    @router.post(
        '/query/geid',
        tags=[_API_TAG],
        response_model=QueryDataInfoResponse,
        summary='Query file/folder information by geid',
    )
    @catch_internal(_API_NAMESPACE)
    async def query_file_folders_by_geid(self, data: QueryDataInfo):
        """Get file/folder information by geid."""
        file_response = QueryDataInfoResponse()
        try:
            user_name = self.current_identity['username']
        except (AttributeError, TypeError):
            return self.current_identity
        geid_list = data.geid
        self._logger.info('API /query/geid'.center(80, '-'))
        self._logger.info(f'Received information geid: {geid_list}')
        self._logger.info(f'User identity: {self.current_identity}')
        response_list = []
        located_geid, query_result = await batch_query_node_by_geid(geid_list)
        for global_entity_id in geid_list:
            self._logger.info(f'Query geid: {global_entity_id}')
            result = {}
            if global_entity_id not in located_geid:
                status = customized_error_template(ECustomizedError.FILE_NOT_FOUND)
                self._logger.info(f'status: {status}')
            elif query_result[global_entity_id].get('archived'):
                status = customized_error_template(ECustomizedError.FILE_FOLDER_ONLY)
                self._logger.info(f'status: {status}')
            else:
                self._logger.info(f'Query result: {query_result[global_entity_id]}')
                project_code = query_result[global_entity_id].get('container_code')
                zone = query_result[global_entity_id].get('zone')
                parent_path = query_result[global_entity_id].get('parent_path')
                name_folder = parent_path.split('/')[0]
                permission = await has_permission(
                    self.current_identity,
                    project_code,
                    'file',
                    zone,
                    'view',
                )
                if not permission:
                    status = customized_error_template(ECustomizedError.PERMISSION_DENIED)
                project_role = get_project_role(self.current_identity, project_code)
                if user_name != name_folder and project_role not in ['platform-admin', 'admin']:
                    status = customized_error_template(ECustomizedError.PERMISSION_DENIED)
                else:
                    status = 'success'
                    result = query_result[global_entity_id]
            response_list.append({'status': status, 'result': result, 'geid': global_entity_id})
        self._logger.info(f'Query file/folder result: {response_list}')
        file_response.result = response_list
        file_response.code = EAPIResponseCode.success
        return file_response.json_response()

    @router.get(
        '/{project_code}/files/query',
        tags=[_API_TAG],
        response_model=GetProjectFileListResponse,
        summary='Get files and folders in the project/folder',
    )
    @catch_internal(_API_NAMESPACE)
    async def get_file_folders(self, project_code, zone, folder, source_type, page, page_size):
        """List files and folders in project."""
        self._logger.info('API file_list_query'.center(80, '-'))
        file_response = GetProjectFileListResponse()
        username = self.current_identity['username']
        permission = await has_permission(self.current_identity, project_code, 'file', zone, 'view')
        self._logger.info(f'User permission: {permission}')
        if not permission:
            file_response.error_msg = 'Project permission denied'
            file_response.code = EAPIResponseCode.forbidden
            return file_response.json_response()
        zone = get_zone(zone)
        project_role = get_project_role(self.current_identity, project_code)
        self._logger.info(
            f'project_role in ["admin", "platform-admin"]: \
                {project_role in ["admin", "platform-admin"]}'
        )
        rel_path, folder_name = separate_rel_path(folder)
        if zone == 0 and project_role not in ['admin', 'platform-admin']:
            if username and not rel_path and folder_name != username:
                file_response.error_msg = customized_error_template(
                    ECustomizedError.PERMISSION_DENIED
                )
                file_response.code = EAPIResponseCode.forbidden
                self._logger.error(
                    f'Returning wrong name folder error: \
                    {EAPIResponseCode.forbidden}, '
                    f'{file_response.error_msg}'
                )
                return file_response.json_response()
            elif username and rel_path and rel_path.split('/')[0] != username:
                file_response.error_msg = customized_error_template(
                    ECustomizedError.PERMISSION_DENIED
                )
                file_response.code = EAPIResponseCode.forbidden
                self._logger.error(
                    f'Returning subfolder not in correct \
                        name folder error: {EAPIResponseCode.forbidden}, \
                            {file_response.error_msg}'
                )
                return file_response.json_response()
            else:
                self._logger.info(
                    f'Getting username: {username}, \
                    project_role: {project_role}, \
                    rel_path: {rel_path}, \
                    foldername: {folder_name}'
                )
        params = {
            'container_code': project_code,
            'container_type': source_type.lower(),
            'recursive': False,
            'zone': zone,
            'archived': False,
            'page': page,
            'page_size': page_size,
            'order': 'desc'
        }
        if folder:
            params['parent_path'] = folder.replace('/', '.')
        self._logger.info(f'Query node payload: {params}')
        folder_info = await query_file_folder(params)
        self._logger.info(f'folder_info: {folder_info}')
        response = folder_info.json()
        self._logger.info(f'folder_response: {response}')
        if response.get('code') != 200:
            file_response.result = response.get('result')
            file_response.code = EAPIResponseCode.internal_error
            file_response.error_msg = 'Error Getting Folder: ' + response.get('error_msg')
            return file_response.json_response()
        else:
            file_response.result = response.get('result')
            file_response.code = EAPIResponseCode.success
            file_response.error_msg = response.get('error_msg')
            return file_response.json_response()
