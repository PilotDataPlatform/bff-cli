import unittest
from .prepare_test import SetupTest
from .logger import Logger

@unittest.skip('ready')
class TestGetAttributes(unittest.TestCase):
    log = Logger(name='test_get_attributes.log')
    test = SetupTest(log)
    app = test.client
    test_api = "/v1/manifest"
    token = test.auth()

    def test_01_get_attributes_without_token(self):
        self.log.info('\n')
        self.log.info("test_01_get_attributes".center(80, '-'))
        param = {'project_code': 'vrecli'}
        try:
            self.log.info(f"GET API: {self.test_api}")
            res = self.app.get(self.test_api, params=param)
            self.log.info(f"RESPONSE: {res.text}")
            res_json = res.json()
            self.log.info(f"COMPARING CODE: {res_json.get('code')}, 403")
            self.assertEqual(res_json.get('code'), 403)
            self.assertEqual(res_json.get('error_msg'), "Token required")
        except Exception as e:
            self.log.error(f"ERROR: {e}")
            raise e

    def test_02_get_attributes(self):
        self.log.info('\n')
        self.log.info("test_02_get_attributes".center(80, '-'))
        param = {'project_code': 'vrecli'}
        headers = {
            'Authorization': 'Bearer ' + self.token
        }
        try:
            self.log.info(f"GET API: {self.test_api}")
            res = self.app.get(self.test_api, headers=headers, params=param)
            self.log.info(f"RESPONSE: {res.text}")
            res_json = res.json()
            self.log.info(f"COMPARING CODE: {res_json.get('code')}, 200")
            self.assertEqual(res_json.get('code'), 200)
            self.assertTrue(len(res_json.get('result')) > 1)
        except Exception as e:
            self.log.error(f"ERROR: {e}")
            raise e

    def test_03_get_attributes_no_access(self):
        self.log.info('\n')
        self.log.info("test_03_get_attributes_no_access".center(80, '-'))
        param = {'project_code': 'vrecli'}
        login_user = {
            "username": "jzhang21",
            "password": "Indoc1234567!",
            "realm": "vre"
        }
        _token = self.test.auth(login_user)
        headers = {
            'Authorization': 'Bearer ' + _token
        }
        try:
            self.log.info(f"GET API: {self.test_api}")
            res = self.app.get(self.test_api, headers=headers, params=param)
            self.log.info(f"RESPONSE: {res.text}")
            res_json = res.json()
            self.log.info(f"COMPARING CODE: {res_json.get('code')}, 403")
            self.assertEqual(res_json.get('code'), 403)
            self.log.info(f"COMPARING: {res_json.get('error_msg')} VS 'Permission Denied'")
            self.assertEqual(res_json.get('error_msg'), "Permission Denied")
        except Exception as e:
            self.log.error(f"ERROR: {e}")
            raise e

    def test_04_get_attributes_project_not_exist(self):
        self.log.info('\n')
        self.log.info("test_04_get_attributes_project_not_exist".center(80, '-'))
        param = {'project_code': 't1000'}
        headers = {
            'Authorization': 'Bearer ' + self.token
        }
        try:
            self.log.info(f"GET API: {self.test_api}")
            res = self.app.get(self.test_api, headers=headers, params=param)
            self.log.info(f"RESPONSE: {res.text}")
            res_json = res.json()
            self.log.info(f"COMPARING CODE: {res_json.get('code')}, 403")
            self.assertEqual(res_json.get('code'), 403)
            self.log.info(f"COMPARING: {res_json.get('error_msg')} VS 'Permission Denied'")
            self.assertEqual(res_json.get('error_msg'), "Permission Denied")
        except Exception as e:
            self.log.error(f"ERROR: {e}")
            raise e

    def test_05_get_project_no_attribute(self):
        self.log.info('\n')
        self.log.info("test_05_get_project_no_attribute".center(80, '-'))
        param = {'project_code': 'testmar04'}
        login_user = {
            "username": "jzhang21",
            "password": "Indoc1234567!",
            "realm": "vre"
        }
        _token = self.test.auth(login_user)
        headers = {
            'Authorization': 'Bearer ' + _token
        }
        try:
            self.log.info(f"GET API: {self.test_api}")
            res = self.app.get(self.test_api, headers=headers, params=param)
            self.log.info(f"RESPONSE: {res.text}")
            res_json = res.json()
            self.log.info(f"COMPARING CODE: {res_json.get('code')}, 200")
            self.assertEqual(res_json.get('code'), 200)
            self.assertEqual(len(res_json.get('result')), 0)
        except Exception as e:
            self.log.error(f"ERROR: {e}")
            raise e

@unittest.skip('ready')
class TestExportAttributes(unittest.TestCase):
    log = Logger(name='test_export_attribute.log')
    test = SetupTest(log)
    app = test.client
    test_api = "/v1/manifest/export"
    token = test.auth()

    def test_01_export_attributes_without_token(self):
        self.log.info('\n')
        self.log.info("test_01_export_attributes_without_token".center(80, '-'))
        param = {'project_code': 'vrecli',
                 'manifest_name': 'Manifest1'}
        try:
            self.log.info(f"GET API: {self.test_api}")
            res = self.app.get(self.test_api, params=param)
            self.log.info(f"RESPONSE: {res.text}")
            res_json = res.json()
            self.log.info(f"COMPARING CODE: {res_json.get('code')}, 403")
            self.assertEqual(res_json.get('code'), 403)
            self.log.info(f"COMPARING ERROR: {res_json.get('error_msg')}, Token required")
            self.assertEqual(res_json.get('error_msg'), "Token required")
        except Exception as e:
            self.log.error(f"ERROR: {e}")
            raise e

    def test_02_export_attributes(self):
        self.log.info('\n')
        self.log.info("test_02_export_attributes".center(80, '-'))
        param = {'project_code': 'vrecli',
                 'manifest_name': 'Manifest1'}
        headers = {
            'Authorization': 'Bearer ' + self.token
        }
        try:
            self.log.info(f"GET API: {self.test_api}")
            res = self.app.get(self.test_api, headers=headers, params=param)
            self.log.info(f"RESPONSE: {res.text}")
            res_json = res.json()
            self.log.info(f"COMPARING CODE: {res_json.get('code')}, 200")
            self.assertEqual(res_json.get('code'), 200)
            self.log.info(f"COMPARING NAME: {res_json.get('result').get('manifest_name')} VS 'Manifest1'")
            self.assertEqual(res_json.get('result').get('manifest_name'),
                             "Manifest1")
            self.log.info(f"COMPARING NUMBER OF ATTRIBUTES: {len(res_json.get('result'))} VS 3")
            self.assertEqual(len(res_json.get('result')), 3)
        except Exception as e:
            self.log.error(f"ERROR: {e}")
            raise e

    def test_03_export_attributes_no_access(self):
        self.log.info('\n')
        self.log.info("test_03_export_attributes_no_access".center(80, '-'))
        param = {'project_code': 'vrecli',
                 'manifest_name': 'Manifest1'}
        login_user = {
            "username": "jzhang21",
            "password": "Indoc1234567!",
            "realm": "vre"
        }
        _token = self.test.auth(login_user)
        headers = {
            'Authorization': 'Bearer ' + _token
        }
        try:
            self.log.info(f"GET API: {self.test_api}")
            res = self.app.get(self.test_api, headers=headers, params=param)
            self.log.info(f"RESPONSE: {res.text}")
            res_json = res.json()
            self.log.info(f"COMPARING CODE: {res_json.get('code')}, 403")
            self.assertEqual(res_json.get('code'), 403)
            self.log.info(f"COMPARING: {res_json.get('error_msg')} VS 'Permission Denied'")
            self.assertEqual(res_json.get('error_msg'), "Permission Denied")
        except Exception as e:
            self.log.error(f"ERROR: {e}")
            raise e

    def test_04_export_attributes_not_exist(self):
        self.log.info('\n')
        self.log.info("test_04_export_attributes_not_exist".center(80, '-'))
        param = {'project_code': 'vrecli',
                 'manifest_name': 'Manifest11111111'}
        headers = {
            'Authorization': 'Bearer ' + self.token
        }
        try:
            self.log.info(f"GET API: {self.test_api}")
            res = self.app.get(self.test_api, headers=headers, params=param)
            self.log.info(f"RESPONSE: {res.text}")
            res_json = res.json()
            self.log.info(f"COMPARING CODE: {res_json.get('code')}, 404")
            self.assertEqual(res_json.get('code'), 404)
            self.log.info(f"COMPARING ERROR: {res_json.get('error_msg')} VS Manifest Not Exist Manifest11111111")
            self.assertEqual(res_json.get('error_msg'), 'Manifest Not Exist Manifest11111111')
        except Exception as e:
            self.log.error(f"ERROR: {e}")
            raise e

    def test_05_export_attributes_project_not_exist(self):
        self.log.info('\n')
        self.log.info("test_05_export_attributes_project_not_exist".center(80, '-'))
        param = {'project_code': 't1000',
                 'manifest_name': 'Manifest1'}
        headers = {
            'Authorization': 'Bearer ' + self.token
        }
        try:
            self.log.info(f"GET API: {self.test_api}")
            res = self.app.get(self.test_api, headers=headers, params=param)
            self.log.info(f"RESPONSE: {res.text}")
            res_json = res.json()
            self.log.info(f"COMPARING CODE: {res_json.get('code')}, 403")
            self.assertEqual(res_json.get('code'), 403)
            self.log.info(f"COMPARING: {res_json.get('error_msg')} VS 'Permission Denied'")
            self.assertEqual(res_json.get('error_msg'), "Permission Denied")
        except Exception as e:
            self.log.error(f"ERROR: {e}")
            raise e


class TestAttachAttributes(unittest.TestCase):
    log = Logger(name='test_attach_attribute.log')
    test = SetupTest(log)
    app = test.client
    test_api = "/v1/manifest/attach"
    token = test.auth()
    file_id = ''
    file_path = ''
    project_code = 'vrecli'


    @classmethod
    def setUpClass(cls):
        cls.log.info(f"{'Test setUp'.center(80, '=')}")
        create_res = cls.test.create_file('vrecli', 'unittest_file')
        cls.log.info(f"CREATE FILE: {create_res}")
        cls.file_id = create_res.get('id')
        cls.file_path = create_res.get('full_path')

    @classmethod
    def tearDownClass(cls):
        cls.log.info('Test tearDown'.center(80, '='))
        delete_res = cls.test.delete_file(cls.file_id)
        cls.log.info(f"DELETE FILE: {delete_res}")

    def test_01_attach_attributes_without_token(self):
        self.log.info('\n')
        self.log.info("test_01_attach_attributes_without_token".center(80, '-'))
        payload = {"manifest_json": {
                  "manifest_name": "Manifest1",
                  "project_code": self.project_code,
                  "attributes": {"attr1": "a1", "attr2": "asdf", "attr3": "t1"},
                  "file_path": self.file_path
                  }
                  }
        try:
            self.log.info(f"POST API: {self.test_api}")
            self.log.info(f"POST PAYLOAD: {payload}")
            res = self.app.post(self.test_api, json=payload)
            self.log.info(f"RESPONSE: {res.text}")
            res_json = res.json()
            self.log.info(f"COMPARING CODE: {res_json.get('code')}, 403")
            self.assertEqual(res_json.get('code'), 403)
            self.log.info(f"COMPARING ERROR: {res_json.get('error_msg')}, Token required")
            self.assertEqual(res_json.get('error_msg'), "Token required")
        except Exception as e:
            self.log.error(f"ERROR: {e}")
            raise e

    def test_02_attach_attributes(self):
        self.log.info('\n')
        self.log.info("test_02_attach_attributes".center(80, '-'))
        payload = {"manifest_json": {
                  "manifest_name": "Manifest1",
                  "project_code": self.project_code,
                  "attributes": {"attr1": "a1", "attr2": "asdf", "attr3": "t1"},
                  "file_path": self.file_path
                  }
                  }
        headers = {
            'Authorization': 'Bearer ' + self.token
        }
        try:
            self.log.info(f"POST API: {self.test_api}")
            self.log.info(f"POST PAYLOAD: {payload}")
            res = self.app.post(self.test_api, headers=headers, json=payload)
            self.log.info(f"RESPONSE: {res.text}")
            res_json = res.json()
            self.log.info(f"COMPARING CODE: {res_json.get('code')}, 200")
            self.assertEqual(res_json.get('code'), 200)
            result = res_json.get('result')[0]
            self.log.info(f"COMPARING labels: {result.get('labels')}, ['File', 'Greenroom', 'Raw']")
            self.assertEqual(result.get('labels'), ['File', 'Greenroom', 'Raw'])
            self.log.info(f"COMPARING path: {result.get('full_path')}, {self.file_path}")
            self.assertEqual(result.get('full_path'), self.file_path)
        except Exception as e:
            self.log.error(f"ERROR: {e}")
            raise e

    def test_03_attach_attributes_wrong_file(self):
        self.log.info('\n')
        self.log.info("test_03_attach_attributes_wrong_file".center(80, '-'))
        wrong_file = self.file_path + '10000'
        payload = {"manifest_json": {
                  "manifest_name": "Manifest1",
                  "project_code": self.project_code,
                  "attributes": {"attr1": "a1", "attr2": "asdf", "attr3": "t1"},
                  "file_path": wrong_file
                  }
                  }
        headers = {
            'Authorization': 'Bearer ' + self.token
        }
        try:
            self.log.info(f"POST API: {self.test_api}")
            self.log.info(f"POST PAYLOAD: {payload}")
            res = self.app.post(self.test_api, headers=headers, json=payload)
            self.log.info(f"RESPONSE: {res.text}")
            res_json = res.json()
            self.log.info(f"COMPARING CODE: {res_json.get('code')}, 400")
            self.assertEqual(res_json.get('code'), 400)
            error = res_json.get('error_msg')
            self.log.info(f"COMPARING ERROR: {error} VS 'File Not Exist'")
            self.assertEqual(error, 'File Not Exist')
        except Exception as e:
            self.log.error(f"ERROR: {e}")
            raise e

    def test_04_attach_attributes_wrong_name(self):
        self.log.info('\n')
        self.log.info("test_04_attach_attributes_wrong_name".center(80, '-'))
        payload = {"manifest_json": {
                  "manifest_name": "Manifest1000",
                  "project_code": self.project_code,
                  "attributes": {"attr1": "a1", "attr2": "asdf", "attr3": "t1"},
                  "file_path": self.file_path
                  }
                  }
        headers = {
            'Authorization': 'Bearer ' + self.token
        }
        try:
            self.log.info(f"POST API: {self.test_api}")
            self.log.info(f"POST PAYLOAD: {payload}")
            res = self.app.post(self.test_api, headers=headers, json=payload)
            self.log.info(f"RESPONSE: {res.text}")
            res_json = res.json()
            self.log.info(f"COMPARING CODE: {res_json.get('code')}, 400")
            self.assertEqual(res_json.get('code'), 400)
            error = res_json.get('error_msg')
            self.log.info(f"COMPARING ERROR: {error} VS 'Manifest Not Exist Manifest1000'")
            self.assertEqual(error, 'Manifest Not Exist Manifest1000')
        except Exception as e:
            self.log.error(f"ERROR: {e}")
            raise e

    def test_05_attach_attributes_no_access(self):
        self.log.info('\n')
        self.log.info("test_04_attach_attributes_wrong_name".center(80, '-'))
        payload = {"manifest_json": {
            "manifest_name": "Manifest1000",
            "project_code": self.project_code,
            "attributes": {"attr1": "a1", "attr2": "asdf", "attr3": "t1"},
            "file_path": self.file_path
        }
        }
        login_user = {
            "username": "jzhang21",
            "password": "Indoc1234567!",
            "realm": "vre"
        }
        _token = self.test.auth(login_user)
        headers = {
            'Authorization': 'Bearer ' + _token
        }
        try:
            self.log.info(f"POST API: {self.test_api}")
            self.log.info(f"POST PAYLOAD: {payload}")
            res = self.app.post(self.test_api, headers=headers, json=payload)
            self.log.info(f"RESPONSE: {res.text}")
            res_json = res.json()
            self.log.info(f"COMPARING CODE: {res_json.get('code')}, 403")
            self.assertEqual(res_json.get('code'), 403)
            error = res_json.get('error_msg')
            self.log.info(f"COMPARING ERROR: {error} VS 'Permission Denied'")
            self.assertEqual(error, 'Permission Denied')
        except Exception as e:
            self.log.error(f"ERROR: {e}")
            raise e

