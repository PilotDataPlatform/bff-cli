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

import pytest
from pytest_httpx import HTTPXMock

pytestmark = pytest.mark.asyncio
test_file_exist_api = '/v1/project/test_project/file/exist'
project_code = 'test_project'


async def test_file_exist_should_return_200(
    test_async_client_auth,
    mocker,
    httpx_mock: HTTPXMock
):
    param = {
        'project_code': project_code,
        'zone': 'zone',
        'file_relative_path': 'fake_user/fake_file',
    }
    header = {'Authorization': 'fake token'}
    httpx_mock.add_response(
        method='GET',
        url=(
            'http://metadata_service/v1/items/search/'
            '?container_code=test_project'
            '&container_type=project'
            '&parent_path=fake_user'
            '&recursive=false'
            '&zone=0'
            '&archived=false'
            '&type=file'
            '&name=fake_file'
        ),
        json={
            'code': 200,
            'error_msg': '',
            'result': [{
                'id': 'item-id',
                'parent': 'parent-id',
                'parent_path': 'fake_user',
                'restore_path': None,
                'archived': False,
                'type': 'file',
                'zone': 0,
                'name': 'fake_file',
                'size': 0,
                'owner': 'fake_user',
                'container_code': project_code,
                'container_type': 'project',
                'created_time': '2022-04-13 18:17:51.008212',
                'last_updated_time': '2022-04-13 18:17:51.008227',
                'storage': {
                    'id': '8cd8cef7-2603-4ec3-b5a0-479e58e4c9d9',
                    'location_uri': '',
                    'version': '1.0'
                },
                'extended': {
                    'id': '96510da0-22f4-4487-ac88-71cd48967c8d',
                    'extra': {
                        'tags': [],
                        'attributes': {}
                    }
                }
            }
            ]
        },
        status_code=200,
    )
    res = await test_async_client_auth.get(
        test_file_exist_api,
        headers=header,
        query_string=param
    )
    assert res.status_code == 200
    res_json = res.json().get('result')
    assert f'{res_json["parent_path"]}/{res_json["name"]}' == \
        param['file_relative_path']


async def test_file_exist_without_token_should_return_200(test_async_client):
    param = {
        'project_code': project_code,
        'zone': 'zone',
        'file_relative_path': 'fake_user/fake_file',
    }
    res = await test_async_client.get(test_file_exist_api, query_string=param)
    res_json = res.json()
    assert res_json.get('code') == 401
    assert res_json.get('error_msg') == 'Token required'
