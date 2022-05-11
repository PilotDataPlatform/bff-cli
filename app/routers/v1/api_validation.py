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

import re

from common import LoggerFactory
from fastapi import APIRouter
from fastapi import Depends
from fastapi_utils.cbv import cbv
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import ConfigClass
from app.models.error_model import InvalidEncryptionError

from ...commons.data_providers.database import DBConnection
from ...models.validation_models import EnvValidatePost
from ...models.validation_models import EnvValidateResponse
from ...models.validation_models import ManifestValidatePost
from ...models.validation_models import ManifestValidateResponse
from ...models.validation_models import ValidateDICOMIDPOST
from ...models.validation_models import ValidateDICOMIDResponse
from ...resources.database_service import RDConnection
from ...resources.error_handler import EAPIResponseCode
from ...resources.error_handler import ECustomizedError
from ...resources.error_handler import catch_internal
from ...resources.error_handler import customized_error_template
from ...resources.validation_service import ManifestValidator
from ...resources.validation_service import decryption

router = APIRouter()


@cbv(router)
class APIValidation:
    _API_TAG = 'V1 Validate'
    _API_NAMESPACE = 'api_validation'
    db_connection = DBConnection

    def __init__(self):
        self._logger = LoggerFactory(self._API_NAMESPACE).get_logger()
        self.db = RDConnection()

    @router.post(
        '/validate/gid', tags=[_API_TAG],
        response_model=ValidateDICOMIDResponse,
        summary='Validate DICOM ID')
    @catch_internal(_API_NAMESPACE)
    async def validate_dicom_id(self, request_payload: ValidateDICOMIDPOST):
        api_response = ValidateDICOMIDResponse()
        dcm_id = request_payload.dcm_id
        is_valid = re.match('^([A-Z]{3})-([0-9]{4})$', dcm_id)
        if is_valid:
            result = 'Valid'
            res_code = EAPIResponseCode.success
        else:
            result = customized_error_template(
                ECustomizedError.INVALID_DICOM_ID)
            res_code = EAPIResponseCode.bad_request
        api_response.result = result
        api_response.code = res_code
        return api_response.json_response()

    @router.post(
        '/validate/manifest', tags=[_API_TAG],
        response_model=ManifestValidateResponse,
        summary='Validate manifest for project')
    @catch_internal(_API_NAMESPACE)
    async def validate_manifest(
        self,
        request_payload: ManifestValidatePost,
        db_session: AsyncSession = Depends(db_connection.get_db)
    ):
        """Validate the manifest based on the project."""
        self._logger.info('API validate_manifest'.center(80, '-'))
        self._logger.info(f'DB URI: {ConfigClass.RDS_DB_URI}')
        api_response = ManifestValidateResponse()
        manifests = request_payload.manifest_json
        manifest_name = manifests['manifest_name']
        project_code = manifests['project_code']
        attributes = manifests.get('attributes', {})
        validation_event = {'project_code': project_code,
                            'manifest_name': manifest_name,
                            'attributes': attributes}
        self._logger.info(f'Validation event: {validation_event}')
        manifest_info = await self.db.get_manifest_name_from_project_db(
            validation_event,
            db_session)
        self._logger.info(f'manifest_info: {manifest_info}')
        if not manifest_info:
            api_response.result = customized_error_template(
                ECustomizedError.MANIFEST_NOT_FOUND) % manifest_name
            api_response.code = EAPIResponseCode.not_found
            return api_response.json_response()
        validation_event['manifest'] = manifest_info
        validator = ManifestValidator()
        attribute_validation_error_msg = await validator.has_valid_attributes(
            validation_event,
            db_session)
        if attribute_validation_error_msg:
            api_response.result = attribute_validation_error_msg
            api_response.code = EAPIResponseCode.bad_request
            return api_response.json_response()
        api_response.code = EAPIResponseCode.success
        api_response.result = 'Valid'
        return api_response.json_response()

    @router.post('/validate/env', tags=[_API_TAG],
                 response_model=EnvValidateResponse,
                 summary='Validate env for CLI commands')
    @catch_internal(_API_NAMESPACE)
    async def validate_env(self, request_payload: EnvValidatePost):
        """Validate the environment accessible zone."""
        self._logger.info('API validate_env'.center(80, '-'))
        self._logger.info(request_payload)
        api_response = EnvValidateResponse()
        encrypted_msg = request_payload.environ
        zone = request_payload.zone
        action = request_payload.action
        self._logger.info(f'msg: {encrypted_msg}')
        self._logger.info(request_payload)
        valid_zones = [
            ConfigClass.GREEN_ZONE_LABEL.lower(),
            ConfigClass.CORE_ZONE_LABEL.lower()]
        if zone not in valid_zones:
            self._logger.debug(f'Invalid zone value: {zone}')
            api_response.code = EAPIResponseCode.bad_request
            api_response.error_msg = customized_error_template(
                ECustomizedError.INVALID_ZONE)
            api_response.result = 'Invalid'
            return api_response.json_response()
        greenroom = ConfigClass.GREEN_ZONE_LABEL.lower()
        core = ConfigClass.CORE_ZONE_LABEL.lower()
        restrict_zone = {
            greenroom: {'upload': [greenroom], 'download': [greenroom]},
            core: {'upload': [greenroom, core], 'download': [core]}}
        if encrypted_msg:
            try:
                current_zone = decryption(
                    encrypted_msg,
                    ConfigClass.CLI_SECRET)
            except InvalidEncryptionError as e:
                self._logger.error(f'Invalid encryption: {e}')
                api_response.code = EAPIResponseCode.bad_request
                api_response.error_msg = customized_error_template(
                    ECustomizedError.INVALID_VARIABLE)
                api_response.result = 'Invalid'
                return api_response.json_response()
        else:
            current_zone = ConfigClass.CORE_ZONE_LABEL.lower()
        permit_action = restrict_zone.get(current_zone)
        permit_zone = permit_action.get(action)
        self._logger.info(f'Current zone: {current_zone}')
        self._logger.info(f'Accessing zone: {zone}')
        self._logger.info(f'Action: {action}')
        self._logger.info(f'permit_action: {permit_action}')
        self._logger.info(f'permit_zone: {permit_zone}')
        if zone in permit_zone:
            result = 'valid'
            error = ''
            code = EAPIResponseCode.success
        else:
            result = 'Invalid'
            attempt = 'upload to' if action == 'upload' else 'download from'
            error = f'Invalid action: {attempt} {zone} in {current_zone}'
            code = EAPIResponseCode.forbidden
        api_response.code = code
        api_response.error_msg = error
        api_response.result = result
        return api_response.json_response()
