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

from app.models.error_model import InvalidEncryptionError

pytestmark = pytest.mark.asyncio
test_validate_manifest_api = '/v1/validate/manifest'
test_validate_env_api = '/v1/validate/env'


async def test_validate_attribute_should_return_200(test_async_client_auth, mocker, httpx_mock):
    mocker.patch('app.routers.v1.api_validation.has_permission', return_value=True)
    httpx_mock.add_response(
        method='GET',
        url='http://metadata_service/v1/template/?project_code=test_project&name=fake_manifest',
        json={
            "code": 200,
            "error_msg": "",
            "page": 0,
            "total": 1,
            "num_of_pages": 1,
            "result": [
                {
                    "id": "fake-id",
                    "name": "fake_manifest",
                    "project_code": "test_project",
                    "attributes": [
                        {
                            "name": "attr1",
                            "optional": False,
                            "type": "multiple_choice",
                            "options": ["a1", "a2", "a3"]
                        },
                        {
                            "name": "attr2",
                            "optional": True,
                            "type": "text",
                            "options": None
                        }
                    ]
                }
            ]
        },
        status_code=200,
    )
    payload = {
        'manifest_json': {
            'manifest_name': 'fake_manifest',
            'project_code': 'test_project',
            'attributes': {
                'attr1': 'a1',
                'attr2': 'test text manifest'
            }
        }
    }
    res = await test_async_client_auth.post(
        test_validate_manifest_api, json=payload)
    res_json = res.json()
    assert res_json.get('code') == 200
    assert res_json.get('result') == 'valid'


async def test_validate_attribute_with_manifest_not_found_return_404(test_async_client_auth, httpx_mock, mocker):
    mocker.patch('app.routers.v1.api_validation.has_permission', return_value=True)
    httpx_mock.add_response(
        method='GET',
        url='http://metadata_service/v1/template/?project_code=test_project&name=fake_manifest',
        json={
            "code": 200,
            "error_msg": "",
            "page": 0,
            "total": 1,
            "num_of_pages": 1,
            "result": []
        },
        status_code=200,
    )
    payload = {
        'manifest_json': {
            'manifest_name': 'fake_manifest',
            'project_code': 'test_project',
            'attributes': {
                'attr1': 'a1',
                'attr2': 'Test manifest text value'
            }
        }
    }
    res = await test_async_client_auth.post(
        test_validate_manifest_api,
        json=payload)
    res_json = res.json()
    assert res_json.get('code') == 404
    assert res_json.get('error_msg') == 'Manifest Not Exist fake_manifest'
    assert res_json.get('result') == 'invalid'


async def test_invalidate_attribute_should_return_400(test_async_client_auth, httpx_mock, mocker):
    mocker.patch('app.routers.v1.api_validation.has_permission', return_value=True)
    httpx_mock.add_response(
        method='GET',
        url='http://metadata_service/v1/template/?project_code=test_project&name=fake_manifest',
        json={
            "code": 200,
            "error_msg": "",
            "page": 0,
            "total": 1,
            "num_of_pages": 1,
            "result": [
                {
                    "id": "fake-id",
                    "name": "fake_manifest",
                    "project_code": "test_project",
                    "attributes": [
                        {
                            "name": "attr1",
                            "optional": False,
                            "type": "multiple_choice",
                            "options": ["a1", "a2", "a3"]
                        },
                        {
                            "name": "attr2",
                            "optional": True,
                            "type": "text",
                            "options": None
                        }
                    ]
                }
            ]
        },
        status_code=200,
    )
    payload = {
        'manifest_json': {
            'manifest_name': 'fake_manifest',
            'project_code': 'test_project',
            'attributes': {
                'attr1': 'a1',
                'attr2': 'Test manifest text value',
                'attr3': 't1'
            }
        }
    }
    res = await test_async_client_auth.post(
        test_validate_manifest_api,
        json=payload)
    res_json = res.json()
    assert res_json.get('code') == 400
    assert res_json.get('error_msg') == 'invalid attribute attr3'
    assert res_json.get('result') == 'invalid'


@pytest.mark.parametrize(
    'test_action, test_zone',
    [('upload', 'gr'), ('upload', 'cr'), ('download', 'cr')])
async def test_validate_env_should_return_200(
    test_async_client_auth,
    test_action,
    test_zone,
    mocker
):
    mocker.patch('app.routers.v1.api_validation.has_permission', return_value=True)
    payload = {'action': test_action, 'environ': '', 'zone': test_zone}
    res = await test_async_client_auth.post(
        test_validate_env_api,
        json=payload)
    response = res.json()
    assert response.get('result') == 'valid'
    assert response.get('code') == 200
    assert response.get('error_msg') == ''


@pytest.mark.parametrize(
    'test_action, test_zone',
    [('upload', 'gr'), ('download', 'gr')])
async def test_validate_env_with_encrypted_message_should_return_200(
    test_async_client_auth,
    mocker,
    test_action,
    test_zone
):
    mocker.patch('app.routers.v1.api_validation.has_permission', return_value=True)
    payload = {'action': test_action, 'environ': 'gr', 'zone': test_zone}
    mocker.patch('app.routers.v1.api_validation.decryption',
                 return_value='gr')
    res = await test_async_client_auth.post(
        test_validate_env_api,
        json=payload)
    response = res.json()
    assert response.get('result') == 'valid'
    assert response.get('code') == 200
    assert response.get('error_msg') == ''


@pytest.mark.parametrize(
    'test_action, test_zone',
    [('download', 'gr')])
async def test_invalidate_env_should_return_403(
    test_async_client_auth,
    test_action,
    test_zone,
    mocker
):
    mocker.patch('app.routers.v1.api_validation.has_permission', return_value=True)
    payload = {'action': test_action, 'environ': '', 'zone': test_zone}
    res = await test_async_client_auth.post(
        test_validate_env_api,
        json=payload)
    response = res.json()
    assert response.get('result') == 'Invalid'
    assert response.get('code') == 403


@pytest.mark.parametrize(
    'test_action, test_zone',
    [('upload', 'cr'), ('download', 'cr')])
async def test_invalidate_env_with_encrypted_message_should_return_403(
    test_async_client_auth, mocker, test_action, test_zone
):
    mocker.patch('app.routers.v1.api_validation.has_permission', return_value=True)
    payload = {'action': test_action, 'environ': 'gr', 'zone': test_zone}
    mocker.patch('app.routers.v1.api_validation.decryption',
                 return_value='gr')
    res = await test_async_client_auth.post(
        test_validate_env_api,
        json=payload)
    response = res.json()
    assert response.get('result') == 'Invalid'
    assert response.get('code') == 403


async def test_validate_env_with_wrong_zone_should_return_400(test_async_client_auth, mocker):
    mocker.patch('app.routers.v1.api_validation.has_permission', return_value=True)
    payload = {'action': 'test_action', 'environ': '', 'zone': 'zone'}
    res = await test_async_client_auth.post(
        test_validate_env_api,
        json=payload)
    response = res.json()
    assert response.get('result') == 'Invalid'
    assert response.get('code') == 400


async def test_validate_env_with_decryption_error_should_return_400(
    test_async_client_auth,
    mocker
):
    payload = {'action': 'test_action', 'environ': 'gr', 'zone': 'gr'}
    mocker.patch('app.routers.v1.api_validation.has_permission', return_value=True)
    mocker.patch('app.routers.v1.api_validation.decryption',
                 side_effect=InvalidEncryptionError(
                     'Invalid encryption, could not decrypt message'))
    res = await test_async_client_auth.post(
        test_validate_env_api,
        json=payload)
    response = res.json()

    assert response.get('result') == 'Invalid'
    assert response.get('code') == 400
