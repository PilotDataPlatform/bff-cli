from fastapi import APIRouter, Depends
from fastapi_utils.cbv import cbv
from ...models.base_models import EAPIResponseCode
from ...models.manifest_models import ManifestListParams, ManifestListResponse, ManifestAttachPost
from ...commons.logger_services.logger_factory_service import SrvLoggerFactory
from ...resources.error_handler import catch_internal
from ...auth import jwt_required
from ...resources.helpers import *
from sqlalchemy.orm import Session

router = APIRouter()


@cbv(router)
class APIManifest:
    _API_TAG = 'v1/manifest'
    _API_NAMESPACE = "api_manifest"

    def __init__(self):
        self._logger = SrvLoggerFactory(self._API_NAMESPACE).get_logger()

    @router.get("/manifest", tags=[_API_TAG],
                response_model=ManifestListResponse,
                summary="Get manifest list by project code")
    @catch_internal(_API_NAMESPACE)
    async def list_manifest(self, request_params: ManifestListParams,
                            db: Session = Depends(get_db),
                            current_identity: dict = Depends(jwt_required)):
        api_response = ManifestListResponse()
        project_code = request_params.project_code
        try:
            username = current_identity['username']
        except (AttributeError, TypeError):
            return current_identity
        manifests = get_manifest_from_project(project_code, db)
        manifest_list = []
        for manifest in manifests:
            attr = get_attributes_in_manifest(manifest, db)
            single_manifest = {'manifest_name': manifest['name'],
                               'id': manifest['id'],
                               'attributes': attr}
            manifest_list.append(single_manifest)
        api_response.result = manifest_list
        api_response.code = EAPIResponseCode.success
        return api_response.json_response()

    @router.post("/manifest/attach", tags=[_API_TAG+'/attach'],
                 response_model=ManifestListResponse,
                 summary="Attach manifest to file")
    @catch_internal(_API_NAMESPACE)
    async def attach_manifest(self, request_payload: ManifestAttachPost,
                              db: Session = Depends(get_db),
                              current_identity: dict = Depends(jwt_required)):
        """CLI will call manifest validation API before attach manifest to file in uploading process"""
        api_response = ManifestListResponse()
        try:
            _ = current_identity['username']
        except (AttributeError, TypeError):
            return current_identity
        manifests = request_payload.manifest_json
        manifest_name = manifests["manifest_name"]
        file_path = manifests["file_path"]
        project_code = manifests['project_code']
        attributes = manifests.get("attributes", {})

        manifest_info = get_manifest_from_project(project_code, db, manifest_name)
        manifest_id = manifest_info.get('id')
        response = attach_manifest_to_file(file_path, manifest_id, attributes)
        if not response:
            result = "File not found"
            res_code = EAPIResponseCode.bad_request
        else:
            result = response
            res_code = EAPIResponseCode.success
        api_response.result = result
        api_response.code = res_code
        return api_response.json_response()

