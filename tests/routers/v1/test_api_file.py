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
        "zone": "0",
        "folder": '',
        "source_type": 'Project'
    }
    header = {'Authorization': 'fake token'}
    mocker.patch('app.routers.v1.api_file.has_permission',
                 return_value=True)
    httpx_mock.add_response(
        method='GET',
        url='http://metadata_service/v1/item/search/?container_code=test_project&container_type=project&parent_path=&recursive=false&zone=0&archived=false',
        json={"code":200,"result": [{ 
                "id": "item-id", 
                "parent": "", 
                "parent_path": "", 
                "restore_path": None, 
                "archived": False, 
                "type": "folder", 
                "zone": 0, 
                "name": "namefolder1", 
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
                "id": "item-id", 
                "parent": "", 
                "parent_path": "", 
                "restore_path": None, 
                "archived": False, 
                "type": "folder", 
                "zone": 0, 
                "name": "namefolder2", 
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
                    ]
                    },
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
    assert 'namefolder1' in name_folders
    assert 'namefolder2' in name_folders


async def test_get_files_in_folder_should_return_200(test_async_client_auth, mocker, httpx_mock: HTTPXMock):
    param = {
        "project_code": project_code,
        "zone": "0",
        "folder": 'testuser/fake_folder',
        "source_type": 'Project'
    }
    header = {'Authorization': 'fake token'}
    mocker.patch('app.routers.v1.api_file.has_permission',
                 return_value=True)
    httpx_mock.add_response(
        method='GET',
        url='http://metadata_service/v1/item/search/?container_code=test_project&container_type=project&parent_path=testuser%2Ffake_folder&recursive=false&zone=0&archived=false',
        json={"code":200,"result": [{ 
                "id": "item-id", 
                "parent": "parent_folder", 
                "parent_path": "testuser/fake_folder", 
                "restore_path": None, 
                "archived": False, 
                "type": "file", 
                "zone": 0, 
                "name": "file1", 
                "size": 10, 
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
                "id": "item-id", 
                "parent": "parent_folder", 
                "parent_path": "testuser/fake_folder", 
                "restore_path": None, 
                "archived": False, 
                "type": "folder", 
                "zone": 0, 
                "name": "file2", 
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
                    ]
                    },
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
    assert 'file1' in files
    assert 'file2' in files


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


async def test_get_files_when_folder_does_not_exist_should_return_403(test_async_client_auth, mocker, httpx_mock):
    param = {"project_code": project_code,
             "zone": "0",
             "folder": "fake_user/fake_folder",
             "source_type": 'Project'}
    header = {'Authorization': 'fake token'}
    mocker.patch('app.routers.v1.api_file.has_permission',
                 return_value={"code": 200,
                               'project_code': project_code,
                               'uploader': 'fake_user'})
    httpx_mock.add_response(
        method='GET',
        url=f'http://metadata_service/v1/item/search/?container_code={project_code}&container_type=project&parent_path=fake_user%2Ffake_folder&recursive=false&zone=0&archived=false',
        json={"code":200,"result": []},
        status_code=200,
    )
    res = await test_async_client_auth.get(test_get_file_api, headers=header, query_string=param)
    res_json = res.json()
    assert res.status_code == 403
    assert res_json.get('error_msg') == 'Folder not exist'

async def test_get_files_when_folder_not_belong_to_user_should_return_403(test_async_client_project_member_auth, mocker):
    param = {"project_code": project_code,
             "zone": 0,
             "folder": "fake_admin/fake_folder",
             "source_type": 'Folder'}
    header = {'Authorization': 'fake token'}
    mocker.patch('app.routers.v1.api_file.has_permission',
             return_value=True)
    res = await test_async_client_project_member_auth.get(test_get_file_api, headers=header, query_string=param)
    res_json = res.json()
    assert res.status_code == 403
    assert res_json.get('error_msg') == "Permission Denied"



async def test_query_file_by_geid_should_get_200(test_async_client_auth, mocker, httpx_mock):
    payload = {'geid': ["file_geid", "folder_file_geid"]}
    header = {'Authorization': 'fake token'}
    httpx_mock.add_response(
        method='GET',
        url='http://metadata_service/v1/item/batch/?ids=file_geid&ids=folder_file_geid',
        json={
                "code": 200,
                "error_msg": "",
                "page": 0,
                "total": 1,
                "num_of_pages": 1,
                "result": [
                    {
                        'id': 'file_geid', 
                        'parent': 'c31b77df-07ae-43ff-a669-39f1748e1fe6', 
                        'parent_path': 'data.vre-storage.cli.jzhang21.cmd_fd_1641915686', 
                        'restore_path': None, 
                        'archived': True, 
                        'type': 'file', 
                        'zone': 0, 
                        'name': 'lay1_test_file_1641915686', 
                        'size': 1048576, 
                        'owner': 'jzhang21', 
                        'container_code': project_code, 
                        'container_type': 'project', 
                        'created_time': '2022-01-11 15:45:54.433842', 
                        'last_updated_time': '2022-01-11 15:51:32.014223', 
                        'storage': {
                            'id': 'eee98a0f-9485-41b6-82b9-115a8754f6db', 
                            'location_uri': 'minio://http://minio.minio:9000/gr-cli/jzhang21/cmd_fd_1641915686/lay1_test_file_1641915686', 
                            'version': 'a1cbf902-b47b-479a-a9cd-783592c7f265'}, 
                            'extended': {
                                'id': 'f99a544f-9fef-49a9-9365-bd250cc81487', 
                                'extra': {'tags': [], 'system_tags': [], 'attributes': {}}
                                }
                        },
                     {
                        'id': 'folder_file_geid', 
                        'parent': 'c31b77df-07ae-43ff-a669-39f1748e1fe6', 
                        'parent_path': 'data.vre-storage.cli.jzhang21.cmd_fd_1641915686', 
                        'restore_path': None, 
                        'archived': True, 
                        'type': 'file', 
                        'zone': 0, 
                        'name': 'lay1_test_file_1641915686', 
                        'size': 1048576, 
                        'owner': 'jzhang21', 
                        'container_code': project_code, 
                        'container_type': 'project', 
                        'created_time': '2022-01-11 15:45:54.433842', 
                        'last_updated_time': '2022-01-11 15:51:32.014223', 
                        'storage': {
                            'id': 'eee98a0f-9485-41b6-82b9-115a8754f6db', 
                            'location_uri': 'minio://http://minio.minio:9000/gr-cli/jzhang21/cmd_fd_1641915686/lay1_test_file_1641915686', 
                            'version': 'a1cbf902-b47b-479a-a9cd-783592c7f265'}, 
                            'extended': {
                                'id': 'f99a544f-9fef-49a9-9365-bd250cc81487', 
                                'extra': {'tags': [], 'system_tags': [], 'attributes': {}}
                                }
                        }
                ]
                },
        status_code=200
    )
    mocker.patch('app.routers.v1.api_file.has_permission',
                 return_value=True)
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
        method='GET',
        url='http://metadata_service/v1/item/batch/?ids=file_geid&ids=folder_file_geid',
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


async def test_query_file_by_geid_when_file_is_archived(test_async_client_auth, httpx_mock):
    payload = {'geid': ["file_geid1"]}
    header = {'Authorization': 'fake token'}
    httpx_mock.add_response(
        method='GET',
        url='http://metadata_service/v1/item/batch/?ids=file_geid1',
        json={
                "code": 200,
                "error_msg": "",
                "page": 0,
                "total": 1,
                "num_of_pages": 1,
                "result": [
                    {
                        'id': 'file_geid1', 
                        'parent': 'c31b77df-07ae-43ff-a669-39f1748e1fe6', 
                        'parent_path': 'data.vre-storage.cli.jzhang21.cmd_fd_1641915686', 
                        'restore_path': None, 
                        'archived': True, 
                        'type': 'file', 
                        'zone': 0, 
                        'name': 'lay1_test_file_1641915686', 
                        'size': 1048576, 
                        'owner': 'jzhang21', 
                        'container_code': project_code, 
                        'container_type': 'project', 
                        'created_time': '2022-01-11 15:45:54.433842', 
                        'last_updated_time': '2022-01-11 15:51:32.014223', 
                        'storage': {
                            'id': 'eee98a0f-9485-41b6-82b9-115a8754f6db', 
                            'location_uri': 'minio://http://minio.minio:9000/gr-cli/jzhang21/cmd_fd_1641915686/lay1_test_file_1641915686', 
                            'version': 'a1cbf902-b47b-479a-a9cd-783592c7f265'}, 
                            'extended': {
                                'id': 'f99a544f-9fef-49a9-9365-bd250cc81487', 
                                'extra': {'tags': [], 'system_tags': [], 'attributes': {}}
                                }
                        }
                ]
                },
        status_code=200
    )
    res = await test_async_client_auth.post(test_query_geid_api, headers=header, json=payload)
    assert res.status_code == 200
    res_json = res.json()
    result = res_json.get('result')
    for entity in result:
        assert entity["result"] == []

