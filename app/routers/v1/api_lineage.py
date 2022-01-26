from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from fastapi_utils.cbv import cbv
from ...models.lineage_models import *
from ...commons.logger_services.logger_factory_service import SrvLoggerFactory
from ...resources.error_handler import catch_internal
from ...resources.dependencies import jwt_required
from ...config import ConfigClass
import httpx

router = APIRouter()


@cbv(router)
class APILineage:
    _API_TAG = 'V1 Lineage'
    _API_NAMESPACE = "api_lineage"

    def __init__(self):
        self._logger = SrvLoggerFactory(self._API_NAMESPACE).get_logger()

    @router.post("/lineage", tags=[_API_TAG],
                 response_model=LineageCreatePost,
                 summary="[PENDING] Create lineage for given geid")
    @catch_internal(_API_NAMESPACE)
    def create_lineage(self, request_payload: LineageCreatePost,
                             current_identity: dict = Depends(jwt_required)):
        api_response = LineageCreateResponse()
        proxy_payload = request_payload.__dict__
        with httpx.Client() as client:
            fw_response = client.post(ConfigClass.PROVENANCE_SERVICE + "/v1/lineage", json=proxy_payload)
        return JSONResponse(content=fw_response.json(), status_code=fw_response.status_code)
