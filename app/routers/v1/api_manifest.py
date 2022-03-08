from fastapi import APIRouter, Depends
from fastapi_utils.cbv import cbv
from ...models.manifest_models import *
from ...resources.error_handler import catch_internal
from ...resources.dependencies import jwt_required, has_permission, get_project_role
from ...resources.helpers import *
from ...resources.database_service import RDConnection
from ...resources. error_handler import customized_error_template, ECustomizedError
from logger import LoggerFactory

router = APIRouter()
_API_TAG = 'V1 manifest'
_API_NAMESPACE = "api_manifest"

@cbv(router)
class APIManifest:
    _API_TAG = 'V1 Manifest'
    _API_NAMESPACE = "api_manifest"

    def __init__(self):
        self._logger = LoggerFactory(self._API_NAMESPACE).get_logger()
        self.db = RDConnection()

    @router.get("/manifest", tags=[_API_TAG],
                response_model=ManifestListResponse,
                summary="Get manifest list by project code (project_code required)")
    @catch_internal(_API_NAMESPACE)
    async def list_manifest(self, project_code: str, current_identity: dict = Depends(jwt_required)):
        api_response = ManifestListResponse()
        try:
            _username = current_identity['username']
            _user_role = current_identity['role']
            _user_id = current_identity["user_id"]
        except (AttributeError, TypeError):
            return current_identity
        self._logger.info("API list_manifest".center(80, '-'))
        self._logger.info(f"User request with identity: {current_identity}")
        self._logger.info(f"User request information: project_code: {project_code},")
        try:
            zone = ConfigClass.GREEN_ZONE_LABEL
            if not has_permission(current_identity, project_code, "file_attribute_template", zone.lower(), "view"):
                api_response.error_msg = "Permission denied"
                api_response.code = EAPIResponseCode.forbidden
                return api_response.json_response()
            mani_project_event = {"project_code": project_code}
            self._logger.info("Getiting project manifests")
            manifests = self.db.get_manifest_name_from_project_in_db(mani_project_event)
            self._logger.info(f"Manifest in project check result: {manifests}")
            self._logger.info("Getting attributes for manifests")
            manifest_list = self.db.get_attributes_in_manifest_in_db(manifests)
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
    async def attach_manifest(self, request_payload: ManifestAttachPost,
                              current_identity: dict = Depends(jwt_required)):
        """CLI will call manifest validation API before attach manifest to file in uploading process"""
        api_response = ManifestAttachResponse()
        try:
            _username = current_identity['username']
            _user_id = current_identity["user_id"]
            _user_role = current_identity['role']
        except (AttributeError, TypeError):
            return current_identity
        self._logger.info("API attach_manifest".center(80, '-'))
        self._logger.info(f"User request with identity: {current_identity}")
        self._logger.info(f"Received payload: {request_payload}")
        try:
            manifests = request_payload.manifest_json
            manifest_name = manifests["manifest_name"]
            project_code = manifests['project_code']
            file_name = manifests['file_name']
            zone = manifests['zone']
            if not has_permission(current_identity, project_code, "file_attribute_template", zone, "attach"):
                api_response.error_msg = "Permission denied"
                api_response.code = EAPIResponseCode.forbidden
                return api_response.json_response()
            project_role = get_project_role(current_identity, project_code)
            self._logger.info(f"project_role: {project_role}")
            zone_type = get_zone(zone)
        except KeyError as e:
            self._logger.error(f"Missing information error: {str(e)}")
            api_response.error_msg = customized_error_template(ECustomizedError.MISSING_INFO) % str(e)
            api_response.code = EAPIResponseCode.bad_request
            api_response.result = str(e)
            return api_response.json_response()
        self._logger.info(f"Getting info for file: {file_name} IN {project_code}")
        file_info = {"query": {
                "name": file_name.split('/')[-1],
                "display_path": file_name,
                "archived": False,
                "project_code": project_code,
                "labels": ['File', zone_type]}}
        file_response = query_node(file_info)
        self._logger.info(f"Query result: {file_response}")
        file_node = file_response.json().get('result')
        self._logger.info(f"line 106: {file_node}")
        if not file_node:
            api_response.error_msg = customized_error_template(ECustomizedError.FILE_NOT_FOUND)
            api_response.code = EAPIResponseCode.not_found
            return api_response.json_response()
        else:
            global_entity_id = file_node[0].get('global_entity_id')
            file_owner = file_node[0].get('uploader')
        self._logger.info(f"Globale entity id for {file_name}: {global_entity_id}")
        self._logger.info(f"File {file_name} uploaded by {file_owner}")
        project_code = manifests['project_code']
        attributes = manifests.get("attributes", {})
        mani_project_event = {"project_code": project_code, "manifest_name": manifest_name}
        self._logger.info(f"Getting manifest from project event: {mani_project_event}")
        manifest_info = self.db.get_manifest_name_from_project_in_db(mani_project_event)
        self._logger.info(f"Manifest information: {manifest_info}")
        if not manifest_info:
            api_response.error_msg = customized_error_template(ECustomizedError.MANIFEST_NOT_FOUND) % manifest_name
            api_response.code = EAPIResponseCode.bad_request
            return api_response.json_response()
        else:
            manifest_info = manifest_info[0]
        manifest_id = manifest_info.get('id')
        annotation_event = {"project_code": project_code,
                            "global_entity_id": global_entity_id,
                            "manifest_id": manifest_id,
                            "attributes": attributes,
                            "username": _username,
                            "project_role": project_role}
        response = attach_manifest_to_file(annotation_event)
        self._logger.info(f"Attach manifest result: {response}")
        if not response:
            api_response.error_msg = customized_error_template(ECustomizedError.FILE_NOT_FOUND)
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
                              current_identity: dict = Depends(jwt_required)):
        """Export manifest from the project"""
        api_response = ManifestExportResponse()
        try:
            _username = current_identity['username']
            _user_role = current_identity['role']
            _user_id = current_identity["user_id"]
        except (AttributeError, TypeError):
            return current_identity
        self._logger.info("API export_manifest".center(80, '-'))
        self._logger.info(f"User request with identity: {current_identity}")
        zone = ConfigClass.GREEN_ZONE_LABEL.lower()
        # CLI user need to export/view attribute first, so that they could attach attribute 
        permission = has_permission(current_identity, project_code, "file_attribute_template", zone, "view")
        self._logger.info(f"User permission: {permission}")
        if not permission:
            api_response.error_msg = "Permission denied"
            api_response.code = EAPIResponseCode.forbidden
            return api_response.json_response()
        manifest_event = {"project_code": project_code,
                          "manifest_name": manifest_name}
        manifest = self.db.get_manifest_name_from_project_in_db(manifest_event)
        self._logger.info(f"Matched manifest in database: {manifest}")
        if not manifest:
            api_response.code = EAPIResponseCode.not_found
            api_response.error_msg = customized_error_template(ECustomizedError.MANIFEST_NOT_FOUND) % manifest_name
            return api_response.json_response()
        else:
            result = self.db.get_attributes_in_manifest_in_db(manifest)[0]
            api_response.code = EAPIResponseCode.success
            api_response.result = result
            return api_response.json_response()
