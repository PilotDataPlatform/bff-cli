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

pytestmark = pytest.mark.asyncio
test_api = '/v1/manifest'
test_export_api = '/v1/manifest/export'
test_manifest_attach_api = '/v1/manifest/attach'
project_code = 'cli'


async def test_get_attributes_without_token(test_async_client):
    payload = {'project_code': project_code}
    res = await test_async_client.get(test_api, query_string=payload)
    res_json = res.json()
    assert res_json.get('code') == 401
    assert res_json.get('error_msg') == 'Token required'


async def test_get_attributes_should_return_200(
    test_async_client_auth,
    mocker,
    create_db_manifest
):
    payload = {'project_code': project_code}
    header = {'Authorization': 'fake token'}
    mocker.patch('app.routers.v1.api_manifest.has_permission',
                 return_value=True)
    res = await test_async_client_auth.get(
        test_api,
        headers=header,
        query_string=payload
    )
    res_json = res.json()
    assert res_json.get('code') == 200
    assert len(res_json.get('result')) >= 1


async def test_get_attributes_no_access_should_return_403(
    test_async_client_auth,
    mocker
):
    payload = {'project_code': project_code}
    headers = {'Authorization': 'fake token'}
    mocker.patch(
        'app.routers.v1.api_manifest.has_permission',
        return_value=False
    )
    res = await test_async_client_auth.get(
        test_api,
        headers=headers,
        query_string=payload
    )
    res_json = res.json()
    assert res_json.get('code') == 403
    assert res_json.get('error_msg').lower() == 'Permission Denied'.lower()


async def test_get_attributes_project_not_exist_should_return_403(
    test_async_client_auth,
    mocker
):
    payload = {'project_code': 't1000'}
    headers = {'Authorization': 'fake token'}
    mocker.patch(
        'app.routers.v1.api_manifest.has_permission',
        return_value=False
    )
    res = await test_async_client_auth.get(
        test_api,
        headers=headers,
        query_string=payload
    )
    res_json = res.json()
    assert res_json.get('code') == 403
    assert res_json.get('error_msg').lower() == 'Permission Denied'.lower()


# # Test export manifest
async def test_export_attributes_without_token(test_async_client):
    param = {'project_code': project_code,
             'manifest_name': 'Manifest1'}
    res = await test_async_client.get(test_export_api, query_string=param)
    res_json = res.json()
    assert res_json.get('code') == 401
    assert res_json.get('error_msg') == 'Token required'


async def test_export_attributes_should_return_200(
    test_async_client_auth,
    mocker,
    create_db_manifest
):
    param = {'project_code': project_code,
             'manifest_name': 'fake_manifest'}
    headers = {'Authorization': 'fake token'}
    mocker.patch('app.routers.v1.api_manifest.has_permission',
                 return_value=True)
    res = await test_async_client_auth.get(
        test_export_api,
        headers=headers,
        query_string=param
    )
    res_json = res.json()
    assert res_json.get('code') == 200
    assert res_json.get('result').get('manifest_name') == 'fake_manifest'
    attribute_len = len(res_json.get('result')['attributes'])
    assert attribute_len == 2


async def test_export_attributes_no_access(test_async_client_auth, mocker):
    param = {'project_code': project_code,
             'manifest_name': 'fake_manifest'}
    headers = {'Authorization': 'fake token'}
    mocker.patch(
        'app.routers.v1.api_manifest.has_permission',
        return_value=False
    )
    res = await test_async_client_auth.get(
        test_export_api,
        headers=headers,
        query_string=param
    )
    res_json = res.json()
    assert res_json.get('code') == 403
    assert res_json.get('error_msg').lower() == 'Permission Denied'.lower()


async def test_export_attributes_not_exist_should_return_404(
    test_async_client_auth,
    mocker,
    create_db_manifest
):
    param = {'project_code': project_code,
             'manifest_name': 'Manifest1'}
    headers = {'Authorization': 'fake token'}
    mocker.patch('app.routers.v1.api_manifest.has_permission',
                 return_value=True)
    res = await test_async_client_auth.get(
        test_export_api,
        headers=headers,
        query_string=param
    )
    res_json = res.json()
    assert res_json.get('code') == 404
    assert res_json.get('error_msg') == 'Manifest Not Exist Manifest1'


async def test_export_attributes_project_not_exist_should_return_403(
    test_async_client_auth,
    mocker
):
    param = {'project_code': 't1000', 'manifest_name': 'fake_manifest'}
    headers = {'Authorization': 'fake token'}
    mocker.patch(
        'app.routers.v1.api_manifest.has_permission',
        return_value=False
    )
    res = await test_async_client_auth.get(
        test_export_api,
        headers=headers,
        query_string=param
    )
    res_json = res.json()
    assert res_json.get('code') == 403
    assert res_json.get('error_msg').lower() == 'Permission Denied'.lower()


async def test_attach_attributes_without_token_should_return_401(
    test_async_client
):
    payload = {'manifest_json': {
        'manifest_name': 'fake manifest',
        'project_code': project_code,
        'attributes': {'fake_attribute': 'a1'},
        'file_name': 'fake_file',
        'zone': 'zone'
    }
    }
    res = await test_async_client.post(test_manifest_attach_api, json=payload)
    res_json = res.json()
    assert res_json.get('code') == 401
    assert res_json.get('error_msg') == 'Token required'


async def test_attach_attributes_should_return_200(
    test_async_client_auth,
    mocker,
    httpx_mock,
    create_db_manifest
):
    payload = {
        'manifest_json': {
            'manifest_name': 'fake_manifest',
            'project_code': project_code,
            'attributes': {'fake_attribute': 'a1'},
            'file_name': 'fake_file',
            'zone': '0'
        }
    }
    header = {'Authorization': 'fake token'}
    mocker.patch('app.routers.v1.api_manifest.has_permission',
                 return_value=True)
    httpx_mock.add_response(
        method='GET',
        url=(
            'http://metadata_service/v1/items/search/'
            '?container_code=cli'
            '&container_type=project'
            '&parent_path='
            '&recursive=false'
            '&zone=0'
            '&archived=false'
            '&name=fake_file'
        ),
        json={
            'code': 200,
            'error_msg': '',
            'result': [{
                'id': 'item-id',
                'parent': '',
                'parent_path': '',
                'restore_path': None,
                'archived': False,
                'type': 'file',
                'zone': 0,
                'name': 'fake_file',
                'size': 0,
                'owner': 'testuser',
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
                        'tags': [
                            'tag1',
                            'tag2'
                        ],
                        'system_tags': [
                            'tag1',
                            'tag2'
                        ],
                        'attributes': {}
                    }
                }
            }
            ]
        },
        status_code=200,
    )
    httpx_mock.add_response(
        method='PUT',
        url='http://metadata_service/v1/items/batch/bequeath/',
        json={
            'code': 200,
            'error_msg': '',
            'page': 0,
            'total': 1,
            'num_of_pages': 1,
            'result': {
                'id': '85465212-168a-4f0c-a7aa-f3a19795d2ff',
                'parent': '28c608ac-1693-4318-a1c4-412caf2cd74a',
                'parent_path': 'path.to.file',
                'type': 'file',
                'zone': 0,
                'name': 'fake_file',
                'size': 0,
                'owner': 'username',
                'container_code': project_code,
                'container_type': 'project',
                'created_time': '2022-04-13 13:30:10.890347',
                'last_updated_time': '2022-04-13 13:30:10.890347',
                'storage': {
                    'id': 'ba623005-8183-419a-972a-e4ce0d539349',
                    'location_uri': 'https://example.com/item',
                    'version': '1.0'
                },
                'extended': {
                    'id': 'dc763d28-7e74-4db3-a702-fa719aa702c6',
                    'extra': {
                        'tags': [
                            'tag1',
                            'tag2'
                        ],
                        'system_tags': [
                            'tag1',
                            'tag2'
                        ],
                        'attributes': {
                            '101778d7-a628-41ea-823b-e4b377f3476c': {
                                'fake_attribute': 'a1'}
                        }
                    }
                }
            }
        },
        status_code=200,
    )
    res = await test_async_client_auth.post(
        test_manifest_attach_api,
        headers=header,
        json=payload
    )
    res_json = res.json()
    assert res_json.get('code') == 200
    result = res_json.get('result')
    assert result.get('extended').get('extra').get('attributes') == {
        '101778d7-a628-41ea-823b-e4b377f3476c': {'fake_attribute': 'a1'}
    }


async def test_attach_attributes_wrong_file_should_return_404(
    test_async_client_auth,
    httpx_mock,
    mocker
):
    payload = {'manifest_json': {
        'manifest_name': 'fake_manifest',
        'project_code': project_code,
        'attributes': {'fake_attribute': 'a1'},
        'file_name': 'fake_wrong_file',
        'zone': 'zone'
    }
    }
    header = {'Authorization': 'fake token'}
    mocker.patch('app.routers.v1.api_manifest.has_permission',
                 return_value=True)
    httpx_mock.add_response(
        method='GET',
        url=(
            'http://metadata_service/v1/items/search/'
            '?container_code=cli'
            '&container_type=project'
            '&parent_path='
            '&recursive=false'
            '&zone=0'
            '&archived=false'
            '&name=fake_wrong_file'
        ),
        json={'code': 200, 'result': []},
        status_code=200,
    )
    res = await test_async_client_auth.post(
        test_manifest_attach_api,
        headers=header,
        json=payload
    )
    res_json = res.json()
    assert res_json.get('code') == 404
    error = res_json.get('error_msg')
    assert error == 'File Not Exist'


async def test_attach_attributes_wrong_name_should_return_400(
    test_async_client_auth,
    httpx_mock,
    create_db_manifest,
    mocker
):
    payload = {'manifest_json': {
        'manifest_name': 'Manifest1',
        'project_code': project_code,
        'attributes': {'fake_attribute': 'wrong name'},
        'file_name': 'fake_file',
        'zone': 'zone'
    }
    }
    header = {'Authorization': 'fake token'}
    mocker.patch('app.routers.v1.api_manifest.has_permission',
                 return_value=True)
    httpx_mock.add_response(
        method='GET',
        url=(
            'http://metadata_service/v1/items/search/'
            f'?container_code={project_code}'
            '&container_type=project'
            '&parent_path='
            '&recursive=false'
            '&zone=0'
            '&archived=false'
            '&name=fake_file'
        ),
        json={
            'code': 200,
            'result': [{
                'id': 'item-id',
                'parent': 'parent-id',
                'parent_path': 'testuser',
                'restore_path': None,
                'archived': False,
                'type': 'file',
                'zone': 0,
                'name': 'fake_file',
                'size': 0,
                'owner': 'testuser',
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
            },
                {
                    'id': 'item-id2',
                    'parent': 'parent-id2'}
            ]
        },
        status_code=200,
    )
    res = await test_async_client_auth.post(
        test_manifest_attach_api,
        headers=header,
        json=payload
    )
    res_json = res.json()
    assert res_json.get('code') == 400
    error = res_json.get('error_msg')
    assert error == 'Manifest Not Exist Manifest1'


async def test_attach_attributes_no_access_should_return_403(
    test_async_client_auth,
    mocker
):
    payload = {'manifest_json': {
        'manifest_name': 'fake manifest',
        'project_code': project_code,
        'attributes': {'fake_attribute': 'wrong name'},
        'file_name': 'fake_file',
        'zone': 'zone'
    }
    }
    header = {'Authorization': 'fake token'}
    mocker.patch(
        'app.routers.v1.api_manifest.has_permission',
        return_value=False
    )
    res = await test_async_client_auth.post(
        test_manifest_attach_api,
        headers=header,
        json=payload
    )
    res_json = res.json()
    assert res_json.get('code') == 403
    error = res_json.get('error_msg')
    assert error.lower() == 'Permission Denied'.lower()


async def test_fail_to_attach_attributes_return_404(
    test_async_client_auth,
    httpx_mock,
    mocker,
    create_db_manifest
):
    payload = {'manifest_json': {
        'manifest_name': 'fake_manifest',
        'project_code': project_code,
        'attributes': {'fake_attribute': 'wrong name'},
        'file_name': 'fake_file',
        'zone': 'zone'
    }
    }
    header = {'Authorization': 'fake token'}
    mocker.patch('app.routers.v1.api_manifest.has_permission',
                 return_value=True)
    httpx_mock.add_response(
        method='GET',
        url=(
            'http://metadata_service/v1/items/search/'
            f'?container_code={project_code}'
            '&container_type=project'
            '&parent_path='
            '&recursive=false'
            '&zone=0'
            '&archived=false'
            '&name=fake_file'
        ),
        json={
            'code': 200,
            'result': [{
                'id': 'item-id',
                'parent': 'parent-id',
                'parent_path': 'testuser',
                'restore_path': None,
                'archived': False,
                'type': 'file',
                'zone': 0,
                'name': 'fake_file',
                'size': 0,
                'owner': 'testuser',
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
            },
                {
                    'id': 'item-id2',
                    'parent': 'parent-id2'}
            ]
        },
        status_code=200,
    )
    mocker.patch('app.routers.v1.api_manifest.attach_manifest_to_file',
                 return_value=None)
    res = await test_async_client_auth.post(
        test_manifest_attach_api,
        headers=header,
        json=payload
    )
    res_json = res.json()
    assert res_json.get('code') == 404
    error = res_json.get('error_msg')
    assert error == 'File Not Exist'
