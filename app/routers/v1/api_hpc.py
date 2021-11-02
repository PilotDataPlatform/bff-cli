from fastapi import APIRouter, Depends
from fastapi_utils.cbv import cbv
from ...models.hpc_models import *
from ...commons.logger_services.logger_factory_service import SrvLoggerFactory
from ...resources.error_handler import catch_internal
from ...resources.dependencies import *
from ...resources.helpers import *

router = APIRouter()
_API_TAG = 'V1 HPC'
_API_NAMESPACE = "api_hpc"


@cbv(router)
class APIProject:
    
    def __init__(self):
        self._logger = SrvLoggerFactory(_API_NAMESPACE).get_logger()

    @router.get("/hpc/auth", tags=[_API_TAG],
                response_model=HPCAuthResponse,
                summary="Get HPC authorization")
    @catch_internal(_API_NAMESPACE)
    async def hpc_auth(self, token_issuer, username, password):
        '''
        Get HPC token for authorization
        '''
        self._logger.info("API hpc_auth".center(80, '-'))
        api_response = HPCAuthResponse()
        try:
        
            token = get_hpc_jwt_token(token_issuer, username, password)
            if token:
                error = ""
                code = EAPIResponseCode.success
                result = token
            else:
                raise AttributeError('Cannot authorized HPC')
        except AttributeError as e:
            result = []
            error_msg = str(e)
            self._logger.info(f"ERROR GETTING HPC TOKEN: {error_msg}")
            if 'open_session' in error_msg:
                error = f"Cannot authorized HPC"
            else:
                error = f"Cannot authorized HPC: {error_msg}"
            code = EAPIResponseCode.internal_error
        api_response.result = result
        api_response.error_msg = error
        api_response.code = code
        return api_response.json_response()

    @router.post("/hpc/job", tags=[_API_TAG],
                response_model=HPCJobInfoResponse,
                summary="HPC job submission")
    @catch_internal(_API_NAMESPACE)
    async def hpc_submit_job(self, request_payload: HPCJobSubmitPost):
        '''
        Submit a job to hpc
        '''
        self._logger.info("API hpc_job".center(80, '-'))
        api_response = HPCJobResponse()
        try:
            self._logger.info(f"SUBMITTING JOB: {request_payload}")
            self._logger.info(f"SUBMITTING JOB: {type(request_payload)}")
            response = submit_hpc_job(request_payload)
            if response:
                error_msg = ""
                result = response
                code = EAPIResponseCode.success
        except HPCError as e:
            result = []
            error_msg = str(e)
            self._logger.info(f"ERROR SUBMITTING HPC JOB: {error_msg}")
            code = EAPIResponseCode.internal_error
        api_response.result = result
        api_response.error_msg = error_msg
        api_response.code = code
        return api_response.json_response()

    @router.get("/hpc/job/{job_id}", tags=[_API_TAG],
                response_model=HPCJobInfoResponse,
                summary="Get HPC authorization")
    @catch_internal(_API_NAMESPACE)
    async def hpc_get_job(self, job_id, host, username, token):
        '''
        Get HPC job information
        '''
        self._logger.info("API hpc_get_job".center(80, '-'))
        api_response = HPCJobInfoResponse()
        try:
        
            token = get_hpc_job_info(job_id, host, username, token)
            if token:
                error = ""
                code = EAPIResponseCode.success
                result = token
            else:
                raise AttributeError('Cannot authorized HPC')
        except AttributeError as e:
            result = []
            error_msg = str(e)
            self._logger.info(f"ERROR GETTING HPC TOKEN: {error_msg}")
            if 'open_session' in error_msg:
                error = f"Cannot authorized HPC"
            else:
                error = f"Cannot authorized HPC: {error_msg}"
            code = EAPIResponseCode.internal_error
        api_response.result = result
        api_response.error_msg = error
        api_response.code = code
        return api_response.json_response()
