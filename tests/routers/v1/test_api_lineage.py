import pytest
from pytest_httpx import HTTPXMock

pytestmark = pytest.mark.asyncio
test_lineage_api = "/v1/lineage"


async def test_create_lineage_should_return_200(test_async_client_auth, httpx_mock: HTTPXMock):
    payload = {
        "project_code": "test_project",
        "input_geid": "fake_input_geid",
        "output_geid": "fake_output_geid",
        "pipeline_name": "pipeline_name",
        "description": "Test lineage"
    }
    header = {'Authorization': 'fake token'}
    httpx_mock.add_response(
        method='POST',
        url='http://provenance_service/v1/lineage',
        json={"mutatedEntities": {
            "UPDATE": [
                {
                    "typeName": "file_data",
                    "guid": "input_guid"
                },
                {
                    "typeName": "file_data",
                    "guid": "output_guid"
                }
            ],
            "CREATE": [
                {
                    "typeName": "Process",
                    "guid": "pipeline_guid"
                }
            ]
        },
        "guidAssignments": {
            "-18306307111308515": "pipeline_guid"
        }},
        status_code=200,
    )
    res = await test_async_client_auth.post(test_lineage_api, headers=header, json=payload)
    assert res.status_code == 200


async def test_create_lineage_with_internal_error_should_return_500(test_async_client_auth, httpx_mock: HTTPXMock):
    payload = {
        "project_code": "test_project",
        "input_geid": "fake_input_geid",
        "output_geid": "fake_output_geid",
        "pipeline_name": "pipeline_name",
        "description": "Test lineage"
    }
    header = {'Authorization': 'fake token'}
    httpx_mock.add_response(
        method='POST',
        url='http://provenance_service/v1/lineage',
        json={},
        status_code=500,
    )
    res = await test_async_client_auth.post(test_lineage_api, headers=header, json=payload)
    assert res.status_code == 500

