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
from fastapi import Request
from fastapi_utils.cbv import cbv

from ...models.base_models import EAPIResponseCode
from ...models.project_models import GetProjectFolderResponse
from ...models.project_models import POSTProjectFile
from ...models.project_models import POSTProjectFileResponse
from ...models.project_models import ProjectListResponse
from ...resources.dependencies import check_file_exist
from ...resources.dependencies import get_project_role
from ...resources.dependencies import has_permission
from ...resources.dependencies import jwt_required
from ...resources.dependencies import transfer_to_pre
from ...resources.dependencies import validate_upload_event
from ...resources.error_handler import ECustomizedError
from ...resources.error_handler import catch_internal
from ...resources.error_handler import customized_error_template
from ...resources.helpers import get_user_projects
from ...resources.helpers import get_zone
from ...resources.helpers import query_node

router = APIRouter()
_API_TAG = 'V1 Projects'
_API_NAMESPACE = 'api_project'


@cbv(router)
class APIProject:
    current_identity: dict = Depends(jwt_required)

    def __init__(self):
        self._logger = LoggerFactory(_API_NAMESPACE).get_logger()

    @router.get(
        '/projects',
        tags=[_API_TAG],
        response_model=ProjectListResponse,
        summary='Get project list that user have access to')
    @catch_internal(_API_NAMESPACE)
    async def list_project(self):
        """Get the project list that user have access to."""
        self._logger.info('API list_project'.center(80, '-'))
        api_response = ProjectListResponse()
        try:
            _ = self.current_identity['username']
        except (AttributeError, TypeError):
            return self.current_identity
        self._logger.info(
            f'User request with identity: {self.current_identity}'
        )
        project_list = await get_user_projects(self.current_identity)
        self._logger.info(f'Getting user projects: {project_list}')
        self._logger.info(f'Number of projects: {len(project_list)}')
        api_response.result = project_list
        api_response.code = EAPIResponseCode.success
        return api_response.json_response()

    @router.post(
        '/project/{project_code}/files',
        response_model=POSTProjectFileResponse,
        summary='pre upload file to the target zone',
        tags=['V1 Files'])
    @catch_internal(_API_NAMESPACE)
    async def project_file_preupload(
        self,
        project_code,
        request: Request,
        data: POSTProjectFile
    ):
        """PRE upload and check existence of file in project."""
        api_response = POSTProjectFileResponse()
        try:
            _ = self.current_identity['role']
        except (AttributeError, TypeError):
            return self.current_identity
        self._logger.info('API project_file_preupload'.center(80, '-'))
        self._logger.info(
            f'User request with identity: \
            {self.current_identity}'
        )
        val_result, val_error = validate_upload_event(
            data.zone,
            self.current_identity,
            project_code
        )
        self._logger.info(
            f'validation code and error: {val_error}'
        )
        if val_error:
            self._logger.error(f'Upload event error: {val_error}')
            code = EAPIResponseCode.forbidden if val_result \
                else EAPIResponseCode.bad_request
            api_response.error_msg = val_error
            api_response.code = code
            api_response.result = val_result
            return api_response.json_response()
        for file in data.data:
            file_result = await check_file_exist(data.zone, file, project_code)
            # Stop upload if file exist
            if file_result.get('code') == 200 and file_result.get('result'):
                api_response.error_msg = 'File with that name already exists'
                api_response.code = EAPIResponseCode.conflict
                api_response.result = data
                return api_response.json_response()
        session_id = request.headers.get('Session-ID')
        result = await transfer_to_pre(data, project_code, session_id)
        if result.status_code == 409:
            api_response.error_msg = result.json()['error_msg']
            api_response.code = EAPIResponseCode.conflict
            return api_response.json_response()
        elif result.status_code != 200:
            api_response.error_msg = 'Upload Error: ' + \
                result.json()['error_msg']
            api_response.code = EAPIResponseCode.internal_error
            return api_response.json_response()
        else:
            api_response.result = result.json()['result']
        return api_response.json_response()

    @router.get(
        '/project/{project_code}/folder',
        tags=[_API_TAG],
        response_model=GetProjectFolderResponse,
        summary='Get folder in the project')
    @catch_internal(_API_NAMESPACE)
    async def get_project_folder(self, project_code, zone, folder):
        """Get folder in project."""
        api_response = GetProjectFolderResponse()
        username = self.current_identity['username']
        self._logger.info('API get_project_folder'.center(80, '-'))
        self._logger.info(f'User request identity: {self.current_identity}')
        zone_type = get_zone(zone.lower())
        error_msg = ''
        permission = await has_permission(
            self.current_identity, project_code, 'file', zone.lower(), 'view')
        if not permission:
            api_response.error_msg = customized_error_template(
                ECustomizedError.PERMISSION_DENIED
            )
            api_response.code = EAPIResponseCode.forbidden
            return api_response.json_response()
        project_role = get_project_role(self.current_identity, project_code)
        name_folder = folder.split('/')[0]
        # verify the name folder access permission
        if zone_type == 0 and project_role not in ['admin', 'platform-admin']:
            if username != name_folder:
                api_response.error_msg = customized_error_template(
                    ECustomizedError.PERMISSION_DENIED
                )
                api_response.code = EAPIResponseCode.forbidden
                return api_response.json_response()
        folder_path = folder.strip('/').split('/')
        parent_path = '/'.join(folder_path[0:-1])
        folder_name = folder_path[-1]

        folder_check_event = {
            'container_code': project_code,
            'container_type': 'project',
            'parent_path': parent_path,
            'recursive': False,
            'zone': get_zone(zone),
            'archived': False,
            'name': folder_name,
        }
        folder_response = await query_node(folder_check_event)
        self._logger.info(f'Folder check event: {folder_check_event}')
        self._logger.info(f'Folder check response: {folder_response.text}')
        response = folder_response.json()
        if response.get('code') != 200:
            error_msg = 'Error Getting Folder: ' + response.get('error_msg')
            response_code = EAPIResponseCode.internal_error
            result = ''
        else:
            res = response.get('result')
            self._logger.info(f'res: {res}')
            if res:
                result = res[0]
                response_code = EAPIResponseCode.success
            else:
                result = res
                response_code = EAPIResponseCode.not_found
                error_msg = 'Folder not exist'
        self._logger.info(f'error_msg: {error_msg}')
        api_response.result = result
        api_response.code = response_code
        api_response.error_msg = error_msg
        return api_response.json_response()
