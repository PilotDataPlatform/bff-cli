import pytest
from app.models.error_model import InvalidEncryptionError
# import unittest
# from app.config import ConfigClass
# from unittest import IsolatedAsyncioTestCase
# from httpx import AsyncClient
# from ...prepare_test import SetupTest
# from ...logger import Logger
# import os

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


# @unittest.skipUnless(case == 'environment' or case == 'all' or case=='', 'Run specific test')
# class TestEnvironmentValidation(IsolatedAsyncioTestCase):
#     log = Logger(name='test_environment_validation.log')
#     test = SetupTest(log)
#     app = test.client
#     test_api = "/v1/validate/env"
#     """
#     CLI Workbench VM Validation rules:

#     Greenroom VM:
#                 Greenroom        Core
#     Upload         Yes            No
#     Download       Yes            No

#     Core VM:
#                 Greenroom        Core
#     Upload         Yes            Yes
#     Download       No             Yes
#     """
#     async def test_01_upload_from_core_to_greenroom(self):
#         self.log.info('\n')
#         self.log.info("test_01_upload_from_greenroom_to_greenroom".center(80, '-'))
#         payload = {"action": 'upload', "environ": "", 'zone': ConfigClass.GREEN_ZONE_LABEL.lower()}
#         try:
#             async with AsyncClient(app=self.app, base_url="http://test") as ac:
#                 res = await ac.post(self.test_api, json=payload)
#             self.log.info(f"RESPONSE: {res.text}")
#             response = res.json()
#             result = response.get('result')
#             code = response.get('code')
#             error = response.get('error_msg')
#             self.log.info(F"COMPARING: {result} VS 'valid'")
#             self.assertEqual(result, 'valid')
#             self.log.info(F"COMPARING: {error} VS ''")
#             self.assertEqual(error, '')
#             self.log.info(F"COMPARING: {code} VS 200")
#             self.assertEqual(code, 200)
#         except Exception as e:
#             self.log.error(f"01 ERROR: {e}")
#             raise e

#     async def test_02_upload_from_core_to_core(self):
#         self.log.info('\n')
#         self.log.info("test_02_upload_from_core_to_core".center(80, '-'))
#         payload = {"action": 'upload', "environ": "", 'zone': ConfigClass.CORE_ZONE_LABEL.lower()}
#         try:
#             async with AsyncClient(app=self.app, base_url="http://test") as ac:
#                 res = await ac.post(self.test_api, json=payload)
#             self.log.info(f"RESPONSE: {res.text}")
#             response = res.json()
#             result = response.get('result')
#             code = response.get('code')
#             error = response.get('error_msg')
#             self.log.info(F"COMPARING: {result} VS 'valid'")
#             self.assertEqual(result, 'valid')
#             self.log.info(F"COMPARING: {error} VS ''")
#             self.assertEqual(error, '')
#             self.log.info(F"COMPARING: {code} VS 200")
#             self.assertEqual(code, 200)
#         except Exception as e:
#             self.log.error(f"02 ERROR: {e}")
#             raise e

#     async def test_03_download_from_core_in_core(self):
#         self.log.info('\n')
#         self.log.info("test_03_download_from_core_in_core".center(80, '-'))
#         payload = {"action": 'download', "environ": "", 'zone': ConfigClass.CORE_ZONE_LABEL.lower()}
#         try:
#             self.log.info(f"PAYLOAD: {payload}")
#             async with AsyncClient(app=self.app, base_url="http://test") as ac:
#                 res = await ac.post(self.test_api, json=payload)
#             self.log.info(f"RESPONSE: {res.text}")
#             response = res.json()
#             result = response.get('result')
#             code = response.get('code')
#             error = response.get('error_msg')
#             self.log.info(F"COMPARING: {result} VS 'valid'")
#             self.assertEqual(result, 'valid')
#             self.log.info(F"COMPARING: {error} VS ''")
#             self.assertEqual(error, '')
#             self.log.info(F"COMPARING: {code} VS 200")
#             self.assertEqual(code, 200)
#         except Exception as e:
#             self.log.error(f"03 ERROR: {e}")
#             raise e

#     async def test_04_download_from_greenroom_in_core(self):
#         self.log.info('\n')
#         self.log.info("test_03_download_from_core_in_core".center(80, '-'))
#         payload = {"action": 'download', "environ": "", 'zone': ConfigClass.GREEN_ZONE_LABEL.lower()}
#         try:
#             async with AsyncClient(app=self.app, base_url="http://test") as ac:
#                 res = await ac.post(self.test_api, json=payload)
#             self.log.info(f"RESPONSE: {res.text}")
#             response = res.json()
#             result = response.get('result')
#             code = response.get('code')
#             error = response.get('error_msg')
#             self.log.info(F"COMPARING: {result} VS 'Invalid'")
#             self.assertEqual(result, 'Invalid')
#             self.log.info(F"COMPARING: {error} VS 'Invalid action: download from {ConfigClass.GREEN_ZONE_LABEL.lower()} in {ConfigClass.CORE_ZONE_LABEL.lower}'")
#             self.assertEqual(error, f'Invalid action: download from {ConfigClass.GREEN_ZONE_LABEL.lower()} in {ConfigClass.CORE_ZONE_LABEL.lower()}')
#             self.log.info(F"COMPARING: {code} VS 403")
#             self.assertEqual(code, 403)
#         except Exception as e:
#             self.log.error(f"04 ERROR: {e}")
#             raise e

#     async def test_05_download_with_invalid_env(self):
#         self.log.info('\n')
#         self.log.info("test_05_download_with_invalid_env".center(80, '-'))
#         payload = {"action": 'download', "environ": "asdf", 'zone': ConfigClass.GREEN_ZONE_LABEL.lower()}
#         try:
#             async with AsyncClient(app=self.app, base_url="http://test") as ac:
#                 res = await ac.post(self.test_api, json=payload)
#             self.log.info(f"RESPONSE: {res.text}")
#             response = res.json()
#             result = response.get('result')
#             code = response.get('code')
#             error = response.get('error_msg')
#             self.log.info(F"COMPARING: {result} VS 'Invalid'")
#             self.assertEqual(result, 'Invalid')
#             self.log.info(F"COMPARING: {error} VS 'Invalid variable'")
#             self.assertEqual(error, 'Invalid variable')
#             self.log.info(F"COMPARING: {code} VS 400")
#             self.assertEqual(code, 400)
#         except Exception as e:
#             self.log.error(f"05 ERROR: {e}")
#             raise e

#     async def test_06_upload_with_invalid_zone(self):
#         self.log.info('\n')
#         self.log.info("test_06_upload_with_invalid_zone".center(80, '-'))
#         payload = {"action": 'upload', "environ": "", 'zone': 'green'}
#         try:
#             async with AsyncClient(app=self.app, base_url="http://test") as ac:
#                 res = await ac.post(self.test_api, json=payload)
#             self.log.info(f"RESPONSE: {res.text}")
#             response = res.json()
#             result = response.get('result')
#             code = response.get('code')
#             error = response.get('error_msg')
#             self.log.info(F"COMPARING: {result} VS 'Invalid'")
#             self.assertEqual(result, 'Invalid')
#             self.log.info(F"COMPARING: {error} VS 'Invalid zone'")
#             self.assertEqual(error, 'Invalid zone')
#             self.log.info(F"COMPARING: {code} VS 400")
#             self.assertEqual(code, 400)
#         except Exception as e:
#             self.log.error(f"06 ERROR: {e}")
#             raise e

#     @unittest.skipIf(zone_env=="", "Missing essential information")
#     async def test_07_upload_from_greenroom_to_greenroom(self):
#         self.log.info('\n')
#         self.log.info("test_07_upload_from_greenroom_to_greenroom".center(80, '-'))
#         payload = {"action": 'upload', "environ": zone_env, 'zone': ConfigClass.GREEN_ZONE_LABEL.lower()}
#         try:
#             async with AsyncClient(app=self.app, base_url="http://test") as ac:
#                 res = await ac.post(self.test_api, json=payload)
#             self.log.info(f"RESPONSE: {res.text}")
#             response = res.json()
#             result = response.get('result')
#             code = response.get('code')
#             error = response.get('error_msg')
#             self.log.info(F"COMPARING: {result} VS 'valid'")
#             self.assertEqual(result, 'valid')
#             self.log.info(F"COMPARING: {error} VS ''")
#             self.assertEqual(error, '')
#             self.log.info(F"COMPARING: {code} VS 200")
#             self.assertEqual(code, 200)
#         except Exception as e:
#             self.log.error(f"07 ERROR: {e}")
#             raise e

#     @unittest.skipIf(zone_env=="", "Missing essential information")
#     async def test_08_upload_from_greenroom_to_core(self):
#         self.log.info('\n')
#         self.log.info("test_08_upload_from_greenroom_to_core".center(80, '-'))
#         payload = {"action": 'upload', "environ": zone_env, 'zone': ConfigClass.CORE_ZONE_LABEL.lower()}
#         try:
#             async with AsyncClient(app=self.app, base_url="http://test") as ac:
#                 res = await ac.post(self.test_api, json=payload)
#             self.log.info(f"RESPONSE: {res.text}")
#             response = res.json()
#             result = response.get('result')
#             code = response.get('code')
#             error = response.get('error_msg')
#             self.log.info(F"COMPARING: {result} VS 'Invalid'")
#             self.assertEqual(result, 'Invalid')
#             self.log.info(F"COMPARING: {error} VS 'Invalid action: upload to {ConfigClass.CORE_ZONE_LABEL.lower()} in {ConfigClass.GREEN_ZONE_LABEL.lower()}'")
#             self.assertEqual(error, f'Invalid action: upload to {ConfigClass.CORE_ZONE_LABEL.lower()} in {ConfigClass.GREEN_ZONE_LABEL.lower()}')
#             self.log.info(F"COMPARING: {code} VS 403")
#             self.assertEqual(code, 403)
#         except Exception as e:
#             self.log.error(f"08 ERROR: {e}")
#             raise e

#     @unittest.skipIf(zone_env=="", "Missing essential information")
#     async def test_09_download_from_core_in_greenroom(self):
#         self.log.info('\n')
#         self.log.info("test_09_download_from_core_in_greenroom".center(80, '-'))
#         payload = {"action": 'download', "environ": zone_env, 'zone': ConfigClass.CORE_ZONE_LABEL.lower()}
#         try:
#             async with AsyncClient(app=self.app, base_url="http://test") as ac:
#                 res = await ac.post(self.test_api, json=payload)
#             self.log.info(f"RESPONSE: {res.text}")
#             response = res.json()
#             result = response.get('result')
#             code = response.get('code')
#             error = response.get('error_msg')
#             self.log.info(F"COMPARING: {result} VS 'Invalid'")
#             self.assertEqual(result, 'Invalid')
#             self.log.info(F"COMPARING: {error} VS 'Invalid action: download from {ConfigClass.CORE_ZONE_LABEL.lower()} in {ConfigClass.GREEN_ZONE_LABEL.lower()}'")
#             self.assertEqual(error, f'Invalid action: download from {ConfigClass.CORE_ZONE_LABEL.lower()} in {ConfigClass.GREEN_ZONE_LABEL.lower()}')
#             self.log.info(F"COMPARING: {code} VS 403")
#             self.assertEqual(code, 403)
#         except Exception as e:
#             self.log.error(f"09 ERROR: {e}")
#             raise e

#     @unittest.skipIf(zone_env=="", "Missing essential information")
#     async def test_10_download_from_greenroom_in_greenroom(self):
#         self.log.info('\n')
#         self.log.info("test_10_download_from_greenroom_in_greenroom".center(80, '-'))
#         payload = {"action": 'download', "environ": zone_env, 'zone': ConfigClass.GREEN_ZONE_LABEL.lower()}
#         try:
#             async with AsyncClient(app=self.app, base_url="http://test") as ac:
#                 res = await ac.post(self.test_api, json=payload)
#             self.log.info(f"RESPONSE: {res.text}")
#             response = res.json()
#             result = response.get('result')
#             code = response.get('code')
#             error = response.get('error_msg')
#             self.log.info(F"COMPARING: {result} VS 'valid'")
#             self.assertEqual(result, 'valid')
#             self.log.info(F"COMPARING: {error} VS ''")
#             self.assertEqual(error, '')
#             self.log.info(F"COMPARING: {code} VS 200")
#             self.assertEqual(code, 200)
#         except Exception as e:
#             self.log.error(f"10 ERROR: {e}")
#             raise e
