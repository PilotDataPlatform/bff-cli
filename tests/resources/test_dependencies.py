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

import jwt
import pytest
from fastapi import Request

from app.models.project_models import POSTProjectFile
from app.resources.dependencies import jwt_required
from app.resources.dependencies import transfer_to_pre
from app.resources.dependencies import validate_upload_event
from app.resources.error_handler import APIException

pytestmark = pytest.mark.asyncio
project_code = 'test_project'


async def test_jwt_required_should_return_successed(httpx_mock):
    mock_request = Request(scope={'type': 'http'})
    encoded_jwt = jwt.encode({
        'realm_access': {'roles': ['platform_admin']},
        'preferred_username': 'test_user',
        'exp': time.time() + 3
    }, key='unittest', algorithm='HS256').decode('utf-8')
    mock_request._headers = {'Authorization': 'Bearer ' + encoded_jwt}
    httpx_mock.add_response(
        method='GET',
        url='http://service_auth/v1/admin/user?username=test_user',
        json={
            'result': {'id': 1, 'role': 'admin'}},
        status_code=200,
    )
    test_result = await jwt_required(mock_request)
    assert test_result['code'] == 200
    assert test_result['user_id'] == 1
    assert test_result['username'] == 'test_user'


async def test_jwt_required_without_token_should_return_unauthorized():
    mock_request = Request(scope={'type': 'http'})
    mock_request._headers = {}
    with pytest.raises(APIException) as e:
        _ = await jwt_required(mock_request)
        assert e.value.status_code == 401
        assert e.value.error_msg == 'Token required'


async def test_jwt_required_with_token_expired_should_return_unauthorized():
    mock_request = Request(scope={'type': 'http'})
    encoded_jwt = jwt.encode({
        'realm_access': {'roles': ['platform_admin']},
        'preferred_username': 'test_user',
        'exp': time.time() - 3
    }, key='unittest', algorithm='HS256').decode('utf-8')
    mock_request._headers = {'Authorization': 'Bearer ' + encoded_jwt}
    test_result = await jwt_required(mock_request)
    response = test_result.__dict__
    assert response['status_code'] == 401


async def test_jwt_required_without_username_return_not_found(httpx_mock):
    mock_request = Request(scope={'type': 'http'})

    encoded_jwt = jwt.encode(
        {
            'realm_access': {'roles': ['platform_admin']},
            'preferred_username': 'test_user',
            'exp': time.time() + 3
        },
        key='unittest',
        algorithm='HS256'
    ).decode('utf-8')
    mock_request._headers = {'Authorization': 'Bearer ' + encoded_jwt}
    httpx_mock.add_response(
        method='GET',
        url='http://service_auth/v1/admin/user?username=test_user',
        json={'result': None},
        status_code=404,
    )
    test_result = await jwt_required(mock_request)
    response = test_result.__dict__
    assert response['status_code'] == 403


def test_validate_upload_event_should_return_invalid_zone():
    identity = {'role': 'member', 'realm_roles': 'member'}
    _, error = validate_upload_event(
        'zone', identity, 'test_project')
    assert error == 'Invalid Zone'


async def test_transfer_to_pre_success(httpx_mock):
    mock_post_model = POSTProjectFile
    mock_post_model.current_folder_node = 'current_folder_node'
    mock_post_model.operator = 'operator'
    mock_post_model.upload_message = 'upload_messagegr'
    mock_post_model.data = 'data'
    mock_post_model.zone = 'cr'
    mock_post_model.job_type = 'job_type'
    httpx_mock.add_response(
        method='POST',
        url='http://data_upload_cr/v1/files/jobs',
        json={},
        status_code=200,
    )
    result = await transfer_to_pre(mock_post_model, project_code, 'session_id')
    assert result.json() == {}


async def test_transfer_to_pre_with_external_service_fail():
    mock_post_model = POSTProjectFile
    mock_post_model.current_folder_node = 'current_folder_node'
    mock_post_model.operator = 'operator'
    mock_post_model.upload_message = 'upload_messagegr'
    mock_post_model.data = 'data'
    mock_post_model.zone = 'cr'
    mock_post_model.job_type = 'job_type'
    result = await transfer_to_pre(mock_post_model, project_code, 'session_id')
    response = result.__dict__
    assert response['status_code'] == 403
