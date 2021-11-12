import unittest
import time
import os
from unittest import mock
from .prepare_test import SetupTest
from .logger import Logger
from unittest.mock import patch
from requests.models import Response
import json

def create_resposne(code, content):
        the_response = Response()
        the_response.status_code = code
        the_response._content = content
        the_response.json()
        return the_response

class TestHPCAuth(unittest.TestCase):
    log = Logger(name='test_hpc_auth.log')
    test = SetupTest(log)
    app = test.client
    test_api = "/v1/hpc/auth"
    token = test.auth()

    @patch('app.resources.helpers.requests.get')
    def test_01_hpc_auth(self, mock_get):
        self.log.info('\n')
        self.log.info("test_01_hpc_auth".center(80, '-'))
        params = {
                "token_issuer": 'host',
                "username": 'username',
                "password": 'password'
                }
        mock_get.return_value = create_resposne(code=200, content=b'{"code": 200,"error_msg":"", "result":{"result":{"token": "fake-token"}}}')
        try:
            self.log.info(f"POST API: {self.test_api}")
            headers = {'Authorization': 'Bearer ' + self.token}
            res = self.app.get(self.test_api, headers=headers, params=params)
            self.log.info(f"RESPONSE: {res.text}")
            response = res.json()
            code = response.get('code')
            error = response.get('error_msg')
            token = response.get('result')
            self.log.info(f"COMPARING TOKEN: {token} VS 'fake-token'")
            self.assertEqual(token, "fake-token")
            self.log.info(f"COMPARING error_msg: {error} VS ''")
            self.assertEqual(error, "")
            self.log.info(f"COMPARING CODE: {code} VS 200")
            self.assertEqual(code, 200)
        except Exception as e:
            self.log.error(f"ERROR test_01_hpc_auth: {e}")
            raise e

class TestHPCSubmit(unittest.TestCase):
    log = Logger(name='test_hpc_submit.log')
    test = SetupTest(log)
    app = test.client
    test_api = "/v1/hpc/job"
    token = test.auth()


    def test_01_hpc_submit_without_script(self):
        self.log.info('\n')
        self.log.info("test_01_hpc_submit_without_script".center(80, '-'))
        payload = {
            "host": "host",
            "username": "username",
            "token": "fake-hpc-token",
            "job_info": {'data': 'some-fake-job'}
        }
        try:
            self.log.info(f"POST API: {self.test_api}")
            headers = {'Authorization': 'Bearer ' + self.token}
            res = self.app.post(self.test_api, headers=headers, json=payload)
            self.log.info(f"RESPONSE: {res.text}")
            response = res.json()
            code = response.get('code')
            error = response.get('error_msg')
            result = response.get('result')
            self.log.info(f"COMPARING result: {result} VS "+"{}")
            self.assertEqual(result, {})
            self.log.info(f"COMPARING error_msg: {error} VS 'Missing script'")
            self.assertEqual(error, "Missing script")
            self.log.info(f"COMPARING CODE: {code} VS 400")
            self.assertEqual(code, 400)
        except Exception as e:
            self.log.error(f"ERROR test_01_hpc_submit_without_script: {e}")
            raise e
    
    @patch('app.resources.helpers.requests.post')
    def test_02_hpc_submit_success(self, mock_post):
        self.log.info('\n')
        self.log.info("test_02_hpc_submit_success".center(80, '-'))
        payload = {
            "host": "host",
            "username": "username",
            "token": "fake-hpc-token",
            "job_info": { "job": { 
                "name": "unit_test", 
                "account": "sc-users"}, 
                "script": "#!/bin/bash\nsleep 300" }
                }
        mock_post.return_value = create_resposne(code=200, content=b'{"code":200,"error_msg":"","result":{"job_id":15178}}')
        try:
            self.log.info(f"POST API: {self.test_api}")
            headers = {'Authorization': 'Bearer ' + self.token}
            res = self.app.post(self.test_api, headers=headers, json=payload)
            self.log.info(f"RESPONSE: {res.text}")
            response = res.json()
            code = response.get('code')
            error = response.get('error_msg')
            result = response.get('result')
            self.log.info(f"COMPARING result: {result} VS 'job_id': 15178")
            self.assertEqual(result, {"job_id":15178})
            self.log.info(f"COMPARING error_msg: {error} VS ''")
            self.assertEqual(error, "")
            self.log.info(f"COMPARING CODE: {code} VS 200")
            self.assertEqual(code, 200)
        except Exception as e:
            self.log.error(f"ERROR test_02_hpc_submit_success: {e}")
            raise e


class TestHPCGetJob(unittest.TestCase):
    log = Logger(name='test_hpc_get_job.log')
    test = SetupTest(log)
    app = test.client
    test_api = "/v1/hpc/job/%s"
    token = test.auth()

    @patch('app.resources.helpers.requests.get')
    def test_01_hpc_get_job_success(self, mock_get):
        self.log.info('\n')
        self.log.info("test_01_hpc_get_job_success".center(80, '-'))
        params = {
            "host": "host",
            "username": "username",
            "token": "fake-hpc-token"
        }
        url = self.test_api.format('12345')
        mock_content = b'{"code":200,"error_msg":"","result":{"job_id":"12345","job_state":"COMPLETED","standard_error":"","standard_input":"","standard_output":""}}'
        self.log.info(f"MOCK content: {mock_content}")
        mock_get.return_value = create_resposne(code=200, content=mock_content)
        try:
            self.log.info(f"POST API: {url}")
            headers = {'Authorization': 'Bearer ' + self.token}
            res = self.app.get(self.test_api, headers=headers, params=params)
            self.log.info(f"RESPONSE: {res.text}")
            response = res.json()
            code = response.get('code')
            error = response.get('error_msg')
            result = response.get('result')
            job_id = result.get('job_id')
            job_state = result.get('job_state')
            self.log.info(f"COMPARING error_msg: {error} VS ''")
            self.assertEqual(error, "")
            self.log.info(f"COMPARING CODE: {code} VS 200")
            self.assertEqual(code, 200)
            self.log.info(f"COMPARING result: {job_id} VS '12345'")
            self.assertEqual(job_id, '12345')
            self.log.info(f"COMPARING result: {job_state} VS 'COMPLETED'")
            self.assertEqual(job_state, 'COMPLETED')
        except Exception as e:
            self.log.error(f"ERROR test_01_hpc_get_job_success: {e}")
            raise e        

    @patch('app.resources.helpers.requests.get')
    def test_02_hpc_get_job_wrong_id(self, mock_get):
        self.log.info('\n')
        self.log.info("test_02_hpc_get_job_wrong_id".center(80, '-'))
        try:
            params = {
                "host": "host",
                "username": "username",
                "token": "fake-hpc-token"
            }
            url = self.test_api.format('123')
            mock_response = {"code":500,"error_msg":"Retrieval of HPC job info failed: Status: 500. Error: {\n   \"meta\": {\n     \"plugin\": {\n       \"type\": \"openapi\\/v0.0.36\",\n       \"name\": \"REST v0.0.36\"\n     },\n     \"Slurm\": {\n       \"version\": {\n         \"major\": 20,\n         \"micro\": 7,\n  \"minor\": 11\n       },\n       \"release\": \"20.11.7\"\n     }\n   },\n   \"errors\": [\n     {\n       \"error\": \"_handle_job_get: unknown job 15179\",\n       \"error_code\": 0\n     }\n   ],\n   \"jobs\": [\n   ]\n }","result":[]}
            mock_content = json.dumps(mock_response).encode()
            self.log.info(f"mock content: {mock_content}")
            mock_get.return_value = create_resposne(code=200, content=mock_content)
        
            self.log.info(f"POST API: {url}")
            headers = {'Authorization': 'Bearer ' + self.token}
            res = self.app.get(self.test_api, headers=headers, params=params)
            self.log.info(f"RESPONSE: {res.text}")
            response = res.json()
            code = response.get('code')
            error = response.get('error_msg')
            result = response.get('result')
            job_id = result.get('job_id')
            job_state = result.get('job_state')
            self.log.info(f"COMPARING error_msg: {error} VS 'Job ID not found'")
            self.assertEqual(error, "Job ID not found")
            self.log.info(f"COMPARING CODE: {code} VS 404")
            self.assertEqual(code, 404)
        except Exception as e:
            self.log.error(f"ERROR test_02_hpc_get_job_wrong_id: {e}")
            raise e        

