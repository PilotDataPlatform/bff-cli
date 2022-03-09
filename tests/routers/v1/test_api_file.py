import pytest
from pytest_httpx import HTTPXMock
from tests.helper import EAPIResponseCode
pytestmark = pytest.mark.asyncio

test_query_geid_api = "/v1/query/geid"
test_get_file_api = "/v1/test_project/files/query"
project_code = "test_project"


async def test_get_name_folders_in_project_should_return_200(test_async_client_auth, mocker, httpx_mock: HTTPXMock):
    param = {
        "project_code": project_code,
        "zone": "gr",
        "folder": '',
        "source_type": 'Container'
    }
    header = {'Authorization': 'fake token'}
    mocker.patch('app.routers.v1.api_file.check_permission',
                 return_value={"code": 200,
                               'project_code': project_code,
                               'uploader': 'fake_user'})
    httpx_mock.add_response(
        method='POST',
        url='http://neo4j_service/v1/neo4j/relations/query',
        json=[{
            "end_node": {
                "name": "test_file"
            },
            "p": {
                "amyguindoc14": {}
            },
            "r": {
                "type": "admin",
                "status": "active"
            },
            "start_node": {
                "id": 4376
            }
        }],
        status_code=200,
    )
    res = await test_async_client_auth.get(test_get_file_api, headers=header, query_string=param)
    res_json = res.json()
    assert res.status_code == 200
    assert res_json.get('code') == 200
    result = res_json.get('result')
    name_folders = []
    for f in result:
        name_folders.append(f.get('name'))
    assert 'test_file' in name_folders


async def test_get_files_in_folder_should_return_200(test_async_client_auth, mocker, httpx_mock: HTTPXMock):
    param = {
        "project_code": project_code,
        "zone": "gr",
        "folder": 'fake_user/fake_folder',
        "source_type": 'Folder'
    }
    header = {'Authorization': 'fake token'}
    mocker.patch('app.routers.v1.api_file.check_permission',
                 return_value={"code": 200,
                               'project_code': project_code,
                               'uploader': 'fake_user'})
    httpx_mock.add_response(
        method='POST',
        url='http://neo4j_service/v2/neo4j/nodes/query',
        json={"result": [{"labels": ["zone", "Folder"],
                          "project_code": "test_project", "name": "fake_folder"}]},
        status_code=200,
    )
    httpx_mock.add_response(
        method='POST',
        url='http://neo4j_service/v1/neo4j/relations/query',
        json=[{
            "end_node": {
                "name": "test_file"
            },
            "p": {
                "amyguindoc14": {}
            },
            "r": {
                "type": "admin",
                "status": "active"
            },
            "start_node": {
                "id": 4376
            }
        }],
        status_code=200,
    )
    res = await test_async_client_auth.get(test_get_file_api, headers=header, query_string=param)
    res_json = res.json()
    assert res.status_code == 200
    assert res_json.get('code') == 200
    result = res_json.get('result')
    files = []
    for f in result:
        files.append(f.get('name'))
    assert 'test_file' in files


async def test_get_folder_without_token(test_async_client):
    param = {
        "project_code": project_code,
        "zone": "zone",
        "folder": '',
        "source_type": 'Container'
    }
    res = await test_async_client.get(test_get_file_api, query_string=param)
    res_json = res.json()
    assert res_json.get('code') == 401
    assert res_json.get('error_msg') == "Token required"


async def test_get_files_in_folder_without_folder_name_should_return_400(test_async_client_auth, mocker):
    param = {"project_code": project_code,
                "zone": "gr",
                "folder": "",
                "source_type": 'Folder'}
    header = {'Authorization': 'fake token'}
    res = await test_async_client_auth.get(test_get_file_api, headers=header, query_string=param)
    res_json = res.json()
    assert res.status_code == 400
    assert res_json.get('error_msg') == "missing folder name"


async def test_get_files_without_permission_should_return_403(test_async_client_auth, mocker):
    param = {"project_code": project_code,
                "zone": "cr",
                "folder": "fake_folder",
                "source_type": 'Folder'}
    header = {'Authorization': 'fake token'}
    mocker.patch('app.routers.v1.api_file.check_permission',
                 return_value={'error_msg': "Permission Denied",
                               'code': EAPIResponseCode.forbidden,
                               'result': "Contributor"})
    res = await test_async_client_auth.get(test_get_file_api, headers=header, query_string=param)
    res_json = res.json()
    assert res.status_code == 403
    assert res_json.get('error_msg') == "Permission Denied"


async def test_get_files_when_folder_does_not_exist_should_return_403(test_async_client_auth, mocker, httpx_mock):
    param = {"project_code": project_code,
             "zone": "gr",
             "folder": "fake_user/fake_folder",
             "source_type": 'Folder'}
    header = {'Authorization': 'fake token'}
    mocker.patch('app.routers.v1.api_file.check_permission',
                 return_value={"code": 200,
                               'project_code': project_code,
                               'uploader': 'fake_user'})
    httpx_mock.add_response(
        method='POST',
        url='http://neo4j_service/v2/neo4j/nodes/query',
        json={"result": []},
        status_code=200,
    )
    res = await test_async_client_auth.get(test_get_file_api, headers=header, query_string=param)
    res_json = res.json()
    assert res.status_code == 403
    assert res_json.get('error_msg') == 'Folder not exist'


async def test_get_files_when_only_namefolder_should_return_403(test_async_client_auth, mocker, httpx_mock):
    param = {"project_code": project_code,
             "zone": "cr",
             "folder": "fake_folder",
             "source_type": 'Folder'}
    header = {'Authorization': 'fake token'}
    mocker.patch('app.routers.v1.api_file.check_permission',
                 return_value={"code": 200,
                               'project_code': project_code,
                               'uploader': 'fake_user'})
    httpx_mock.add_response(
        method='POST',
        url='http://neo4j_service/v2/neo4j/nodes/query',
        json={"result": [{"labels": ["zone", "Folder"],
                          "project_code": "test_project", "name": "fake_folder"}]},
        status_code=200,
    )
    res = await test_async_client_auth.get(test_get_file_api, headers=header, query_string=param)
    res_json = res.json()
    assert res.status_code == 403
    assert res_json.get('error_msg') == "Permission Denied"


async def test_get_files_when_folder_not_belong_to_user_should_return_403(test_async_client_auth, mocker, httpx_mock):
    param = {"project_code": project_code,
             "zone": "cr",
             "folder": "fake_admin/fake_folder",
             "source_type": 'Folder'}
    header = {'Authorization': 'fake token'}
    mocker.patch('app.routers.v1.api_file.check_permission',
                 return_value={"code": 200,
                               'project_code': project_code,
                               'uploader': 'fake_user'})
    httpx_mock.add_response(
        method='POST',
        url='http://neo4j_service/v2/neo4j/nodes/query',
        json={"result": [{"labels": ["zone", "Folder"],
                          "project_code": "test_project", "name": "fake_folder"}]},
        status_code=200,
    )
    res = await test_async_client_auth.get(test_get_file_api, headers=header, query_string=param)
    res_json = res.json()
    assert res.status_code == 403
    assert res_json.get('error_msg') == "Permission Denied"


async def test_get_files_when_neo4j_broke_should_return_500(test_async_client_auth, mocker, httpx_mock: HTTPXMock):
    param = {"project_code": project_code,
             "zone": "cr",
             "folder": "fake_user/fake_folder",
             "source_type": 'Folder'}
    header = {'Authorization': 'fake token'}
    mocker.patch('app.routers.v1.api_file.check_permission',
                 return_value={"code": 200,
                               'project_code': project_code,
                               'uploader': 'fake_user'})
    httpx_mock.add_response(
        method='POST',
        url='http://neo4j_service/v2/neo4j/nodes/query',
        json={"result": [{"labels": ["zone", "Folder"],
                          "project_code": "test_project", "name": "fake_folder"}]},
        status_code=200,
    )
    httpx_mock.add_response(
        method='POST',
        url='http://neo4j_service/v1/neo4j/relations/query',
        status_code=500,
    )
    res = await test_async_client_auth.get(test_get_file_api, headers=header, query_string=param)
    assert res.status_code == 500


async def test_query_file_by_geid_should_get_200(test_async_client_auth, mocker, httpx_mock):
    payload = {'geid': ["file_geid", "folder_file_geid"]}
    header = {'Authorization': 'fake token'}
    httpx_mock.add_response(
        method='POST',
        url='http://neo4j_service/v1/neo4j/nodes/query/geids',
        json={
            "result": [
                {
                    "labels": ["File"],
                    "global_entity_id": "file_geid",
                    "display_path": "testuser/fake_file",
                    "project_code": project_code,
                    "archived": False
                },
                {
                    "labels": ["Folder"],
                    "global_entity_id": "folder_file_geid",
                    "display_path": "testuser/fake_folder",
                    "project_code": project_code,
                    "archived": False
                }
            ]
        },
        status_code=200,
    )
    mocker.patch('app.routers.v1.api_file.check_permission',
                 return_value={"code": 200,
                               'project_code': project_code,
                               'uploader': 'testuser'})
    res = await test_async_client_auth.post(test_query_geid_api, headers=header, json=payload)
    assert res.status_code == 200
    res_json = res.json()
    result = res_json.get('result')
    assert len(result) == 2
    for entity in result:
        assert entity["geid"] in payload['geid']


async def test_query_file_by_geid_wiht_token(test_async_client):
    payload = {'geid': ["file_geid", "folder_file_geid"]}
    res = await test_async_client.post(test_query_geid_api, json=payload)
    res_json = res.json()
    assert res_json.get('code') == 401
    assert res_json.get('error_msg') == "Token required"


async def test_query_file_by_geid_when_file_not_found(test_async_client_auth, httpx_mock):
    payload = {'geid': ["file_geid", "folder_file_geid"]}
    header = {'Authorization': 'fake token'}
    httpx_mock.add_response(
        method='POST',
        url='http://neo4j_service/v1/neo4j/nodes/query/geids',
        json={
            "result": []
        },
        status_code=200,
    )
    res = await test_async_client_auth.post(test_query_geid_api, headers=header, json=payload)
    assert res.status_code == 200
    res_json = res.json()
    result = res_json.get('result')
    for entity in result:
        assert entity["status"] == 'File Not Exist'
        assert entity["result"] == []


async def test_query_file_by_geid_get_trashfile(test_async_client_auth, httpx_mock):
    payload = {'geid': ["file_geid"]}
    header = {'Authorization': 'fake token'}
    httpx_mock.add_response(
        method='POST',
        url='http://neo4j_service/v1/neo4j/nodes/query/geids',
        json={
            "result": [
                {
                    "labels": ["TrashFile"],
                    "global_entity_id": "file_geid",
                    "display_path": "testuser/fake_file",
                    "project_code": project_code,
                    "archived": False
                }
            ]
        },
        status_code=200,
    )
    res = await test_async_client_auth.post(test_query_geid_api, headers=header, json=payload)
    assert res.status_code == 200
    res_json = res.json()
    result = res_json.get('result')
    for entity in result:
        assert entity["result"] == []


async def test_query_file_by_geid_when_file_is_archived(test_async_client_auth, httpx_mock):
    payload = {'geid': ["file_geid"]}
    header = {'Authorization': 'fake token'}
    httpx_mock.add_response(
        method='POST',
        url='http://neo4j_service/v1/neo4j/nodes/query/geids',
        json={
            "result": [
                {
                    "labels": ["File"],
                    "global_entity_id": "file_geid",
                    "display_path": "testuser/fake_file",
                    "project_code": project_code,
                    "archived": True
                }
            ]
        },
        status_code=200,
    )
    res = await test_async_client_auth.post(test_query_geid_api, headers=header, json=payload)
    assert res.status_code == 200
    res_json = res.json()
    result = res_json.get('result')
    for entity in result:
        assert entity["result"] == []


async def test_query_file_by_geid_without_permission(test_async_client_auth, httpx_mock, mocker):
    payload = {'geid': ["file_geid", "folder_file_geid"]}
    header = {'Authorization': 'fake token'}
    httpx_mock.add_response(
        method='POST',
        url='http://neo4j_service/v1/neo4j/nodes/query/geids',
        json={
            "result": [
                {
                    "labels": ["File"],
                    "global_entity_id": "file_geid",
                    "display_path": "testuser/fake_file",
                    "project_code": project_code,
                    "archived": False
                },
                {
                    "labels": ["Folder"],
                    "global_entity_id": "folder_file_geid",
                    "display_path": "testuser/fake_folder",
                    "project_code": project_code,
                    "archived": False
                }
            ]
        },
        status_code=200,
    )
    mocker.patch('app.routers.v1.api_file.check_permission',
                 return_value={'error_msg': "Permission Denied",
                               'code': EAPIResponseCode.forbidden,
                               'result': "Contributor"})
    res = await test_async_client_auth.post(test_query_geid_api, headers=header, json=payload)
    assert res.status_code == 200
    res_json = res.json()
    result = res_json.get('result')
    for entity in result:
        assert entity["status"] == "Permission Denied"
        assert entity["result"] == []
