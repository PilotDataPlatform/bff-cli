from fastapi import APIRouter, Depends
from fastapi_utils.cbv import cbv
from ...models.manifest_models import *
from ...commons.logger_services.logger_factory_service import SrvLoggerFactory
from ...resources.error_handler import catch_internal
from ...auth import jwt_required
from ...resources.helpers import *
from sqlalchemy.orm import Session
from ...resources. error_handler import customized_error_template, ECustomizedError

router = APIRouter()


@cbv(router)
class APIManifest:
    _API_TAG = 'v1/manifest'
    _API_NAMESPACE = "api_manifest"

    def __init__(self):
        self._logger = SrvLoggerFactory(self._API_NAMESPACE).get_logger()

    @router.get("/manifest", tags=[_API_TAG],
                response_model=ManifestListResponse,
                summary="Get manifest list by project code (project_code required)")
    @catch_internal(_API_NAMESPACE)
    async def list_manifest(self, project_code: str,
                            db: Session = Depends(get_db),
                            current_identity: dict = Depends(jwt_required)):
        api_response = ManifestListResponse()
        try:
            _username = current_identity['username']
        except (AttributeError, TypeError):
            return current_identity
        mani_project_event = {"project_code": project_code, 'session': db}
        manifests = get_manifest_name_from_project_in_db(mani_project_event)
        manifest_list = []
        for manifest in manifests:
            mani_project_event['manifest'] = manifest
            attr = get_attributes_in_manifest_in_db(manifest)
            single_manifest = {'manifest_name': manifest['name'],
                               'id': manifest['id'],
                               'attributes': attr}
            manifest_list.append(single_manifest)
        api_response.result = manifest_list
        api_response.code = EAPIResponseCode.success
        return api_response.json_response()

    @router.post("/manifest/attach", tags=[_API_TAG],
                 response_model=ManifestAttachResponse,
                 summary="Attach manifest to file")
    @catch_internal(_API_NAMESPACE)
    async def attach_manifest(self, request_payload: ManifestAttachPost,
                              db: Session = Depends(get_db),
                              current_identity: dict = Depends(jwt_required)):
        """CLI will call manifest validation API before attach manifest to file in uploading process"""
        api_response = ManifestListResponse()
        try:
            _username = current_identity['username']
        except (AttributeError, TypeError):
            return current_identity
        manifests = request_payload.manifest_json
        manifest_name = manifests["manifest_name"]
        file_path = manifests["file_path"]
        project_code = manifests['project_code']
        attributes = manifests.get("attributes", {})
        mani_project_event = {"project_code": project_code, "manifest_name": manifest_name, "session": db}
        manifest_info = get_manifest_name_from_project_in_db(mani_project_event)
        manifest_id = manifest_info.get('id')
        response = attach_manifest_to_file(file_path, manifest_id, attributes)
        if not response:
            result = customized_error_template(ECustomizedError.FILE_NOT_FOUND)
            res_code = EAPIResponseCode.bad_request
        else:
            result = response
            res_code = EAPIResponseCode.success
        api_response.result = result
        api_response.code = res_code
        return api_response.json_response()

    @router.post("/manifest/validate", tags=[_API_TAG],
                 response_model=ManifestValidateResponse,
                 summary="Validate manifest for project")
    @catch_internal(_API_NAMESPACE)
    async def validate_manifest(self, request_payload: ManifestValidatePost,
                                db: Session = Depends(get_db)):
        """Validate the manifest based on the project"""
        api_response = ManifestListResponse()
        manifests = request_payload.manifest_json
        manifest_name = manifests["manifest_name"]
        project_code = manifests['project_code']
        attributes = manifests.get("attributes", {})
        validation_event = {"project_code": project_code,
                            "manifest_name": manifest_name,
                            "attributes": attributes,
                            "session": db}
        manifest_info = get_manifest_name_from_project_in_db(validation_event)
        if not manifest_info:
            api_response.result = customized_error_template(ECustomizedError.MANIFEST_NOT_FOUND)
            api_response.code = EAPIResponseCode.not_found
            return api_response.json_response()
        validation_event["manifest"] = manifest_info
        attribute_validation_error_msg = has_valid_attributes(validation_event)
        if attribute_validation_error_msg:
            api_response.result = attribute_validation_error_msg
            api_response.code = EAPIResponseCode.bad_request
            return api_response.json_response()
        api_response.code = EAPIResponseCode.success
        api_response.result = 'Valid'
        return api_response.json_response()
