from fastapi import APIRouter, Depends, Request
from fastapi_utils.cbv import cbv
from ...models.models_data_download import EDataDownloadStatus, PreDataDowanloadPOST, PreDataDowanloadResponse, GetDataDownloadStatusRespon
from ...models.base_models import APIResponse, EAPIResponseCode
from ...models.manifest_models import ManifestListResponse, ManifestListParams
from ...commons.logger_services.logger_factory_service import SrvLoggerFactory
from ...resources.error_handler import catch_internal, ECustomizedError, customized_error_template
from ...config import ConfigClass
from ...auth import jwt_required
from ...commons.data_providers.models import Base, DataManifestModel, DataAttributeModel
from ...commons.data_providers.database import SessionLocal, engine
from sqlalchemy.orm import Session

router = APIRouter()
Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@cbv(router)
class APIManifestList:
    _API_TAG = 'v1/manifest'
    _API_NAMESPACE = "api_manifest"
    current_identity: dict = Depends(jwt_required)

    def __init__(self):
        self._logger = SrvLoggerFactory(self._API_NAMESPACE).get_logger()

    @router.get("/manifest", tags=[_API_TAG],
                response_model=ManifestListResponse,
                summary="Get manifest list by project code")
    @catch_internal(_API_NAMESPACE)
    async def list_manifest(self, project_code: str, db: Session = Depends(get_db)):
        api_response = ManifestListResponse()
        jwt_status = self.current_identity
        try:
            username = jwt_status['username']
        except (AttributeError, TypeError):
            return jwt_status
        manifests = db.query(DataManifestModel.name, DataManifestModel.id).filter_by(project_code=project_code).all()
        results = []
        for manifest in manifests:
            attributes = db.query(DataAttributeModel.name,
                                  DataAttributeModel.type,
                                  DataAttributeModel.optional,
                                  DataAttributeModel.value).\
                filter_by(manifest_id=manifest[1]).\
                order_by(DataAttributeModel.id.asc()).all()
            for attr in attributes:
                result = {"name": attr[0],
                          "type": attr[1],
                          "optional": attr[2],
                          "value": attr[3]}
                results.append(result)
        api_response.result = results
        api_response.code = EAPIResponseCode.success
        return api_response.json_response()
