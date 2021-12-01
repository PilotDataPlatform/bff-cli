from fastapi import APIRouter, Depends
from fastapi_utils.cbv import cbv
from ...models.manifest_models import *
from ...commons.logger_services.logger_factory_service import SrvLoggerFactory
from ...commons.data_providers.database import DBConnection
from ...resources.error_handler import catch_internal
from ...resources.dependencies import jwt_required, check_permission
from ...resources.helpers import *
from ...resources.database_service import RDConnection
from ...resources. error_handler import customized_error_template, ECustomizedError
from ...service_logger.logger_factory_service import SrvLoggerFactory

router = APIRouter()


@cbv(router)
class APIManifest:
    _API_TAG = 'V1 Manifest'
    _API_NAMESPACE = "api_manifest"

    def __init__(self):
        self._logger = SrvLoggerFactory(self._API_NAMESPACE).get_logger()
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
        except (AttributeError, TypeError):
            return current_identity
        self._logger.info("API list_manifest".center(80, '-'))
        self._logger.info(f"User request with identity: {current_identity}")
        self._logger.info(f"User request information: project_code: {project_code},")
        try:
            permission_check_event = {'user_role': _user_role,
                                      'username': _username,
                                      'project_code': project_code}
            self._logger.info(f"User permission check event: {permission_check_event}")
            code, result = has_permission(permission_check_event)
            self._logger.info(f"User permission code: {code}, permission result: {result}")
            if result != 'permit':
                api_response.error_msg = result
                api_response.code = code
                return api_response.json_response()
            mani_project_event = {"project_code": project_code}
            self._logger.info("Getiting project manifests")
            manifests = self.db.get_manifest_name_from_project_in_db(mani_project_event)
            self._logger.info(f"Manifest in project check result: {manifests}")
            manifest_list = []
            self._logger.info("Getting attributes for manifests")
            for manifest in manifests:
                self._logger.info(f"Getting attributes for manifest: {manifest}")
                mani_project_event['manifest'] = manifest
                attr = self.db.get_attributes_in_manifest_in_db(mani_project_event)
                single_manifest = {'manifest_name': manifest['name'],
                                   'id': manifest['id'],
                                   'attributes': attr}
                manifest_list.append(single_manifest)
            self._logger.info(f"Returning manifest list: {manifest_list}")
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
            zone_type = get_zone(manifests['zone'])
            zone = get_zone(zone_type)
        except KeyError as e:
            self._logger.error(f"Missing information error: {str(e)}")
            api_response.error_msg = customized_error_template(ECustomizedError.MISSING_INFO) % str(e)
            api_response.code = EAPIResponseCode.bad_request
            api_response.result = str(e)
            return api_response.json_response()
        permission_event = {'user_id': _user_id,
                            'username': _username,
                            'role': _user_role,
                            'project_code': project_code,
                            'zone': zone}
        permission = check_permission(permission_event)
        self._logger.info(f"Permission check event: {permission_event}")
        self._logger.info(f"Permission check result: {permission}")
        error_msg = permission.get('error_msg', '')
        if error_msg:
            api_response.error_msg = error_msg
            api_response.code = permission.get('code')
            api_response.result = permission.get('result')
            return api_response.json_response()
        uploader = permission.get('uploader')
        project_role = permission.get('project_role')
        self._logger.info(f"Getting info for file: {file_name} IN {project_code}")
        file_node = query_file_in_project(project_code, file_name, zone)
        if not file_node:
            api_response.error_msg = customized_error_template(ECustomizedError.FILE_NOT_FOUND)
            api_response.code = EAPIResponseCode.not_found
            return api_response.json_response()
        else:
            file_node = file_node.get('result')
            global_entity_id = file_node[0].get('global_entity_id')
            file_owner = file_node[0].get('uploader')
        self._logger.info(f"Globale entity id for {file_name}: {global_entity_id}")
        self._logger.info(f"File {file_name} uploaded by {file_owner}")
        if _user_role == 'admin' or project_role == 'admin':
            pass
        elif zone == 'VRECore' and project_role == 'collaborator':
            pass
        elif zone == 'Greenroom' and file_owner == uploader:
            pass
        else:
            api_response.error_msg = customized_error_template(ECustomizedError.PERMISSION_DENIED)
            api_response.code = EAPIResponseCode.forbidden
            return api_response.json_response()
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
        except (AttributeError, TypeError):
            return current_identity
        self._logger.info("API attach_manifest".center(80, '-'))
        self._logger.info(f"User request with identity: {current_identity}")
        permission_check_event = {'user_role': _user_role,
                                  'username': _username,
                                  'project_code': project_code}
        self._logger.info(f"Permission check event: {permission_check_event}")
        code, result = has_permission(permission_check_event)
        self._logger.info(f"Permission code: {code}, permission result: {result}")
        if result != 'permit':
            api_response.error_msg = result
            api_response.code = code
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
            manifest_event['manifest'] = manifest
            attributes = self.db.get_attributes_in_manifest_in_db(manifest_event)
            result = {'manifest_name': manifest_name,
                      'project_code': project_code,
                      'attributes': attributes}
            self._logger.info(f"Returning result: {result}")
            api_response.code = EAPIResponseCode.success
            api_response.result = result
            return api_response.json_response()
