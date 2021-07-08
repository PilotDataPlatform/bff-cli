import unittest
from .prepare_test import SetupTest
from .logger import Logger
import os


@unittest.skip("Deprecated for now")
class TestGetProjectFilesFolders(unittest.TestCase):
    log = Logger(name='test_file_download.log')
    test = SetupTest(log)
    app = test.client
    token = test.auth()
    project_code = os.environ.get('project_code')
    contributor_file = os.environ.get('contributor_file')
    admin_file = os.environ.get('admin_file')
    collaborator_file_core = os.environ.get('collaborator_file_core')
    test_api = f"/v1/files/download/pre"

    def test_01_contributor_download_file_gr(self):
        self.log.info('\n')
        self.log.info("test_01_contributor_download_file_gr".center(80, '-'))
        self.log.info(f"POST API: {self.test_api}")
        self.log.info(f"Target file: {self.contributor_file}")
        try:
            login = {"username": 'jzhang33',
                     "password": "Indoc1234567!",
                     "realm": "vre"}
            token = self.test.auth(login)
            payload = {"files": [{"geid": self.contributor_file}],
                       "operator": "jzhang33",
                       "project_code": self.project_code,
                       "session_id": "downloadtest",
                       "zone": "Greenroom"
                       }
            headers = {"Authorization": 'Bearer ' + token}
            self.log.info(payload)
            self.log.info(headers)
            res = self.app.post(self.test_api, headers=headers, json=payload)
            self.log.info(res.text)
            res_json = res.json()
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res_json.get('code'), 200)
            result = res_json.get('result')
            geid = result.get('geid').split('/')[-1]
            self.log.info(f"COMPARING GEID: {geid} VS {self.contributor_file}")
            self.assertEqual(geid, self.contributor_file)
        except Exception as e:
            self.log.error(f"test_01 error: {e}")
            raise e

    def test_02_contributor_download_others_file(self):
        self.log.info('\n')
        self.log.info("test_02_contributor_download_others_file".center(80, '-'))
        self.log.info(f"POST API: {self.test_api}")
        self.log.info(f"Target file: {self.admin_file}")
        try:
            login = {"username": 'jzhang33',
                     "password": "Indoc1234567!",
                     "realm": "vre"}
            token = self.test.auth(login)
            payload = {"files": [{"geid": self.admin_file}],
                       "operator": "jzhang33",
                       "project_code": self.project_code,
                       "session_id": "downloadtest",
                       "zone": "Greenroom"
                       }
            headers = {"Authorization": 'Bearer ' + token}
            self.log.info(payload)
            self.log.info(headers)
            res = self.app.post(self.test_api, headers=headers, json=payload)
            self.log.info(res.text)
            res_json = res.json()
            self.assertEqual(res.status_code, 403)
            self.assertEqual(res_json.get('code'), 403)
            error = res_json.get('error_msg')
            self.log.info(f"COMPARING ERROR MSG: {error} VS 'Permission Denied'")
            self.assertEqual(error, 'Permission Denied')
        except Exception as e:
            self.log.error(f"test_02 error: {e}")
            raise e

    def test_03_contributor_download_core_file(self):
        self.log.info('\n')
        self.log.info("test_03_contributor_download_core_file".center(80, '-'))
        self.log.info(f"POST API: {self.test_api}")
        self.log.info(f"Target file: {self.collaborator_file_core}")
        try:
            login = {"username": 'jzhang33',
                     "password": "Indoc1234567!",
                     "realm": "vre"}
            token = self.test.auth(login)
            payload = {"files": [{"geid": self.collaborator_file_core}],
                       "operator": "jzhang33",
                       "project_code": self.project_code,
                       "session_id": "downloadtest",
                       "zone": "VRECore"
                       }
            headers = {"Authorization": 'Bearer ' + token}
            self.log.info(payload)
            self.log.info(headers)
            res = self.app.post(self.test_api, headers=headers, json=payload)
            self.log.info(res.text)
            res_json = res.json()
            self.assertEqual(res.status_code, 403)
            self.assertEqual(res_json.get('code'), 403)
            error = res_json.get('error_msg')
            self.log.info(f"COMPARING ERROR MSG: {error} VS 'Permission Denied'")
            self.assertEqual(error, 'Permission Denied')
        except Exception as e:
            self.log.error(f"test_03 error: {e}")
            raise e

    def test_04_admin_download_file(self):
        self.log.info('\n')
        self.log.info("test_04_admin_download_file".center(80, '-'))
        self.log.info(f"POST API: {self.test_api}")
        self.log.info(f"Target file: {self.admin_file}")
        try:
            payload = {"files": [{"geid": self.admin_file}],
                       "operator": "jzhang21",
                       "project_code": self.project_code,
                       "session_id": "downloadtest",
                       "zone": "Greenroom"
                       }
            headers = {"Authorization": 'Bearer ' + self.token}
            self.log.info(payload)
            self.log.info(headers)
            res = self.app.post(self.test_api, headers=headers, json=payload)
            self.log.info(res.text)
            res_json = res.json()
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res_json.get('code'), 200)
            result = res_json.get('result')
            geid = result.get('geid').split('/')[-1]
            self.log.info(f"COMPARING GEID: {geid} VS {self.admin_file}")
            self.assertEqual(geid, self.admin_file)
        except Exception as e:
            self.log.error(f"test_04 error: {e}")
            raise e

    def test_05_collaborator_download_core_file(self):
        self.log.info('\n')
        self.log.info("test_05_collaborator_download_core_file".center(80, '-'))
        self.log.info(f"POST API: {self.test_api}")
        self.log.info(f"Target file: {self.collaborator_file_core}")
        try:
            login = {"username": 'jzhang3',
                     "password": "Indoc1234567!",
                     "realm": "vre"}
            token = self.test.auth(login)
            payload = {"files": [{"geid": self.collaborator_file_core}],
                       "operator": "jzhang3",
                       "project_code": self.project_code,
                       "session_id": "downloadtest",
                       "zone": "VRECore"
                       }
            headers = {"Authorization": 'Bearer ' + token}
            self.log.info(f"POST PAYLOAD: {payload}")
            self.log.info(F"POST HEADRERS: {headers}")
            res = self.app.post(self.test_api, headers=headers, json=payload)
            self.log.info(f"POST RESPONE: {res.text}")
            res_json = res.json()
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res_json.get('code'), 200)
            result = res_json.get('result')
            geid = result.get('geid').split('/')[-1]
            self.log.info(f"COMPARING GEID: {geid} VS {self.collaborator_file_core}")
            self.assertEqual(geid, self.collaborator_file_core)
        except Exception as e:
            self.log.error(f"test_05 error: {e}")
            raise e

    def test_06_collaborator_download_others_file_gr(self):
        self.log.info('\n')
        self.log.info("test_06_collaborator_download_others_file_gr".center(80, '-'))
        self.log.info(f"POST API: {self.test_api}")
        self.log.info(f"Target file: {self.contributor_file}")
        try:
            login = {"username": 'jzhang3',
                     "password": "Indoc1234567!",
                     "realm": "vre"}
            token = self.test.auth(login)
            payload = {"files": [{"geid": self.contributor_file}],
                       "operator": "jzhang33",
                       "project_code": self.project_code,
                       "session_id": "downloadtest",
                       "zone": "Greenroom"
                       }
            headers = {"Authorization": 'Bearer ' + token}
            self.log.info(payload)
            self.log.info(headers)
            res = self.app.post(self.test_api, headers=headers, json=payload)
            self.log.info(res.text)
            res_json = res.json()
            self.assertEqual(res.status_code, 403)
            self.assertEqual(res_json.get('code'), 403)
            error = res_json.get('error_msg')
            self.log.info(f"COMPARING ERROR MSG: {error} VS 'Permission Denied'")
            self.assertEqual(error, 'Permission Denied')
        except Exception as e:
            self.log.error(f"test_06 error: {e}")
            raise e
