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
from fastapi.responses import JSONResponse
from fastapi_utils.cbv import cbv

from ...config import ConfigClass
from ...models.lineage_models import LineageCreatePost
from ...resources.dependencies import jwt_required
from ...resources.error_handler import catch_internal

router = APIRouter()


@cbv(router)
class APILineage:
    _API_TAG = 'V1 Lineage'
    _API_NAMESPACE = 'api_lineage'

    def __init__(self):
        self._logger = LoggerFactory(self._API_NAMESPACE).get_logger()

    @router.post('/lineage', tags=[_API_TAG],
                 response_model=LineageCreatePost,
                 summary='[PENDING] Create lineage for given geid')
    @catch_internal(_API_NAMESPACE)
    async def create_lineage(
        self,
        request_payload: LineageCreatePost,
        current_identity: dict = Depends(jwt_required)
    ):
        self._logger.info('API Lineage'.center(80, '-'))
        proxy_payload = request_payload.__dict__
        url = ConfigClass.PROVENANCE_SERVICE + '/v1/lineage'
        self._logger.info(f'url: {url}')
        self._logger.info(f'payload: {proxy_payload}')
        async with httpx.AsyncClient() as client:
            fw_response = await client.post(
                url,
                json=proxy_payload,
                timeout=100,
                follow_redirects=True)
        return JSONResponse(
            content=fw_response.json(),
            status_code=fw_response.status_code)
