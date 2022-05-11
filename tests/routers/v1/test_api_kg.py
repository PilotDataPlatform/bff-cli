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
test_kg_api = '/v1/kg/resources'


async def test_kg_import_resource_should_return_200(
    test_async_client_kg_auth,
    httpx_mock: HTTPXMock
):
    payload = {
        'dataset_code': [],
        'data': {
            'kg_cli_test.json': {
                'key_value_pairs': {
                    'definition_file': True,
                    'file_type': 'KG unit test',
                    'existing_duplicate': False
                }
            }
        }
    }
    httpx_mock.add_response(
        method='POST',
        url='http://kg_service/v1/resources',
        json={
            'code': 200,
            'error_msg': '',
            'result': {
                'processing': {
                    'kg_cli_test.json': {
                        '@id': 'http://kgURL/_/uuid',
                    }
                },
                'ignored': {}
            }
        },
        status_code=200,
    )
    header = {
        'schema': 'Bearer',
        'credentials': 'fake_token'
    }
    res = await test_async_client_kg_auth.post(
        test_kg_api, headers=header, json=payload)
    res_json = res.json()
    assert res_json.get('code') == 200
    assert len(res_json.get('result').get('processing')) == 1
    assert len(res_json.get('result').get('ignored')) == 0


async def test_kg_import_existed_resource_should_return_200(
    test_async_client_kg_auth,
    httpx_mock: HTTPXMock
):
    payload = {
        'dataset_code': [],
        'data': {
            'kg_cli_test.json': {
                'key_value_pairs': {
                    'definition_file': True,
                    'file_type': 'KG unit test',
                    'existing_duplicate': False
                }
            }
        }
    }
    httpx_mock.add_response(
        method='POST',
        url='http://kg_service/v1/resources',
        json={
            'code': 200,
            'error_msg': '',
            'result': {
                'processing': {},
                'ignored': {
                    'kg_cli_test.json': {
                        '@id': 'http://kgURL/_/uuid',
                    }
                }
            }
        },
        status_code=200,
    )
    header = {
        'schema': 'Bearer',
        'credentials': 'fake_token'
    }
    res = await test_async_client_kg_auth.post(
        test_kg_api, headers=header, json=payload)
    res_json = res.json()
    assert res_json.get('code') == 200
    assert len(res_json.get('result').get('processing')) == 0
    assert len(res_json.get('result').get('ignored')) == 1
