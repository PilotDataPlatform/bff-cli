import unittest

from app.config import ConfigClass
from .prepare_test import SetupTest
from .logger import Logger
import os

"""
cases: generate, attribute, environment
"""
case = "all"
zone_env=""

@unittest.skipUnless(case == 'generate' or case == 'all' or case=='', 'Run specific test')
class TestGenerateIDValidation(unittest.TestCase):
    log = Logger(name='test_gid_validation.log')
    test = SetupTest(log)
    app = test.client
    test_api = "/v1/validate/gid"

    def test_01_validate_gid(self):
        self.log.info('\n')
        self.log.info("test_01_validate_gid".center(80, '-'))
        payload = {'generate_id': 'ABC-1234'}
        try:
            res = self.app.post(self.test_api, json=payload)
            self.log.info(f"RESPONSE: {res.text}")
            res_json = res.json()
            self.log.info(f"COMPARING CODE: {res_json.get('code')}, 200")
            self.assertEqual(res_json.get('code'), 200)
            self.log.info(f"COMPARING RESULT: {res_json.get('result')}, 'Valid'")
            self.assertEqual(res_json.get('result'), 'Valid')
        except Exception as e:
            self.log.error(f"ERROR: {e}")
            raise e

    def test_02_test_gid_not_3_letters(self):
        self.log.info('\n')
        self.log.info("test_02_test_gid_not_3_letters".center(80, '-'))
        payload = {'generate_id': 'AC-1234'}
        try:
            res = self.app.post(self.test_api, json=payload)
            self.log.info(f"RESPONSE: {res.text}")
            res_json = res.json()
            self.log.info(f"COMPARING CODE: {res_json.get('code')}, 400")
            self.assertEqual(res_json.get('code'), 400)
            self.log.info(f"COMPARING RESULT: {res_json.get('result')}, 'Invalid Generate ID'")
            self.assertEqual(res_json.get('result'), 'Invalid Generate ID')
        except Exception as e:
            self.log.error(f"ERROR: {e}")
            raise e

    def test_03_test_gid_not_3_capital_letters(self):
        self.log.info('\n')
        self.log.info("test_03_test_gid_not_3_capital_letters".center(80, '-'))
        payload = {'generate_id': 'AbC-1234'}
        try:
            res = self.app.post(self.test_api, json=payload)
            self.log.info(f"RESPONSE: {res.text}")
            res_json = res.json()
            self.log.info(f"COMPARING CODE: {res_json.get('code')}, 400")
            self.assertEqual(res_json.get('code'), 400)
            self.log.info(f"COMPARING RESULT: {res_json.get('result')}, 'Invalid Generate ID'")
            self.assertEqual(res_json.get('result'), 'Invalid Generate ID')
        except Exception as e:
            self.log.error(f"ERROR: {e}")
            raise e

    def test_04_test_gid_not_4_numbers(self):
        self.log.info('\n')
        self.log.info("test_04_test_gid_not_4_numbers".center(80, '-'))
        payload = {'generate_id': 'ABC-134'}
        try:
            res = self.app.post(self.test_api, json=payload)
            self.log.info(f"RESPONSE: {res.text}")
            res_json = res.json()
            self.log.info(f"COMPARING CODE: {res_json.get('code')}, 400")
            self.assertEqual(res_json.get('code'), 400)
            self.log.info(f"COMPARING RESULT: {res_json.get('result')}, 'Invalid Generate ID'")
            self.assertEqual(res_json.get('result'), 'Invalid Generate ID')
        except Exception as e:
            self.log.error(f"ERROR: {e}")
            raise e

    def test_05_test_not_hyphen(self):
        self.log.info('\n')
        self.log.info("test_05_test_not_hyphen".center(80, '-'))
        payload = {'generate_id': 'ABC1234'}
        try:
            res = self.app.post(self.test_api, json=payload)
            self.log.info(f"RESPONSE: {res.text}")
            res_json = res.json()
            self.log.info(f"COMPARING CODE: {res_json.get('code')}, 400")
            self.assertEqual(res_json.get('code'), 400)
            self.log.info(f"COMPARING RESULT: {res_json.get('result')}, 'Invalid Generate ID'")
            self.assertEqual(res_json.get('result'), 'Invalid Generate ID')
        except Exception as e:
            self.log.error(f"ERROR: {e}")
            raise e

    def test_06_test_more_than_3_letter(self):
        self.log.info('\n')
        self.log.info("test_06_test_not_hyphen".center(80, '-'))
        payload = {'generate_id': 'ABCD-1234'}
        try:
            res = self.app.post(self.test_api, json=payload)
            self.log.info(f"RESPONSE: {res.text}")
            res_json = res.json()
            self.log.info(f"COMPARING CODE: {res_json.get('code')}, 400")
            self.assertEqual(res_json.get('code'), 400)
            self.log.info(f"COMPARING RESULT: {res_json.get('result')}, 'Invalid Generate ID'")
            self.assertEqual(res_json.get('result'), 'Invalid Generate ID')
        except Exception as e:
            self.log.error(f"ERROR: {e}")
            raise e

    def test_07_test_more_than_4_numbers(self):
        self.log.info('\n')
        self.log.info("test_07_test_more_than_4_numbers".center(80, '-'))
        payload = {'generate_id': 'ABCD-12345'}
        try:
            res = self.app.post(self.test_api, json=payload)
            self.log.info(f"RESPONSE: {res.text}")
            res_json = res.json()
            self.log.info(f"COMPARING CODE: {res_json.get('code')}, 400")
            self.assertEqual(res_json.get('code'), 400)
            self.log.info(f"COMPARING RESULT: {res_json.get('result')}, 'Invalid Generate ID'")
            self.assertEqual(res_json.get('result'), 'Invalid Generate ID')
        except Exception as e:
            self.log.error(f"ERROR: {e}")
            raise e

    def test_08_test_contain_other_characters(self):
        self.log.info('\n')
        self.log.info("test_08_test_contain_other_characters".center(80, '-'))
        payload = {'generate_id': 'ABCD-123!'}
        try:
            res = self.app.post(self.test_api, json=payload)
            self.log.info(f"RESPONSE: {res.text}")
            res_json = res.json()
            self.log.info(f"COMPARING CODE: {res_json.get('code')}, 400")
            self.assertEqual(res_json.get('code'), 400)
            self.log.info(f"COMPARING RESULT: {res_json.get('result')}, 'Invalid Generate ID'")
            self.assertEqual(res_json.get('result'), 'Invalid Generate ID')
        except Exception as e:
            self.log.error(f"ERROR: {e}")
            raise e


@unittest.skipUnless(case == 'attribute' or case == 'all' or case=='', 'Run specific test')
class TestAttributeValidation(unittest.TestCase):
    log = Logger(name='test_attribute_validation.log')
    test = SetupTest(log)
    app = test.client
    test_api = "/v1/validate/manifest"
    project_code = os.environ.get('project_code')

    def test_01_validate_attribute(self):
        self.log.info('\n')
        self.log.info("test_01_validate_attribute".center(80, '-'))
        payload = {
            "manifest_json": {
                "manifest_name": "Manifest1",
                "project_code": self.project_code,
                "attributes": {
                    "attr1": "a1",
                    "attr2": "Test manifest text value",
                    "attr3": "t1"
                }
            }
        }
        try:
            res = self.app.post(self.test_api, json=payload)
            self.log.info(f"RESPONSE: {res.text}")
            res_json = res.json()
            self.log.info(f"COMPARING CODE: {res_json.get('code')}, 200")
            self.assertEqual(res_json.get('code'), 200)
            self.log.info(f"COMPARING RESULT: {res_json.get('result')}, 'Valid'")
            self.assertEqual(res_json.get('result'), 'Valid')
        except Exception as e:
            self.log.error(f"ERROR: {e}")
            raise e

    def test_02_validate_attribute_name_not_exist(self):
        self.log.info('\n')
        self.log.info("test_02_validate_attribute_name_not_exist".center(80, '-'))
        payload = {
            "manifest_json": {
                "manifest_name": "Manifest",
                "project_code": self.project_code,
                "attributes": {
                    "attr1": "a1",
                    "attr2": "Test manifest text value",
                    "attr3": "t1"
                }
            }
        }
        try:
            res = self.app.post(self.test_api, json=payload)
            self.log.info(f"RESPONSE: {res.text}")
            res_json = res.json()
            self.log.info(f"COMPARING CODE: {res_json.get('code')}, 404")
            self.assertEqual(res_json.get('code'), 404)
            self.log.info(f"COMPARING RESULT: {res_json.get('result')}, 'Manifest Not Exist Manifest'")
            self.assertEqual(res_json.get('result'), 'Manifest Not Exist Manifest')
        except Exception as e:
            self.log.error(f"ERROR: {e}")
            raise e

    def test_03_validate_attribute_type_wrong(self):
        self.log.info('\n')
        self.log.info("test_03_validate_attribute_type_wrong".center(80, '-'))
        payload = {
            "manifest_json": {
                "manifest_name": "Manifest1",
                "project_code": self.project_code,
                "attributes": {
                    "attr1": "Test attr",
                    "attr2": "Test attr text value",
                    "attr3": "t1"
                }
            }
        }
        try:
            res = self.app.post(self.test_api, json=payload)
            self.log.info(f"RESPONSE: {res.text}")
            res_json = res.json()
            self.log.info(f"COMPARING CODE: {res_json.get('code')}, 400")
            self.assertEqual(res_json.get('code'), 400)
            self.log.info(f"COMPARING RESULT: {res_json.get('result')}, 'Invalid Choice Field attr1'")
            self.assertEqual(res_json.get('result'), 'Invalid Choice Field attr1')
        except Exception as e:
            self.log.error(f"ERROR: {e}")
            raise e

    def test_04_validate_attribute_value_wrong(self):
        self.log.info('\n')
        self.log.info("test_04_validate_attribute_value_wrong".center(80, '-'))
        payload = {
            "manifest_json": {
                "manifest_name": "Manifest1",
                "project_code": self.project_code,
                "attributes": {
                    "attr1": "a1",
                    "attr2": "Test attr text value",
                    "attr3": "t1000"
                }
            }
        }
        try:
            res = self.app.post(self.test_api, json=payload)
            self.log.info(f"RESPONSE: {res.text}")
            res_json = res.json()
            self.log.info(f"COMPARING CODE: {res_json.get('code')}, 400")
            self.assertEqual(res_json.get('code'), 400)
            self.log.info(f"COMPARING RESULT: {res_json.get('result')}, 'Invalid Choice Field attr3'")
            self.assertEqual(res_json.get('result'), 'Invalid Choice Field attr3')
        except Exception as e:
            self.log.error(f"ERROR: {e}")
            raise e

    def test_05_validate_attribute_text_too_long(self):
        self.log.info('\n')
        self.log.info("test_05_validate_attribute_text_too_long".center(80, '-'))
        payload = {
            "manifest_json": {
                "manifest_name": "Manifest1",
                "project_code": self.project_code,
                "attributes": {
                    "attr1": "a1",
                    "attr2": "z4S0zP2E2GR6UgINM9L4yqawILEsGVKRNzAW8p8fxwXZT85CHdtBvdBCXiPU1tX5zPKHa01MugMksD61QGcBan1RcXBOJekAjGFCI",
                    "attr3": "t1"
                }
            }
        }
        try:
            res = self.app.post(self.test_api, json=payload)
            self.log.info(f"RESPONSE: {res.text}")
            res_json = res.json()
            self.log.info(f"COMPARING CODE: {res_json.get('code')}, 400")
            self.assertEqual(res_json.get('code'), 400)
            self.log.info(f"COMPARING RESULT: {res_json.get('result')}, 'Text Too Long attr2'")
            self.assertEqual(res_json.get('result'), 'Text Too Long attr2')
        except Exception as e:
            self.log.error(f"ERROR: {e}")
            raise e

    def test_06_validate_with_attribute_not_exist(self):
        self.log.info('\n')
        self.log.info("test_06_validate_with_attribute_not_exist".center(80, '-'))
        payload = {
            "manifest_json": {
                "manifest_name": "Manifest1",
                "project_code": self.project_code,
                "attributes": {
                    "attr1": "a1",
                    "attr2": "test attribute",
                    "attr4": "t1"
                }
            }
        }
        try:
            res = self.app.post(self.test_api, json=payload)
            self.log.info(f"RESPONSE: {res.text}")
            res_json = res.json()
            self.log.info(f"COMPARING CODE: {res_json.get('code')}, 400")
            self.assertEqual(res_json.get('code'), 400)
            self.log.info(f"COMPARING RESULT: {res_json.get('result')}, 'Invalid Attribute attr4'")
            self.assertEqual(res_json.get('result'), 'Invalid Attribute attr4')
        except Exception as e:
            self.log.error(f"ERROR: {e}")
            raise e

    def test_07_validate_with_missing_mandatory_attribute(self):
        self.log.info('\n')
        self.log.info("test_07_validate_with_missing_mandatory_attribute".center(80, '-'))
        payload = {
            "manifest_json": {
                "manifest_name": "Manifest1",
                "project_code": self.project_code,
                "attributes": {
                    "attr2": "test attribute",
                    "attr3": "t1"
                }
            }
        }
        try:
            res = self.app.post(self.test_api, json=payload)
            self.log.info(f"RESPONSE: {res.text}")
            res_json = res.json()
            self.log.info(f"COMPARING CODE: {res_json.get('code')}, 400")
            self.assertEqual(res_json.get('code'), 400)
            self.log.info(f"COMPARING RESULT: {res_json.get('result')}, 'Missing Required Attribute attr1'")
            self.assertEqual(res_json.get('result'), 'Missing Required Attribute attr1')
        except Exception as e:
            self.log.error(f"ERROR: {e}")
            raise e

    def test_08_project_code_not_exist(self):
        self.log.info('\n')
        self.log.info("test_08_project_code_not_exist".center(80, '-'))
        payload = {
            "manifest_json": {
                "manifest_name": "Manifest1",
                "project_code": "vrec100000000000",
                "attributes": {
                    "attr2": "test attribute",
                    "attr3": "t1"
                }
            }
        }
        try:
            res = self.app.post(self.test_api, json=payload)
            self.log.info(f"RESPONSE: {res.text}")
            res_json = res.json()
            self.log.info(f"COMPARING CODE: {res_json.get('code')}, 404")
            self.assertEqual(res_json.get('code'), 404)
            self.log.info(f"COMPARING RESULT: {res_json.get('result')}, 'Manifest Not Exist Manifest1'")
            self.assertEqual(res_json.get('result'), 'Manifest Not Exist Manifest1')
        except Exception as e:
            self.log.error(f"ERROR: {e}")
            raise e


@unittest.skipUnless(case == 'environment' or case == 'all' or case=='', 'Run specific test')
class TestEnvironmentValidation(unittest.TestCase):
    log = Logger(name='test_environment_validation.log')
    test = SetupTest(log)
    app = test.client
    test_api = "/v1/validate/env"
    """
    VRE CLI Workbench VM Validation rules:

    Greenroom VM:
                Greenroom       VRECore
    Upload         Yes            No
    Download       Yes            No

    VRECore VM:
                Greenroom       VRECore
    Upload         Yes            Yes
    Download       No             Yes
    """
    def test_01_upload_from_vrecore_to_greenroom(self):
        self.log.info('\n')
        self.log.info("test_01_upload_from_greenroom_to_greenroom".center(80, '-'))
        payload = {"action": 'upload', "environ": "", 'zone': 'greenroom'}
        try:
            res = self.app.post(self.test_api, json=payload)
            self.log.info(f"RESPONSE: {res.text}")
            response = res.json()
            result = response.get('result')
            code = response.get('code')
            error = response.get('error_msg')
            self.log.info(F"COMPARING: {result} VS 'valid'")
            self.assertEqual(result, 'valid')
            self.log.info(F"COMPARING: {error} VS ''")
            self.assertEqual(error, '')
            self.log.info(F"COMPARING: {code} VS 200")
            self.assertEqual(code, 200)
        except Exception as e:
            self.log.error(f"01 ERROR: {e}")
            raise e

    def test_02_upload_from_vrecore_to_vrecore(self):
        self.log.info('\n')
        self.log.info("test_02_upload_from_vrecore_to_vrecore".center(80, '-'))
        payload = {"action": 'upload', "environ": "", 'zone': 'vrecore'}
        try:
            res = self.app.post(self.test_api, json=payload)
            self.log.info(f"RESPONSE: {res.text}")
            response = res.json()
            result = response.get('result')
            code = response.get('code')
            error = response.get('error_msg')
            self.log.info(F"COMPARING: {result} VS 'valid'")
            self.assertEqual(result, 'valid')
            self.log.info(F"COMPARING: {error} VS ''")
            self.assertEqual(error, '')
            self.log.info(F"COMPARING: {code} VS 200")
            self.assertEqual(code, 200)
        except Exception as e:
            self.log.error(f"02 ERROR: {e}")
            raise e

    def test_03_download_from_vrecore_in_vrecore(self):
        self.log.info('\n')
        self.log.info("test_03_download_from_vrecore_in_vrecore".center(80, '-'))
        payload = {"action": 'download', "environ": "", 'zone': 'vrecore'}
        try:
            res = self.app.post(self.test_api, json=payload)
            self.log.info(f"RESPONSE: {res.text}")
            response = res.json()
            result = response.get('result')
            code = response.get('code')
            error = response.get('error_msg')
            self.log.info(F"COMPARING: {result} VS 'valid'")
            self.assertEqual(result, 'valid')
            self.log.info(F"COMPARING: {error} VS ''")
            self.assertEqual(error, '')
            self.log.info(F"COMPARING: {code} VS 200")
            self.assertEqual(code, 200)
        except Exception as e:
            self.log.error(f"03 ERROR: {e}")
            raise e

    def test_04_download_from_greenroom_in_vrecore(self):
        self.log.info('\n')
        self.log.info("test_03_download_from_vrecore_in_vrecore".center(80, '-'))
        payload = {"action": 'download', "environ": "", 'zone': 'greenroom'}
        try:
            res = self.app.post(self.test_api, json=payload)
            self.log.info(f"RESPONSE: {res.text}")
            response = res.json()
            result = response.get('result')
            code = response.get('code')
            error = response.get('error_msg')
            self.log.info(F"COMPARING: {result} VS 'Invalid'")
            self.assertEqual(result, 'Invalid')
            self.log.info(F"COMPARING: {error} VS 'Invalid action: download from greenroom in vrecore'")
            self.assertEqual(error, 'Invalid action: download from greenroom in vrecore')
            self.log.info(F"COMPARING: {code} VS 403")
            self.assertEqual(code, 403)
        except Exception as e:
            self.log.error(f"04 ERROR: {e}")
            raise e

    def test_05_download_with_invalid_env(self):
        self.log.info('\n')
        self.log.info("test_05_download_with_invalid_env".center(80, '-'))
        payload = {"action": 'download', "environ": "asdf", 'zone': 'greenroom'}
        try:
            res = self.app.post(self.test_api, json=payload)
            self.log.info(f"RESPONSE: {res.text}")
            response = res.json()
            result = response.get('result')
            code = response.get('code')
            error = response.get('error_msg')
            self.log.info(F"COMPARING: {result} VS 'Invalid'")
            self.assertEqual(result, 'Invalid')
            self.log.info(F"COMPARING: {error} VS 'Invalid variable'")
            self.assertEqual(error, 'Invalid variable')
            self.log.info(F"COMPARING: {code} VS 400")
            self.assertEqual(code, 400)
        except Exception as e:
            self.log.error(f"05 ERROR: {e}")
            raise e

    def test_06_upload_with_invalid_zone(self):
        self.log.info('\n')
        self.log.info("test_06_upload_with_invalid_zone".center(80, '-'))
        payload = {"action": 'upload', "environ": "", 'zone': 'green'}
        try:
            res = self.app.post(self.test_api, json=payload)
            self.log.info(f"RESPONSE: {res.text}")
            response = res.json()
            result = response.get('result')
            code = response.get('code')
            error = response.get('error_msg')
            self.log.info(F"COMPARING: {result} VS 'Invalid'")
            self.assertEqual(result, 'Invalid')
            self.log.info(F"COMPARING: {error} VS 'Invalid zone'")
            self.assertEqual(error, 'Invalid zone')
            self.log.info(F"COMPARING: {code} VS 400")
            self.assertEqual(code, 400)
        except Exception as e:
            self.log.error(f"06 ERROR: {e}")
            raise e

    @unittest.skipIf(zone_env=="", "Missing essential information")
    def test_07_upload_from_greenroom_to_greenroom(self):
        self.log.info('\n')
        self.log.info("test_07_upload_from_greenroom_to_greenroom".center(80, '-'))
        payload = {"action": 'upload', "environ": zone_env, 'zone': 'greenroom'}
        try:
            res = self.app.post(self.test_api, json=payload)
            self.log.info(f"RESPONSE: {res.text}")
            response = res.json()
            result = response.get('result')
            code = response.get('code')
            error = response.get('error_msg')
            self.log.info(F"COMPARING: {result} VS 'valid'")
            self.assertEqual(result, 'valid')
            self.log.info(F"COMPARING: {error} VS ''")
            self.assertEqual(error, '')
            self.log.info(F"COMPARING: {code} VS 200")
            self.assertEqual(code, 200)
        except Exception as e:
            self.log.error(f"07 ERROR: {e}")
            raise e

    @unittest.skipIf(zone_env=="", "Missing essential information")
    def test_08_upload_from_greenroom_to_vrecore(self):
        self.log.info('\n')
        self.log.info("test_08_upload_from_greenroom_to_vrecore".center(80, '-'))
        payload = {"action": 'upload', "environ": zone_env, 'zone': 'vrecore'}
        try:
            res = self.app.post(self.test_api, json=payload)
            self.log.info(f"RESPONSE: {res.text}")
            response = res.json()
            result = response.get('result')
            code = response.get('code')
            error = response.get('error_msg')
            self.log.info(F"COMPARING: {result} VS 'Invalid'")
            self.assertEqual(result, 'Invalid')
            self.log.info(F"COMPARING: {error} VS 'Invalid action: upload to vrecore in greenroom'")
            self.assertEqual(error, 'Invalid action: upload to vrecore in greenroom')
            self.log.info(F"COMPARING: {code} VS 403")
            self.assertEqual(code, 403)
        except Exception as e:
            self.log.error(f"08 ERROR: {e}")
            raise e

    @unittest.skipIf(zone_env=="", "Missing essential information")
    def test_09_download_from_vrecore_in_greenroom(self):
        self.log.info('\n')
        self.log.info("test_09_download_from_vrecore_in_greenroom".center(80, '-'))
        payload = {"action": 'download', "environ": zone_env, 'zone': 'vrecore'}
        try:
            res = self.app.post(self.test_api, json=payload)
            self.log.info(f"RESPONSE: {res.text}")
            response = res.json()
            result = response.get('result')
            code = response.get('code')
            error = response.get('error_msg')
            self.log.info(F"COMPARING: {result} VS 'Invalid'")
            self.assertEqual(result, 'Invalid')
            self.log.info(F"COMPARING: {error} VS 'Invalid action: download from vrecore in greenroom'")
            self.assertEqual(error, 'Invalid action: download from vrecore in greenroom')
            self.log.info(F"COMPARING: {code} VS 403")
            self.assertEqual(code, 403)
        except Exception as e:
            self.log.error(f"09 ERROR: {e}")
            raise e

    @unittest.skipIf(zone_env=="", "Missing essential information")
    def test_10_download_from_greenroom_in_greenroom(self):
        self.log.info('\n')
        self.log.info("test_10_download_from_greenroom_in_greenroom".center(80, '-'))
        payload = {"action": 'download', "environ": zone_env, 'zone': 'greenroom'}
        try:
            res = self.app.post(self.test_api, json=payload)
            self.log.info(f"RESPONSE: {res.text}")
            response = res.json()
            result = response.get('result')
            code = response.get('code')
            error = response.get('error_msg')
            self.log.info(F"COMPARING: {result} VS 'valid'")
            self.assertEqual(result, 'valid')
            self.log.info(F"COMPARING: {error} VS ''")
            self.assertEqual(error, '')
            self.log.info(F"COMPARING: {code} VS 200")
            self.assertEqual(code, 200)
        except Exception as e:
            self.log.error(f"10 ERROR: {e}")
            raise e
