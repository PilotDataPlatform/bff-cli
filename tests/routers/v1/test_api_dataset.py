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

test_dataset_api = '/v1/datasets'
dataset_code = 'testdataset'
test_dataset_detailed_api = '/v1/dataset/testdataset'
pytestmark = pytest.mark.asyncio


async def test_list_dataset_without_token(test_async_client):
    res = await test_async_client.get(test_dataset_api)
    res_json = res.json()
    assert res_json.get('code') == 401
    assert res_json.get('error_msg') == 'Token required'


async def test_list_dataset_should_successed(
    test_async_client_auth,
    httpx_mock: HTTPXMock
):
    header = {'Authorization': 'fake token'}
    httpx_mock.add_response(
        method='POST',
        url='http://dataset_service/v1/users/testuser/datasets',
        json={
            'code': 200,
            'error_msg': '',
            'page': 0,
            'total': 1,
            'num_of_pages': 1,
            'result': [{
                'id': 'fake-geid',
                'source': '',
                'authors': ['user1', 'user2'],
                'code': dataset_code,
                'type': 'GENERAL',
                'modality': [],
                'collection_method': [],
                'license': '',
                'tags': [],
                'description': 'my description',
                'size': 0,
                'total_files': 0,
                'title': 'test dataset',
                'creator': 'testuser',
                'project_id': 'None',
                'created_at': '2022-03-31T15:00:04',
                'updated_at': '2022-03-31T15:00:04'
            }]
        },
        status_code=200,
    )
    res = await test_async_client_auth.get(test_dataset_api, headers=header)
    res_json = res.json()
    assert res_json.get('code') == 200
    datasets = []
    for d in res_json.get('result'):
        datasets.append(d.get('code'))
    assert dataset_code in datasets


async def test_list_empty_dataset(
    test_async_client_auth,
    httpx_mock: HTTPXMock
):
    header = {'Authorization': 'fake token'}
    httpx_mock.add_response(
        method='POST',
        url='http://dataset_service/v1/users/testuser/datasets',
        json={
            'code': 200,
            'error_msg': '',
            'page': 0,
            'total': 1,
            'num_of_pages': 1,
            'result': []
        },
        status_code=200,
    )
    res = await test_async_client_auth.get(test_dataset_api, headers=header)
    res_json = res.json()
    assert res_json.get('code') == 200
    assert res_json.get('result') == []


async def test_get_dataset_detail_without_token(test_async_client):
    res = await test_async_client.get(test_dataset_detailed_api)
    res_json = res.json()
    assert res_json.get('code') == 401
    assert res_json.get('error_msg') == 'Token required'


async def test_get_dataset_detail_should_successed(
    test_async_client_auth,
    httpx_mock,
    mocker,
    create_db_dataset_metrics
):
    header = {'Authorization': 'fake token'}
    httpx_mock.add_response(
        method='GET',
        url=f'http://dataset_service/v1/dataset-peek/{dataset_code}',
        json={
            'code': 200,
            'error_msg': '',
            'page': 0,
            'total': 1,
            'num_of_pages': 1,
            'result': {
                'id': 'fake_geid',
                'source': '',
                'authors': ['user1', 'user2'],
                'code': dataset_code,
                'type': 'GENERAL',
                'modality': [],
                'collection_method': [],
                'license': '',
                'tags': [],
                'description': 'my description',
                'size': 0,
                'total_files': 0,
                'title': 'my title',
                'creator': 'testuser',
                'project_id': 'None',
                'created_at': '2022-03-31T15:00:04',
                'updated_at': '2022-03-31T15:00:04'
            }
        },
        status_code=200,
    )
    res = await test_async_client_auth.get(
        test_dataset_detailed_api, headers=header)
    res_json = res.json()
    assert res_json.get('code') == 200
    result = res_json.get('result')
    _dataset_info = result.get('general_info')
    assert _dataset_info['creator'] == 'testuser'
    _version_info = result.get('version_detail')
    assert _version_info[0]['dataset_code'] == dataset_code
    _version_no = result.get('version_no')
    assert _version_no == 1


async def test_get_dataset_detail_no_access(
    test_async_client_auth,
    httpx_mock
):
    header = {'Authorization': 'fake token'}
    httpx_mock.add_response(
        method='GET',
        url=f'http://dataset_service/v1/dataset-peek/{dataset_code}',
        json={
            'code': 200,
            'error_msg': '',
            'page': 0,
            'total': 1,
            'num_of_pages': 1,
            'result': {
                'id': 'fake_geid',
                'source': '',
                'authors': ['user1', 'user2'],
                'code': dataset_code,
                'type': 'GENERAL',
                'modality': [],
                'collection_method': [],
                'license': '',
                'tags': [],
                'description': 'my description',
                'size': 0,
                'total_files': 0,
                'title': 'my title',
                'creator': 'fakeuser',
                'project_id': 'None',
                'created_at': '2022-03-31T15:00:04',
                'updated_at': '2022-03-31T15:00:04'
            }
        },
        status_code=200,
    )
    res = await test_async_client_auth.get(
        test_dataset_detailed_api, headers=header)
    res_json = res.json()
    assert res_json.get('code') == 403
    assert res_json.get('error_msg') == 'Permission Denied'


async def test_get_dataset_detail_not_exist(
    test_async_client_auth,
    httpx_mock
):
    header = {'Authorization': 'fake token'}
    httpx_mock.add_response(
        method='GET',
        url=f'http://dataset_service/v1/dataset-peek/{dataset_code}',
        json={
            "code": 404,
            "error_msg": "Not Found, invalid dataset code",
            "page": 0,
            "total": 1,
            "num_of_pages": 1,
            "result": {}
        },
        status_code=200,
    )
    res = await test_async_client_auth.get(
        test_dataset_detailed_api, headers=header)
    res_json = res.json()
    assert res_json.get('code') == 404
    assert res_json.get('error_msg') == 'Cannot found given dataset code'
