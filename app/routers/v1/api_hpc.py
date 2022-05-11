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
from fastapi_utils.cbv import cbv

from ...models.error_model import HPCError
from ...models.hpc_models import HPCAuthPost
from ...models.hpc_models import HPCAuthResponse
from ...models.hpc_models import HPCJobInfoResponse
from ...models.hpc_models import HPCJobResponse
from ...models.hpc_models import HPCJobSubmitPost
from ...models.hpc_models import HPCNodeInfoResponse
from ...models.hpc_models import HPCNodesResponse
from ...models.hpc_models import HPCPartitionInfoResponse
from ...models.hpc_models import HPCPartitonsResponse
from ...resources.error_handler import EAPIResponseCode
from ...resources.error_handler import catch_internal
from ...resources.hpc import get_hpc_job_info
from ...resources.hpc import get_hpc_jwt_token
from ...resources.hpc import get_hpc_node_by_name
from ...resources.hpc import get_hpc_nodes
from ...resources.hpc import get_hpc_partition_name
from ...resources.hpc import get_hpc_partitions
from ...resources.hpc import submit_hpc_job

router = APIRouter()
_API_TAG = 'V1 HPC'
_API_NAMESPACE = 'api_hpc'


@cbv(router)
class APIProject:
    def __init__(self):
        self._logger = LoggerFactory(_API_NAMESPACE).get_logger()

    @router.post(
        '/hpc/auth',
        tags=[_API_TAG],
        response_model=HPCAuthResponse,
        summary='HPC authentication')
    @catch_internal(_API_NAMESPACE)
    async def hpc_auth(self, request_payload: HPCAuthPost):
        """post HPC token for authorization."""
        self._logger.info('API hpc_auth'.center(80, '-'))
        api_response = HPCAuthResponse()
        try:
            token_issuer = request_payload.token_issuer
            username = request_payload.username
            password = request_payload.password
            token = await get_hpc_jwt_token(token_issuer, username, password)
            if token:
                error = ''
                code = EAPIResponseCode.success
                result = token
            else:
                raise AttributeError('Cannot authorized HPC')
        except AttributeError as e:
            result = []
            error_msg = str(e)
            self._logger.info(f'ERROR GETTING HPC TOKEN: {error_msg}')
            if 'open_session' in error_msg:
                error = 'Cannot authorized HPC'
            else:
                error = f'Cannot authorized HPC: {error_msg}'
            code = EAPIResponseCode.internal_error
        api_response.result = result
        api_response.error_msg = error
        api_response.code = code
        return api_response.json_response()

    @router.post(
        '/hpc/job',
        tags=[_API_TAG],
        response_model=HPCJobResponse,
        summary='HPC job submission')
    @catch_internal(_API_NAMESPACE)
    async def hpc_submit_job(self, request_payload: HPCJobSubmitPost):
        """Submit a job to hpc."""
        self._logger.info('API hpc_job'.center(80, '-'))
        api_response = HPCJobResponse()
        result = {}
        try:
            self._logger.info(f'SUBMITTING JOB: {request_payload}')
            self._logger.info(f'SUBMITTING JOB: {type(request_payload)}')
            response = await submit_hpc_job(request_payload)
            if response:
                error_msg = ''
                result = response
                code = EAPIResponseCode.success
        except HPCError as e:
            self._logger.error(f'HPC ERROR: {e}')
            code = e.code
            error_msg = e.error_msg
            self._logger.info(f'ERROR SUBMITTING HPC JOB: {error_msg}')
        except Exception as e:
            code = EAPIResponseCode.internal_error
            error_msg = str(e)
            self._logger.error(f'ERROR SUBMITTING HPC JOB: {error_msg}')
        api_response.result = result
        api_response.error_msg = error_msg
        api_response.code = code
        return api_response.json_response()

    @router.get('/hpc/job/{job_id}', tags=[_API_TAG],
                response_model=HPCJobInfoResponse,
                summary='Get HPC job information')
    @catch_internal(_API_NAMESPACE)
    async def hpc_get_job(self, job_id, host, username, token):
        """Get HPC job information."""
        self._logger.info('API hpc_get_job'.center(80, '-'))
        api_response = HPCJobInfoResponse()
        result = {}
        try:
            information = await get_hpc_job_info(job_id, host, username, token)
            if information:
                error = ''
                code = EAPIResponseCode.success
                result = information
            else:
                self._logger.info(f'ERROR GETTING HPC job: {information}')
                raise HPCError('Cannot get HPC job information')
        except HPCError as job_error:
            self._logger.info(f'ERROR GETTING HPC job: {job_error}')
            code = job_error.code
            error = job_error.error_msg
        except Exception as e:
            self._logger.info(f'ERROR GETTING HPC job: {e}')
            code = EAPIResponseCode.internal_error
            error = e
        self._logger.info(
            f"RESPONSE: 'code': {code}, \
                'result': {result}, 'error_msg': {error}")
        api_response.result = result
        api_response.error_msg = error
        api_response.code = code
        return api_response.json_response()

    @router.get('/hpc/nodes', tags=[_API_TAG],
                response_model=HPCNodesResponse,
                summary='Get HPC nodes')
    @catch_internal(_API_NAMESPACE)
    async def hpc_get_nodes(self, host, username, token):
        """Get HPC job information."""
        self._logger.info('API hpc_get_nodes'.center(80, '-'))
        api_response = HPCNodesResponse()
        result = {}
        try:
            information = await get_hpc_nodes(host, username, token)
            if information:
                error = ''
                code = EAPIResponseCode.success
                result = information
            else:
                self._logger.info(f'ERROR GETTING HPC nodes: {information}')
                raise HPCError('Cannot get HPC nodes')
        except HPCError as job_error:
            self._logger.info(f'ERROR GETTING HPC nodes: {job_error}')
            code = job_error.code
            error = job_error.error_msg
        except Exception as e:
            self._logger.info(f'ERROR GETTING HPC nodes: {e}')
            code = EAPIResponseCode.internal_error
            error = e
        self._logger.info(
            f"RESPONSE: 'code': {code}, \
                'result': {result}, 'error_msg': {error}")
        api_response.result = result
        api_response.error_msg = error
        api_response.code = code
        return api_response.json_response()

    @router.get('/hpc/nodes/{node_name}', tags=[_API_TAG],
                response_model=HPCNodeInfoResponse,
                summary='Get HPC node information')
    @catch_internal(_API_NAMESPACE)
    async def hpc_get_node_info(self, node_name, host, username, token):
        """Get HPC node information."""
        self._logger.info('API hpc_get_node_info'.center(80, '-'))
        api_response = HPCNodeInfoResponse()
        result = {}
        try:
            information = await get_hpc_node_by_name(
                host, username, token, node_name)
            if information:
                error = ''
                code = EAPIResponseCode.success
                result = information
            else:
                self._logger.info(
                    f'ERROR GETTING HPC node {node_name}: {information}')
                raise HPCError('Cannot get HPC nodes information')
        except HPCError as job_error:
            self._logger.info(f'ERROR GETTING HPC nodes: {job_error}')
            code = job_error.code
            error = job_error.error_msg
        except Exception as e:
            self._logger.info(f'ERROR GETTING HPC nodes: {e}')
            code = EAPIResponseCode.internal_error
            error = e
        self._logger.info(
            f"RESPONSE: 'code': {code}, \
                'result': {result}, 'error_msg': {error}")
        api_response.result = result
        api_response.error_msg = error
        api_response.code = code
        return api_response.json_response()

    @router.get('/hpc/partitions', tags=[_API_TAG],
                response_model=HPCPartitonsResponse,
                summary='Get HPC partitions')
    @catch_internal(_API_NAMESPACE)
    async def hpc_list_partitions(self, host, username, token):
        """Get HPC partitions information."""
        self._logger.info('API hpc_list_partitions'.center(80, '-'))
        api_response = HPCPartitonsResponse()
        result = {}
        try:
            information = await get_hpc_partitions(host, username, token)
            if information:
                error = ''
                code = EAPIResponseCode.success
                result = information
            else:
                self._logger.info(
                    f'ERROR GETTING HPC partitions: {information}')
                raise HPCError('Cannot get HPC partitions')
        except HPCError as job_error:
            self._logger.info(f'ERROR GETTING HPC partitions: {job_error}')
            code = job_error.code
            error = job_error.error_msg
        except Exception as e:
            self._logger.info(f'ERROR GETTING HPC partitions: {e}')
            code = EAPIResponseCode.internal_error
            error = e
        self._logger.info(
            f"RESPONSE: 'code': {code}, \
                'result': {result}, 'error_msg': {error}")
        api_response.result = result
        api_response.error_msg = error
        api_response.code = code
        return api_response.json_response()

    @router.get('/hpc/partitions/{partition_name}', tags=[_API_TAG],
                response_model=HPCPartitionInfoResponse,
                summary='Get HPC partition info')
    @catch_internal(_API_NAMESPACE)
    async def hpc_get_partition_info(
        self,
        partition_name,
        host,
        username,
        token
    ):
        """Get HPC information of a partition."""
        self._logger.info('API hpc_get_partition_info'.center(80, '-'))
        api_response = HPCPartitionInfoResponse()
        result = {}
        try:
            information = await get_hpc_partition_name(
                host, username, token, partition_name)
            if information:
                error = ''
                code = EAPIResponseCode.success
                result = information
            else:
                self._logger.info(
                    f'ERROR GETTING HPC partition: {information}')
                raise HPCError(f'Cannot get HPC partition: {partition_name}')
        except HPCError as job_error:
            self._logger.info(f'ERROR GETTING HPC partition: {job_error}')
            code = job_error.code
            error = job_error.error_msg
        except Exception as e:
            self._logger.info(f'ERROR GETTING HPC partitions: {e}')
            code = EAPIResponseCode.internal_error
            error = e
        self._logger.info(
            f"RESPONSE: 'code': {code}, \
                'result': {result}, 'error_msg': {error}")
        api_response.result = result
        api_response.error_msg = error
        api_response.code = code
        return api_response.json_response()
