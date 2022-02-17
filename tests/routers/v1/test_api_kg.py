import pytest
from pytest_httpx import HTTPXMock
import app.routers.v1.api_kg
from fastapi.security import HTTPBasicCredentials, HTTPBearer

test_kg_api = "/v1/kg/resources"


@pytest.mark.asyncio
async def test_kg_import_resource_should_return_200(test_async_client_kg_auth, httpx_mock: HTTPXMock):
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
            "code": 200,
            "error_msg": "",
            "result": {
                "processing": {
                    "kg_cli_test.json": {
                        "@id": "http://kgURL/_/uuid",
                    }
                },
                "ignored": {}
            }
        },
        status_code=200,
    )
    header = {
        "schema": 'Bearer',
        "credentials": 'fake_token'
    }
    res = await test_async_client_kg_auth.post(test_kg_api, headers=header, json=payload)
    res_json = res.json()
    assert res_json.get('code') == 200
    assert len(res_json.get('result').get('processing')) == 1
    assert len(res_json.get('result').get('ignored')) == 0


@pytest.mark.asyncio
async def test_kg_import_existed_resource_should_return_200(test_async_client_kg_auth, httpx_mock: HTTPXMock):
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
            "code": 200,
            "error_msg": "",
            "result": {
                "processing": {},
                "ignored": {
                    "kg_cli_test.json": {
                        "@id": "http://kgURL/_/uuid",
                    }
                }
            }
        },
        status_code=200,
    )
    header = {
        "schema": 'Bearer',
        "credentials": 'fake_token'
    }
    res = await test_async_client_kg_auth.post(test_kg_api, headers=header, json=payload)
    res_json = res.json()
    assert res_json.get('code') == 200
    assert len(res_json.get('result').get('processing')) == 0
    assert len(res_json.get('result').get('ignored')) == 1

