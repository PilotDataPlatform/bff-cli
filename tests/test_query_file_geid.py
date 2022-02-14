from app.config import ConfigClass
import time
import os
from .prepare_test import SetupTest
from logger import LoggerFactory
from unittest import IsolatedAsyncioTestCase
from httpx import AsyncClient

class TestQueryFileGeid(IsolatedAsyncioTestCase):
    log = LoggerFactory(name='test_query_file_geid.log').get_logger()
    test = SetupTest(log)
    app = test.client
    test_api = "/v1/query/geid"
    token = test.auth()
    file_geid = ''
    folder_file_geid = ''
    folder_file_core_geid = ''
    file_id = ''
    folder_file_id = ''
    folder_file_core_id = ''
    project_code = os.environ.get('project_code')
    file_name = 'unittest_file_' + str(time.time())[0:10]
    folder = "unittest folder1"
    folder_core = "unittest core1"
    uploader = 'jzhang10'
    trash_geid = '18aff571-1669-4d39-932f-01f4d1495ec7-1626111037'

    @classmethod
    def setUpClass(cls):
        cls.log.info(f"{'Test setUp'.center(80, '=')}")
        create_res = cls.test.create_file(cls.project_code, cls.file_name, uploader=cls.uploader)
        create_folder_file_res = cls.test.create_file(cls.project_code, cls.file_name,
                                                      folder=cls.folder, uploader=cls.uploader)
        folder_file_core_res = cls.test.create_file(cls.project_code, cls.file_name,
                                                    folder=cls.folder_core, zone=ConfigClass.CORE_ZONE_LABEL,
                                                    uploader=cls.uploader)
        cls.log.info(f"CREATE FILE: {create_res}")
        cls.file_geid = create_res.get('global_entity_id')
        cls.log.info(f"CREATE FOLDER FILE: {create_folder_file_res}")
        cls.folder_file_geid = create_folder_file_res.get('global_entity_id')
        cls.log.info(f"CREATE FOLDER FILE CORE: {folder_file_core_res}")
        cls.folder_file_core_geid = folder_file_core_res.get('global_entity_id')

        cls.file_id = create_res.get('id')
        cls.folder_file_id = create_folder_file_res.get('id')
        cls.folder_file_core_id = folder_file_core_res.get('id')

    @classmethod
    def tearDownClass(cls):
        cls.log.info('Test tearDown'.center(80, '='))
        delete_res = cls.test.delete_file(cls.file_id)
        cls.log.info(f"DELETE FILE: {delete_res}")
        delete_folder_file_res = cls.test.delete_file(cls.folder_file_id)
        cls.log.info(f"DELETE FOLDER FILE: {delete_folder_file_res}")
        delete_folder_file_core_res = cls.test.delete_file(cls.folder_file_core_id)
        cls.log.info(f"DELETE FOLDER FILE: {delete_folder_file_core_res}")

    async def test_01_query_file_by_geid(self):
        self.log.info('\n')
        self.log.info("test_01_query_file_by_geid".center(80, '-'))
        payload = {'geid': [self.file_geid, self.folder_file_geid, self.folder_file_core_geid]}
        _token = self.test.auth()
        try:
            self.log.info(f"POST API: {self.test_api}")
            self.log.info(f"POST PAYLOAD: {payload}")
            async with AsyncClient(app=self.app, base_url="http://test") as ac:
                headers = {'Authorization': 'Bearer ' + _token}
                res = await ac.post(self.test_api, headers=headers, json=payload)
            self.log.info(f"RESPONSE: {res.text}")
            res_json = res.json()
            result = res_json.get('result')
            self.log.info(f"Query result: {result}")
            for file in result:
                status = file.get('status')
                self.log.info(f'Query status: {status}')
                self.log.info(f"Comparing status: 'success' VS {status}")
                self.assertEqual('success', status)
                file_info = file.get('result')[0]
                self.log.info(f'File info: {file_info}')
                geid = file_info.get('global_entity_id')
                self.log.info(f'File geid: {geid}')
                project_code = file_info.get('project_code')
                self.log.info(f"Comparing project code: {self.project_code} VS {project_code}")
                self.assertEqual(self.project_code, project_code)
                if geid == self.file_geid:
                    display_path = f"{self.uploader}/{self.file_name}"
                    labels = ['File', ConfigClass.GREEN_ZONE_LABEL]
                    query_display_path = file_info.get('display_path')
                    query_label = file_info.get('labels')
                    self.log.info(f"Comparing display_path: {display_path} VS {query_display_path}")
                    self.assertEqual(display_path, query_display_path)
                    self.log.info(f"Comparing labels: {set(labels)} VS {set(query_label)}")
                    self.assertEqual(set(labels), set(query_label))
                elif geid == self.folder_file_geid:
                    display_path = f"{self.uploader}/{self.folder}/{self.file_name}"
                    labels = ['File', ConfigClass.GREEN_ZONE_LABEL]
                    query_display_path = file_info.get('display_path')
                    query_label = file_info.get('labels')
                    self.log.info(f"Comparing display_path: {display_path} VS {query_display_path}")
                    self.assertEqual(display_path, query_display_path)
                    self.log.info(f"Comparing labels: {set(labels)} VS {set(query_label)}")
                    self.assertEqual(set(labels), set(query_label))
                elif geid == self.folder_file_core_geid:
                    display_path = f"{self.uploader}/{self.folder_core}/{self.file_name}"
                    labels = ['File', ConfigClass.CORE_ZONE_LABEL]
                    query_display_path = file_info.get('display_path')
                    query_label = file_info.get('labels')
                    self.log.info(f"Comparing display_path: {display_path} VS {query_display_path}")
                    self.assertEqual(display_path, query_display_path)
                    self.log.info(f"Comparing labels: {set(labels)} VS {set(query_label)}")
                    self.assertEqual(set(labels), set(query_label))
                else:
                    raise Exception('Invalid geid retreived')
        except Exception as e:
            self.log.error(f"ERROR: {e}")
            raise e

    async def test_02_query_file_by_non_exist_geid(self):
        self.log.info('\n')
        self.log.info("test_02_query_file_by_non_exist_geid".center(80, '-'))
        fake_geid = 'abcdefg-1234567'
        payload = {'geid': [fake_geid]}
        _token = self.test.auth()
        try:
            self.log.info(f"POST API: {self.test_api}")
            self.log.info(f"POST PAYLOAD: {payload}")
            async with AsyncClient(app=self.app, base_url="http://test") as ac:
                headers = {'Authorization': 'Bearer ' + _token}
                res = await ac.post(self.test_api, headers=headers, json=payload)
            self.log.info(f"RESPONSE: {res.text}")
            res_json = res.json()
            result = res_json.get('result')
            self.log.info(f"Query result: {result}")
            for file in result:
                status = file.get('status')
                self.log.info(f'Query status: {status}')
                self.assertEqual('File Not Exist', status)
                geid = file.get('geid')
                file_result = file.get('result')
                self.assertEqual(file_result, [])
                self.assertEqual(geid, fake_geid)
        except Exception as e:
            self.log.error(f"ERROR: {e}")
            raise e

    async def test_03_query_file_by_no_access_user(self):
        self.log.info('\n')
        self.log.info("test_03_query_file_by_no_access_user".center(80, '-'))
        file_geid_list = [self.file_geid, self.folder_file_geid, self.folder_file_core_geid]
        payload = {'geid': file_geid_list}
        login_user = {
            "username": "jzhang33",
            "password": "Indoc1234567!"
        }
        _token = self.test.auth(login_user)
        try:
            self.log.info(f"POST API: {self.test_api}")
            self.log.info(f"POST PAYLOAD: {payload}")
            async with AsyncClient(app=self.app, base_url="http://test") as ac:
                headers = {'Authorization': 'Bearer ' + _token}
                res = await ac.post(self.test_api, headers=headers, json=payload)
            self.log.info(f"RESPONSE: {res.text}")
            res_json = res.json()
            result = res_json.get('result')
            self.log.info(f"Query result: {result}")
            for file in result:
                status = file.get('status')
                self.log.info(f'Query status: {status}')
                self.assertEqual('Permission Denied', status)
                geid = file.get('geid')
                file_result = file.get('result')
                self.assertEqual(file_result, [])
                self.assertIn(geid, file_geid_list)
        except Exception as e:
            self.log.error(f"ERROR: {e}")
            raise e

    async def test_04_query_file_by_no_access_user(self):
        self.log.info('\n')
        self.log.info("test_04_query_file_by_no_access_user".center(80, '-'))
        payload = {'geid': [self.trash_geid]}
        _token = self.test.auth()
        try:
            self.log.info(f"POST API: {self.test_api}")
            self.log.info(f"POST PAYLOAD: {payload}")
            async with AsyncClient(app=self.app, base_url="http://test") as ac:
                headers = {'Authorization': 'Bearer ' + _token}
                res = await ac.post(self.test_api, headers=headers, json=payload)
            self.log.info(f"RESPONSE: {res.text}")
            res_json = res.json()
            result = res_json.get('result')
            self.log.info(f"Query result: {result}")
            for file in result:
                status = file.get('status')
                self.log.info(f'Query status: {status}')
                self.assertEqual('Can only work on file or folder not in Trash Bin', status)
                geid = file.get('geid')
                file_result = file.get('result')
                self.assertEqual(file_result, [])
                self.assertIn(geid, self.trash_geid)
        except Exception as e:
            self.log.error(f"ERROR: {e}")
            raise e


