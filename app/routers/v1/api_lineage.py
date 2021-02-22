from fastapi import APIRouter, Depends
from fastapi_utils.cbv import cbv
from ...models.lineage_models import *
from ...commons.logger_services.logger_factory_service import SrvLoggerFactory
from ...resources.error_handler import catch_internal
from ...auth import jwt_required
from ...resources.helpers import *
from sqlalchemy.orm import Session
from ...resources. error_handler import customized_error_template, ECustomizedError

router = APIRouter()


@cbv(router)
class APILineage:
    _API_TAG = 'v1/lineage'
    _API_NAMESPACE = "api_lineage"

    def __init__(self):
        self._logger = SrvLoggerFactory(self._API_NAMESPACE).get_logger()

    @router.post("/lineage", tags=[_API_TAG],
                 response_model=LineageCreatePost,
                 summary="[PENDING] Create lineage for given file")
    @catch_internal(_API_NAMESPACE)
    async def create_lineage(self, request_payload: LineageCreatePost,
                             current_identity: dict = Depends(jwt_required)):
        api_response = LineageCreateResponse()
        try:
            _username = current_identity['username']
        except (AttributeError, TypeError):
            return current_identity
        project_code = request_payload.project_code
        file_name = request_payload.filename
        file_path = get_file_path(project_code, file_name)
        if not file_path:
            api_response.result = customized_error_template(ECustomizedError.PROJECT_NOT_FOUND)
            api_response.code = EAPIResponseCode.success
            return api_response.json_response()
        """
        payload = {
            "inputFullPath": file_path,
            "outputFullPath": outputFullPath,
            "projectCode": project_code,
            "pipelineName": pipelineName,
            "description": description,
        }
        res = requests.post(
            url=ConfigClass.METADATA_API + '/v1/lineage',
            json=payload
        )
        if res.status_code == 200:
            _logger.info('Lineage Created: ' + inputFullPath + ':to:' + outputFullPath)
            return res.json()
        else:
            _logger.error(res.text)
            raise (Exception(res.text))
        """
        api_response.result = file_path
        api_response.code = EAPIResponseCode.success
        return api_response.json_response()
