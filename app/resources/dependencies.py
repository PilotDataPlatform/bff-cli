from .helpers import *
from fastapi import Request
import time
import json
import jwt as pyjwt
import requests
from ..config import ConfigClass
from ..models.base_models import APIResponse, EAPIResponseCode


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
        code = EAPIResponseCode.not_found
        return error_msg, code


async def jwt_required(request: Request):
    api_response = APIResponse()
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
