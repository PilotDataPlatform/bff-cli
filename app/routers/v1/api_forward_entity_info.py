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

from ...models.entity_info_models import CheckFileResponse
from ...resources.dependencies import check_file_exist
from ...resources.dependencies import jwt_required
from ...resources.error_handler import EAPIResponseCode
from ...resources.error_handler import catch_internal
from ...resources.helpers import separate_rel_path

router = APIRouter()


@cbv(router)
class APIFileInfo:
    _API_TAG = 'File INFO'
    _API_NAMESPACE = 'api_file_info'

    def __init__(self):
        self._logger = LoggerFactory(self._API_NAMESPACE).get_logger()

    @router.get('/project/{project_code}/file/exist', tags=[_API_TAG],
                response_model=CheckFileResponse,
                summary='Check source file')
    @catch_internal(_API_NAMESPACE)
    async def check_source_file(
        self,
        project_code,
        zone,
        file_relative_path,
        current_identity: dict = Depends(jwt_required)
    ):
        api_response = CheckFileResponse()
        try:
            _ = current_identity['role']
        except (AttributeError, TypeError):
            return current_identity
        rel_path, file_name = separate_rel_path(file_relative_path)
        file = {
            'resumable_relative_path': rel_path,
            'resumable_filename': file_name
        }
        response = await check_file_exist(zone, file, project_code)
        api_response.result = response.get('result')[0]
        api_response.code = EAPIResponseCode.success
        api_response.error_msg = response.get('error_msg')
        self._logger.info(f'api_response.json_response: \
            {api_response.json_response()}')
        return api_response.json_response()
