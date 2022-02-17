import pytest
from pytest_httpx import HTTPXMock
from enum import Enum

test_query_geid_api = "/v1/query/geid"
test_get_file_api = "/v1/test_project/files/query"
project_code = "test_project"

# test get file/folder api in ptoject/folder


@pytest.mark.asyncio
async def test_get_name_folders_in_project_should_return_200(test_async_client_auth, mocker, httpx_mock: HTTPXMock):
    param = {
        "project_code": project_code,
        "zone": "zone",
        "folder": '',
        "source_type": 'Container'
    }
    header = {'Authorization': 'fake token'}
    mocker.patch('app.routers.v1.api_file.verify_list_event',
                 return_value=(EAPIResponseCode.success, ''))
    mocker.patch('app.routers.v1.api_file.get_zone',
                 return_value="zone")
    mocker.patch('app.routers.v1.api_file.check_permission',
                 return_value={"code": 200, 
                               'project_code': project_code,
                               'uploader': 'fake_user'})
    mocker.patch('app.routers.v1.api_file.get_parent_label',
                 return_value="Container")
    mocker.patch('app.routers.v1.api_file.separate_rel_path',
                 return_value=('', "fake_user"))
    mocker.patch('app.routers.v1.api_file.check_folder_exist',
                 return_value=(EAPIResponseCode.success, ''))
    httpx_mock.add_response(
        method='POST',
        url='http://neo4j_service/v1/neo4j/relations/query',
        json=[{'end_node':{"name": "fake_user"}}],
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
    assert 'fake_user' in name_folders


@pytest.mark.asyncio
async def test_get_files_in_folder_should_return_200(test_async_client_auth, mocker, httpx_mock: HTTPXMock):
    param = {
        "project_code": project_code,
        "zone": "zone",
        "folder": 'fake_user/fake_folder',
        "source_type": 'Folder'
    }
    header = {'Authorization': 'fake token'}
    mocker.patch('app.routers.v1.api_file.verify_list_event',
                 return_value=(EAPIResponseCode.success, ''))
    mocker.patch('app.routers.v1.api_file.get_zone',
                 return_value="zone")
    mocker.patch('app.routers.v1.api_file.check_permission',
                 return_value={"code": 200,
                               'project_code': project_code,
                               'uploader': 'fake_user'})
    mocker.patch('app.routers.v1.api_file.get_parent_label',
                 return_value="Folder")
    mocker.patch('app.routers.v1.api_file.separate_rel_path',
                 return_value=('fake_user/fake_folder', "fake_user"))
    mocker.patch('app.routers.v1.api_file.check_folder_exist',
                 return_value=(EAPIResponseCode.success, ''))
    httpx_mock.add_response(
        method='POST',
        url='http://neo4j_service/v1/neo4j/relations/query',
        json=[{'end_node': {"name": "fake_file"}}],
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
    assert 'fake_file' in files


@pytest.mark.asyncio
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


@pytest.mark.asyncio
async def test_get_files_in_folder_without_folder_name_should_return_400(test_async_client_auth, mocker):
    param = {"project_code": project_code,
                "zone": "zone",
                "folder": "",
                "source_type": 'Folder'}
    header = {'Authorization': 'fake token'}
    mocker.patch('app.routers.v1.api_file.verify_list_event',
                 return_value=(EAPIResponseCode.bad_request, 'missing folder name'))
    res = await test_async_client_auth.get(test_get_file_api, headers=header, query_string=param)
    res_json = res.json()
    assert res.status_code == 400
    assert res_json.get('error_msg') == "missing folder name"


@pytest.mark.asyncio
async def test_get_files_without_permission_should_return_403(test_async_client_auth, mocker):
    param = {"project_code": project_code,
                "zone": "zone",
                "folder": "fake_folder",
                "source_type": 'Folder'}
    header = {'Authorization': 'fake token'}
    mocker.patch('app.routers.v1.api_file.verify_list_event',
                 return_value=(EAPIResponseCode.success, ''))
    mocker.patch('app.routers.v1.api_file.get_zone',
                 return_value="zone")
    mocker.patch('app.routers.v1.api_file.check_permission',
                 return_value={'error_msg': "Permission Denied",
                               'code': EAPIResponseCode.forbidden,
                               'result': "Contributor"})
    res = await test_async_client_auth.get(test_get_file_api, headers=header, query_string=param)
    res_json = res.json()
    assert res.status_code == 403
    assert res_json.get('error_msg') == "Permission Denied"


@pytest.mark.asyncio
async def test_get_files_when_folder_does_not_exist_should_return_403(test_async_client_auth, mocker):
    param = {"project_code": project_code,
             "zone": "zone",
             "folder": "fake_folder",
             "source_type": 'Folder'}
    header = {'Authorization': 'fake token'}
    mocker.patch('app.routers.v1.api_file.verify_list_event',
                 return_value=(EAPIResponseCode.success, ''))
    mocker.patch('app.routers.v1.api_file.get_zone',
                 return_value="zone")
    mocker.patch('app.routers.v1.api_file.check_permission',
                 return_value={"code": 200,
                               'project_code': project_code,
                               'uploader': 'fake_user'})
    mocker.patch('app.routers.v1.api_file.get_parent_label',
                 return_value="Folder")
    mocker.patch('app.routers.v1.api_file.separate_rel_path',
                 return_value=('fake_user/fake_folder', "fake_user"))
    mocker.patch('app.routers.v1.api_file.check_folder_exist',
                 return_value=(EAPIResponseCode.not_found, 'Folder not exist'))
    res = await test_async_client_auth.get(test_get_file_api, headers=header, query_string=param)
    res_json = res.json()
    assert res.status_code == 403
    assert res_json.get('error_msg') == 'Folder not exist'


@pytest.mark.asyncio
async def test_get_files_when_no_namefolder_should_return_403(test_async_client_auth, mocker):
    param = {"project_code": project_code,
             "zone": "zone",
             "folder": "fake_folder",
             "source_type": 'Folder'}
    header = {'Authorization': 'fake token'}
    mocker.patch('app.routers.v1.api_file.verify_list_event',
                 return_value=(EAPIResponseCode.success, ''))
    mocker.patch('app.routers.v1.api_file.get_zone',
                 return_value="zone")
    mocker.patch('app.routers.v1.api_file.check_permission',
                 return_value={"code": 200,
                               'project_code': project_code,
                               'uploader': 'fake_user'})
    mocker.patch('app.routers.v1.api_file.get_parent_label',
                 return_value="Folder")
    mocker.patch('app.routers.v1.api_file.separate_rel_path',
                 return_value=('', "fake_folder"))
    mocker.patch('app.routers.v1.api_file.check_folder_exist',
                 return_value=(EAPIResponseCode.success, ''))
    res = await test_async_client_auth.get(test_get_file_api, headers=header, query_string=param)
    res_json = res.json()
    assert res.status_code == 403
    assert res_json.get('error_msg') == "Permission Denied"


@pytest.mark.asyncio
async def test_get_files_when_folder_not_belong_to_user_should_return_403(test_async_client_auth, mocker):
    param = {"project_code": project_code,
             "zone": "zone",
             "folder": "fake_folder",
             "source_type": 'Folder'}
    header = {'Authorization': 'fake token'}
    mocker.patch('app.routers.v1.api_file.verify_list_event',
                 return_value=(EAPIResponseCode.success, ''))
    mocker.patch('app.routers.v1.api_file.get_zone',
                 return_value="zone")
    mocker.patch('app.routers.v1.api_file.check_permission',
                 return_value={"code": 200,
                               'project_code': project_code,
                               'uploader': 'fake_user'})
    mocker.patch('app.routers.v1.api_file.get_parent_label',
                 return_value="Folder")
    mocker.patch('app.routers.v1.api_file.separate_rel_path',
                 return_value=('fake_admin/fake_folder', "fake_folder"))
    mocker.patch('app.routers.v1.api_file.check_folder_exist',
                 return_value=(EAPIResponseCode.success, ''))
    res = await test_async_client_auth.get(test_get_file_api, headers=header, query_string=param)
    res_json = res.json()
    assert res.status_code == 403
    assert res_json.get('error_msg') == "Permission Denied"


@pytest.mark.asyncio
async def test_get_files_when_neo4j_broke_should_return_500(test_async_client_auth, mocker, httpx_mock: HTTPXMock):
    param = {"project_code": project_code,
             "zone": "zone",
             "folder": "fake_folder",
             "source_type": 'Folder'}
    header = {'Authorization': 'fake token'}
    mocker.patch('app.routers.v1.api_file.verify_list_event',
                 return_value=(EAPIResponseCode.success, ''))
    mocker.patch('app.routers.v1.api_file.get_zone',
                 return_value="zone")
    mocker.patch('app.routers.v1.api_file.check_permission',
                 return_value={"code": 200,
                               'project_code': project_code,
                               'uploader': 'fake_user'})
    mocker.patch('app.routers.v1.api_file.get_parent_label',
                 return_value="Folder")
    mocker.patch('app.routers.v1.api_file.separate_rel_path',
                 return_value=('fake_user/fake_folder', "fake_user"))
    mocker.patch('app.routers.v1.api_file.check_folder_exist',
                 return_value=(EAPIResponseCode.success, ''))
    httpx_mock.add_response(
        method='POST',
        url='http://neo4j_service/v1/neo4j/relations/query',
        status_code=500,
    )
    res = await test_async_client_auth.get(test_get_file_api, headers=header, query_string=param)
    assert res.status_code == 500


@pytest.mark.asyncio
async def test_query_file_by_geid_should_get_200(test_async_client_auth, mocker):
    payload = {'geid': ["file_geid", "folder_file_geid"]}
    header = {'Authorization': 'fake token'}
    mocker.patch('app.routers.v1.api_file.batch_query_node_by_geid',
                 return_value=(["file_geid", "folder_file_geid"], {
                     "file_geid":{
                        "labels":["File"],
                        "archived":False,
                        "project_code": project_code,
                        "display_path": "fake_user/fake_file"
                     },
                     "folder_file_geid":{
                         "labels": ["Folder"],
                         "archived": False,
                         "project_code": project_code,
                         "display_path": "fake_user/fake_folder"
                     }
                 }))
    mocker.patch('app.routers.v1.api_file.check_permission',
                 return_value={"code": 200,
                               'project_code': project_code,
                               'uploader': 'fake_user'})
    res = await test_async_client_auth.post(test_query_geid_api, headers=header, json=payload)
    assert res.status_code == 200
    res_json = res.json()
    result = res_json.get('result')
    assert len(result) == 2
    for entity in result:
        assert entity["geid"] in payload['geid']
    

@pytest.mark.asyncio
async def test_query_file_by_geid_wiht_token(test_async_client):
    payload = {'geid': ["file_geid", "folder_file_geid"]}
    res = await test_async_client.post(test_query_geid_api, json=payload)
    res_json = res.json()
    assert res_json.get('code') == 401
    assert res_json.get('error_msg') == "Token required"


@pytest.mark.asyncio
async def test_query_file_by_geid_when_file_not_found(test_async_client_auth, mocker):
    payload = {'geid': ["file_geid", "folder_file_geid"]}
    header = {'Authorization': 'fake token'}
    mocker.patch('app.routers.v1.api_file.batch_query_node_by_geid',
                 return_value=([], {}))
    res = await test_async_client_auth.post(test_query_geid_api, headers=header, json=payload)
    assert res.status_code == 200
    res_json = res.json()
    result = res_json.get('result')
    for entity in result:
        assert entity["status"] == 'File Not Exist'
        assert entity["result"] == []


@pytest.mark.asyncio
async def test_query_file_by_geid_get_trashfile(test_async_client_auth, mocker):
    payload = {'geid': ["file_geid", "folder_file_geid"]}
    header = {'Authorization': 'fake token'}
    mocker.patch('app.routers.v1.api_file.batch_query_node_by_geid',
                 return_value=(["file_geid"], {
                     "file_geid": {
                         "labels": ["TrashFile"],
                         "archived": False,
                         "project_code": project_code,
                         "display_path": "fake_user/fake_file"
                     }
                 }))
    res = await test_async_client_auth.post(test_query_geid_api, headers=header, json=payload)
    assert res.status_code == 200
    res_json = res.json()
    result = res_json.get('result')
    for entity in result:
        assert entity["result"] == []


@pytest.mark.asyncio
async def test_query_file_by_geid_when_file_is_archived(test_async_client_auth, mocker):
    payload = {'geid': ["file_geid", "folder_file_geid"]}
    header = {'Authorization': 'fake token'}
    mocker.patch('app.routers.v1.api_file.batch_query_node_by_geid',
                 return_value=(["file_geid"], {
                     "file_geid": {
                         "labels": ["File"],
                         "archived": True,
                         "project_code": project_code,
                         "display_path": "fake_user/fake_file"
                     }
                 }))
    res = await test_async_client_auth.post(test_query_geid_api, headers=header, json=payload)
    assert res.status_code == 200
    res_json = res.json()
    result = res_json.get('result')
    for entity in result:
        assert entity["result"] == []


@pytest.mark.asyncio
async def test_query_file_by_geid_without_permission(test_async_client_auth, mocker):
    payload = {'geid': ["file_geid", "folder_file_geid"]}
    header = {'Authorization': 'fake token'}
    mocker.patch('app.routers.v1.api_file.batch_query_node_by_geid',
                 return_value=(["file_geid", "folder_file_geid"], {
                     "file_geid": {
                         "labels": ["File"],
                         "archived": False,
                         "project_code": project_code,
                         "display_path": "fake_user/fake_file"
                     },
                     "folder_file_geid": {
                         "labels": ["Folder"],
                         "archived": False,
                         "project_code": project_code,
                         "display_path": "fake_user/fake_folder"
                     }
                 }))
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


class EAPIResponseCode(Enum):
    success = 200
    internal_error = 500
    bad_request = 400
    not_found = 404
    forbidden = 403
    unauthorized = 401
    conflict = 409
