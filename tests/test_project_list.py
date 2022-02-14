import unittest
from .prepare_test import SetupTest
from logger import LoggerFactory
from unittest import IsolatedAsyncioTestCase
from httpx import AsyncClient


class TestFiles(IsolatedAsyncioTestCase):
    log = LoggerFactory(name='test_projects.log').get_logger()
    test = SetupTest(log)
    app = test.client
    test_api = "/v1/projects"

    async def test_01_admin_get_list(self):
        self.log.info("test_01_admin_get_list".center(80, '-'))
        payload = {
            "username": "admin",
            "password": "admin"
        }
        token = self.test.auth(payload)
        self.log.info(f"GET API: {self.test_api}")
        try:
            async with AsyncClient(app=self.app, base_url="http://test") as ac:
                headers = {'Authorization': 'Bearer ' + token}
                res = await ac.get(self.test_api, headers=headers)
            self.log.info(f"COMPARING status_code: {res.status_code} VS 200")
            self.assertEqual(res.status_code, 200)
            res_json = res.json()
            projects = res_json.get('result')
            self.log.info(f"Total projects get in API: {len(projects)}")
            all_project = self.test.get_projects()
            self.log.info(f"COMPARING LENGTH: {len(projects)} VS {len(all_project)}")
            self.assertEqual(len(projects), len(all_project))
        except Exception as e:
            self.log.error(f"ERROR: {e}")
            raise e

    async def test_02_platform_user_get_list(self):
        self.log.info("test_02_platform_user_get_list".center(80, '-'))
        payload = {
            "username": "jzhang21",
            "password": "Indoc1234567!"
        }
        token = self.test.auth(payload)
        self.log.info(f"GET API: {self.test_api}")
        try:
            async with AsyncClient(app=self.app, base_url="http://test") as ac:
                headers = {'Authorization': 'Bearer ' + token}
                res = await ac.get(self.test_api, headers=headers)
            self.log.info(f"COMPARING status_code: {res.status_code} VS 200")
            self.assertEqual(res.status_code, 200)
            res_json = res.json()
            projects = res_json.get('result')
            self.log.info(f"Listed projects: {projects}")
            self.log.info(f"COMPARING LENGTH: {len(projects)} 3")
            self.assertEqual(len(projects), 3)
        except Exception as e:
            self.log.error(f"ERROR: {e}")
            raise e
