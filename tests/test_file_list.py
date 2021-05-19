import unittest
from .prepare_test import SetupTest
from .logger import Logger
import os


class TestGetProjectFilesFolders(unittest.TestCase):
    log = Logger(name='test_list_files_folders.log')
    test = SetupTest(log)
    app = test.client
    token = test.auth()
    project_code = os.environ.get('project_code')
    test_api = f"/v1/{project_code}/files/query"

    def test_01_get_files_and_folders_gr(self):
        self.log.info('\n')
        self.log.info("test_01_get_files_and_folders_gr".center(80, '-'))
        self.log.info(f"GET API: {self.test_api}")
        try:
            param = {"project_code": self.project_code,
                     "zone": 'greenroom',
                     "folder": '',
                     "source_type": 'Dataset'}
            headers = {"Authorization": 'Bearer ' + self.token}
            res = self.app.get(self.test_api, headers=headers, params=param)
            self.log.info(res.text)
            res_json = res.json()
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res_json.get('code'), 200)
            result = res_json.get('result')
            self.log.info(f'Get files: {len(result)}')
            for f in result:
                self.log.info(f"COMPARING LABELS: 'Greenroom' VS {f.get('labels')}")
                self.assertIn('Greenroom', f.get('labels'))
                self.log.info(f"COMPARING PROJECT CODE: {self.project_code} VS {f.get('project_code')}")
                self.assertEqual(self.project_code, f.get('project_code'))
        except Exception as e:
            self.log.error(f"test_01 error: {e}")
            raise e

    def test_02_get_files_and_folders_vrecore(self):
        self.log.info('\n')
        self.log.info("test_02_get_files_and_folders_vrecore".center(80, '-'))
        self.log.info(f"GET API: {self.test_api}")
        try:
            param = {"project_code": self.project_code,
                     "zone": 'vrecore',
                     "folder": '',
                     "source_type": 'Dataset'}
            headers = {"Authorization": 'Bearer ' + self.token}
            res = self.app.get(self.test_api, headers=headers, params=param)
            self.log.info(res.text)
            res_json = res.json()
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res_json.get('code'), 200)
            result = res_json.get('result')
            self.log.info(f'Get files: {len(result)}')
            for f in result:
                self.log.info(f"COMPARING LABELS: 'VRECore' VS {f.get('labels')}")
                self.assertIn('VRECore', f.get('labels'))
                self.log.info(f"COMPARING PROJECT CODE: {self.project_code} VS {f.get('project_code')}")
                self.assertEqual(self.project_code, f.get('project_code'))
        except Exception as e:
            self.log.error(f"test_02 error: {e}")
            raise e

    def test_03_contributor_get_vrecore(self):
        self.log.info('\n')
        self.log.info("test_03_contributor_get_vrecore".center(80, '-'))
        self.log.info(f"GET API: {self.test_api}")
        try:
            auth_user = {'username': 'jzhang33',
                         'password': 'Indoc1234567!',
                         'realm': 'vre'}
            token = self.test.auth(auth_user)
            param = {"project_code": self.project_code,
                     "zone": 'vrecore',
                     "folder": '',
                     "source_type": 'Dataset'}
            headers = {"Authorization": 'Bearer ' + token}
            res = self.app.get(self.test_api, headers=headers, params=param)
            self.log.info(res.text)
            res_json = res.json()
            self.assertEqual(res.status_code, 403)
            self.assertEqual(res_json.get('code'), 403)
            result = res_json.get('result')
            error_msg = res_json.get('error_msg')
            self.log.info(f"COMPARING RESULT: {result} VS " + '{}')
            self.assertEqual(result, {})
            self.log.info(f"COMPARING ERROR: {error_msg} VS 'Permission Denied' ")
            self.assertEqual(error_msg, 'Permission Denied')
        except Exception as e:
            self.log.error(f"test_03 error: {e}")
            raise e

    def test_04_get_files_in_folder_not_exist(self):
        self.log.info('\n')
        self.log.info("test_04_get_files_in_folder_not_exist".center(80, '-'))
        self.log.info(f"GET API: {self.test_api}")
        try:
            param = {"project_code": self.project_code,
                     "zone": 'greenroom',
                     "folder": 'thefolderthatcannotexist05191047',
                     "source_type": 'Folder'}
            headers = {"Authorization": 'Bearer ' + self.token}
            self.log.info(param)
            res = self.app.get(self.test_api, headers=headers, params=param)
            self.log.info(res.text)
            res_json = res.json()
            result = res_json.get('result')
            self.assertEqual(res.status_code, 404)
            self.assertEqual(res_json.get('code'), 404)
            error_msg = res_json.get('error_msg')
            self.log.info(f"COMPARING RESULT: {result} VS " + '{}')
            self.assertEqual(result, {})
            self.log.info(f"COMPARING ERROR: {error_msg} VS 'Folder not exist' ")
            self.assertEqual(error_msg, 'Folder not exist')
        except Exception as e:
            self.log.error(f"test_04 error: {e}")
            raise e

    def test_05_get_files_in_project_not_exist(self):
        self.log.info('\n')
        self.log.info("test_05_get_files_in_project_not_exist".center(80, '-'))
        try:
            test_api = self.test_api.replace(self.project_code, self.project_code+'05191047')
            self.log.info(f"GET API: {test_api}")
            param = {"project_code": self.project_code,
                     "zone": 'greenroom',
                     "folder": '',
                     "source_type": 'Dataset'}
            headers = {"Authorization": 'Bearer ' + self.token}
            self.log.info(param)
            res = self.app.get(test_api, headers=headers, params=param)
            self.log.info(res.text)
            res_json = res.json()
            result = res_json.get('result')
            error_msg = res_json.get('error_msg')
            self.assertEqual(res.status_code, 404)
            self.assertEqual(res_json.get('code'), 404)
            self.log.info(f"COMPARING RESULT: {result} VS " + "{}")
            self.assertEqual(result, {})
            self.log.info(f"COMPARING ERROR: {error_msg} VS 'Project not found'")
            self.assertEqual(error_msg, 'Project not found')
        except Exception as e:
            self.log.error(f"test_05 error: {e}")
            raise e

    def test_06_non_project_member_get_files(self):
        self.log.info('\n')
        self.log.info("test_06_non_project_member_get_files".center(80, '-'))
        self.log.info(f"GET API: {self.test_api}")
        try:
            auth_user = {'username': 'jzhang4',
                         'password': 'Indoc1234567!',
                         'realm': 'vre'}
            token = self.test.auth(auth_user)
            param = {"project_code": self.project_code,
                     "zone": 'Greenroom',
                     "folder": '',
                     "source_type": 'Dataset'}
            headers = {"Authorization": 'Bearer ' + token}
            res = self.app.get(self.test_api, headers=headers, params=param)
            self.log.info(res.text)
            res_json = res.json()
            self.assertEqual(res.status_code, 403)
            self.assertEqual(res_json.get('code'), 403)
            result = res_json.get('result')
            error_msg = res_json.get('error_msg')
            self.log.info(f"COMPARING RESULT: {result} VS 'User not in the project'")
            self.assertEqual(result, 'User not in the project')
            self.log.info(f"COMPARING ERROR: {error_msg} VS 'Permission Denied' ")
            self.assertEqual(error_msg, 'Permission Denied')
        except Exception as e:
            self.log.error(f"test_06 error: {e}")
            raise e

    def test_07_get_files_in_folder_not_exist(self):
        self.log.info('\n')
        self.log.info("test_04_get_files_in_folder_not_exist".center(80, '-'))
        self.log.info(f"GET API: {self.test_api}")
        try:
            param = {"project_code": self.project_code,
                     "zone": 'greenroom',
                     "folder": 'thefolderthatcannotexist05191047',
                     "source_type": 'Folder'}
            headers = {"Authorization": 'Bearer ' + self.token}
            self.log.info(param)
            res = self.app.get(self.test_api, headers=headers, params=param)
            self.log.info(res.text)
            res_json = res.json()
            result = res_json.get('result')
            self.assertEqual(res.status_code, 404)
            self.assertEqual(res_json.get('code'), 404)
            error_msg = res_json.get('error_msg')
            self.log.info(f"COMPARING RESULT: {result} VS " + '{}')
            self.assertEqual(result, {})
            self.log.info(f"COMPARING ERROR: {error_msg} VS 'Folder not exist' ")
            self.assertEqual(error_msg, 'Folder not exist')
        except Exception as e:
            self.log.error(f"test_04 error: {e}")
            raise e

