from app.config import ConfigClass
from .prepare_test import SetupTest
from logger import LoggerFactory
import os
from unittest import IsolatedAsyncioTestCase
from httpx import AsyncClient

class TestGetProjectFilesFolders(IsolatedAsyncioTestCase):
    log = LoggerFactory(name='test_project_get_folder.log').get_logger()
    test = SetupTest(log)
    app = test.client
    token = test.auth()
    project_code = os.environ.get('project_code')
    test_api = f"/v1/project/{project_code}/folder"
    folder_name = 'unittest folder1'
    folder_core = 'unittest core1'
    admin_user = 'jzhang10'
    contributor_user = 'jzhang33'

    async def test_01_get_folder_gr(self):
        self.log.info('\n')
        self.log.info("test_01_get_folder_gr".center(80, '-'))
        self.log.info(f"GET API: {self.test_api}")
        try:
            param = {'zone': 'greenroom',
                     'project_code': self.project_code,
                     'folder': f"{self.admin_user}/{self.folder_name}"
                     }
            async with AsyncClient(app=self.app, base_url="http://test") as ac:
                headers = {"Authorization": 'Bearer ' + self.token}
                self.log.info(f"GET PARAM: {param}")
                res = await ac.get(self.test_api, headers=headers, params=param)
            self.log.info(res.text)
            res_json = res.json()
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res_json.get('code'), 200)
            result = res_json.get('result')
            labels = result.get('labels')
            name = result.get('name')
            project = result.get('project_code')
            self.log.info(f"COMPARING LABELS: {labels} VS ['Greenroom', 'Folder']")
            self.assertEqual(set(labels), {'Greenroom', 'Folder'})
            self.log.info(f"COMPARING name: {name} VS {self.folder_name}")
            self.assertEqual(name, self.folder_name)
            self.log.info(f"COMPARING project: {project} VS {self.project_code}")
            self.assertEqual(project, self.project_code)
        except Exception as e:
            self.log.error(f"test_01 error: {e}")
            raise e

    async def test_02_get_sub_folder_gr(self):
        self.log.info('\n')
        self.log.info("test_02_get_sub_folder_gr".center(80, '-'))
        self.log.info(f"GET API: {self.test_api}")
        sub_foldername = 'folder1'
        relative_path = f'{self.admin_user}/{self.folder_name}'
        folder_path = f'{self.admin_user}/{self.folder_name}/{sub_foldername}'
        try:
            param = {'zone': 'greenroom',
                     'project_code': self.project_code,
                     'folder': folder_path}
            async with AsyncClient(app=self.app, base_url="http://test") as ac:
                headers = {"Authorization": 'Bearer ' + self.token}
                res = await ac.get(self.test_api, headers=headers, params=param)
            self.log.info(res.text)
            res_json = res.json()
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res_json.get('code'), 200)
            result = res_json.get('result')
            labels = result.get('labels')
            name = result.get('name')
            project = result.get('project_code')
            rel_path = result.get('folder_relative_path')
            self.log.info(f"COMPARING LABELS: {labels} VS ['Greenroom', 'Folder']")
            self.assertEqual(set(labels), {'Greenroom', 'Folder'})
            self.log.info(f"COMPARING name: {name} VS {sub_foldername}")
            self.assertEqual(name, sub_foldername)
            self.log.info(f"COMPARING project: {project} VS {self.project_code}")
            self.assertEqual(project, self.project_code)
            self.log.info(f"COMPARING relative_path: {rel_path} VS {relative_path}")
            self.assertEqual(rel_path, relative_path)
        except Exception as e:
            self.log.error(f"test_02 error: {e}")
            raise e

    async def test_03_get_folder_no_access_gr(self):
        self.log.info('\n')
        self.log.info("test_03_get_folder_no_access_gr".center(80, '-'))
        self.log.info(f"GET API: {self.test_api}")
        try:
            token = self.test.auth(self.test.login_contributor())
            param = {'zone': 'greenroom',
                     'project_code': self.project_code,
                     'folder': f'{self.admin_user}/{self.folder_name}'}
            async with AsyncClient(app=self.app, base_url="http://test") as ac:
                headers = {"Authorization": 'Bearer ' + token}
                res = await ac.get(self.test_api, headers=headers, params=param)
            self.log.info(res.text)
            res_json = res.json()
            self.assertEqual(res.status_code, 403)
            self.assertEqual(res_json.get('code'), 403)
            self.log.info(f"COMPARING ERROR: {res_json.get('error_msg')} VS 'Permission Denied'")
            self.assertEqual(res_json.get('error_msg'), 'Permission Denied')
        except Exception as e:
            self.log.error(f"test_03 error: {e}")
            raise e

    async def test_04_get_folder_no_access_core(self):
        self.log.info('\n')
        self.log.info("test_04_get_folder_no_access_core".center(80, '-'))
        self.log.info(f"GET API: {self.test_api}")
        try:
            token = self.test.auth(self.test.login_contributor())
            param = {'zone': ConfigClass.CORE_ZONE_LABEL.lower(),
                     'project_code': self.project_code,
                     'folder': f'{self.contributor_user}/{self.folder_core}'}
            async with AsyncClient(app=self.app, base_url="http://test") as ac:
                headers = {"Authorization": 'Bearer ' + token}
                self.log.info(f"GET PARAM: {param}")
                res = await ac.get(self.test_api, headers=headers, params=param)
            self.log.info(res.text)
            res_json = res.json()
            self.assertEqual(res.status_code, 403)
            self.assertEqual(res_json.get('code'), 403)
            self.log.info(f"COMPARING ERROR: {res_json.get('error_msg')} VS 'Permission Denied'")
            self.assertEqual(res_json.get('error_msg'), 'Permission Denied')
        except Exception as e:
            self.log.error(f"test_04 error: {e}")
            raise e

    async def test_05_get_folder_core(self):
        self.log.info('\n')
        self.log.info("test_05_get_folder_core".center(80, '-'))
        self.log.info(f"GET API: {self.test_api}")
        try:
            param = {'zone': ConfigClass.CORE_ZONE_LABEL.lower(),
                     'project_code': self.project_code,
                     'folder': f'{self.admin_user}/{self.folder_core}'}
            async with AsyncClient(app=self.app, base_url="http://test") as ac:
                headers = {"Authorization": 'Bearer ' + self.token}
                self.log.info(f"Get params: {param}")
                res = await ac.get(self.test_api, headers=headers, params=param)
            self.log.info(res.text)
            res_json = res.json()
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res_json.get('code'), 200)
            result = res_json.get('result')
            labels = result.get('labels')
            name = result.get('name')
            project = result.get('project_code')
            rel_path = result.get('folder_relative_path')
            self.log.info(f"COMPARING LABELS: {labels} VS f{[ConfigClass.CORE_ZONE_LABEL, 'Folder']}")
            self.assertEqual(set(labels), {ConfigClass.CORE_ZONE_LABEL, 'Folder'})
            self.log.info(f"COMPARING name: {name} VS {self.folder_core}")
            self.assertEqual(name, self.folder_core)
            self.log.info(f"COMPARING project: {project} VS {self.project_code}")
            self.assertEqual(project, self.project_code)
            self.log.info(f"COMPARING relative_path: {rel_path} VS {self.admin_user}")
            self.assertEqual(rel_path, self.admin_user)
        except Exception as e:
            self.log.error(f"test_05 error: {e}")
            raise e

    async def test_06_get_sub_folder_core(self):
        self.log.info('\n')
        self.log.info("test_06_get_sub_folder_core".center(80, '-'))
        self.log.info(f"GET API: {self.test_api}")
        sub_folder = 'core1'
        folder_path = f'{self.admin_user}/{self.folder_core}/{sub_folder}'
        relative_path = f'{self.admin_user}/{self.folder_core}'
        try:
            param = {'zone': ConfigClass.CORE_ZONE_LABEL.lower(),
                     'project_code': self.project_code,
                     'folder': folder_path}
            async with AsyncClient(app=self.app, base_url="http://test") as ac:
                headers = {"Authorization": 'Bearer ' + self.token}
                self.log.info(f"Get param: {param}")
                res = await ac.get(self.test_api, headers=headers, params=param)
            self.log.info(res.text)
            res_json = res.json()
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res_json.get('code'), 200)
            result = res_json.get('result')
            labels = result.get('labels')
            name = result.get('name')
            project = result.get('project_code')
            rel_path = result.get('folder_relative_path')
            self.log.info(f"COMPARING LABELS: {labels} VS {[ConfigClass.CORE_ZONE_LABEL, 'Folder']}")
            self.assertEqual(set(labels), {ConfigClass.CORE_ZONE_LABEL, 'Folder'})
            self.log.info(f"COMPARING name: {name} VS {sub_folder}")
            self.assertEqual(name, sub_folder)
            self.log.info(f"COMPARING project: {project} VS {self.project_code}")
            self.assertEqual(project, self.project_code)
            self.log.info(f"COMPARING relative_path: {rel_path} VS {relative_path}")
            self.assertEqual(rel_path, relative_path)
        except Exception as e:
            self.log.error(f"test_06 error: {e}")
            raise e

    async def test_07_get_folder_not_exist_core(self):
        self.log.info('\n')
        self.log.info("test_07_get_folder_not_exist_core".center(80, '-'))
        self.log.info(f"GET API: {self.test_api}")
        sub_folder = 'core2021'
        relative_path = f'{self.admin_user}/{self.folder_core}/{sub_folder}'
        try:
            param = {'zone': ConfigClass.CORE_ZONE_LABEL.lower(),
                     'project_code': self.project_code,
                     'folder': relative_path}
            async with AsyncClient(app=self.app, base_url="http://test") as ac:
                headers = {"Authorization": 'Bearer ' + self.token}
                self.log.info(f"Get param: {param}")
                res = await ac.get(self.test_api, headers=headers, params=param)
            self.log.info(res.text)
            res_json = res.json()
            self.assertEqual(res.status_code, 404)
            self.assertEqual(res_json.get('code'), 404)
            self.log.info(f"COMPARING ERROR: {res_json.get('error_msg')} VS 'Folder not exist'")
            self.assertEqual(res_json.get('error_msg'), 'Folder not exist')
            self.log.info(f"COMPARING RESULT: {res_json.get('result')} VS []")
            self.assertEqual(res_json.get('result'), [])
        except Exception as e:
            self.log.error(f"test_07 error: {e}")
            raise e
