from fastapi import APIRouter, Depends
from fastapi_utils.cbv import cbv
from ...models.hpc_models import HPCAuthResponse
from ...commons.logger_services.logger_factory_service import SrvLoggerFactory
from ...resources.error_handler import catch_internal
from ...resources.dependencies import *
from ...resources.helpers import *
from fastapi.security import HTTPBasicCredentials, HTTPBearer

router = APIRouter()
_API_TAG = 'V1 HPC'
_API_NAMESPACE = "api_hpc"


@cbv(router)
class APIProject:
    security = HTTPBearer()
    
    def __init__(self):
        self._logger = SrvLoggerFactory(_API_NAMESPACE).get_logger()

    @router.get("/hpc/auth", tags=[_API_TAG],
                response_model=HPCAuthResponse,
                summary="Get HPC authorization")
    @catch_internal(_API_NAMESPACE)
    async def hpc_auth(self, token_issuer, password, credentials: HTTPBasicCredentials = Depends(security)):
        '''
        Get HPC token for authorization
        '''
        self._logger.info("API hpc_auth".center(80, '-'))
        api_response = HPCAuthResponse()
        try:
            token = credentials.credentials
            token = get_hpc_jwt_token(token_issuer, token, password)
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
