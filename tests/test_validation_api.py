import unittest
from .prepare_test import SetupTest
from .logger import Logger
import os


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
