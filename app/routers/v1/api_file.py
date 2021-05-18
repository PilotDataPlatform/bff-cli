from fastapi import APIRouter, Depends
from fastapi_utils.cbv import cbv
from ...models.project_models import *
from ...commons.logger_services.logger_factory_service import SrvLoggerFactory
from ...resources.error_handler import catch_internal
from ...resources.dependencies import *
from ...resources.helpers import *


router = APIRouter()
_API_TAG = 'V1 files'
_API_NAMESPACE = "api_files"


@cbv(router)
class APIProject:
    current_identity: dict = Depends(jwt_required)

    def __init__(self):
        self._logger = SrvLoggerFactory(_API_NAMESPACE).get_logger()

    @router.get("/{project_code}/files/query", tags=[_API_TAG],
                response_model=GetProjectFolderResponse,
                summary="Get files and folders in the project/folder")
    @catch_internal(_API_NAMESPACE)
    async def get_file_folders(self, project_code, zone, folder, source_type):
        """
        Get folder in project
        """
        api_response = GetProjectFolderResponse()
        try:
            role = self.current_identity["role"]
            user_id = self.current_identity["user_id"]
            user_name = self.current_identity['username']
        except (AttributeError, TypeError):
            return self.current_identity
        if source_type == 'Folder' and not folder:
            api_response.code = EAPIResponseCode.bad_request
            api_response.error_msg = 'missing folder name'
            return api_response.json_response()
        elif source_type == 'Dataset' and folder:
            api_response.code = EAPIResponseCode.bad_request
            api_response.error_msg = 'Query project does not require folder name'
            return api_response.json_response()
        if role == "admin":
            project_role = 'admin'
        else:
            project_role, code = get_project_role(user_id, project_code)
            if project_role == 'User not in the project':
                api_response.error_msg = customized_error_template(ECustomizedError.PERMISSION_DENIED)
                api_response.code = EAPIResponseCode.forbidden
                api_response.result = project_role
                return api_response.json_response()
        zone_type = get_zone(zone)
        parent_label = get_parent_label(source_type)
        rel_path, folder_name = separate_rel_path(folder)
        if parent_label == 'Dataset':
            parent_attribute = {'code': project_code}
        else:
            parent_attribute = {'project_code': project_code,
                                'name': folder_name,
                                'folder_relative_path': rel_path}
        if project_role != 'admin' and zone_type == 'Greenroom':
            child_attribute = {'project_code': project_code,
                               'uploader': user_name}
        elif project_role != 'contributor' and zone_type == 'VRECore':
            child_attribute = {'project_code': project_code}
        else:
            api_response.code = EAPIResponseCode.forbidden
            api_response.error_msg = 'Permission Denied'
            return api_response.json_response()
        print(parent_attribute)
        zone_label = [zone_type]
        url = ConfigClass.NEO4J_SERVICE + "relations/query"
        payload = {"start_label": parent_label,
                   "start_params": parent_attribute,
                   "end_label": zone_label,
                   "end_params": child_attribute}
        print(payload)
        res = requests.post(url, json=payload)
        res = res.json()
        query_result = []
        for f in res:
            query_result.append(f.get('end_node'))
        api_response.result = query_result
        api_response.code = EAPIResponseCode.success
        return api_response.json_response()


def get_parent_label(source):
    return {
        'folder': 'Folder',
        'dataset': 'Dataset'
    }.get(source.lower(), None)


def separate_rel_path(folder_path):
    folder_layers = folder_path.strip('/').split('/')
    if len(folder_layers) > 1:
        rel_path = '/'.join(folder_layers[:-1])
        folder_name = folder_layers[-1]
    else:
        rel_path = ''
        folder_name = folder_path
    return rel_path, folder_name



