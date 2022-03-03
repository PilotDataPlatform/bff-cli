import pytest
from tests.helper import EAPIResponseCode

test_api = "/v1/manifest"
test_export_api = "/v1/manifest/export"
test_manifest_attach_api = "/v1/manifest/attach"
project_code = "cli"

@pytest.mark.asyncio
async def test_get_attributes_without_token(test_async_client):
    payload = {'project_code': project_code}
    res = await test_async_client.get(test_api, query_string=payload)
    res_json = res.json()
    assert res_json.get('code') == 401
    assert res_json.get('error_msg') == "Token required"

@pytest.mark.asyncio
async def test_get_attributes_should_return_200(test_async_client_auth, mocker):
    payload = {'project_code': project_code}
    header = {'Authorization': 'fake token'}
    mocker.patch('app.routers.v1.api_manifest.has_permission', return_value=True)
    mocker.patch('app.routers.v1.api_manifest.RDConnection.get_manifest_name_from_project_in_db', \
        mock_get_manifest_name_from_project_in_db)
    mocker.patch('app.routers.v1.api_manifest.RDConnection.get_attributes_in_manifest_in_db', \
        mock_get_attributes_in_manifest_in_db)
    res = await test_async_client_auth.get(test_api, headers=header, query_string=payload)
    res_json = res.json()
    assert res_json.get('code')== 200
    assert len(res_json.get('result')) >= 1


@pytest.mark.asyncio
async def test_get_attributes_no_access_should_return_403(test_async_client_auth, mocker):
    payload = {'project_code': project_code}
    headers = {'Authorization': 'fake token'}
    mocker.patch('app.routers.v1.api_manifest.has_permission', return_value=False)
    res = await test_async_client_auth.get(test_api, headers=headers, query_string=payload)
    res_json = res.json()
    assert res_json.get('code') == 403
    assert res_json.get('error_msg').lower() == "Permission Denied".lower()

@pytest.mark.asyncio
async def test_get_attributes_project_not_exist_should_return_403(test_async_client_auth, mocker):
    payload = {'project_code': 't1000'}
    headers = {'Authorization': 'fake token'}
    mocker.patch('app.routers.v1.api_manifest.has_permission', return_value=False)
    res = await test_async_client_auth.get(test_api, headers=headers, query_string=payload)
    res_json = res.json()
    assert res_json.get('code') == 403
    assert res_json.get('error_msg').lower() == "Permission Denied".lower()


# Test export manifest
@pytest.mark.asyncio
async def test_export_attributes_without_token(test_async_client):
    param = {'project_code': project_code,
             'manifest_name': 'Manifest1'}
    res = await test_async_client.get(test_export_api, query_string=param)
    res_json = res.json()
    assert res_json.get('code') == 401
    assert res_json.get('error_msg') == "Token required"

@pytest.mark.asyncio
async def test_export_attributes_should_return_200(test_async_client_auth, mocker):
    param = {'project_code': project_code,
                'manifest_name': 'fake_manifest'}
    headers = {'Authorization': 'fake token'}
    mocker.patch('app.routers.v1.api_manifest.has_permission', return_value=True)
    mocker.patch('app.routers.v1.api_manifest.RDConnection.get_manifest_name_from_project_in_db', \
        mock_get_manifest_name_from_project_in_db)
    mocker.patch('app.routers.v1.api_manifest.RDConnection.get_attributes_in_manifest_in_db', \
        mock_get_attributes_in_manifest_in_db)
    res = await test_async_client_auth.get(test_export_api, headers=headers, query_string=param)
    res_json = res.json()
    assert res_json.get('code') == 200
    assert res_json.get('result').get('manifest_name') == "fake_manifest"
    attribute_len = len(res_json.get('result')["attributes"])
    assert attribute_len == 1

@pytest.mark.asyncio
async def test_export_attributes_no_access(test_async_client_auth, mocker):
    param = {'project_code': project_code,
                'manifest_name': 'fake_manifest'}
    headers = {'Authorization': 'fake token'}
    mocker.patch('app.routers.v1.api_manifest.has_permission', return_value=False)
    res = await test_async_client_auth.get(test_export_api, headers=headers, query_string=param)
    res_json = res.json()
    assert res_json.get('code') == 403
    assert res_json.get('error_msg').lower() == "Permission Denied".lower()

@pytest.mark.asyncio
async def test_export_attributes_not_exist_should_return_404(test_async_client_auth, mocker):
    param = {'project_code': project_code,
                'manifest_name': 'Manifest1'}
    headers = {'Authorization': 'fake token'}
    mocker.patch('app.routers.v1.api_manifest.has_permission', return_value=True)
    mocker.patch('app.routers.v1.api_manifest.RDConnection.get_manifest_name_from_project_in_db', \
        mock_get_manifest_name_from_project_in_db)
    res = await test_async_client_auth.get(test_export_api, headers=headers, query_string=param)
    res_json = res.json()
    assert res_json.get('code') == 404
    assert res_json.get('error_msg') == 'Manifest Not Exist Manifest1'

@pytest.mark.asyncio
async def test_export_attributes_project_not_exist_should_return_403(test_async_client_auth, mocker):
    param = {'project_code': 't1000', 'manifest_name': 'fake_manifest'}
    headers = {'Authorization': 'fake token'}
    mocker.patch('app.routers.v1.api_manifest.has_permission', return_value=False)
    res = await test_async_client_auth.get(test_export_api, headers=headers, query_string=param)
    res_json = res.json()
    assert res_json.get('code') == 403
    assert res_json.get('error_msg').lower() == "Permission Denied".lower()

# test attach manifest to file
@pytest.mark.asyncio
async def test_attach_attributes_without_token_should_return_401(test_async_client):
    payload = {"manifest_json": {
                "manifest_name": "fake manifest",
                "project_code": project_code,
                "attributes": {"fake_attribute": "a1"},
                "file_name": "fake_file",
                "zone": "zone"
                }
            }
    res = await test_async_client.post(test_manifest_attach_api, json=payload)
    res_json = res.json()
    assert res_json.get('code') == 401
    assert res_json.get('error_msg') == "Token required"

@pytest.mark.asyncio
async def test_attach_attributes_should_return_200(test_async_client_auth, mocker):
    payload = {"manifest_json": {
                "manifest_name": "fake manifest",
                "project_code": project_code,
                "attributes": {"fake_attribute": "a1"},
                "file_name": "fake_file",
                "zone": "zone"
                }
            }
    header = {'Authorization': 'fake token'}
    mocker.patch('app.routers.v1.api_manifest.has_permission', return_value=True)
    mocker.patch('app.routers.v1.api_manifest.query_node',
                 return_value={
            "code": 200,
            "error_msg": "",
            "result": [
                {
                    "id": 1234,
                    "labels": [
                        "Folder",
                        "Core"
                    ],
                    "global_entity_id": "geid",
                    "display_path": "fake_user/fake_file",
                    "project_code": project_code,
                    "operator": "fake_user",
                    "tags": [],
                    "folder_level": 1,
                    "archived": False,
                    "list_priority": 10,
                    "folder_relative_path": "fake_user",
                    "time_lastmodified": "2021-11-19T20:33:52",
                    "uploader": "fake_user",
                    "name": "fake_file",
                    "time_created": "2021-11-19T20:33:52"
                }
            ],
            "page": 0,
            "total": 1,
            "num_of_pages": 1
        })
    mocker.patch('app.routers.v1.api_manifest.RDConnection.get_manifest_name_from_project_in_db',
                 mock_get_manifest_name_from_project_in_db)
    mocker.patch('app.routers.v1.api_manifest.attach_manifest_to_file',
                 return_value={
                     "code": 200,
                     "error_msg": "",
                     "result": {
                         'operation_status': 'SUCCEED'
                     }
                 })
    res = await test_async_client_auth.post(test_manifest_attach_api, headers=header, json=payload)
    res_json = res.json()
    assert res_json.get('code') == 200
    result = res_json.get('result')
    assert result.get('operation_status') == 'SUCCEED'

@pytest.mark.asyncio
async def test_attach_attributes_wrong_file_should_return_404(test_async_client_auth, mocker):
    payload = {"manifest_json": {
                "manifest_name": "fake manifest",
                "project_code": project_code,
                "attributes": {"fake_attribute": "a1"},
                "file_name": "fake_wrong_file",
                "zone": "zone"
                }
            }
    header = {'Authorization': 'fake token'}
    mocker.patch('app.routers.v1.api_manifest.has_permission', return_value=True)
    mocker.patch('app.routers.v1.api_manifest.query_node',
                 return_value={
            "code": 200,
            "error_msg": "",
            "result": [],
            "page": 0,
            "total": 1,
            "num_of_pages": 1
        })
    res = await test_async_client_auth.post(test_manifest_attach_api, headers=header, json=payload)
    res_json = res.json()
    assert res_json.get('code') == 404
    error = res_json.get('error_msg')
    assert error == 'File Not Exist' 


@pytest.mark.asyncio
async def test_attach_attributes_wrong_name_should_return_400(test_async_client_auth, mocker):
    payload = {"manifest_json": {
                "manifest_name": "Manifest1",
                "project_code": project_code,
                "attributes": {"fake_attribute": "wrong name"},
                "file_name": "fake_file",
                "zone": "zone"
                }
            }
    header = {'Authorization': 'fake token'}
    mocker.patch('app.routers.v1.api_manifest.has_permission', return_value=True)
    mocker.patch('app.routers.v1.api_manifest.query_node',
                 return_value={
            "code": 200,
            "error_msg": "",
            "result": [
                {
                    "id": 1234,
                    "labels": [
                        "Folder",
                        "Core"
                    ],
                    "global_entity_id": "geid",
                    "display_path": "fake_user/fake_file",
                    "project_code": project_code,
                    "operator": "fake_user",
                    "tags": [],
                    "folder_level": 1,
                    "archived": False,
                    "list_priority": 10,
                    "folder_relative_path": "fake_user",
                    "time_lastmodified": "2021-11-19T20:33:52",
                    "uploader": "fake_user",
                    "name": "fake_file",
                    "time_created": "2021-11-19T20:33:52"
                }
            ],
            "page": 0,
            "total": 1,
            "num_of_pages": 1
        })
    mocker.patch('app.routers.v1.api_manifest.RDConnection.get_manifest_name_from_project_in_db',
                 mock_get_manifest_name_from_project_in_db)
    res = await test_async_client_auth.post(test_manifest_attach_api, headers=header, json=payload)
    res_json = res.json()
    assert res_json.get('code') == 400
    error = res_json.get('error_msg')
    assert error == 'Manifest Not Exist Manifest1'

@pytest.mark.asyncio
async def test_attach_attributes_no_access_should_return_403(test_async_client_auth, mocker):
    payload = {"manifest_json": {
                "manifest_name": "fake manifest",
                "project_code": project_code,
                "attributes": {"fake_attribute": "wrong name"},
                "file_name": "fake_file",
                "zone": "zone"
                }
            }
    header = {'Authorization': 'fake token'}
    mocker.patch('app.routers.v1.api_manifest.has_permission', return_value=False)
    res = await test_async_client_auth.post(test_manifest_attach_api, headers=header, json=payload)
    res_json = res.json()
    assert res_json.get('code') == 403
    error = res_json.get('error_msg')
    assert error.lower() == 'Permission Denied'.lower()


@pytest.mark.asyncio
async def test_fail_to_attach_attributes_return_404(test_async_client_auth, mocker):
    payload = {"manifest_json": {
        "manifest_name": "fake manifest",
        "project_code": project_code,
        "attributes": {"fake_attribute": "wrong name"},
        "file_name": "fake_file",
        "zone": "zone"
    }
    }
    header = {'Authorization': 'fake token'}
    mocker.patch('app.routers.v1.api_manifest.has_permission', return_value=True)
    mocker.patch('app.routers.v1.api_manifest.query_node',
                 return_value={
            "code": 200,
            "error_msg": "",
            "result": [
                {
                    "id": 1234,
                    "labels": [
                        "Folder",
                        "Core"
                    ],
                    "global_entity_id": "geid",
                    "display_path": "fake_user/fake_file",
                    "project_code": project_code,
                    "operator": "fake_user",
                    "tags": [],
                    "folder_level": 1,
                    "archived": False,
                    "list_priority": 10,
                    "folder_relative_path": "fake_user",
                    "time_lastmodified": "2021-11-19T20:33:52",
                    "uploader": "fake_user",
                    "name": "fake_file",
                    "time_created": "2021-11-19T20:33:52"
                }
            ],
            "page": 0,
            "total": 1,
            "num_of_pages": 1
        })
    mocker.patch('app.routers.v1.api_manifest.RDConnection.get_manifest_name_from_project_in_db',
                 mock_get_manifest_name_from_project_in_db)
    mocker.patch('app.routers.v1.api_manifest.attach_manifest_to_file',
                 return_value=None)
    res = await test_async_client_auth.post(test_manifest_attach_api, headers=header, json=payload)
    res_json = res.json()
    assert res_json.get('code') == 404
    error = res_json.get('error_msg')
    assert error == 'File Not Exist'


def mock_get_manifest_name_from_project_in_db(arg1, arg2):
    if arg2.get("manifest_name", "") == "Manifest1":
        return ""
    result = [{'name': "fake_manifest", 'id': 1}]
    return result


def mock_get_attributes_in_manifest_in_db(arg1, arg2):
    result = [
        {
            'manifest_name': 'fake_manifest',
            'attributes': [{"name": "fake_attribute", "type": "type", "optional": True,
                                "value": ""}]
        }
    ]
    return result
