import unittest
import time
import os
from .prepare_test import SetupTest
from .logger import Logger

# To run particular test, edit the case_to_run_variable with following values:
# dataset list: list
# dataset detail: detail
# run all tests: '' or 'all'

case_to_run = ''

no_access_user_name = "jzhang53"
no_access_user_password = "Indoc1234567!"


@unittest.skipIf(case_to_run == 'detail', 'Run specific test')
class TestListDataset(unittest.TestCase):
    log = Logger(name='test_list_dataset.log')
    test = SetupTest(log)
    app = test.client
    test_api = "/v1/datasets"
    token = test.auth()
    dataset_code = os.environ.get('dataset_code')

    def test_01_list_dataset_without_token(self):
        self.log.info('\n')
        self.log.info("test_01_list_dataset_without_token".center(80, '-'))
        try:
            self.log.info(f"GET API: {self.test_api}")
            res = self.app.get(self.test_api)
            self.log.info(f"RESPONSE: {res.text}")
            res_json = res.json()
            self.log.info(f"COMPARING CODE: {res_json.get('code')}, 401")
            self.assertEqual(res_json.get('code'), 401)
            self.assertEqual(res_json.get('error_msg'), "Token required")
        except Exception as e:
            self.log.error(f"ERROR 01: {e}")
            raise e

    def test_02_list_dataset(self):
        self.log.info('\n')
        self.log.info("test_02_list_dataset".center(80, '-'))
        try:
            self.log.info(f"GET API: {self.test_api}")
            headers = {'Authorization': 'Bearer ' + self.token}
            res = self.app.get(self.test_api, headers=headers)
            self.log.info(f"RESPONSE: {res.text}")
            res_json = res.json()
            self.log.info(f"COMPARING CODE: {res_json.get('code')}, 200")
            self.assertEqual(res_json.get('code'), 200)
            datasets = []
            for d in res_json.get('result'):
                datasets.append(d.get('code'))
            self.assertIn(self.dataset_code, datasets)
        except Exception as e:
            self.log.error(f"ERROR 02: {e}")
            raise e
    
    def test_03_list_dataset_no_dataset(self):
        self.log.info('\n')
        self.log.info("test_03_list_dataset_no_dataset".center(80, '-'))
        try:
            self.log.info(f"GET API: {self.test_api}")
            _token = self.test.auth({'username': no_access_user_name, 'password': no_access_user_password})
            headers = {'Authorization': 'Bearer ' + _token}
            res = self.app.get(self.test_api, headers=headers)
            self.log.info(f"RESPONSE: {res.text}")
            res_json = res.json()
            self.log.info(f"COMPARING CODE: {res_json.get('code')}, 200")
            self.assertEqual(res_json.get('code'), 200)
            self.assertEqual(res_json.get('result'), [])
        except Exception as e:
            self.log.error(f"ERROR 03: {e}")
            raise e


@unittest.skipIf(case_to_run == 'list', 'Run specific test')
class TestDatasetDetail(unittest.TestCase):
    log = Logger(name='test_dataset_detail.log')
    test = SetupTest(log)
    app = test.client
    test_api = "/v1/dataset/"
    token = test.auth()
    dataset_code = os.environ.get('dataset_code')

    def test_01_get_dataset_detail_without_token(self):
        self.log.info('\n')
        self.log.info("test_01_get_dataset_detail_without_token".center(80, '-'))
        try:
            _test_api = self.test_api + self.dataset_code
            self.log.info(f"GET API: {_test_api}")
            res = self.app.get(_test_api)
            self.log.info(f"RESPONSE: {res.text}")
            res_json = res.json()
            self.log.info(f"COMPARING CODE: {res_json.get('code')}, 401")
            self.assertEqual(res_json.get('code'), 401)
            self.assertEqual(res_json.get('error_msg'), "Token required")
        except Exception as e:
            self.log.error(f"ERROR 01: {e}")
            raise e

    def test_02_get_dataset_detail(self):
            self.log.info('\n')
            self.log.info("test_02_get_dataset_detail".center(80, '-'))
            try:
                _test_api = self.test_api + self.dataset_code
                self.log.info(f"GET API: {_test_api}")
                headers = {'Authorization': 'Bearer ' + self.token}
                res = self.app.get(_test_api, headers=headers)
                self.log.info(f"RESPONSE: {res.text}")
                res_json = res.json()
                self.log.info(f"COMPARING CODE: {res_json.get('code')}, 200")
                self.assertEqual(res_json.get('code'), 200)
                result = res_json.get('result')
                self.log.info(f"RESULT: {result}")
                _dataset_info = result.get('general_info')
                versions = result.get('version_detail')
                version_list = []
                for v in versions:
                    version_list.append(v.get('version'))
                self.log.info(f"COMPARING VERSIONS: '1.0' IN {version_list}")
                self.assertIn('1.0', version_list)
                _dataset_code = _dataset_info.get('code')
                _dataset_tag = _dataset_info.get('tags')
                _dataset_label = _dataset_info.get('labels')
                _dataset_modality = _dataset_info.get('modality')
                _dataset_creator = _dataset_info.get('creator')
                _dataset_type = _dataset_info.get('type')
                self.log.info(f"COMPARING CODE: {_dataset_code} VS {self.dataset_code}")
                self.assertEqual(_dataset_code, self.dataset_code)
                self.log.info(f"COMPARING TAGS: ['tag1', 'tag2', 'tag3'] VS {_dataset_tag}")
                self.assertEqual(['tag1', 'tag2', 'tag3'], _dataset_tag)
                self.log.info(f"COMPARING labels: ['Dataset'] VS {_dataset_label}")
                self.assertEqual(['Dataset'], _dataset_label)
                self.log.info(f"COMPARING modality: ['neuroimaging','microscopy','histological approach'] VS {_dataset_modality}")
                self.assertEqual(["neuroimaging","microscopy","histological approach"], _dataset_modality)
                self.log.info(f"COMPARING labels: 'jzhang10' VS {_dataset_creator}")
                self.assertEqual('jzhang10', _dataset_creator)
                self.log.info(f"COMPARING type: 'GENERAL' VS {_dataset_type}")
                self.assertEqual('GENERAL', _dataset_type)
            except Exception as e:
                self.log.error(f"ERROR 02: {e}")
                raise e

    def test_03_get_dataset_detail_no_version(self):
            self.log.info('\n')
            self.log.info("test_03_get_dataset_detail_no_version".center(80, '-'))
            try:
                _code = os.environ.get('dataset_no_version')
                _test_api = self.test_api + _code
                self.log.info(f"GET API: {_test_api}")
                headers = {'Authorization': 'Bearer ' + self.token}
                res = self.app.get(_test_api, headers=headers)
                self.log.info(f"RESPONSE: {res.text}")
                res_json = res.json()
                self.log.info(f"COMPARING CODE: {res_json.get('code')}, 200")
                self.assertEqual(res_json.get('code'), 200)
                result = res_json.get('result')
                self.log.info(f"RESULT: {result}")
                _dataset_info = result.get('general_info')
                versions = result.get('version_detail')
                version_list = []
                for v in versions:
                    version_list.append(v.get('version'))
                self.log.info(f"COMPARING VERSIONS: [] VS {version_list}")
                self.assertEqual([], version_list)
                _dataset_code = _dataset_info.get('code')
                _dataset_tag = _dataset_info.get('tags')
                _dataset_label = _dataset_info.get('labels')
                _dataset_modality = _dataset_info.get('modality')
                _dataset_creator = _dataset_info.get('creator')
                _dataset_type = _dataset_info.get('type')
                self.log.info(f"COMPARING CODE: {_dataset_code} VS {_code}")
                self.assertEqual(_dataset_code, _code)
                self.log.info(f"COMPARING TAGS: ['t1'] VS {_dataset_tag}")
                self.assertEqual(['t1'], _dataset_tag)
                self.log.info(f"COMPARING labels: ['Dataset'] VS {_dataset_label}")
                self.assertEqual(['Dataset'], _dataset_label)
                self.log.info(f"COMPARING modality: ['anatomical approach', 'neuroimaging'] VS {_dataset_modality}")
                self.assertEqual(['anatomical approach', 'neuroimaging'], _dataset_modality)
                self.log.info(f"COMPARING labels: 'jzhang10' VS {_dataset_creator}")
                self.assertEqual('jzhang10', _dataset_creator)
                self.log.info(f"COMPARING type: 'BIDS' VS {_dataset_type}")
                self.assertEqual('BIDS', _dataset_type)
            except Exception as e:
                self.log.error(f"ERROR 03: {e}")
                raise e

    def test_04_get_dataset_detail_no_access(self):
        self.log.info('\n')
        self.log.info("test_04_get_dataset_detail_no_access".center(80, '-'))
        try:
            _code = os.environ.get('other_user_dataset')
            _test_api = self.test_api + _code
            self.log.info(f"GET API: {_test_api}")
            headers = {'Authorization': 'Bearer ' + self.token}
            res = self.app.get(_test_api, headers=headers)
            self.log.info(f"RESPONSE: {res.text}")
            res_json = res.json()
            self.log.info(f"COMPARING CODE: {res_json.get('code')}, 403")
            self.assertEqual(res_json.get('code'), 403)
            self.assertEqual(res_json.get('error_msg'), "Permission Denied")
        except Exception as e:
            self.log.error(f"ERROR 01: {e}")
            raise e

    def test_05_get_dataset_detail_not_exist(self):
        self.log.info('\n')
        self.log.info("test_05_get_dataset_detail_not_exist".center(80, '-'))
        try:
            _test_api = self.test_api + self.dataset_code +'123'
            self.log.info(f"GET API: {_test_api}")
            headers = {'Authorization': 'Bearer ' + self.token}
            res = self.app.get(_test_api, headers=headers)
            self.log.info(f"RESPONSE: {res.text}")
            res_json = res.json()
            self.log.info(f"COMPARING CODE: {res_json.get('code')}, 404")
            self.assertEqual(res_json.get('code'), 404)
            self.assertEqual(res_json.get('error_msg'), "Cannot found given dataset code")
        except Exception as e:
            self.log.error(f"ERROR 05: {e}")
            raise e
