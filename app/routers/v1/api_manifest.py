from fastapi import APIRouter, Depends
from fastapi_utils.cbv import cbv
from ...models.base_models import EAPIResponseCode
from ...models.manifest_models import ManifestListResponse
from ...commons.logger_services.logger_factory_service import SrvLoggerFactory
from ...resources.error_handler import catch_internal
from ...auth import jwt_required
from ...resources.helpers import get_db, get_manifest_from_project, get_attributes_in_manifest
from sqlalchemy.orm import Session

router = APIRouter()


@cbv(router)
class APIManifestList:
    _API_TAG = 'v1/manifest'
    _API_NAMESPACE = "api_manifest"

    def __init__(self):
        self._logger = SrvLoggerFactory(self._API_NAMESPACE).get_logger()

    @router.get("/manifest", tags=[_API_TAG],
                response_model=ManifestListResponse,
                summary="Get manifest list by project code")
    @catch_internal(_API_NAMESPACE)
    async def list_manifest(self, project_code: str,
                            db: Session = Depends(get_db),
                            current_identity: dict = Depends(jwt_required)):
        api_response = ManifestListResponse()
        try:
            username = current_identity['username']
        except (AttributeError, TypeError):
            return current_identity
        manifests = get_manifest_from_project(project_code, db)
        manifest_list = {}
        for manifest in manifests:
            attr = get_attributes_in_manifest(manifest, db)
            manifest_list[manifest['name']] = attr
        api_response.result = manifest_list
        api_response.code = EAPIResponseCode.success
        return api_response.json_response()
