import pytest
from pytest_httpx import HTTPXMock

test_file_exist_api = "/v1/project/test_project/file/exist"
project_code = "test_project"

@pytest.mark.asyncio
async def test_file_exist_should_return_200(test_async_client_auth, mocker, httpx_mock: HTTPXMock):
    param = {
        "project_code": project_code,
        "zone": "zone",
        "file_relative_path": "fake_user/fake_file",
    }
    header = {'Authorization': 'fake token'}
    httpx_mock.add_response(
        method='GET',
        url=f'http://fileinfo_service/v1/project/test_project/file/exist?project_code={project_code}&zone=zone&file_relative_path=fake_user/fake_file',
        json=[{
            "id": 20394,
            "display_path": "fake_user/fake_file"}],
        status_code=200,
    )
    res = await test_async_client_auth.get(test_file_exist_api, headers=header, query_string=param)
    assert res.status_code == 200
    res_json = res.json()[0]
    assert res_json["display_path"] == param["file_relative_path"]


@pytest.mark.asyncio
async def test_file_exist_without_token_should_return_200(test_async_client):
    param = {
        "project_code": project_code,
        "zone": "zone",
        "file_relative_path": "fake_user/fake_file",
    }
    res = await test_async_client.get(test_file_exist_api, query_string=param)
    res_json = res.json()
    assert res_json.get('code') == 401
    assert res_json.get('error_msg') == "Token required"

