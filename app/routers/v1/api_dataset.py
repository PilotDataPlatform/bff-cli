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

from app.resources.helpers import get_dataset
from app.resources.helpers import get_dataset_versions
from app.resources.helpers import list_datasets
from ...models.base_models import EAPIResponseCode
from ...models.dataset_models import DatasetDetailResponse
from ...models.dataset_models import DatasetListResponse
from ...resources.dependencies import jwt_required
from ...resources.error_handler import ECustomizedError
from ...resources.error_handler import catch_internal
from ...resources.error_handler import customized_error_template

router = APIRouter()
_API_TAG = 'V1 dataset'
_API_NAMESPACE = 'api_dataset'


@cbv(router)
class APIDataset:
    current_identity: dict = Depends(jwt_required)

    def __init__(self):
        self._logger = LoggerFactory(_API_NAMESPACE).get_logger()

    @router.get('/datasets', tags=[_API_TAG],
                response_model=DatasetListResponse,
                summary='Get dataset list that user have access to')
    @catch_internal(_API_NAMESPACE)
    async def list_datasets(self, page=0, page_size=10):
        """Get the dataset list that user have access to."""
        self._logger.info('API list_datasets'.center(80, '-'))
        api_response = DatasetListResponse()
        try:
            username = self.current_identity['username']
        except (AttributeError, TypeError):
            return self.current_identity
        self._logger.info(
            f'User request with identity: {self.current_identity}')
        dataset_list = await list_datasets(username, page, page_size)
        self._logger.info(f'Getting user datasets: {dataset_list}')
        self._logger.info(f'Number of datasets: {len(dataset_list)}')
        api_response.result = dataset_list
        api_response.code = EAPIResponseCode.success
        return api_response.json_response()

    @router.get('/dataset/{dataset_code}', tags=[_API_TAG],
                response_model=DatasetDetailResponse,
                summary='Get dataset detail based on the dataset code')
    @catch_internal(_API_NAMESPACE)
    async def get_dataset(self, dataset_code, page=0, page_size=10):
        """Get the dataset detail by dataset code."""
        self._logger.info('API get_dataset'.center(80, '-'))
        api_response = DatasetDetailResponse()
        try:
            username = self.current_identity['username']
        except (AttributeError, TypeError):
            return self.current_identity
        self._logger.info(
            f'User request with identity: {self.current_identity}')
        node = await get_dataset(dataset_code)
        self._logger.info(f'Getting user dataset node: {node}')
        if not node:
            api_response.code = EAPIResponseCode.not_found
            api_response.error_msg = customized_error_template(
                ECustomizedError.DATASET_NOT_FOUND)
            return api_response.json_response()
        elif node.get('creator') != username:
            api_response.code = EAPIResponseCode.forbidden
            api_response.error_msg = customized_error_template(
                ECustomizedError.PERMISSION_DENIED)
            return api_response.json_response()
        node_geid = node.get('id')
        dataset_query_event = {
            'dataset_geid': node_geid,
            'page': page,
            'page_size': page_size
        }
        self._logger.info(f'Dataset query: {dataset_query_event}')
        versions = await get_dataset_versions(dataset_query_event)
        self._logger.info(f'Dataset versions: {versions}')
        dataset_detail = {
            'general_info': node,
            'version_detail': versions,
            'version_no': len(versions)}
        api_response.result = dataset_detail
        api_response.code = EAPIResponseCode.success
        return api_response.json_response()
