import unittest
import time
import os
from unittest import mock
from .prepare_test import SetupTest
from .logger import Logger
from unittest.mock import patch
from requests.models import Response
import json

# cases for HPC are: all, auth, job, node, partition
case = 'all'
def create_resposne(code, content):
        the_response = Response()
        the_response.status_code = code
        the_response._content = content
        the_response.json()
        return the_response

@unittest.skipUnless(case == 'all' or case == 'auth', 'specified cases')
class TestHPCAuth(unittest.TestCase):
    log = Logger(name='test_hpc_auth.log')
    test = SetupTest(log)
    app = test.client
    test_api = "/v1/hpc/auth"
    token = test.auth()

    @patch('app.resources.hpc.requests.post')
    def test_01_hpc_auth(self, mock_post):
        self.log.info('\n')
        self.log.info("test_01_hpc_auth".center(80, '-'))
        payload = {
                "token_issuer": 'host',
                "username": 'username',
                "password": 'password'
                }
        mock_post.return_value = create_resposne(code=200, content=b'{"code": 200,"error_msg":"", "result":{"token": "fake-token"}}')
        try:
            self.log.info(f"POST API: {self.test_api}")
            headers = {'Authorization': 'Bearer ' + self.token}
            res = self.app.post(self.test_api, headers=headers, json=payload)
            self.log.info(f"RESPONSE: {res.text}")
            response = res.json()
            code = response.get('code')
            error = response.get('error_msg')
            token = response.get('result').get('token')
            self.log.info(f"COMPARING TOKEN: {token} VS 'fake-token'")
            self.assertEqual(token, "fake-token")
            self.log.info(f"COMPARING error_msg: {error} VS ''")
            self.assertEqual(error, "")
            self.log.info(f"COMPARING CODE: {code} VS 200")
            self.assertEqual(code, 200)
        except Exception as e:
            self.log.error(f"ERROR test_01_hpc_auth: {e}")
            raise e

@unittest.skipUnless(case == 'all' or case == 'job', 'specified cases')
class TestHPCJob(unittest.TestCase):
    log = Logger(name='test_hpc_job.log')
    test = SetupTest(log)
    app = test.client
    token = test.auth()


    def test_01_hpc_submit_without_script(self):
        self.log.info('\n')
        self.log.info("test_01_hpc_submit_without_script".center(80, '-'))
        payload = {
            "host": "http://host",
            "username": "username",
            "token": "fake-hpc-token",
            "job_info": {'data': 'some-fake-job'}
        }
        try:
            test_api = "/v1/hpc/job"
            self.log.info(f"POST API: {test_api}")
            headers = {'Authorization': 'Bearer ' + self.token}
            res = self.app.post(test_api, headers=headers, json=payload)
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
    
    @patch('app.resources.hpc.requests.post')
    def test_02_hpc_submit_success(self, mock_post):
        self.log.info('\n')
        self.log.info("test_02_hpc_submit_success".center(80, '-'))
        payload = {
            "host": "http://host",
            "username": "username",
            "token": "fake-hpc-token",
            "job_info": { "job": { 
                "name": "unit_test", 
                "account": "sc-users"}, 
                "script": "#!/bin/bash\nsleep 300" }
                }
        mock_post.return_value = create_resposne(code=200, content=b'{"code":200,"error_msg":"","result":{"job_id":15178}}')
        try:
            test_api = "/v1/hpc/job"
            self.log.info(f"POST API: {test_api}")
            headers = {'Authorization': 'Bearer ' + self.token}
            res = self.app.post(test_api, headers=headers, json=payload)
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

    @patch('app.resources.hpc.requests.get')
    def test_03_hpc_get_job_success(self, mock_get):
        self.log.info('\n')
        self.log.info("test_03_hpc_get_job_success".center(80, '-'))
        params = {
            "host": "http://host",
            "username": "username",
            "token": "fake-hpc-token"
        }
        test_api = "/v1/hpc/job/%s".format('12345')
        mock_content = b'{"code":200,"error_msg":"","result":{"job_id":"12345","job_state":"COMPLETED","standard_error":"","standard_input":"","standard_output":""}}'
        self.log.info(f"MOCK content: {mock_content}")
        mock_get.return_value = create_resposne(code=200, content=mock_content)
        try:
            self.log.info(f"POST API: {test_api}")
            headers = {'Authorization': 'Bearer ' + self.token}
            res = self.app.get(test_api, headers=headers, params=params)
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
            self.log.error(f"ERROR test_03_hpc_get_job_success: {e}")
            raise e        

    @patch('app.resources.hpc.requests.get')
    def test_04_hpc_get_job_wrong_id(self, mock_get):
        self.log.info('\n')
        self.log.info("test_04_hpc_get_job_wrong_id".center(80, '-'))
        try:
            params = {
                "host": "http://host",
                "username": "username",
                "token": "fake-hpc-token"
            }
            test_api = "/v1/hpc/job/%s".format('123')
            mock_response = {"code":500,"error_msg":"Retrieval of HPC job info failed: Status: 500. Error: {\n   \"meta\": {\n     \"plugin\": {\n       \"type\": \"openapi\\/v0.0.36\",\n       \"name\": \"REST v0.0.36\"\n     },\n     \"Slurm\": {\n       \"version\": {\n         \"major\": 20,\n         \"micro\": 7,\n  \"minor\": 11\n       },\n       \"release\": \"20.11.7\"\n     }\n   },\n   \"errors\": [\n     {\n       \"error\": \"_handle_job_get: unknown job 15179\",\n       \"error_code\": 0\n     }\n   ],\n   \"jobs\": [\n   ]\n }","result":[]}
            mock_content = json.dumps(mock_response).encode()
            self.log.info(f"mock content: {mock_content}")
            mock_get.return_value = create_resposne(code=200, content=mock_content)
            self.log.info(f"POST API: {test_api}")
            headers = {'Authorization': 'Bearer ' + self.token}
            res = self.app.get(test_api, headers=headers, params=params)
            self.log.info(f"RESPONSE: {res.text}")
            response = res.json()
            code = response.get('code')
            error = response.get('error_msg')
            self.log.info(f"COMPARING error_msg: {error} VS 'Job ID not found'")
            self.assertEqual(error, "Job ID not found")
            self.log.info(f"COMPARING CODE: {code} VS 404")
            self.assertEqual(code, 404)
        except Exception as e:
            self.log.error(f"ERROR test_04_hpc_get_job_wrong_id: {e}")
            raise e

    @patch('app.resources.hpc.requests.post')
    def test_05_hpc_submit_without_protocol(self, mock_post):
        self.log.info('\n')
        self.log.info("test_05_hpc_submit_without_protocol".center(80, '-'))
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
            test_api = "/v1/hpc/job"
            self.log.info(f"POST API: {test_api}")
            headers = {'Authorization': 'Bearer ' + self.token}
            res = self.app.post(test_api, headers=headers, json=payload)
            self.log.info(f"RESPONSE: {res.text}")
            response = res.json()
            code = response.get('code')
            error = response.get('error_msg')
            result = response.get('result')
            self.log.info(f"COMPARING code: {code} VS 400")
            self.assertEqual(code, 400)
            self.log.info(f"COMPARING error_msg: {error} VS 'HPC protocal required'")
            self.assertEqual(error, "HPC protocal required")
        except Exception as e:
            self.log.error(f"ERROR test_05_hpc_submit_without_protocol: {e}")
            raise e

    @patch('app.resources.hpc.requests.get')
    def test_06_hpc_get_job_without_protocol(self, mock_get):
        self.log.info('\n')
        self.log.info("test_06_hpc_get_job_without_protocol".center(80, '-'))
        try:
            params = {
                "host": "host",
                "username": "username",
                "token": "fake-hpc-token"
            }
            test_api = "/v1/hpc/job/%s".format('123')
            mock_response = {"code":500,"error_msg":"Retrieval of HPC job info failed: Status: 500. Error: {\n   \"meta\": {\n     \"plugin\": {\n       \"type\": \"openapi\\/v0.0.36\",\n       \"name\": \"REST v0.0.36\"\n     },\n     \"Slurm\": {\n       \"version\": {\n         \"major\": 20,\n         \"micro\": 7,\n  \"minor\": 11\n       },\n       \"release\": \"20.11.7\"\n     }\n   },\n   \"errors\": [\n     {\n       \"error\": \"_handle_job_get: unknown job 15179\",\n       \"error_code\": 0\n     }\n   ],\n   \"jobs\": [\n   ]\n }","result":[]}
            mock_content = json.dumps(mock_response).encode()
            self.log.info(f"mock content: {mock_content}")
            mock_get.return_value = create_resposne(code=200, content=mock_content)
            self.log.info(f"POST API: {test_api}")
            headers = {'Authorization': 'Bearer ' + self.token}
            res = self.app.get(test_api, headers=headers, params=params)
            self.log.info(f"RESPONSE: {res.text}")
            response = res.json()
            code = response.get('code')
            error = response.get('error_msg')
            self.log.info(f"COMPARING error_msg: {error} VS 'HPC protocal required'")
            self.assertEqual(error, "HPC protocal required")
            self.log.info(f"COMPARING CODE: {code} VS 400")
            self.assertEqual(code, 400)
        except Exception as e:
            self.log.error(f"ERROR test_06_hpc_get_job_without_protocol: {e}")
            raise e

@unittest.skipUnless(case == 'all' or case == 'node', 'specified cases')
class TestHPCNode(unittest.TestCase):
    log = Logger(name='test_hpc_node.log')
    test = SetupTest(log)
    app = test.client
    token = test.auth()

    @patch('app.resources.hpc.requests.get')
    def test_01_hpc_list_nodes(self, mock_get):
        self.log.info('\n')
        self.log.info("test_01_hpc_list_nodes".center(80, '-'))
        params = {
            "host": "http://host",
            "username": "username",
            "token": "fake-hpc-token"
            }
        mock_get.return_value = create_resposne(code=200, content=b'{"code": 200,"error_msg": "","result": [{"hostname1": {"cores": 42,"cpu": 200,"free_memory": 100000,"gpus": 8,"threads": 6,"state": "idle"}},{"hostname2": {"cores": 20,"cpu": 100,"free_memory": 200000,"gpus": 4,"threads": 2,"state": "down"}}]}')
        try:
            test_api = "/v1/hpc/nodes"
            self.log.info(f"GET API: {test_api}")
            self.log.info(f"GET PARAMS: {params}")
            headers = {'Authorization': 'Bearer ' + self.token}
            res = self.app.get(test_api, headers=headers, params=params)
            self.log.info(f"RESPONSE: {res.text}")
            response = res.json()
            code = response.get('code')
            error = response.get('error_msg')
            result = response.get('result')
            exp_node1 = {"hostname1":{"cores":42,"cpu":200,"free_memory":100000,"gpus":8,"threads":6,"state":"idle"}}
            exp_node2 = {"hostname2":{"cores":20,"cpu":100,"free_memory":200000,"gpus":4,"threads":2,"state":"down"}}
            self.log.info(f"COMPARING result: {exp_node1} IN {result}")
            self.assertIn(exp_node1, result)
            self.log.info(f"COMPARING result: {exp_node2} IN {result}")
            self.assertIn(exp_node2, result)
            self.log.info(f"COMPARING CODE: {code} VS 200")
            self.assertEqual(code, 200)
        except Exception as e:
            self.log.error(f"ERROR test_01_hpc_list_nodes: {e}")
            raise e

    @patch('app.resources.hpc.requests.get')
    def test_02_hpc_get_node(self, mock_get):
        self.log.info('\n')
        self.log.info("test_02_hpc_get_node".center(80, '-'))
        params = {
            "host": "http://host",
            "username": "username",
            "token": "fake-hpc-token"
            }
        mock_get.return_value = create_resposne(code=200, content=b'{"code": 200,"error_msg": "","result": [{"hostname1": {"cores": 42,"cpu": 200,"free_memory": 100000,"gpus": 8,"threads": 6,"state": "idle"}}]}')
        try:
            node_name = "fake_name"
            test_api = f"/v1/hpc/nodes/{node_name}"
            self.log.info(f"GET API: {test_api}")
            self.log.info(f"GET PARAMS: {params}")
            headers = {'Authorization': 'Bearer ' + self.token}
            res = self.app.get(test_api, headers=headers, params=params)
            self.log.info(f"RESPONSE: {res.text}")
            response = res.json()
            code = response.get('code')
            error = response.get('error_msg')
            result = response.get('result')
            exp_node1 = {"hostname1":{"cores":42,"cpu":200,"free_memory":100000,"gpus":8,"threads":6,"state":"idle"}}
            self.log.info(f"COMPARING result: {exp_node1} IN {result}")
            self.assertIn(exp_node1, result)
            self.log.info(f"COMPARING CODE: {code} VS 200")
            self.assertEqual(code, 200)
        except Exception as e:
            self.log.error(f"ERROR test_02_hpc_get_node: {e}")
            raise e

    @patch('app.resources.hpc.requests.get')
    def test_03_hpc_get_node_wrong_name(self, mock_get):
        self.log.info('\n')
        self.log.info("test_03_hpc_get_node_wrong_name".center(80, '-'))
        params = {
            "host": "http://host",
            "username": "username",
            "token": "fake-hpc-token"
            }
        mock_get.return_value = create_resposne(code=200, content=b'{"code": 404, "error_msg": "Invalid node name specified", "result": ""}')
        try:
            node_name = "wrong_name"
            test_api = f"/v1/hpc/nodes/{node_name}"
            self.log.info(f"GET API: {test_api}")
            self.log.info(f"GET PARAMS: {params}")
            headers = {'Authorization': 'Bearer ' + self.token}
            res = self.app.get(test_api, headers=headers, params=params)
            self.log.info(f"RESPONSE: {res.text}")
            response = res.json()
            code = response.get('code')
            error = response.get('error_msg')
            self.log.info(f"COMPARING result: 'Node name not found' IN '{error}'")
            self.assertIn('Node name not found', error)
            self.log.info(f"COMPARING CODE: {code} VS 404")
            self.assertEqual(code, 404)
        except Exception as e:
            self.log.error(f"ERROR test_03_hpc_get_node_wrong_name: {e}")
            raise e

    @patch('app.resources.hpc.requests.get')
    def test_04_hpc_list_nodes_without_protocol(self, mock_get):
        self.log.info('\n')
        self.log.info("test_04_hpc_list_nodes_without_protocol".center(80, '-'))
        params = {
            "host": "host",
            "username": "username",
            "token": "fake-hpc-token"
            }
        mock_get.return_value = create_resposne(code=200, content=b'{"code": 200,"error_msg": "","result": [{"hostname1": {"cores": 42,"cpu": 200,"free_memory": 100000,"gpus": 8,"threads": 6,"state": "idle"}},{"hostname2": {"cores": 20,"cpu": 100,"free_memory": 200000,"gpus": 4,"threads": 2,"state": "down"}}]}')
        try:
            test_api = "/v1/hpc/nodes"
            self.log.info(f"GET API: {test_api}")
            self.log.info(f"GET PARAMS: {params}")
            headers = {'Authorization': 'Bearer ' + self.token}
            res = self.app.get(test_api, headers=headers, params=params)
            self.log.info(f"RESPONSE: {res.text}")
            response = res.json()
            code = response.get('code')
            error = response.get('error_msg')
            self.log.info(f"COMPARING error: {error} IN 'HPC protocal required'")
            self.assertIn(error, 'HPC protocal required')
            self.log.info(f"COMPARING CODE: {code} VS 400")
            self.assertEqual(code, 400)
        except Exception as e:
            self.log.error(f"ERROR test_04_hpc_list_nodes_without_protocol: {e}")
            raise e

    @patch('app.resources.hpc.requests.get')
    def test_05_hpc_get_node_without_protocol(self, mock_get):
        self.log.info('\n')
        self.log.info("test_05_hpc_get_node_without_protocol".center(80, '-'))
        params = {
            "host": "host",
            "username": "username",
            "token": "fake-hpc-token"
            }
        mock_get.return_value = create_resposne(code=200, content=b'{"code": 200,"error_msg": "","result": [{"hostname1": {"cores": 42,"cpu": 200,"free_memory": 100000,"gpus": 8,"threads": 6,"state": "idle"}}]}')
        try:
            node_name = "fake_name"
            test_api = f"/v1/hpc/nodes/{node_name}"
            self.log.info(f"GET API: {test_api}")
            self.log.info(f"GET PARAMS: {params}")
            headers = {'Authorization': 'Bearer ' + self.token}
            res = self.app.get(test_api, headers=headers, params=params)
            self.log.info(f"RESPONSE: {res.text}")
            response = res.json()
            code = response.get('code')
            error = response.get('error_msg')
            self.log.info(f"COMPARING result: {error} IN 'HPC protocal required'")
            self.assertIn(error, 'HPC protocal required')
            self.log.info(f"COMPARING CODE: {code} VS 400")
            self.assertEqual(code, 400)
        except Exception as e:
            self.log.error(f"ERROR test_05_hpc_get_node_without_protocol: {e}")
            raise e

@unittest.skipUnless(case == 'all' or case == 'partition', 'specified cases')
class TestHPCPartition(unittest.TestCase):
    log = Logger(name='test_hpc_partition.log')
    test = SetupTest(log)
    app = test.client
    token = test.auth()

    @patch('app.resources.hpc.requests.get')
    def test_01_hpc_list_partitions(self, mock_get):
        self.log.info('\n')
        self.log.info("test_01_hpc_list_partitions".center(80, '-'))
        params = {
            "host": "http://host",
            "username": "username",
            "token": "fake-hpc-token"
            }
        
        mock_get.return_value = create_resposne(code=200, content=b'{"code": 200,"error_msg": "","result": [{"partition_name1": {"nodes": ["s-sc-gpu01, s-sc-gpu03"],"tres": "cpu=1500,mem=20000M,node=2,billing=3000"}},{"partition_name2": {"nodes": ["s-sc-gpu02"],"tres": "cpu=2500,mem=10000M,node=1,billing=2000"}}]}')
        try:
            test_api = "/v1/hpc/partitions"
            self.log.info(f"GET API: {test_api}")
            self.log.info(f"GET PARAMS: {params}")
            headers = {'Authorization': 'Bearer ' + self.token}
            res = self.app.get(test_api, headers=headers, params=params)
            self.log.info(f"RESPONSE: {res.text}")
            response = res.json()
            code = response.get('code')
            error = response.get('error_msg')
            result = response.get('result')
            exp_partition1 = {"partition_name1": {"nodes": ["s-sc-gpu01, s-sc-gpu03"],"tres": "cpu=1500,mem=20000M,node=2,billing=3000"}}
            exp_partition2 = {"partition_name2": {"nodes": ["s-sc-gpu02"],"tres": "cpu=2500,mem=10000M,node=1,billing=2000"}}
            self.log.info(f"COMPARING result: {exp_partition1} IN {result}")
            self.assertIn(exp_partition1, result)
            self.log.info(f"COMPARING result: {exp_partition2} IN {result}")
            self.assertIn(exp_partition2, result)
            self.log.info(f"COMPARING CODE: {code} VS 200")
            self.assertEqual(code, 200)
        except Exception as e:
            self.log.error(f"ERROR test_01_hpc_list_partitions: {e}")
            raise e

    @patch('app.resources.hpc.requests.get')
    def test_02_hpc_get_partition(self, mock_get):
        self.log.info('\n')
        self.log.info("test_02_hpc_get_partition".center(80, '-'))
        params = {
            "host": "http://host",
            "username": "username",
            "token": "fake-hpc-token"
            }
        mock_get.return_value = create_resposne(code=200, content=b'{"code": 200,"error_msg": "","result": [{"partition_name1": {"nodes": ["s-sc-gpu01, s-sc-gpu03"],"tres": "cpu=1500,mem=20000M,node=2,billing=3000"}}]}')
        try:
            partition_name = "fake_name"
            test_api = f"/v1/hpc/partitions/{partition_name}"
            self.log.info(f"GET API: {test_api}")
            self.log.info(f"GET PARAMS: {params}")
            headers = {'Authorization': 'Bearer ' + self.token}
            res = self.app.get(test_api, headers=headers, params=params)
            self.log.info(f"RESPONSE: {res.text}")
            response = res.json()
            code = response.get('code')
            error = response.get('error_msg')
            result = response.get('result')
            exp_partition1 = {"partition_name1": {"nodes": ["s-sc-gpu01, s-sc-gpu03"],"tres": "cpu=1500,mem=20000M,node=2,billing=3000"}}
            self.log.info(f"COMPARING result: {exp_partition1} IN {result}")
            self.assertIn(exp_partition1, result)
            self.log.info(f"COMPARING CODE: {code} VS 200")
            self.assertEqual(code, 200)
        except Exception as e:
            self.log.error(f"ERROR test_02_hpc_get_partition: {e}")
            raise e

    @patch('app.resources.hpc.requests.get')
    def test_03_hpc_get_partition_wrong_name(self, mock_get):
        self.log.info('\n')
        self.log.info("test_03_hpc_get_partition_wrong_name".center(80, '-'))
        params = {
            "host": "http://host",
            "username": "username",
            "token": "fake-hpc-token"
            }
        mock_get.return_value = create_resposne(code=200, content=b'{"code": 404, "error_msg": "Invalid partition name specified", "result": ""}')
        try:
            partition_name = "wrong_name"
            test_api = f"/v1/hpc/partitions/{partition_name}"
            self.log.info(f"GET API: {test_api}")
            self.log.info(f"GET PARAMS: {params}")
            headers = {'Authorization': 'Bearer ' + self.token}
            res = self.app.get(test_api, headers=headers, params=params)
            self.log.info(f"RESPONSE: {res.text}")
            response = res.json()
            code = response.get('code')
            error = response.get('error_msg')
            self.log.info(f"COMPARING result: 'Partition name not found' IN '{error}'")
            self.assertIn('Partition name not found', error)
            self.log.info(f"COMPARING CODE: {code} VS 404")
            self.assertEqual(code, 404)
        except Exception as e:
            self.log.error(f"ERROR test_03_hpc_get_partition_wrong_name: {e}")
            raise e

    @patch('app.resources.hpc.requests.get')
    def test_04_hpc_list_partitions_without_protocol(self, mock_get):
        self.log.info('\n')
        self.log.info("test_04_hpc_list_partitions_without_protocol".center(80, '-'))
        params = {
            "host": "host",
            "username": "username",
            "token": "fake-hpc-token"
            }
        
        mock_get.return_value = create_resposne(code=200, content=b'{"code": 200,"error_msg": "","result": [{"partition_name1": {"nodes": ["s-sc-gpu01, s-sc-gpu03"],"tres": "cpu=1500,mem=20000M,node=2,billing=3000"}},{"partition_name2": {"nodes": ["s-sc-gpu02"],"tres": "cpu=2500,mem=10000M,node=1,billing=2000"}}]}')
        try:
            test_api = "/v1/hpc/partitions"
            self.log.info(f"GET API: {test_api}")
            self.log.info(f"GET PARAMS: {params}")
            headers = {'Authorization': 'Bearer ' + self.token}
            res = self.app.get(test_api, headers=headers, params=params)
            self.log.info(f"RESPONSE: {res.text}")
            response = res.json()
            code = response.get('code')
            error = response.get('error_msg')
            self.log.info(f"COMPARING error: {error} IN 'HPC protocal required'")
            self.assertIn(error, 'HPC protocal required')
            self.log.info(f"COMPARING CODE: {code} VS 400")
            self.assertEqual(code, 400)
        except Exception as e:
            self.log.error(f"ERROR test_04_hpc_list_partitions_without_protocol: {e}")
            raise e

    @patch('app.resources.hpc.requests.get')
    def test_05_hpc_get_partition_without_protocol(self, mock_get):
        self.log.info('\n')
        self.log.info("test_05_hpc_get_partition_without_protocol".center(80, '-'))
        params = {
            "host": "host",
            "username": "username",
            "token": "fake-hpc-token"
            }
        mock_get.return_value = create_resposne(code=200, content=b'{"code": 200,"error_msg": "","result": [{"partition_name1": {"nodes": ["s-sc-gpu01, s-sc-gpu03"],"tres": "cpu=1500,mem=20000M,node=2,billing=3000"}}]}')
        try:
            partition_name = "fake_name"
            test_api = f"/v1/hpc/partitions/{partition_name}"
            self.log.info(f"GET API: {test_api}")
            self.log.info(f"GET PARAMS: {params}")
            headers = {'Authorization': 'Bearer ' + self.token}
            res = self.app.get(test_api, headers=headers, params=params)
            self.log.info(f"RESPONSE: {res.text}")
            response = res.json()
            code = response.get('code')
            error = response.get('error_msg')
            self.log.info(f"COMPARING result: {error} IN 'HPC protocal required'")
            self.assertIn(error, 'HPC protocal required')
            self.log.info(f"COMPARING CODE: {code} VS 400")
            self.assertEqual(code, 400)
        except Exception as e:
            self.log.error(f"ERROR test_05_hpc_get_partition_without_protocol: {e}")
            raise e
