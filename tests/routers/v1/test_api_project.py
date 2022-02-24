import pytest
from requests.models import Response
from tests.helper import EAPIResponseCode

test_project_api = "/v1/projects"
test_get_project_file_api = "/v1/project/test_project/files"
test_get_project_folder_api = "/v1/project/test_project/folder"
project_code = "test_project"


@pytest.mark.asyncio
async def test_get_project_list_should_return_200(test_async_client_auth, mocker):
    test_project = ["project1", "project2", "project3"]
    mocker.patch('app.routers.v1.api_project.get_user_projects',
                 return_value=test_project)
    header = {'Authorization': 'fake token'}
    res = await test_async_client_auth.get(test_project_api, headers=header)
    res_json = res.json()
    projects = res_json.get('result')
    assert res.status_code == 200
    assert len(projects) == len(test_project)


@pytest.mark.asyncio
async def test_get_project_list_without_token_should_return_401(test_async_client):
    res = await test_async_client.get(test_project_api)
    res_json = res.json()
    assert res_json.get('code') == 401
    assert res_json.get('error_msg') == "Token required"


@pytest.mark.asyncio
async def test_upload_files_into_project_should_return_200(test_async_client_auth, mocker):
    payload = {
        "operator": "test_user",
        "upload_message": "test",
        "type": "processed",
        "zone": "zone",
        "filename": "fake.png",
        "job_type": "AS_FILE",
        "dcm_id": "undefined",
        "current_folder_node": "",
        "data": [{"resumable_filename": "fake.png", "resumable_relative_path": ""}]
        }
    mocker.patch('app.routers.v1.api_project.validate_upload_event',
                 return_value=None)
    mocker.patch('app.routers.v1.api_project.void_check_file_in_zone',
                 return_value={})
    mock_response = Response()
    mock_response.status_code = 200
    mock_response._content = b'{ "result" : "SUCCESSED" }'
    mocker.patch('app.routers.v1.api_project.transfer_to_pre',
                 return_value=mock_response)
    header = {'Authorization': 'fake token'}
    response = await test_async_client_auth.post(test_get_project_file_api, headers=header, json=payload)
    assert response.status_code == 200
    assert response.json()["result"] == "SUCCESSED"


@pytest.mark.asyncio
async def test_upload_files_with_invalid_upload_event_should_return_400(test_async_client_auth, mocker):
    payload = {
        "operator": "test_user",
        "upload_message": "test",
        "type": "processed",
        "zone": "zone",
        "filename": "fake.png",
        "job_type": "AS_FILE",
        "dcm_id": "undefined",
        "current_folder_node": "",
        "data": [{"resumable_filename": "fake.png", "resumable_relative_path": ""}]
    }
    mocker.patch('app.routers.v1.api_project.validate_upload_event',
                 return_value="Invalid Zone")
    header = {'Authorization': 'fake token'}
    response = await test_async_client_auth.post(test_get_project_file_api, headers=header, json=payload)
    res_json = response.json()
    assert res_json.get('code') == 400
    assert res_json.get('error_msg') == "Invalid Zone"


@pytest.mark.asyncio
async def test_upload_for_project_member_should_return_200(test_async_client_project_member_auth, mocker):
    payload = {
        "operator": "test_user",
        "upload_message": "test",
        "type": "processed",
        "zone": "zone",
        "filename": "fake.png",
        "job_type": "AS_FILE",
        "dcm_id": "undefined",
        "current_folder_node": "",
        "data": [{"resumable_filename": "fake.png", "resumable_relative_path": ""}]
    }
    mocker.patch('app.routers.v1.api_project.validate_upload_event',
                 return_value=None)
    mocker.patch('app.routers.v1.api_project.void_check_file_in_zone',
                 return_value={})
    mocker.patch('app.routers.v1.api_project.get_project_role',
                 return_value=('User not in the project', 400))
    header = {'Authorization': 'fake token'}
    response = await test_async_client_project_member_auth.post(test_get_project_file_api, headers=header, json=payload)
    res_json = response.json()
    assert res_json.get('code') == 403
    assert res_json.get('error_msg') == 'Permission Denied'
    assert res_json.get('result') == 'User not in the project'


@pytest.mark.asyncio
async def test_upload_for_contributor_into_core_should_return_403(test_async_client_project_member_auth, mocker):
    payload = {
        "operator": "test_user",
        "upload_message": "test",
        "type": "processed",
        "zone": "cr",
        "filename": "fake.png",
        "job_type": "AS_FILE",
        "dcm_id": "undefined",
        "current_folder_node": "",
        "data": [{"resumable_filename": "fake.png", "resumable_relative_path": ""}]
    }
    mocker.patch('app.routers.v1.api_project.validate_upload_event',
                 return_value=None)
    mocker.patch('app.routers.v1.api_project.void_check_file_in_zone',
                 return_value={})
    mocker.patch('app.routers.v1.api_project.get_project_role',
                 return_value=("contributor", 200))
    header = {'Authorization': 'fake token'}
    response = await test_async_client_project_member_auth.post(test_get_project_file_api, headers=header, json=payload)
    res_json = response.json()
    print(res_json)
    assert res_json.get('code') == 403
    assert res_json.get('error_msg') == 'Permission Denied'
    assert res_json.get('result') == 'contributor'


@pytest.mark.asyncio
async def test_upload_with_conflict_should_return_409(test_async_client_auth, mocker):
    payload = {
        "operator": "test_user",
        "upload_message": "test",
        "type": "processed",
        "zone": "zone",
        "filename": "fake.png",
        "job_type": "AS_FILE",
        "dcm_id": "undefined",
        "current_folder_node": "",
        "data": [{"resumable_filename": "fake.png", "resumable_relative_path": ""}]
    }
    mocker.patch('app.routers.v1.api_project.validate_upload_event',
                 return_value=None)
    mocker.patch('app.routers.v1.api_project.void_check_file_in_zone',
                 return_value={})
    mock_response = Response()
    mock_response.status_code = 409
    mock_response._content = b'{ "error_msg" : "mock_conflict" }'
    mocker.patch('app.routers.v1.api_project.transfer_to_pre',
                 return_value=mock_response)
    header = {'Authorization': 'fake token'}
    response = await test_async_client_auth.post(test_get_project_file_api, headers=header, json=payload)
    res_json = response.json()
    assert res_json.get('code') == 409
    assert res_json.get('error_msg') == "mock_conflict"


@pytest.mark.asyncio
async def test_upload_with_internal_error_should_return_500(test_async_client_auth, mocker):
    payload = {
        "operator": "test_user",
        "upload_message": "test",
        "type": "processed",
        "zone": "zone",
        "filename": "fake.png",
        "job_type": "AS_FILE",
        "dcm_id": "undefined",
        "current_folder_node": "",
        "data": [{"resumable_filename": "fake.png", "resumable_relative_path": ""}]
    }
    mocker.patch('app.routers.v1.api_project.validate_upload_event',
                 return_value=None)
    mocker.patch('app.routers.v1.api_project.void_check_file_in_zone',
                 return_value={})
    mock_response = Response()
    mock_response.status_code = 400
    mock_response._content = b'{ "error_msg" : "mock_internal_error" }'
    mocker.patch('app.routers.v1.api_project.transfer_to_pre',
                 return_value=mock_response)
    header = {'Authorization': 'fake token'}
    response = await test_async_client_auth.post(test_get_project_file_api, headers=header, json=payload)
    res_json = response.json()
    assert res_json.get('code') == 500
    assert res_json.get('error_msg') == "Upload Error: mock_internal_error"


@pytest.mark.asyncio
async def test_get_folder_in_project_should_return_200(test_async_client_auth, mocker):
    param = {'zone': 'zone',
                'project_code': project_code,
                'folder': "fake_user/fake_folder"
                }
    mocker.patch('app.routers.v1.api_project.get_zone',
                 return_value="zone")
    mocker.patch('app.routers.v1.api_project.check_permission',
                 return_value={ 'project_code': project_code})
    mock_response = Response()
    mock_response.status_code = 200
    mock_response._content = b'{"result": [{"labels": ["zone", "Folder"], \
        "project_code": "test_project", "name": "fake_folder"}]}'
    mocker.patch('app.routers.v1.api_project.http_query_node_zone',
                 return_value=mock_response)
    header = {'Authorization': 'fake token'}
    res = await test_async_client_auth.get(test_get_project_folder_api, headers=header, query_string=param)
    res_json = res.json()
    assert res_json.get('code') == 200
    result = res_json.get('result')
    assert set(result.get('labels')) == {'zone', 'Folder'}
    assert result.get('name') == "fake_folder"
    assert result.get('project_code') == project_code


@pytest.mark.asyncio
async def test_get_folder_in_project_without_token_should_return_401(test_async_client):
    param = {'zone': 'zone',
             'project_code': project_code,
             'folder': "fake_user/fake_folder"
             }
    res = await test_async_client.get(test_get_project_folder_api, query_string=param)
    res_json = res.json()
    print(res_json)
    assert res_json.get('code') == 401
    assert res_json.get('error_msg') == "Token required"


@pytest.mark.asyncio
async def test_get_folder_in_project_without_permission_should_return_403(test_async_client_auth, mocker):
    param = {'zone': 'zone',
             'project_code': project_code,
             'folder': "fake_user/fake_folder"
             }
    mocker.patch('app.routers.v1.api_project.get_zone',
                 return_value="zone")
    mocker.patch('app.routers.v1.api_project.check_permission',
                 return_value={'error_msg': "Permission Denied",
                               'code': EAPIResponseCode.forbidden,
                               'result': "Contributor"})
    header = {'Authorization': 'fake token'}
    res = await test_async_client_auth.get(test_get_project_folder_api, headers=header, query_string=param)
    res_json = res.json()
    assert res.status_code == 403
    assert res_json.get('error_msg') == "Permission Denied"


@pytest.mark.asyncio
async def test_get_folder_in_project_with_uploader_not_own_namefolder_should_return_403(test_async_client_auth, mocker):
    param = {'zone': 'zone',
             'project_code': project_code,
             'folder': "testuser/fake_folder"
             }
    mocker.patch('app.routers.v1.api_project.get_zone',
                 return_value="zone")
    mocker.patch('app.routers.v1.api_project.check_permission',
                 return_value={"code": 200,
                               'project_code': project_code,
                               'uploader': 'fake_user'})
    header = {'Authorization': 'fake token'}
    res = await test_async_client_auth.get(test_get_project_folder_api, headers=header, query_string=param)
    res_json = res.json()
    assert res.status_code == 403
    assert res_json.get('error_msg') == "Permission Denied"


@pytest.mark.asyncio
async def test_get_folder_fail_when_query_node_should_return_500(test_async_client_auth, mocker):
    param = {'zone': 'zone',
             'project_code': project_code,
             'folder': "fake_user/fake_folder"
             }
    mocker.patch('app.routers.v1.api_project.get_zone',
                 return_value="zone")
    mocker.patch('app.routers.v1.api_project.check_permission',
                 return_value={'project_code': project_code})
    mock_response = Response()
    mock_response.status_code = 400
    mock_response._content = b'{"result": [], "error_msg":"mock error"}'
    mocker.patch('app.routers.v1.api_project.http_query_node_zone',
                 return_value=mock_response)
    header = {'Authorization': 'fake token'}
    res = await test_async_client_auth.get(test_get_project_folder_api, headers=header, query_string=param)
    res_json = res.json()
    assert res_json.get('code') == 500
    assert res_json.get('error_msg') == "Upload Error: mock error"


@pytest.mark.asyncio
async def test_get_folder_in_project_with_folder_not_found_should_return_404(test_async_client_auth, mocker):
    param = {'zone': 'zone',
             'project_code': project_code,
             'folder': "fake_user/fake_folder"
             }
    mocker.patch('app.routers.v1.api_project.get_zone',
                 return_value="zone")
    mocker.patch('app.routers.v1.api_project.check_permission',
                 return_value={'project_code': project_code})
    mock_response = Response()
    mock_response.status_code = 200
    mock_response._content = b'{"result": []}'
    mocker.patch('app.routers.v1.api_project.http_query_node_zone',
                 return_value=mock_response)
    header = {'Authorization': 'fake token'}
    res = await test_async_client_auth.get(test_get_project_folder_api, headers=header, query_string=param)
    res_json = res.json()
    assert res.status_code == 404
    assert res_json.get('error_msg') == 'Folder not exist'
