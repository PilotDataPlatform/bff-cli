from .helpers import *
from fastapi import Request
import time
import json
import jwt as pyjwt
import requests
from ..config import ConfigClass
from ..models.base_models import APIResponse, EAPIResponseCode

api_response = APIResponse()


def get_project_role(user_id, project_code):
    project = get_dataset_node(project_code)
    if not project:
        error_msg = customized_error_template(
            ECustomizedError.PROJECT_NOT_FOUND)
        code = EAPIResponseCode.not_found
        return error_msg, code
    project_id = project.get("id")
    role_check_result = get_user_role(user_id, project_id)
    if role_check_result:
        role = role_check_result.get("r").get('type')
        code = EAPIResponseCode.success
        return role, code
    else:
        error_msg = customized_error_template(
            ECustomizedError.USER_NOT_IN_PROJECT)
        code = EAPIResponseCode.forbidden
        return error_msg, code


async def jwt_required(request: Request):
    token = request.headers.get('Authorization')
    if token:
        token = token.replace("Bearer ", "")
    else:
        api_response.code = EAPIResponseCode.forbidden
        api_response.error_msg = "Token required"
        return api_response.json_response()
    payload = pyjwt.decode(token, verify=False)
    username: str = payload.get("preferred_username")
    exp = payload.get('exp')
    if time.time() - exp > 0:
        api_response.code = EAPIResponseCode.forbidden
        api_response.error_msg = "Token expired"
        return api_response.json_response()
    # check if user is existed in neo4j
    url = ConfigClass.NEO4J_SERVICE + "nodes/User/query"
    res = requests.post(
        url=url,
        json={"name": username}
    )
    if res.status_code != 200:
        api_response.code = EAPIResponseCode.forbidden
        api_response.error_msg = "Neo4j service: " + json.loads(res.text)
        return api_response.json_response()
    users = res.json()
    if not users:
        api_response.code = EAPIResponseCode.not_found
        api_response.error_msg = f"Neo4j service: User {username} does not exist."
        return api_response.json_response()
    user_id = users[0]['id']
    role = users[0]['role']
    if username is None:
        api_response.code = EAPIResponseCode.not_found
        api_response.error_msg = "User not found"
        return api_response.json_response()
    return {"code": 200, "user_id": user_id, "username": username, "role": role}


def check_permission(event: dict):
    """
    event = {'user_id': user_id,
             'username': username,
             'role': role,
             'project_code': project_code,
             'zone': zone}
    """
    user_id = event.get('user_id')
    username = event.get('username')
    role = event.get('role')
    project_code = event.get('project_code')
    zone = event.get('zone')
    project_role, code = get_project_role(user_id, project_code)
    if role == "admin" and code != EAPIResponseCode.not_found:
        project_role = 'admin'
        permission = {'project_role': project_role}
    elif project_role == 'User not in the project':
        permission = {'error_msg': customized_error_template(ECustomizedError.PERMISSION_DENIED),
                      'code': code,
                      'result': project_role}
        return permission
    elif code == EAPIResponseCode.not_found:
        permission = {'error_msg': customized_error_template(ECustomizedError.PROJECT_NOT_FOUND),
                      'code': code,
                      'result': {}}
        return permission
    else:
        permission = {'project_role': project_role}
    if project_role != 'admin' and zone.lower() == 'greenroom':
        permission['project_code'] = project_code
        permission['uploader'] = username
    elif project_role != 'contributor' and zone.lower() == 'vrecore':
        permission['project_code'] = project_code
    elif project_role == 'admin':
        permission['project_code'] = project_code
    else:
        permission = {'error_msg': customized_error_template(ECustomizedError.PERMISSION_DENIED),
                      'code': EAPIResponseCode.forbidden,
                      'result': {}}
        return permission
    return permission


def void_check_file_in_zone(data, file, project_code):
    payload = {"type": data.type,
               "zone": data.zone,
               "file_relative_path": file.get('resumable_relative_path') + '/' +
                                     file.get('resumable_filename'),
               "project_code": project_code
               }
    try:
        result = requests.get(ConfigClass.FILEINFO_HOST + f'/v1/project/{project_code}/file/exist/', params=payload)
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
    if zone == "vrecore":
        # url = "http://127.0.0.1:5079" + "/v1/files/jobs"
        url = ConfigClass.UPLOAD_VRE + "/v1/files/jobs"
    else:
        url = ConfigClass.UPLOAD_GREENROOM + "/v1/files/jobs"
    return url


def validate_upload_event(zone, data_type=None):
    if zone not in ["vrecore", "greenroom"]:
        error_msg = "Invalid Zone"
        return error_msg
    if data_type and data_type not in ["raw", "processed"]:
        error_msg = "Invalid Type"
        return error_msg


def transfer_to_pre(data, project_code, session_id):
    try:
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
        result = requests.post(url, headers=headers, json=payload)
        return result
    except Exception as e:
        api_response.error_msg = f"Upload service  error: {e}"
        api_response.code = EAPIResponseCode.forbidden
        return api_response.json_response()
