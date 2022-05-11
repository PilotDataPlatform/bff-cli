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

import httpx
from common import LoggerFactory
from fastapi import APIRouter
from fastapi import Depends
from fastapi.security import HTTPBasicCredentials
from fastapi.security import HTTPBearer
from fastapi_utils.cbv import cbv

from ...config import ConfigClass
from ...models.kg_models import KGImportPost
from ...models.kg_models import KGResponseModel
from ...resources.dependencies import jwt_required
from ...resources.error_handler import catch_internal

router = APIRouter()
_API_TAG = 'V1 KG'
_API_NAMESPACE = 'api_kg'


@cbv(router)
class APIProject:
    current_identity: dict = Depends(jwt_required)
    security = HTTPBearer()

    def __init__(self):
        self._logger = LoggerFactory(_API_NAMESPACE).get_logger()

    @router.post(
        '/kg/resources',
        tags=[_API_TAG],
        response_model=KGResponseModel,
        summary='Import kg_resources')
    @catch_internal(_API_NAMESPACE)
    async def kg_import(
        self,
        request_payload: KGImportPost,
        credentials: HTTPBasicCredentials = Depends(security)
    ):
        """Import kg_resource."""
        self._logger.info('API KG IMPORT'.center(80, '-'))
        url = ConfigClass.KG_SERVICE + '/v1/resources'
        self._logger.info(f'Requesting url: {url}')
        payload = {
            'data': request_payload.data
        }
        token = credentials.credentials
        headers = {'Authorization': 'Bearer ' + token}
        self._logger.info(f'Request payload: {payload}')
        self._logger.info(f'Request headers: {headers}')
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers)
        self._logger.info(f'Response: {response.text}')
        content = response.json()
        self._logger.info(f'Response content: {content}')
        return content
