import time

import httpx
import jwt as pyjwt
from fastapi import Request
from logger import LoggerFactory

from app.resources.error_handler import APIException

from ..config import ConfigClass
from ..models.base_models import APIResponse, EAPIResponseCode
from .helpers import *

api_response = APIResponse()


_logger = LoggerFactory("Dependencies").get_logger()


async def jwt_required(request: Request):
    token = request.headers.get('Authorization')
    if token:
        token = token.replace("Bearer ", "")
    else:
        raise APIException(error_msg="Token required", status_code=EAPIResponseCode.unauthorized.value)
    payload = pyjwt.decode(token, verify=False)
    username: str = payload.get("preferred_username")
    realm_roles = payload["realm_access"]["roles"]
    exp = payload.get('exp')
    if time.time() - exp > 0:
        api_response.code = EAPIResponseCode.unauthorized
        api_response.error_msg = "Token expired"
        return api_response.json_response()

    if username is None:
        api_response.code = EAPIResponseCode.not_found
        api_response.error_msg = "User not found"
        return api_response.json_response()

    # check if user is existed in keycloak
    with httpx.Client() as client:
        payload = {
            "username": username,
        }
        res = client.get(ConfigClass.AUTH_SERVICE + "/v1/admin/user", params=payload)
    if res.status_code != 200:
        api_response.code = EAPIResponseCode.forbidden
        api_response.error_msg = "Auth Service: " + str(res.json())
        return api_response.json_response()

    user = res.json()["result"]
    if not user:
        api_response.code = EAPIResponseCode.not_found
        api_response.error_msg = f"Auth service: User {username} does not exist."
        return api_response.json_response()

    user_id = user['id']
    role = user['role']
    return {
        "code": 200,
        "user_id": user_id,
        "username": username,
        "role": role,
        "token": token,
        "realm_roles": realm_roles
    }


def get_project_role(current_identity, project_code):
    role = None
    _logger.info('get_project_role'.center(80,'='))
    _logger.info(f'Received identity: {current_identity}, project_code: {project_code}')
    if current_identity["role"] == "admin":
        role = "platform_admin"
    else:
        possible_roles = [project_code + "-" +
                          i for i in ["admin", "contributor", "collaborator"]]
        for realm_role in current_identity["realm_roles"]:
            # if this is a role for the correct project
            if realm_role in possible_roles:
                role = realm_role.replace(project_code + "-", "")
    return role


def has_permission(current_identity, project_code, resource, zone, operation):
    if current_identity["role"] == "admin":
        role = "platform_admin"
    else:
        if not project_code:
            _logger.info("No project code and not a platform admin, permission denied")
            return False
        role = get_project_role(current_identity, project_code)
        if not role:
            _logger.info("Unable to get project role in permissions check, user might not belong to project")
            return False
    try:
        payload = {
            "role": role,
            "resource": resource,
            "zone": zone,
            "operation": operation,
        }
        _logger.info(f"Permission payload: {payload}")
        with httpx.Client() as client:
            response = client.get(ConfigClass.AUTH_SERVICE + "/v1/authorize", params=payload)
        _logger.info(f"Permission response: {response.text}")
        if response.status_code != 200:
            error_msg = f"Error calling authorize API - {response.json()}"
            raise APIException(status_code=response.status_code, error_msg=error_msg)
        if response.json()["result"].get("has_permission"):
            return True
        else:
            return False
    except Exception as e:
        error_msg = str(e)
        _logger.info(f"Exception on authorize call: {error_msg}")
        raise APIException(status_code=EAPIResponseCode.internal_error, error_msg=error_msg)


def void_check_file_in_zone(data, file, project_code):
    payload = {"type": data.type,
               "zone": data.zone,
               "file_relative_path": file.get('resumable_relative_path') + '/' +
                                     file.get('resumable_filename'),
               "project_code": project_code
               }
    try:
        with httpx.Client() as client:
            result = client.get(ConfigClass.FILEINFO_HOST + f'/v1/project/{project_code}/file/exist/', params=payload)
        result = result.json()
    except Exception as e:
        api_response.error_msg = f"EntityInfo service  error: {e}"
        api_response.code = EAPIResponseCode.forbidden
        return api_response.json_response()
    if result['code'] in [404, 200]:
        api_response.error_msg = "debug finding file"
        api_response.code = EAPIResponseCode.bad_request
        api_response.result = result
        return api_response.json_response()
    else:
        api_response.error_msg = "File with that name already exists"
        api_response.code = EAPIResponseCode.conflict
        api_response.result = data
        return api_response.json_response()


def select_url_by_zone(zone):
    if zone == ConfigClass.CORE_ZONE_LABEL.lower():
        url = ConfigClass.DATA_UPLOAD_SERVICE_CORE + "/v1/files/jobs"
    else:
        url = ConfigClass.DATA_UPLOAD_SERVICE_GREENROOM + "/v1/files/jobs"
    return url


def validate_upload_event(zone, data_type=None):
    if zone not in [ConfigClass.CORE_ZONE_LABEL.lower(), ConfigClass.GREEN_ZONE_LABEL.lower()]:
        error_msg = "Invalid Zone"
        return error_msg
    if data_type and data_type not in ["raw", "processed"]:
        error_msg = "Invalid Type"
        return error_msg


def transfer_to_pre(data, project_code, session_id):
    try:
        _logger.info("transfer_to_pre".center(80, '-'))
        payload = {
            "current_folder_node": data.current_folder_node,
            "project_code": project_code,
            "operator": data.operator,
            "upload_message": data.upload_message,
            "data": data.data,
            "job_type": data.job_type
        }
        headers = {
            "Session-ID": session_id
        }
        url = select_url_by_zone(data.zone)
        _logger.info(f'url: {url}')
        _logger.info(f'payload: {payload}')
        with httpx.Client() as client:
            result = client.post(url, headers=headers, json=payload)
        return result
    except Exception as e:
        api_response.error_msg = f"Upload service  error: {e}"
        api_response.code = EAPIResponseCode.forbidden
        return api_response.json_response()
