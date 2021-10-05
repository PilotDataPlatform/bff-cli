from logging import error
from app.models.error_model import InvalidEncryptionError
from fastapi import APIRouter, Depends
from fastapi_utils.cbv import cbv
from ...commons.logger_services.logger_factory_service import SrvLoggerFactory
from ...commons.data_providers.database import DBConnection
from ...resources.error_handler import catch_internal
from ...resources.helpers import *
from ...resources.validation_service import ManifestValidator, decryption
from ...resources.database_service import RDConnection
from ...models.validation_models import *
import re

router = APIRouter()


@cbv(router)
class APIValidation:
    _API_TAG = 'V1 Validate'
    _API_NAMESPACE = "api_validation"

    def __init__(self):
        self._logger = SrvLoggerFactory(self._API_NAMESPACE).get_logger()
        self.db = RDConnection()

    @router.post("/validate/gid", tags=[_API_TAG],
                 response_model=ValidateGenerateIDResponse,
                 summary="Validate GENERATE ID")
    @catch_internal(_API_NAMESPACE)
    async def validate_generate_id(self, request_payload: ValidateGenerateIDPOST):
        api_response = ValidateGenerateIDResponse()
        generate_id = request_payload.generate_id
        is_valid = re.match("^([A-Z]{3})-([0-9]{4})$", generate_id)
        if is_valid:
            result = "Valid"
            res_code = EAPIResponseCode.success
        else:
            result = customized_error_template(ECustomizedError.INVALID_GENERATE_ID)
            res_code = EAPIResponseCode.bad_request
        api_response.result = result
        api_response.code = res_code
        return api_response.json_response()

    @router.post("/validate/manifest", tags=[_API_TAG],
                 response_model=ManifestValidateResponse,
                 summary="Validate manifest for project")
    @catch_internal(_API_NAMESPACE)
    async def validate_manifest(self, request_payload: ManifestValidatePost):
        """Validate the manifest based on the project"""
        self._logger.info("API validate_manifest".center(80, '-'))
        api_response = ManifestValidateResponse()
        manifests = request_payload.manifest_json
        manifest_name = manifests["manifest_name"]
        project_code = manifests['project_code']
        attributes = manifests.get("attributes", {})
        validation_event = {"project_code": project_code,
                            "manifest_name": manifest_name,
                            "attributes": attributes}
        self._logger.info(f"Validation event: {validation_event}")                    
        manifest_info = self.db.get_manifest_name_from_project_in_db(validation_event)
        if not manifest_info:
            api_response.result = customized_error_template(ECustomizedError.MANIFEST_NOT_FOUND) % manifest_name
            api_response.code = EAPIResponseCode.not_found
            return api_response.json_response()
        validation_event["manifest"] = manifest_info
        validator = ManifestValidator()
        attribute_validation_error_msg = validator.has_valid_attributes(validation_event)
        if attribute_validation_error_msg:
            api_response.result = attribute_validation_error_msg
            api_response.code = EAPIResponseCode.bad_request
            return api_response.json_response()
        api_response.code = EAPIResponseCode.success
        api_response.result = 'Valid'
        return api_response.json_response()

    @router.post("/validate/env", tags=[_API_TAG],
                 response_model=EnvValidateResponse,
                 summary="Validate env for CLI commands")
    @catch_internal(_API_NAMESPACE)
    async def validate_env(self, request_payload: EnvValidatePost):
        """Validate the environment accessible zone"""
        self._logger.info("API validate_env".center(80, '-'))
        self._logger.info(request_payload)
        api_response = EnvValidateResponse()
        encrypted_msg = request_payload.environ
        zone = request_payload.zone
        action = request_payload.action
        self._logger.info(f'msg: {encrypted_msg}')
        if zone not in ['greenroom', 'vrecore']:
            api_response.code = EAPIResponseCode.bad_request
            api_response.error_msg = customized_error_template(ECustomizedError.INVALID_ZONE)
            api_response.result = ""
            return api_response.json_response()
        restrict_zone = {
        'greenroom': {'upload': ['greenroom'], 'download': ['greenroom']},
        'vrecore': {'upload': ['greenroom', 'vrecore'], 'download': ['vrecore']}
        }
        if encrypted_msg:
            try:
                current_zone = decryption(encrypted_msg, ConfigClass.CLI_SECRET)
            except InvalidEncryptionError:
                api_response.code = EAPIResponseCode.bad_request
                api_response.error_msg = customized_error_template(ECustomizedError.INVALID_VARIABLE)
                api_response.result = ""
                return api_response.json_response()
        else:
            current_zone = 'vrecore'
        permit_action = restrict_zone.get(current_zone)
        permit_zone = permit_action.get(action)
        self._logger.info(f"Current zone: {current_zone}")
        self._logger.info(f"Accessing zone: {zone}")
        self._logger.info(f"Action: {action}")
        self._logger.info(f"permit_action: {permit_action}")
        self._logger.info(f"permit_zone: {permit_zone}")
        if zone in permit_zone:
            result = 'valid'
            error = ''
            code = EAPIResponseCode.success
        else:
            result = 'Invalid'
            attempt = "upload to" if action == "upload" else "download from"
            error = f'Invalid action: {attempt} {zone} in {current_zone}'
            code = EAPIResponseCode.forbidden
        api_response.code = code
        api_response.error_msg = error
        api_response.result = result
        return api_response.json_response()

