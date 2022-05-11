# Copyright (C) 2022 Indoc Research
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import time

import httpx
import jwt as pyjwt
from common import LoggerFactory
from fastapi import Request

from app.resources.error_handler import APIException
from app.resources.error_handler import ECustomizedError
from app.resources.error_handler import customized_error_template

from .helpers import get_zone
from .helpers import query_node
from ..config import ConfigClass
from ..models.base_models import APIResponse
from ..models.base_models import EAPIResponseCode

api_response = APIResponse()
_logger = LoggerFactory('Dependencies').get_logger()


async def jwt_required(request: Request):
    token = request.headers.get('Authorization')
    if token:
        token = token.replace('Bearer ', '')
    else:
        raise APIException(
            error_msg='Token required',
            status_code=EAPIResponseCode.unauthorized.value
        )
    payload = pyjwt.decode(token, verify=False)
    username: str = payload.get('preferred_username')
    realm_roles = payload['realm_access']['roles']
    exp = payload.get('exp')
    if time.time() - exp > 0:
        api_response.code = EAPIResponseCode.unauthorized
        api_response.error_msg = 'Token expired'
        return api_response.json_response()
    if username is None:
        api_response.code = EAPIResponseCode.not_found
        api_response.error_msg = 'User not found'
        return api_response.json_response()

    # check if user is existed in keycloak
    async with httpx.AsyncClient() as client:
        payload = {
            'username': username,
        }
        res = await client.get(
            ConfigClass.AUTH_SERVICE + '/v1/admin/user',
            params=payload
        )
    if res.status_code != 200:
        api_response.code = EAPIResponseCode.forbidden
        api_response.error_msg = 'Auth Service: ' + str(res.json())
        return api_response.json_response()

    user = res.json()['result']
    if not user:
        api_response.code = EAPIResponseCode.not_found
        api_response.error_msg = f'Auth service: {username} does not exist.'
        return api_response.json_response()

    user_id = user['id']
    role = user['role']
    return {
        'code': 200,
        'user_id': user_id,
        'username': username,
        'role': role,
        'token': token,
        'realm_roles': realm_roles
    }


def get_project_role(current_identity, project_code):
    role = None
    _logger.info('get_project_role'.center(80, '='))
    _logger.info(
        f'Received identity: {current_identity}, project_code: {project_code}'
    )
    if current_identity['role'] == 'admin':
        role = 'platform-admin'
    else:
        possible_roles = [
            project_code + '-' + i for i in [
                'admin', 'contributor', 'collaborator']]
        for realm_role in current_identity['realm_roles']:
            # if this is a role for the correct project
            if realm_role in possible_roles:
                role = realm_role.replace(project_code + '-', '')
    return role


async def has_permission(identity, project_code, resource, zone, operation):
    if identity['role'] == 'admin':
        role = 'platform_admin'
    else:
        if not project_code:
            _logger.info(
                'No project code and not a platform admin, permission denied')
            return False
        role = get_project_role(identity, project_code)
        if not role:
            _logger.info(
                'Unable to get project role in permissions check, \
                    user might not belong to project'
            )
            return False
    try:
        payload = {
            'role': role,
            'resource': resource,
            'zone': zone,
            'operation': operation,
        }
        async with httpx.AsyncClient() as client:
            response = await client.get(
                ConfigClass.AUTH_SERVICE + '/v1/authorize',
                params=payload
            )
        if response.status_code != 200:
            error_msg = f'Error calling authorize API - {response.json()}'
            raise APIException(
                status_code=response.status_code,
                error_msg=error_msg
            )
        if response.json()['result'].get('has_permission'):
            return True
        else:
            return False
    except Exception as e:
        error_msg = str(e)
        _logger.info(f'Exception on authorize call: {error_msg}')
        raise APIException(
            status_code=EAPIResponseCode.internal_error,
            error_msg=error_msg
        )


async def check_file_exist(zone, file, project_code):
    try:
        query = {
            'container_code': project_code,
            'container_type': 'project',
            'parent_path': file.get('resumable_relative_path'),
            'recursive': False,
            'zone': get_zone(zone),
            'archived': False,
            'type': 'file',
            'name': file.get('resumable_filename'),
        }
        response = await query_node(query)
        result = response.json()
        return result
    except Exception as e:
        api_response.error_msg = f'Getting file error: {e}'
        api_response.code = EAPIResponseCode.forbidden
        return api_response.json_response()


def select_url_by_zone(zone):
    if zone == ConfigClass.CORE_ZONE_LABEL.lower():
        url = ConfigClass.DATA_UPLOAD_SERVICE_CORE + '/v1/files/jobs'
    else:
        url = ConfigClass.DATA_UPLOAD_SERVICE_GREENROOM + '/v1/files/jobs'
    return url


def validate_upload_event(zone, current_identity, project_code):
    zones = [
        ConfigClass.CORE_ZONE_LABEL.lower(),
        ConfigClass.GREEN_ZONE_LABEL.lower()
    ]
    if zone not in zones:
        error_msg = 'Invalid Zone'
        result = ''
        return result, error_msg
    role = current_identity['role']
    if role != 'admin':
        project_role = get_project_role(
            current_identity,
            project_code
        )
        restrict_zone = ConfigClass.CORE_ZONE_LABEL.lower()
        if zone == restrict_zone and project_role == 'contributor':
            error_msg = customized_error_template(
                ECustomizedError.PERMISSION_DENIED
            )
            result = project_role
        elif not project_role:
            error_msg = customized_error_template(
                ECustomizedError.PERMISSION_DENIED
            )
            result = 'User not in the project'
    return result, error_msg


async def transfer_to_pre(data, project_code, session_id):
    try:
        _logger.info('transfer_to_pre'.center(80, '-'))
        payload = {
            'current_folder_node': data.current_folder_node,
            'project_code': project_code,
            'operator': data.operator,
            'upload_message': data.upload_message,
            'data': data.data,
            'job_type': data.job_type
        }
        headers = {
            'Session-ID': session_id
        }
        url = select_url_by_zone(data.zone)
        async with httpx.AsyncClient() as client:
            result = await client.post(url, headers=headers, json=payload)
        return result
    except Exception as e:
        api_response.error_msg = f'Upload service  error: {e}'
        api_response.code = EAPIResponseCode.forbidden
        return api_response.json_response()
