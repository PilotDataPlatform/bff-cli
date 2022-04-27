from fastapi import APIRouter
from fastapi import Depends
from fastapi_utils.cbv import cbv
from ...models.manifest_models import ManifestListResponse
from ...models.manifest_models import ManifestAttachResponse
from ...models.manifest_models import ManifestAttachPost
from ...models.manifest_models import ManifestExportResponse
from ...resources.error_handler import catch_internal
from ...resources.error_handler import EAPIResponseCode
from ...resources.dependencies import jwt_required
from ...resources.dependencies import get_project_role
from ...resources.dependencies import has_permission
from ...resources.helpers import get_zone
from ...resources.helpers import query_node
from ...resources.helpers import attach_manifest_to_file
from ...resources.helpers import separate_rel_path
from ...resources.database_service import RDConnection
from ...resources. error_handler import customized_error_template
from ...resources. error_handler import ECustomizedError
from logger import LoggerFactory
from sqlalchemy.ext.asyncio import AsyncSession
from app.commons.data_providers.database import DBConnection
from app.config import ConfigClass

router = APIRouter()


@cbv(router)
class APIManifest:
    _API_TAG = 'V1 Manifest'
    _API_NAMESPACE = "api_manifest"
    db_connection = DBConnection

    def __init__(self):
        self._logger = LoggerFactory(self._API_NAMESPACE).get_logger()
        self.db = RDConnection()

    @router.get(
        "/manifest", tags=[_API_TAG],
        response_model=ManifestListResponse,
        summary="Get manifest list by project code")
    @catch_internal(_API_NAMESPACE)
    async def list_manifest(
        self, project_code: str,
        current_identity: dict = Depends(jwt_required),
        db_session: AsyncSession = Depends(db_connection.get_db)):
        api_response = ManifestListResponse()
        try:
            _ = current_identity['username']
        except (AttributeError, TypeError):
            return current_identity
        self._logger.info("API list_manifest".center(80, '-'))
        self._logger.info(f"User request with identity: {current_identity}")
        self._logger.info(
            f"User request information: project_code: {project_code}"
            )
        try:
            zone = ConfigClass.GREEN_ZONE_LABEL
            permission = await has_permission(
                current_identity,
                project_code,
                "file_attribute_template",
                zone.lower(),
                "view"
                )
            if not permission:
                api_response.error_msg = "Permission denied"
                api_response.code = EAPIResponseCode.forbidden
                return api_response.json_response()
            mani_project_event = {"project_code": project_code}
            self._logger.info("Getiting project manifests")
            manifests = await self.db.get_manifest_name_from_project_db(
                mani_project_event,
                db_session
                )
            self._logger.info(f"Manifest in project check result: {manifests}")
            self._logger.info("Getting attributes for manifests")
            manifest_list = await self.db.get_attributes_in_manifest_db(
                manifests,
                db_session
                )
            api_response.result = manifest_list
            api_response.code = EAPIResponseCode.success
            return api_response.json_response()
        except Exception as e:
            self._logger.error(f'Error listing manifest: {e}')
            api_response.code = EAPIResponseCode.internal_error
            api_response.error_msg = str(e)
            return api_response.json_response()

    @router.post("/manifest/attach", tags=[_API_TAG],
                 response_model=ManifestAttachResponse,
                 summary="Attach manifest to file")
    @catch_internal(_API_NAMESPACE)
    async def attach_manifest(
        self,
        request_payload: ManifestAttachPost,
        current_identity: dict = Depends(jwt_required),
        db_session: AsyncSession = Depends(db_connection.get_db)
        ):
        """
        CLI will call manifest validation API
        before attach manifest to file after uploading process
        """
        api_response = ManifestAttachResponse()
        try:
            _ = current_identity['username']
        except (AttributeError, TypeError):
            return current_identity
        self._logger.info("API attach_manifest".center(80, '-'))
        self._logger.info(f"User request with identity: {current_identity}")
        self._logger.info(f"Received payload: {request_payload}")
        try:
            manifests = request_payload.manifest_json
            manifest_name = manifests["manifest_name"]
            project_code = manifests['project_code']
            file_path = manifests['file_name']
            zone = manifests['zone']
            permission = await has_permission(
                current_identity,
                project_code,
                "file_attribute_template",
                zone,
                "attach"
                )
            if not permission:
                api_response.error_msg = "Permission denied"
                api_response.code = EAPIResponseCode.forbidden
                return api_response.json_response()
            project_role = get_project_role(
                current_identity,
                project_code
                )
            self._logger.info(f"project_role: {project_role}")
            # zone_type = get_zone(zone)
        except KeyError as e:
            self._logger.error(f"Missing information error: {str(e)}")
            api_response.error_msg = customized_error_template(
                ECustomizedError.MISSING_INFO
                ) % str(e)
            api_response.code = EAPIResponseCode.bad_request
            api_response.result = str(e)
            return api_response.json_response()
        self._logger.info(
            f"Getting info for file: {file_path} IN {project_code}"
            )
        parent_path, file_name = separate_rel_path(file_path)
        file_info = {
                    'container_code': project_code,
                    'container_type': 'project',
                    'parent_path': parent_path,
                    'recursive': False,
                    'zone': get_zone(zone),
                    'archived': False,
                    'name': file_name,
                }
        file_response = await query_node(file_info)
        self._logger.info(f"Query result: {file_response}")
        file_node = file_response.json().get('result')
        self._logger.info(f"line 106: {file_node}")
        if not file_node:
            api_response.error_msg = customized_error_template(
                ECustomizedError.FILE_NOT_FOUND)
            api_response.code = EAPIResponseCode.not_found
            return api_response.json_response()
        else:
            global_entity_id = file_node[0].get('global_entity_id')
            file_owner = file_node[0].get('uploader')
            file_type = file_node[0].get('type')
        self._logger.info(
            f"Globale entity id for {file_name}: {global_entity_id}")
        self._logger.info(f"File {file_name} uploaded by {file_owner}")
        project_code = manifests['project_code']
        attributes = manifests.get("attributes", {})
        mani_project_event = {
            "project_code": project_code,
            "manifest_name": manifest_name
            }
        self._logger.info(
            f"Getting manifest from project event: {mani_project_event}")
        manifest_info = await self.db.get_manifest_name_from_project_db(
            mani_project_event,
            db_session
            )
        self._logger.info(f"Manifest information: {manifest_info}")
        if not manifest_info:
            api_response.error_msg = customized_error_template(
                ECustomizedError.MANIFEST_NOT_FOUND) % manifest_name
            api_response.code = EAPIResponseCode.bad_request
            return api_response.json_response()
        else:
            manifest_info = manifest_info[0]
        manifest_id = manifest_info.get('id')
        annotation_event = {
            "project_code": project_code,
            "global_entity_id": global_entity_id,
            "manifest_id": manifest_id,
            "attributes": attributes,
            'file_type': file_type
            }
        response = await attach_manifest_to_file(annotation_event)
        self._logger.info(f"Attach manifest result: {response}")
        if not response:
            api_response.error_msg = customized_error_template(
                ECustomizedError.FILE_NOT_FOUND)
            api_response.code = EAPIResponseCode.not_found
            return api_response.json_response()
        else:
            api_response.result = response.get('result')
            api_response.code = EAPIResponseCode.success
            return api_response.json_response()

    @router.get("/manifest/export", tags=[_API_TAG],
                response_model=ManifestExportResponse,
                summary="Export manifest from project")
    @catch_internal(_API_NAMESPACE)
    async def export_manifest(self, project_code, manifest_name,
                              current_identity: dict = Depends(jwt_required),
                              db_session: AsyncSession = Depends(db_connection.get_db)):
        """Export manifest from the project"""
        api_response = ManifestExportResponse()
        try:
            _ = current_identity['username']
        except (AttributeError, TypeError):
            return current_identity
        self._logger.info("API export_manifest".center(80, '-'))
        self._logger.info(f"User request with identity: {current_identity}")
        zone = ConfigClass.GREEN_ZONE_LABEL.lower()
        # CLI user need to export/view attribute first,
        # so that they could attach attribute
        permission = await has_permission(
            current_identity,
            project_code,
            "file_attribute_template",
            zone,
            "view")
        self._logger.info(f"User permission: {permission}")
        if not permission:
            api_response.error_msg = "Permission denied"
            api_response.code = EAPIResponseCode.forbidden
            return api_response.json_response()
        manifest_event = {"project_code": project_code,
                          "manifest_name": manifest_name}
        manifest = await self.db.get_manifest_name_from_project_db(
            manifest_event,
            db_session)
        self._logger.info(f"Matched manifest in database: {manifest}")
        if not manifest:
            api_response.code = EAPIResponseCode.not_found
            api_response.error_msg = customized_error_template(
                ECustomizedError.MANIFEST_NOT_FOUND) % manifest_name
            return api_response.json_response()
        else:
            db_result = await self.db.get_attributes_in_manifest_db(
                manifest,
                db_session)
            result = db_result[0]
            self._logger.debug(f"Attributes result {result}")
            api_response.code = EAPIResponseCode.success
            api_response.result = result
            return api_response.json_response()
