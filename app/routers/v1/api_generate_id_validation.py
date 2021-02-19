from fastapi import APIRouter, Depends
from fastapi_utils.cbv import cbv
from ...models.base_models import EAPIResponseCode
from ...models.validate_generate_id_models import ValidateGenerateIDPOST, ValidateGenerateIDResponse
from ...commons.logger_services.logger_factory_service import SrvLoggerFactory
from ...resources.error_handler import catch_internal
from ...auth import jwt_required
import re

router = APIRouter()


@cbv(router)
class APIManifestList:
    _API_TAG = 'vrecli/v1/validgid'
    _API_NAMESPACE = "api_generate_validate"

    def __init__(self):
        self._logger = SrvLoggerFactory(self._API_NAMESPACE).get_logger()

    @router.post("/validgid", tags=[_API_TAG],
                 response_model=ValidateGenerateIDResponse,
                 summary="Validate GENERATE ID")
    @catch_internal(_API_NAMESPACE)
    async def validate_generate_id(self, requst_payload: ValidateGenerateIDPOST):
        api_response = ValidateGenerateIDResponse()
        generate_id = requst_payload.generate_id
        is_valid = re.match("^([A-Z]{3})-([0-9]{4})$", generate_id)
        if is_valid:
            result = "Valid"
            res_code = EAPIResponseCode.success
        else:
            result = "Invalid"
            res_code = EAPIResponseCode.bad_request
        api_response.result = result
        api_response.code = res_code
        return api_response.json_response()
