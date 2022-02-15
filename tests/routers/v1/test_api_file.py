import unittest

from app.config import ConfigClass
from ...prepare_test import SetupTest
from ...logger import Logger
import time
from unittest import IsolatedAsyncioTestCase
from httpx import AsyncClient
case_to_run = ''
no_access_user_name = "jzhang53"
no_access_user_password = "Indoc1234567!"

admin_user = 'jzhang10'
collaborator_user = 'jzhang3'
contributor_user = 'jzhang33'

pre_defined_folder = "admin_folder"


@unittest.skipIf(case_to_run == 'core', 'Run specific test')
class TestGetFilesFoldersGR(IsolatedAsyncioTestCase):
    log = Logger(name='test_list_files_folders.log')
    test = SetupTest(log)
    app = test.client
    token = test.auth()
    project_code = "cli"
    test_api = f"/v1/{project_code}/files/query"
    to_delete = []
    admin_gr = ""
    collaborator_gr = ""
    contributor_gr = ""
    admin_core = ""
    collaborator_core = ""
    contributor_core = ""
    zone = ConfigClass.GREEN_ZONE_LABEL.lower()

    @classmethod
    def setUpClass(cls):
        cls.admin_gr = "admin_gr_" + str(time.time() * 1000)[0:12]
        cls.collaborator_gr = "collaborator_gr_" + str(time.time() * 1000)[0:12]
        cls.contributor_gr = "contributor_gr_" + str(time.time() * 1000)[0:12]
        cls.collaborator_folder_file_gr = "collaborator_folder_gr_" + str(time.time() * 1000)[0:12]
        cls.contributor_folder_file_gr = "contributor__folder_gr_" + str(time.time() * 1000)[0:12]
        # create GR files
        admin_file_res_gr = cls.test.create_file(cls.project_code, cls.admin_gr, uploader=admin_user)
        cls.log.info(f"admin {ConfigClass.GREEN_ZONE_LABEL} file response: {admin_file_res_gr}")
        collaborator_res_gr = cls.test.create_file(cls.project_code, cls.collaborator_gr,
                                                   uploader=collaborator_user)
        cls.log.info(f"collaborator {ConfigClass.GREEN_ZONE_LABEL} file response: {collaborator_res_gr}")
        contributor_res_gr = cls.test.create_file(cls.project_code, cls.contributor_gr,
                                                  uploader=contributor_user)
        cls.log.info(f"contributor {ConfigClass.GREEN_ZONE_LABEL} file response: {contributor_res_gr}")
        # create file in folder
        collaborator_folder_gr = cls.test.create_file(cls.project_code, cls.collaborator_folder_file_gr,
                                                      folder=pre_defined_folder, uploader=collaborator_user)
        cls.log.info(f"collaborator {ConfigClass.GREEN_ZONE_LABEL} folder file response: {collaborator_folder_gr}")
        contributor_folder_gr = cls.test.create_file(cls.project_code, cls.contributor_folder_file_gr,
                                                     folder=pre_defined_folder, uploader=contributor_user)
        cls.log.info(f"contributor {ConfigClass.GREEN_ZONE_LABEL} folder file response: {contributor_folder_gr}")

        admin_id = admin_file_res_gr.get('id')
        collaborator_id = collaborator_res_gr.get('id')
        contributor_id = contributor_res_gr.get('id')
        collaborator_folder_file_id = collaborator_folder_gr.get('id')
        contributor_folder_file_id = contributor_folder_gr.get('id')
        cls.to_delete = [admin_id, collaborator_id, contributor_id,
                         collaborator_folder_file_id, contributor_folder_file_id]
        cls.log.info(f'file ID list: {cls.to_delete}')

    @classmethod
    def tearDownClass(cls):
        cls.log.info("DELETING FILES".center(80, '-'))
        cls.log.info(f"Files to be deleted: {cls.to_delete}")
        for file_id in cls.to_delete:
            cls.test.delete_file(file_id)

    async def test_01_admin_get_name_folders(self):
        self.log.info('\n')
        self.log.info("test_01_get_name_folder".center(80, '-'))
        self.log.info(f"GET API: {self.test_api}")
        try:
            param = {"project_code": self.project_code,
                     "zone": self.zone,
                     "folder": '',
                     "source_type": 'Container'}
            async with AsyncClient(app=self.app, base_url="http://test") as ac:
                headers = {"Authorization": 'Bearer ' + self.token}
                res = await ac.get(self.test_api, headers=headers, params=param)
            self.log.info(res.text)
            res_json = res.json()
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res_json.get('code'), 200)
            result = res_json.get('result')
            self.log.info(f'Get files: {len(result)}')
            name_folders = []
            for f in result:
                self.log.info(f"{f.get('name')}")
                name_folders.append(f.get('name'))
                self.log.info(f"COMPARING LABELS: {ConfigClass.GREEN_ZONE_LABEL} VS {f.get('labels')}")
                self.assertIn(ConfigClass.GREEN_ZONE_LABEL, f.get('labels'))
                self.log.info(f"COMPARING PROJECT CODE: {self.project_code} VS {f.get('project_code')}")
                self.assertEqual(self.project_code, f.get('project_code'))
            self.log.info(f"Check jzhang10 IN {name_folders}")
            self.assertIn('jzhang10', name_folders)
            self.log.info(f"Check jzhang3 IN {name_folders}")
            self.assertIn('jzhang3', name_folders)
            self.log.info(f"Check jzhang33 IN {name_folders}")
            self.assertIn('jzhang33', name_folders)
        except Exception as e:
            self.log.error(f"test_01 error: {e}")
            raise e

    async def test_02_collaborator_get_name_folders(self):
        self.log.info('\n')
        self.log.info("test_02_collaborator_get_name_folder".center(80, '-'))
        self.log.info(f"GET API: {self.test_api}")
        try:
            param = {"project_code": self.project_code,
                     "zone": self.zone,
                     "folder": '',
                     "source_type": 'Container'}
            token = self.test.auth(self.test.login_collaborator())
            async with AsyncClient(app=self.app, base_url="http://test") as ac:
                headers = {"Authorization": 'Bearer ' + token}
                res = await ac.get(self.test_api, headers=headers, params=param)
            self.log.info(res.text)
            res_json = res.json()
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res_json.get('code'), 200)
            result = res_json.get('result')
            self.log.info(f'Get files: {len(result)}')
            name_folders = []
            for f in result:
                self.log.info(f"{f.get('name')}")
                name_folders.append(f.get('name'))
                self.log.info(f"COMPARING LABELS: {ConfigClass.GREEN_ZONE_LABEL} VS {f.get('labels')}")
                self.assertIn(ConfigClass.GREEN_ZONE_LABEL, f.get('labels'))
                self.log.info(f"COMPARING PROJECT CODE: {self.project_code} VS {f.get('project_code')}")
                self.assertEqual(self.project_code, f.get('project_code'))
            self.log.info(f"Check jzhang10 NOT IN {name_folders}")
            self.assertNotIn('jzhang10', name_folders)
            self.log.info(f"Check jzhang3 IN {name_folders}")
            self.assertIn('jzhang3', name_folders)
            self.log.info(f"Check jzhang33 NOT IN {name_folders}")
            self.assertNotIn('jzhang33', name_folders)
        except Exception as e:
            self.log.error(f"test_02 error: {e}")
            raise e

    async def test_03_contributor_get_name_folders(self):
        self.log.info('\n')
        self.log.info("test_03_contributor_get_name_folders".center(80, '-'))
        self.log.info(f"GET API: {self.test_api}")
        try:
            param = {"project_code": self.project_code,
                     "zone": self.zone,
                     "folder": '',
                     "source_type": 'Container'}
            token = self.test.auth(self.test.login_contributor())
            async with AsyncClient(app=self.app, base_url="http://test") as ac:
                headers = {"Authorization": 'Bearer ' + token}
                res = await ac.get(self.test_api, headers=headers, params=param)
            self.log.info(res.text)
            res_json = res.json()
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res_json.get('code'), 200)
            result = res_json.get('result')
            self.log.info(f'Get files: {len(result)}')
            name_folders = []
            for f in result:
                self.log.info(f"{f.get('name')}")
                name_folders.append(f.get('name'))
                self.log.info(f"COMPARING LABELS: {ConfigClass.GREEN_ZONE_LABEL} VS {f.get('labels')}")
                self.assertIn(ConfigClass.GREEN_ZONE_LABEL, f.get('labels'))
                self.log.info(f"COMPARING PROJECT CODE: {self.project_code} VS {f.get('project_code')}")
                self.assertEqual(self.project_code, f.get('project_code'))
            self.log.info(f"Check jzhang10 NOT IN {name_folders}")
            self.assertNotIn('jzhang10', name_folders)
            self.log.info(f"Check jzhang3 NOT IN {name_folders}")
            self.assertNotIn('jzhang3', name_folders)
            self.log.info(f"Check jzhang33 IN {name_folders}")
            self.assertIn('jzhang33', name_folders)
        except Exception as e:
            self.log.error(f"test_03 error: {e}")
            raise e

    async def test_04_admin_get_files_contributor_folder_gr(self):
        self.log.info('\n')
        self.log.info("test_04_admin_get_files_contributor_folder_gr".center(80, '-'))
        self.log.info(f"GET API: {self.test_api}")
        try:
            param = {"project_code": self.project_code,
                     "zone": self.zone,
                     "folder": contributor_user,
                     "source_type": 'Folder'}
            async with AsyncClient(app=self.app, base_url="http://test") as ac:
                headers = {"Authorization": 'Bearer ' + self.token}
                self.log.info(f"GET PARAM {param}")
                res = await ac.get(self.test_api, headers=headers, params=param)
            self.log.info(res.text)
            res_json = res.json()
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res_json.get('code'), 200)
            result = res_json.get('result')
            files = []
            for f in result:
                self.log.info(f"{f.get('name')}")
                files.append(f.get('name'))
            self.log.info(f"Check {self.contributor_gr} IN {files}")
            self.assertIn(self.contributor_gr, files)
        except Exception as e:
            self.log.error(f"test_04 error: {e}")
            raise e

    async def test_05_collaborator_get_files_contributor_folder_gr(self):
        self.log.info('\n')
        self.log.info("test_05_collaborator_get_files_contributor_folder_gr".center(80, '-'))
        self.log.info(f"GET API: {self.test_api}")
        try:
            param = {"project_code": self.project_code,
                     "zone": self.zone,
                     "folder": contributor_user,
                     "source_type": 'Folder'}
            token = self.test.auth(self.test.login_collaborator())
            async with AsyncClient(app=self.app, base_url="http://test") as ac:
                headers = {"Authorization": 'Bearer ' + token}
                res = await ac.get(self.test_api, headers=headers, params=param)
            self.log.info(res.text)
            res_json = res.json()
            self.assertEqual(res.status_code, 403)
            self.assertEqual(res_json.get('code'), 403)
            result = res_json.get('result')
            files = []
            for f in result:
                self.log.info(f"{f.get('name')}")
                files.append(f.get('name'))
            self.log.info(f"Check [] == {files}")
            self.assertEqual([], files)
        except Exception as e:
            self.log.error(f"test_05 error: {e}")
            raise e

    async def test_06_contributor_get_files_admin_folder_gr(self):
        self.log.info('\n')
        self.log.info("test_06_contributor_get_files_admin_folder_gr".center(80, '-'))
        self.log.info(f"GET API: {self.test_api}")
        try:
            param = {"project_code": self.project_code,
                     "zone": self.zone,
                     "folder": admin_user,
                     "source_type": 'Folder'}
            token = self.test.auth(self.test.login_contributor())
            async with AsyncClient(app=self.app, base_url="http://test") as ac:
                headers = {"Authorization": 'Bearer ' + token}
                res = await ac.get(self.test_api, headers=headers, params=param)
            self.log.info(res.text)
            res_json = res.json()
            self.assertEqual(res.status_code, 403)
            self.assertEqual(res_json.get('code'), 403)
            result = res_json.get('result')
            files = []
            for f in result:
                self.log.info(f"{f.get('name')}")
                files.append(f.get('name'))
            self.log.info(f"Check [] == {files}")
            self.assertEqual([], files)
        except Exception as e:
            self.log.error(f"test_06 error: {e}")
            raise e

    async def test_07_contributor_get_folder_file_gr(self):
        self.log.info('\n')
        self.log.info("test_07_contributor_get_folder_file_gr".center(80, '-'))
        self.log.info(f"GET API: {self.test_api}")
        try:
            param = {"project_code": self.project_code,
                     "zone": self.zone,
                     "folder": f"{contributor_user}/{pre_defined_folder}",
                     "source_type": 'Folder'}
            token = self.test.auth(self.test.login_contributor())
            async with AsyncClient(app=self.app, base_url="http://test") as ac:
                headers = {"Authorization": 'Bearer ' + token}
                self.log.info(f'Get params: {param}')
                res = await ac.get(self.test_api, headers=headers, params=param)
            self.log.info(res.text)
            res_json = res.json()
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res_json.get('code'), 200)
            result = res_json.get('result')
            files = []
            for f in result:
                self.log.info(f"{f.get('name')}")
                files.append(f.get('name'))
            self.log.info(f"Check {self.contributor_folder_file_gr} IN {files}")
            self.assertIn(self.contributor_folder_file_gr, files)
        except Exception as e:
            self.log.error(f"test_07 error: {e}")
            raise e

    async def test_08_collaborator_get_folder_file_gr(self):
        self.log.info('\n')
        self.log.info("test_08_collaborator_get_folder_file_gr".center(80, '-'))
        self.log.info(f"GET API: {self.test_api}")
        try:
            param = {"project_code": self.project_code,
                     "zone": self.zone,
                     "folder": f"{collaborator_user}/{pre_defined_folder}",
                     "source_type": 'Folder'}
            self.log.info(f'Get params: {param}')
            token = self.test.auth(self.test.login_collaborator())
            async with AsyncClient(app=self.app, base_url="http://test") as ac:
                headers = {"Authorization": 'Bearer ' + token}
                res = await ac.get(self.test_api, headers=headers, params=param)
            self.log.info(res.text)
            res_json = res.json()
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res_json.get('code'), 200)
            result = res_json.get('result')
            files = []
            for f in result:
                self.log.info(f"{f.get('name')}")
                files.append(f.get('name'))
            self.log.info(f"Check {self.collaborator_folder_file_gr} IN {files}")
            self.assertIn(self.collaborator_folder_file_gr, files)
        except Exception as e:
            self.log.error(f"test_07 error: {e}")
            raise e


@unittest.skipIf(case_to_run == 'greenroom', 'Run specific test')
class TestGetFilesFoldersCore(IsolatedAsyncioTestCase):
    log = Logger(name='test_list_files_folders.log')
    test = SetupTest(log)
    app = test.client
    token = test.auth()
    project_code = "cli"
    test_api = f"/v1/{project_code}/files/query"
    file_id = []
    to_delete = []
    admin_gr = ""
    collaborator_gr = ""
    contributor_gr = ""
    admin_core = ""
    collaborator_core = ""
    contributor_core = ""
    zone = ConfigClass.CORE_ZONE_LABEL.lower()

    @classmethod
    def setUpClass(cls):
        # core files
        admin_file_core = "admin_core_" + str(time.time() * 1000)[0:12]
        collaborator_file_core = "collaborator_core_" + str(time.time() * 1000)[0:12]
        contributor_file_core = "contributor_core_" + str(time.time() * 1000)[0:12]
        # create Core files
        core = ConfigClass.CORE_ZONE_LABEL
        admin_file_res_core = cls.test.create_file(cls.project_code, admin_file_core,
                                                   zone=core, uploader=admin_user)
        cls.log.info(f"admin core file response: {admin_file_res_core}")
        collaborator_file_res_core = cls.test.create_file(cls.project_code, collaborator_file_core,
                                                          zone=core,
                                                          uploader=collaborator_user)
        cls.log.info(f"collaborator core file response: {collaborator_file_res_core}")
        contributor_file_res_core = cls.test.create_file(cls.project_code, contributor_file_core,
                                                         zone=core,
                                                         uploader=contributor_user)
        cls.log.info(f"contributor core file response: {contributor_file_res_core}")

        admin_core_id = admin_file_res_core.get('id')
        collaborator_core_id = collaborator_file_res_core.get('id')
        contributor_core_id = contributor_file_res_core.get('id')

        cls.to_delete = [admin_core_id, collaborator_core_id, contributor_core_id]
        cls.log.info(f'file geid list: {cls.file_id}')
        cls.admin_core = admin_file_core
        cls.collaborator_core = collaborator_file_core
        cls.contributor_core = contributor_file_core

    @classmethod
    def tearDownClass(cls):
        cls.log.info("DELETING FILES".center(80, '-'))
        cls.log.info(f"Files to be deleted: {cls.to_delete}")
        for file_id in cls.to_delete:
            cls.test.delete_file(file_id)

    async def test_01_admin_get_name_folders_core(self):
        self.log.info('\n')
        self.log.info("test_01_get_name_folder_core".center(80, '-'))
        self.log.info(f"GET API: {self.test_api}")
        try:
            param = {"project_code": self.project_code,
                     "zone": self.zone,
                     "folder": '',
                     "source_type": 'Container'}
            async with AsyncClient(app=self.app, base_url="http://test") as ac:
                headers = {"Authorization": 'Bearer ' + self.token}
                res = await ac.get(self.test_api, headers=headers, params=param)
            self.log.info(res.text)
            res_json = res.json()
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res_json.get('code'), 200)
            result = res_json.get('result')
            self.log.info(f'Get files: {len(result)}')
            name_folders = []
            for f in result:
                self.log.info(f"{f.get('name')}")
                name_folders.append(f.get('name'))
                self.log.info(f"COMPARING LABELS: {ConfigClass.CORE_ZONE_LABEL} VS {f.get('labels')}")
                self.assertIn(ConfigClass.CORE_ZONE_LABEL, f.get('labels'))
                self.log.info(f"COMPARING PROJECT CODE: {self.project_code} VS {f.get('project_code')}")
                self.assertEqual(self.project_code, f.get('project_code'))
            self.log.info(f"Check jzhang10 IN {name_folders}")
            self.assertIn('jzhang10', name_folders)
            self.log.info(f"Check jzhang3 IN {name_folders}")
            self.assertIn('jzhang3', name_folders)
            self.log.info(f"Check jzhang33 IN {name_folders}")
            self.assertIn('jzhang33', name_folders)
        except Exception as e:
            self.log.error(f"test_01 error: {e}")
            raise e

    async def test_02_collaborator_get_name_folders(self):
        self.log.info('\n')
        self.log.info("test_02_collaborator_get_name_folder".center(80, '-'))
        self.log.info(f"GET API: {self.test_api}")
        try:
            param = {"project_code": self.project_code,
                     "zone": self.zone,
                     "folder": '',
                     "source_type": 'Container'}
            token = self.test.auth(self.test.login_collaborator())
            async with AsyncClient(app=self.app, base_url="http://test") as ac:
                headers = {"Authorization": 'Bearer ' + token}
                res = await ac.get(self.test_api, headers=headers, params=param)
            self.log.info(res.text)
            res_json = res.json()
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res_json.get('code'), 200)
            result = res_json.get('result')
            self.log.info(f'Get files: {len(result)}')
            name_folders = []
            for f in result:
                self.log.info(f"{f.get('name')}")
                name_folders.append(f.get('name'))
                self.log.info(f"COMPARING LABELS: {ConfigClass.CORE_ZONE_LABEL} VS {f.get('labels')}")
                self.assertIn(ConfigClass.CORE_ZONE_LABEL, f.get('labels'))
                self.log.info(f"COMPARING PROJECT CODE: {self.project_code} VS {f.get('project_code')}")
                self.assertEqual(self.project_code, f.get('project_code'))
            self.log.info(f"Check jzhang10 IN {name_folders}")
            self.assertIn('jzhang10', name_folders)
            self.log.info(f"Check jzhang3 IN {name_folders}")
            self.assertIn('jzhang3', name_folders)
            self.log.info(f"Check jzhang33 IN {name_folders}")
            self.assertIn('jzhang33', name_folders)
        except Exception as e:
            self.log.error(f"test_02 error: {e}")
            raise e

    async def test_03_contributor_get_name_folders_core(self):
        self.log.info('\n')
        self.log.info("test_03_contributor_get_name_folders_core".center(80, '-'))
        self.log.info(f"GET API: {self.test_api}")
        try:
            param = {"project_code": self.project_code,
                     "zone": self.zone,
                     "folder": '',
                     "source_type": 'Container'}
            token = self.test.auth(self.test.login_contributor())
            async with AsyncClient(app=self.app, base_url="http://test") as ac:
                headers = {"Authorization": 'Bearer ' + token}
                res = await ac.get(self.test_api, headers=headers, params=param)
            self.log.info(res.text)
            res_json = res.json()
            self.assertEqual(res.status_code, 403)
            self.assertEqual(res_json.get('code'), 403)
            result = res_json.get('result')
            self.log.info(f'Get files: {len(result)}')
            self.assertEqual(len(result), 0)
        except Exception as e:
            self.log.error(f"test_03 error: {e}")
            raise e

    async def test_04_admin_get_files_contributor_folder_core(self):
        self.log.info('\n')
        self.log.info("test_04_admin_get_files_contributor_folder_core".center(80, '-'))
        self.log.info(f"GET API: {self.test_api}")
        try:
            param = {"project_code": self.project_code,
                     "zone": self.zone,
                     "folder": contributor_user,
                     "source_type": 'Folder'}
            async with AsyncClient(app=self.app, base_url="http://test") as ac:
                headers = {"Authorization": 'Bearer ' + self.token}
                res = await ac.get(self.test_api, headers=headers, params=param)
            self.log.info(res.text)
            res_json = res.json()
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res_json.get('code'), 200)
            result = res_json.get('result')
            files = []
            for f in result:
                self.log.info(f"{f.get('name')}")
                files.append(f.get('name'))
            self.log.info(f"Check {self.contributor_gr} IN {files}")
            self.assertIn(self.contributor_core, files)
        except Exception as e:
            self.log.error(f"test_04 error: {e}")
            raise e

    async def test_05_collaborator_get_files_contributor_folder_core(self):
        self.log.info('\n')
        self.log.info("test_05_collaborator_get_files_contributor_folder_core".center(80, '-'))
        self.log.info(f"GET API: {self.test_api}")
        try:
            param = {"project_code": self.project_code,
                     "zone": self.zone,
                     "folder": contributor_user,
                     "source_type": 'Folder'}
            token = self.test.auth(self.test.login_collaborator())
            async with AsyncClient(app=self.app, base_url="http://test") as ac:
                headers = {"Authorization": 'Bearer ' + token}
                res = await ac.get(self.test_api, headers=headers, params=param)
            self.log.info(res.text)
            res_json = res.json()
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res_json.get('code'), 200)
            result = res_json.get('result')
            files = []
            for f in result:
                self.log.info(f"{f.get('name')}")
                files.append(f.get('name'))
            self.log.info(f"Check {self.contributor_gr} IN {files}")
            self.assertIn(self.contributor_core, files)
        except Exception as e:
            self.log.error(f"test_05 error: {e}")
            raise e

    async def test_06_contributor_get_files_admin_folder_core(self):
        self.log.info('\n')
        self.log.info("test_06_contributor_get_files_admin_folder_core".center(80, '-'))
        self.log.info(f"GET API: {self.test_api}")
        try:
            param = {"project_code": self.project_code,
                     "zone": self.zone,
                     "folder": admin_user,
                     "source_type": 'Folder'}
            token = self.test.auth(self.test.login_contributor())
            async with AsyncClient(app=self.app, base_url="http://test") as ac:
                headers = {"Authorization": 'Bearer ' + token}
                res = await ac.get(self.test_api, headers=headers, params=param)
            self.log.info(res.text)
            res_json = res.json()
            self.assertEqual(res.status_code, 403)
            self.assertEqual(res_json.get('code'), 403)
            result = res_json.get('result')
            files = []
            for f in result:
                self.log.info(f"{f.get('name')}")
                files.append(f.get('name'))
            self.log.info(f"Check [] == {files}")
            self.assertEqual([], files)
        except Exception as e:
            self.log.error(f"test_06 error: {e}")
            raise e

