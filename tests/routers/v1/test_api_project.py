import pytest
from requests.models import Response
from pytest_httpx import HTTPXMock
pytestmark = pytest.mark.asyncio
test_project_api = "/v1/projects"
test_get_project_file_api = "/v1/project/test_project/files"
test_get_project_folder_api = "/v1/project/test_project/folder"
project_code = "test_project"


async def test_get_project_list_should_return_200(
    test_async_client_auth, mocker):
    test_project = ["project1", "project2", "project3"]
    mocker.patch(
        'app.routers.v1.api_project.get_user_projects',
        return_value=test_project)
    header = {'Authorization': 'fake token'}
    res = await test_async_client_auth.get(test_project_api, headers=header)
    res_json = res.json()
    projects = res_json.get('result')
    assert res.status_code == 200
    assert len(projects) == len(test_project)


async def test_get_project_list_without_token_should_return_401(
    test_async_client):
    res = await test_async_client.get(test_project_api)
    res_json = res.json()
    assert res_json.get('code') == 401
    assert res_json.get('error_msg') == "Token required"


async def test_upload_files_into_project_should_return_200(
    test_async_client_auth, mocker):
    payload = {
        "operator": "test_user",
        "upload_message": "test",
        "type": "processed",
        "zone": "zone",
        "filename": "fake.png",
        "job_type": "AS_FILE",
        "dcm_id": "undefined",
        "current_folder_node": "",
        "data": [
            {"resumable_filename": "fake.png", "resumable_relative_path": ""}
            ]
        }
    mocker.patch('app.routers.v1.api_project.validate_upload_event',
                 return_value=None)
    mocker.patch('app.routers.v1.api_project.check_file_exist',
                 return_value={})
    mock_response = Response()
    mock_response.status_code = 200
    mock_response._content = b'{ "result" : "SUCCESSED" }'
    mocker.patch('app.routers.v1.api_project.transfer_to_pre',
                 return_value=mock_response)
    header = {'Authorization': 'fake token'}
    response = await test_async_client_auth.post(
        test_get_project_file_api,
        headers=header,
        json=payload
        )
    assert response.status_code == 200
    assert response.json()["result"] == "SUCCESSED"


async def test_upload_files_with_invalid_upload_event_should_return_400(
    test_async_client_auth, mocker):
    payload = {
        "operator": "test_user",
        "upload_message": "test",
        "type": "processed",
        "zone": "zone",
        "filename": "fake.png",
        "job_type": "AS_FILE",
        "dcm_id": "undefined",
        "current_folder_node": "",
        "data": [
            {"resumable_filename": "fake.png", "resumable_relative_path": ""}
            ]
    }
    mocker.patch(
        'app.routers.v1.api_project.validate_upload_event',
        return_value="Invalid Zone")
    header = {'Authorization': 'fake token'}
    response = await test_async_client_auth.post(
        test_get_project_file_api,
        headers=header,
        json=payload)
    res_json = response.json()
    assert res_json.get('code') == 400
    assert res_json.get('error_msg') == "Invalid Zone"


async def test_upload_for_project_member_should_return_403(
    test_async_client_project_member_auth, mocker
    ):
    payload = {
        "operator": "testuser",
        "upload_message": "test",
        "type": "processed",
        "zone": "gr",
        "filename": "fake.png",
        "job_type": "AS_FILE",
        "dcm_id": "undefined",
        "current_folder_node": "",
        "data": [
            {"resumable_filename": "fake.png", "resumable_relative_path": ""}
            ]
    }
    mocker.patch('app.routers.v1.api_project.check_file_exist',
                 return_value={})
    header = {'Authorization': 'fake token'}
    response = await test_async_client_project_member_auth.post(
        test_get_project_file_api,
        headers=header,
        json=payload)
    res_json = response.json()
    assert res_json.get('code') == 403
    assert res_json.get('error_msg') == 'Permission Denied'
    assert res_json.get('result') == 'User not in the project'


async def test_upload_for_contributor_into_core_should_return_403(
    test_async_client_project_member_auth, mocker):
    payload = {
        "operator": "test_user",
        "upload_message": "test",
        "type": "processed",
        "zone": "cr",
        "filename": "fake.png",
        "job_type": "AS_FILE",
        "dcm_id": "undefined",
        "current_folder_node": "",
        "data": [
            {"resumable_filename": "fake.png", "resumable_relative_path": ""}
            ]
    }
    mocker.patch('app.routers.v1.api_project.validate_upload_event',
                 return_value=None)
    mocker.patch('app.routers.v1.api_project.check_file_exist',
                 return_value={})
    header = {'Authorization': 'fake token'}
    response = await test_async_client_project_member_auth.post(
        test_get_project_file_api,
        headers=header,
        json=payload)
    res_json = response.json()
    assert res_json.get('code') == 403
    assert res_json.get('error_msg') == 'Permission Denied'
    assert res_json.get('result') == 'User not in the project'


async def test_upload_with_conflict_should_return_409(
    test_async_client_auth, mocker):
    payload = {
        "operator": "test_user",
        "upload_message": "test",
        "type": "processed",
        "zone": "zone",
        "filename": "fake.png",
        "job_type": "AS_FILE",
        "dcm_id": "undefined",
        "current_folder_node": "",
        "data": [
            {"resumable_filename": "fake.png", "resumable_relative_path": ""}
            ]
    }
    mocker.patch(
        'app.routers.v1.api_project.validate_upload_event',
        return_value=None)
    mocker.patch(
        'app.routers.v1.api_project.check_file_exist',
        return_value={})
    mock_response = Response()
    mock_response.status_code = 409
    mock_response._content = b'{ "error_msg" : "mock_conflict" }'
    mocker.patch('app.routers.v1.api_project.transfer_to_pre',
                 return_value=mock_response)
    header = {'Authorization': 'fake token'}
    response = await test_async_client_auth.post(
        test_get_project_file_api,
        headers=header,
        json=payload
        )
    res_json = response.json()
    assert res_json.get('code') == 409
    assert res_json.get('error_msg') == "mock_conflict"


async def test_upload_with_internal_error_should_return_500(
    test_async_client_auth, mocker
    ):
    payload = {
        "operator": "test_user",
        "upload_message": "test",
        "type": "processed",
        "zone": "zone",
        "filename": "fake.png",
        "job_type": "AS_FILE",
        "dcm_id": "undefined",
        "current_folder_node": "",
        "data": [
            {"resumable_filename": "fake.png", "resumable_relative_path": ""}
            ]
    }
    mocker.patch(
        'app.routers.v1.api_project.validate_upload_event',
        return_value=None)
    mocker.patch(
        'app.routers.v1.api_project.check_file_exist',
        return_value={})
    mock_response = Response()
    mock_response.status_code = 400
    mock_response._content = b'{ "error_msg" : "mock_internal_error" }'
    mocker.patch('app.routers.v1.api_project.transfer_to_pre',
                 return_value=mock_response)
    header = {'Authorization': 'fake token'}
    response = await test_async_client_auth.post(
        test_get_project_file_api,
        headers=header,
        json=payload
        )
    res_json = response.json()
    assert res_json.get('code') == 500
    assert res_json.get('error_msg') == "Upload Error: mock_internal_error"


async def test_get_folder_in_project_should_return_200(
    test_async_client_auth,
    mocker,
    httpx_mock: HTTPXMock):
    param = {
        'zone': 'zone',
        'project_code': project_code,
        'folder': "testuser/fake_folder"
        }
    mocker.patch(
        'app.routers.v1.api_project.get_zone',
        return_value="zone")
    mocker.patch(
        'app.routers.v1.api_project.has_permission',
        return_value=True)
    httpx_mock.add_response(
        method='GET',
        url=(
            'http://metadata_service/v1/items/search/'
            '?container_code=test_project'
            '&container_type=project'
            '&parent_path=testuser'
            '&recursive=false'
            '&zone=zone'
            '&archived=false'
            '&name=fake_folder'
            ),
        json={
            "code": 200,
            "result": [{
                "id": "item-id",
                "parent": "parent-id",
                "parent_path": "testuser",
                "restore_path": None,
                "archived": False,
                "type": "folder",
                "zone": 0,
                "name": "fake_folder",
                "size": 0,
                "owner": "testuser",
                "container_code": project_code,
                "container_type": "project",
                "created_time": "2022-04-13 18:17:51.008212",
                "last_updated_time": "2022-04-13 18:17:51.008227",
                "storage": {
                    "id": "8cd8cef7-2603-4ec3-b5a0-479e58e4c9d9",
                    "location_uri": "",
                    "version": "1.0"
                    },
                "extended": {
                    "id": "96510da0-22f4-4487-ac88-71cd48967c8d",
                    "extra": {
                        "tags": [],
                        "attributes": {}
                            }
                        }
                    },
                {
                    "id": "item-id2",
                    "parent": "parent-id2"}
                    ]
                    },
        status_code=200,
    )
    header = {'Authorization': 'fake token'}
    res = await test_async_client_auth.get(
        test_get_project_folder_api,
        headers=header,
        query_string=param
        )
    res_json = res.json()
    assert res_json.get('code') == 200
    result = res_json.get('result')
    assert result.get('type') == 'folder'
    assert result.get('name') == "fake_folder"
    assert result.get('zone') == 0
    assert result.get('container_code') == project_code


async def test_get_folder_in_project_without_token_should_return_401(
    test_async_client):
    param = {'zone': 'zone',
             'project_code': project_code,
             'folder': "fake_user/fake_folder"
             }
    res = await test_async_client.get(
        test_get_project_folder_api,
        query_string=param
        )
    res_json = res.json()
    assert res_json.get('code') == 401
    assert res_json.get('error_msg') == "Token required"


async def test_get_folder_in_project_without_permission_should_return_403(
    test_async_client_auth, mocker):
    param = {'zone': 'zone',
             'project_code': project_code,
             'folder': "fake_user/fake_folder"
             }
    mocker.patch(
        'app.routers.v1.api_project.get_zone',
        return_value="zone")
    mocker.patch(
        'app.routers.v1.api_project.has_permission',
        return_value=False
        )
    header = {'Authorization': 'fake token'}
    res = await test_async_client_auth.get(
        test_get_project_folder_api,
        headers=header,
        query_string=param
        )
    res_json = res.json()
    assert res.status_code == 403
    assert res_json.get('error_msg') == "Permission Denied"


async def test_get_folder_not_in_own_namefolder_should_return_403(
    test_async_client_auth, mocker):
    param = {'zone': 'zone',
             'project_code': project_code,
             'folder': "testuser/fake_folder"
             }
    mocker.patch(
        'app.routers.v1.api_project.get_zone',
        return_value="zone")
    mocker.patch(
        'app.routers.v1.api_project.has_permission',
        return_value=False
        )
    header = {'Authorization': 'fake token'}
    res = await test_async_client_auth.get(
        test_get_project_folder_api,
        headers=header,
        query_string=param)
    res_json = res.json()
    assert res.status_code == 403
    assert res_json.get('error_msg') == "Permission Denied"


async def test_get_folder_fail_when_query_node_should_return_500(
    test_async_client_auth, mocker):
    param = {'zone': 'zone',
             'project_code': project_code,
             'folder': "testuser/fake_folder"
             }
    mocker.patch(
        'app.routers.v1.api_project.get_zone',
        return_value="zone")
    mocker.patch(
        'app.routers.v1.api_project.has_permission',
        return_value=True)
    mock_response = Response()
    mock_response.status_code = 400
    mock_response._content = b'{"result": [], "error_msg":"mock error"}'
    mocker.patch('app.routers.v1.api_project.query_node',
                 return_value=mock_response)
    header = {'Authorization': 'fake token'}
    res = await test_async_client_auth.get(
        test_get_project_folder_api,
        headers=header,
        query_string=param)
    res_json = res.json()
    assert res_json.get('code') == 500
    assert res_json.get('error_msg') == "Error Getting Folder: mock error"


async def test_get_folder_in_project_with_folder_not_found_should_return_404(
    test_async_client_auth, mocker,
    httpx_mock: HTTPXMock):
    param = {'zone': 'zone',
             'project_code': project_code,
             'folder': "testuser/fake_folder"
             }
    mocker.patch('app.routers.v1.api_project.get_zone',
                 return_value="zone")
    mocker.patch(
        'app.routers.v1.api_project.has_permission',
        return_value=True
        )
    httpx_mock.add_response(
        method='GET',
        url=(
            'http://metadata_service/v1/items/search/'
            '?container_code=test_project'
            '&container_type=project'
            '&parent_path=testuser'
            '&recursive=false'
            '&zone=zone'
            '&archived=false'
            '&name=fake_folder'
            ),
        json={"code": 200, "result": []},
        status_code=200,
    )
    header = {'Authorization': 'fake token'}
    res = await test_async_client_auth.get(
        test_get_project_folder_api,
        headers=header,
        query_string=param
        )
    res_json = res.json()
    assert res.status_code == 404
    assert res_json.get('error_msg') == 'Folder not exist'
