import pytest
from app.models.error_model import InvalidEncryptionError


test_validate_id_api = '/v1/validate/gid'
test_validate_manifest_api = '/v1/validate/manifest'
test_validate_env_api = '/v1/validate/env'


@pytest.mark.asyncio
async def test_validate_gid_should_return_200(test_async_client_auth):
    payload = {'generate_id': 'ABC-1234'}
    res = await test_async_client_auth.post(test_validate_id_api, json=payload)
    res_json = res.json()
    assert res_json.get('code') == 200
    assert res_json.get('result') == 'Valid'


@pytest.mark.asyncio
@pytest.mark.parametrize("test_input",["A-1234", "ABC-12", "abc-1234", "ABC-12345", "ABC12345", "ABC-!"])
async def test_invalidate_gid_should_return_400(test_async_client_auth, test_input):
    payload = {'generate_id': test_input}
    res = await test_async_client_auth.post(test_validate_id_api, json=payload)
    res_json = res.json()
    assert res_json.get('code') == 400
    assert res_json.get('result') == 'Invalid Generate ID'


@pytest.mark.asyncio
async def test_validate_attribute_should_return_200(test_async_client_auth, mocker):
    payload = {
        "manifest_json": {
            "manifest_name": "fake_manifest",
            "project_code": "test_project",
            "attributes": {
                "attr1": "a1",
                "attr2": "Test manifest text value",
                "attr3": "t1"
            }
        }
    }
    mocker.patch('app.routers.v1.api_validation.RDConnection.get_manifest_name_from_project_in_db',
             mock_get_manifest_name_from_project_in_db)
    mocker.patch('app.routers.v1.api_validation.ManifestValidator.has_valid_attributes',
                 mock_has_valid_attributes)
    res = await test_async_client_auth.post(test_validate_manifest_api, json=payload)
    res_json = res.json()
    assert res_json.get('code') == 200
    assert res_json.get('result') == 'Valid'


@pytest.mark.asyncio
async def test_validate_attribute_with_manifest_not_found_return_404(test_async_client_auth, mocker):
    payload = {
        "manifest_json": {
            "manifest_name": "Manifest1",
            "project_code": "test_project",
            "attributes": {
                "attr1": "a1",
                "attr2": "Test manifest text value",
                "attr3": "t1"
            }
        }
    }
    mocker.patch('app.routers.v1.api_validation.RDConnection.get_manifest_name_from_project_in_db',
                 mock_get_manifest_name_from_project_in_db)
    res = await test_async_client_auth.post(test_validate_manifest_api, json=payload)
    res_json = res.json()
    assert res_json.get('code') == 404
    assert res_json.get('result') == 'Manifest Not Exist Manifest1'


@pytest.mark.asyncio
async def test_invalidate_attribute_should_return_400(test_async_client_auth, mocker):
    payload = {
        "manifest_json": {
            "manifest_name": "Manifest",
            "project_code": "test_project",
            "attributes": {
                "attr1": "a1",
                "attr2": "Test manifest text value",
                "attr3": "t1"
            }
        }
    }
    mocker.patch('app.routers.v1.api_validation.RDConnection.get_manifest_name_from_project_in_db',
                 mock_get_manifest_name_from_project_in_db)
    mocker.patch('app.routers.v1.api_validation.ManifestValidator.has_valid_attributes',
                 mock_has_valid_attributes)
    res = await test_async_client_auth.post(test_validate_manifest_api, json=payload)
    res_json = res.json()
    assert res_json.get('code') == 400
    assert res_json.get('result') == 'mock error'


@pytest.mark.asyncio
@pytest.mark.parametrize("test_action, test_zone", [("upload", "gr"), ("upload", "cr"), ("download", "cr")])
async def test_validate_env_should_return_200(test_async_client_auth, test_action, test_zone):
    payload = {"action": test_action, "environ": "", 'zone': test_zone}
    res = await test_async_client_auth.post(test_validate_env_api, json=payload)
    response = res.json()
    assert  response.get('result') == 'valid'
    assert response.get('code') == 200
    assert response.get('error_msg') == ''


@pytest.mark.asyncio
@pytest.mark.parametrize("test_action, test_zone", [("upload", "gr"), ("download", "gr")])
async def test_validate_env_with_encrypted_message_should_return_200(test_async_client_auth, mocker, test_action, test_zone):
    payload = {"action": test_action, "environ": "gr", 'zone': test_zone}
    mocker.patch('app.routers.v1.api_validation.decryption',
                 return_value="gr")
    res = await test_async_client_auth.post(test_validate_env_api, json=payload)
    response = res.json()
    assert response.get('result') == 'valid'
    assert response.get('code') == 200
    assert response.get('error_msg') == ''


@pytest.mark.asyncio
@pytest.mark.parametrize("test_action, test_zone", [("download", "gr")])
async def test_invalidate_env_should_return_403(test_async_client_auth, test_action, test_zone):
    payload = {"action": test_action, "environ": "", 'zone': test_zone}
    res = await test_async_client_auth.post(test_validate_env_api, json=payload)
    response = res.json()
    assert response.get('result') == 'Invalid'
    assert response.get('code') == 403


@pytest.mark.asyncio
@pytest.mark.parametrize("test_action, test_zone", [("upload", "cr"), ("download", "cr")])
async def test_invalidate_env_with_encrypted_message_should_return_403(test_async_client_auth, mocker, test_action, test_zone):
    payload = {"action": test_action, "environ": "gr", 'zone': test_zone}
    mocker.patch('app.routers.v1.api_validation.decryption',
                 return_value="gr")
    res = await test_async_client_auth.post(test_validate_env_api, json=payload)
    response = res.json()
    assert response.get('result') == 'Invalid'
    assert response.get('code') == 403


@pytest.mark.asyncio
async def test_validate_env_with_wrong_zone_should_return_400(test_async_client_auth):
    payload = {"action": "test_action", "environ": "", 'zone': "zone"}
    res = await test_async_client_auth.post(test_validate_env_api, json=payload)
    response = res.json()
    assert response.get('result') == 'Invalid'
    assert response.get('code') == 400


@pytest.mark.asyncio
async def test_validate_env_with_decryption_error_should_return_400(test_async_client_auth, mocker):
    payload = {"action": "test_action", "environ": "gr", 'zone': "gr"}
    mocker.patch('app.routers.v1.api_validation.decryption',
                 side_effect=InvalidEncryptionError("Invalid encryption, could not decrypt message"))
    res = await test_async_client_auth.post(test_validate_env_api, json=payload)
    response = res.json()

    assert response.get('result') == 'Invalid'
    assert response.get('code') == 400


def mock_has_valid_attributes(arg1, arg2):
    if arg2.get("manifest_name", "") == "Manifest":
        return "mock error"
    return ""


def mock_get_manifest_name_from_project_in_db(arg1, arg2):
    if arg2.get("manifest_name", "") == "Manifest1":
        return ""
    result = [{'name': "fake_manifest", 'id': 1}]
    return result
