import unittest
import time
import os
from .prepare_test import SetupTest
from .logger import Logger


class TestKGImport(unittest.TestCase):
    log = Logger(name='test_kg_import.log')
    test = SetupTest(log)
    app = test.client
    test_api = "/v1/kg/resources"
    token = test.auth()
    dataset_code = os.environ.get('dataset_code')

    def test_01_kg_import_resource(self):
        self.log.info('\n')
        self.log.info("test_01_kg_import_resource".center(80, '-'))
        try:
            self.log.info(f"POST API: {self.test_api}")
            payload = {
                'dataset_code': [], 
                'data': {
                    'kg_cli_test1_1634922993.json': {
                        'key_value_pairs': {
                            'definition_file': True, 
                            'file_type': 'KG unit test', 
                            'existing_duplicate': False
                            }
                            }
                        }
                    }
            token = self.test.auth()
            headers = {"Authorization": 'Bearer ' + token}
            res = self.app.post(self.test_api, headers=headers, json=payload)
            self.log.info(f"RESPONSE: {res.text}")
            res_json = res.json()
            self.log.info(f"COMPARING CODE: {res_json.get('code')}, 200")
            self.assertEqual(res_json.get('code'), 200)
            self.log.info(f"COMPARING: {len(res_json.get('result').get('processing'))} VS 1")
            self.assertEqual(len(res_json.get('result').get('processing')), 1)
            self.log.info(f"COMPARING # of ignored: {len(res_json.get('result').get('ignored'))} VS 0")
            self.assertEqual(len(res_json.get('result').get('ignored')), 0)
        except Exception as e:
            self.log.error(f"ERROR test_01_kg_import_resource: {e}")
            raise e

    def test_02_kg_import_resource_exist(self):
        self.log.info('\n')
        self.log.info("test_02_kg_import_resource_exist".center(80, '-'))
        try:
            self.log.info(f"POST API: {self.test_api}")
            payload = {
                'dataset_code': [], 
                'data': {
                    'kg_cli_test1_1634922993.json': {
                        '@id': '1634922993', 
                        '@type': 'unit test', 
                        'key_value_pairs': {
                            'definition_file': True, 
                            'file_type': 'KG unit test', 
                            'existing_duplicate': False
                            }
                            }
                        }
                    }
            token = self.test.auth()
            headers = {"Authorization": 'Bearer ' + token}
            res = self.app.post(self.test_api, headers=headers, json=payload)
            self.log.info(f"RESPONSE: {res.text}")
            res_json = res.json()
            self.log.info(f"COMPARING CODE: {res_json.get('code')}, 200")
            self.assertEqual(res_json.get('code'), 200)
            self.log.info(f"COMPARING: {res_json.get('result').get('processing')} VS {''}")
            self.assertEqual(res_json.get('result').get('processing'), {})
            self.log.info(f"COMPARING # of ignored: {len(res_json.get('result').get('ignored'))} VS 1")
            self.assertEqual(len(res_json.get('result').get('ignored')), 1)
        except Exception as e:
            self.log.error(f"ERROR test_02_kg_import_resource_exist: {e}")
            raise e


