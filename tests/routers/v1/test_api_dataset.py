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
        url='http://neo4j_service/v1/neo4j/nodes/Dataset/query',
        json=[
            {'code': dataset_code},
        ],
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
        url='http://neo4j_service/v1/neo4j/nodes/Dataset/query',
        json=[],
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
        method='POST',
        url='http://neo4j_service/v1/neo4j/nodes/Dataset/query',
        json=[{
            'labels': ['Dataset'],
            'global_entity_id': 'fake_geid',
            'creator': 'testuser',
            'modality': [],
            'code': 'test0111'
        }],
        status_code=200,
    )
    res = await test_async_client_auth.get(
        test_dataset_detailed_api, headers=header)
    res_json = res.json()
    assert res_json.get('code') == 200
    result = res_json.get('result')
    _dataset_info = result.get('general_info')[0]
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
        method='POST',
        url='http://neo4j_service/v1/neo4j/nodes/Dataset/query',
        json=[{
            'labels': ['Dataset'],
            'global_entity_id': 'fake_geid',
            'creator': 'fakeuser',
            'modality': [],
            'code': 'test0111'
        }],
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
        method='POST',
        url='http://neo4j_service/v1/neo4j/nodes/Dataset/query',
        json=[{
            'labels': ['None'],
            'global_entity_id': 'fake_geid',
            'creator': 'testuser',
            'modality': [],
            'code': 'test0111'
        }],
        status_code=200,
    )
    res = await test_async_client_auth.get(
        test_dataset_detailed_api, headers=header)
    res_json = res.json()
    assert res_json.get('code') == 404
    assert res_json.get('error_msg') == 'Cannot found given dataset code'


async def mock_get_dataset_versions(arg1, arg2):
    mock_dataset_version = [
        {
            'dataset_code': dataset_code
        }
    ]
    return mock_dataset_version
